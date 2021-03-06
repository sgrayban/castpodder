#
# Copyright (c) 2005-2006 Scott Grayban and the CastPodder Team
#
# $Id: iPodderWindows.py 147 2006-11-07 08:17:03Z sgrayban $

"""
CastPodder is Copright © 2005-2006 Scott Grayban
Read the file Software_License_Agreement.txt for more info.

"""
__license__ = "Commercial"

import sys
import wx
import wx.xrc as xrc
import listctrl  as  listmix
from   gui import images
import gui.tree
from   ipodder.contrib import feedparser
import platform
import os.path
from   localization import LanguageModule
import sys
if sys.version_info[0] == 2 and sys.version_info[1] <= 3:
    import webbrowser
else:
    from ipodder.contrib import webbrowser

# Skinning
from   gui.skin import STRIPE_EVEN_COLOR, STRIPE_ODD_COLOR

FEEDWINDOW_AUTH_TAB = 2

class AutoWidthListCtrl(wx.ListCtrl,listmix.ListCtrlAutoWidthMixin):
    def __init__(self):
        p = wx.PreListCtrl()
        self.PostCreate(p)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class MainPanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self):
        p = wx.PrePanel()
        self.PostCreate(p)
        self.initialized = False
        
    def InitSortMixin(self,list,sm_up,sm_dn):
        self.initialized = True
        self.list = list
        self.sm_up = sm_up
        self.sm_dn = sm_dn
        self.ResetSortMixin()
        listmix.ColumnSorterMixin.__init__(self, 4)
        #Re-assign this method so we can re-stripe after a sort.
        self.list.SortItems = self.SortItems
       
    def ResetSortMixin(self):
        if not self.initialized:
            return
        self.itemDataMap = {}
        for n in range(self.list.GetItemCount()):
            mb = self.list.GetItem(n,2).GetText()
            if mb == "":
                mbstring = "0.0"
            else:
                mbstring = mb
            self.itemDataMap[self.list.GetItemData(n)] = (
                self.list.GetItem(n,0).GetText(),
                self.list.GetItem(n,1).GetText(),
                float(mbstring),
                self.list.GetItem(n,3).GetText()
            )
        if hasattr(self,"_col"):
            self.GetListCtrl().SortItems(self.GetColumnSorter())
        
    def GetListCtrl(self):
        return self.list

    #Supports re-striping
    def SortItems(self,columnSorter):
        wx.ListCtrl.SortItems(self.list,columnSorter)
        for i in range(self.list.GetItemCount()):
            if i % 2 == 0:
                self.list.SetItemBackgroundColour(i,STRIPE_ODD_COLOR)
            else:
                self.list.SetItemBackgroundColour(i,STRIPE_EVEN_COLOR)

    #Slight variation on the library version: bash col 0 to lowercase first.
    def __MyColumnSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]

        if col == 0:
            item1 = item1.lower()
            item2 = item2.lower()

        #i18n stuff crashes on mac
	cmpVal = cmp(item1, item2)

        # If the items are equal then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = apply(cmp, self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal
    
    def GetColumnSorter(self):
        return self.__MyColumnSorter

    # Used by the ColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def GetState(self):
        return (self._col,self._colSortFlag[self._col])

    def SetState(self,state):
        self._col = state[0]
        self._colSortFlag[state[0]] = state[1]
        self.SortListItems()

class FeedWindow(wx.Dialog):
    def __init__(self):
        p = wx.PreDialog()
        self.PostCreate(p)
        wx.EVT_BUTTON(self, xrc.XRCID("FEEDWINCANCEL"),self.OnCancel)
        wx.EVT_BUTTON(self, xrc.XRCID("FEEDWINOK"),self.OnSaveSettings)
        wx.EVT_CHECKBOX(self, xrc.XRCID("FEEDWINCLEANUP"),self.OnCleanupChk)
        self.initialized = False
        self.feedinfo = None
        self.parent = None

    def _(self,key):
        return self.m_stringtable.GetText(self.m_currentlanguage,key)

    def ValueControl(self, id, label):
        xrc.XRCCTRL(self, id).SetLabel(self._(label))

    def SetLanguages(self):
        self.ValueControl("FEEWDINCANCEL", "str_cancel")
        self.ValueControl("FEEDWINOK", "str_ok")
        self.ValueControl("FEEDWINCLEANUP", "str_auto_delete")
        self.ValueControl("FEEDWINCLEANUPDAYSLBL", "str_days_old")
        self.ValueControl("LBL_FEEDWINTITLE", "str_title")
        self.ValueControl("LBL_FEEDWINURL", "str_url")
        self.ValueControl("LBL_FEEDWINUSERNAME", "str_username")
        self.ValueControl("LBL_FEEDWINPASSWORD", "str_password")
        self.notebook.SetPageText(0, self._("str_general"))
        self.notebook.SetPageText(1, self._("str_authentication"))

    def Init(self, ipodder):
        self.ipodder = ipodder
        self.feedwintitle = xrc.XRCCTRL(self,"FEEDWINTITLE")
        self.feedwinurl = xrc.XRCCTRL(self,"FEEDWINURL")
        self.feedwinusername = xrc.XRCCTRL(self,"FEEDWINUSERNAME")
        self.feedwinpassword = xrc.XRCCTRL(self,"FEEDWINPASSWORD")
        self.feedwingotosubs = xrc.XRCCTRL(self,"FEEDWINGOTOSUBS")
        self.feedwincleanup = xrc.XRCCTRL(self,"FEEDWINCLEANUP")
        self.feedwincleanupdays = xrc.XRCCTRL(self,"FEEDWINCLEANUPMAXDAYS")
        self.notebook = xrc.XRCCTRL(self,"FEEDWINNOTEBOOK")
        self.initialized = True
        self.m_currentlanguage = self.ipodder.config.screen_language
        xrc.XRCCTRL(self,"FEEDWINOK").MoveBeforeInTabOrder(xrc.XRCCTRL(self,"FEEDWINCANCEL"))
        self.m_stringtable = LanguageModule.StringTable(self.m_currentlanguage)        

    def SetParent(self,parent):
        self.parent = parent

    def OnCleanupChk(self,event):
        self.feedwincleanupdays.Enable(event.IsChecked())
    
    def OnCancel(self, event):
        self.feedinfo = None
        self.Show(0)

    def UpdateFeed(self,feedinfo,ipodder,newfeed=None):
        if not self.initialized:
            self.Init(ipodder)
        if feedinfo:
            self.SetLabel(self._("str_edit_feed"))
            self.feedinfo = feedinfo
            self.feedwinurl.SetValue(feedinfo.url)
            self.feedwintitle.SetValue(feedinfo.title)
            #self.feedwinusername.SetValue(feedinfo.username)
            #self.feedwinpassword.SetValue(feedinfo.password)
            self.feedwincleanup.SetValue(feedinfo.cleanup_enabled)
            self.feedwincleanupdays.SetValue("%d" % feedinfo.cleanup_max_days)
            self.feedwincleanupdays.Enable(feedinfo.cleanup_enabled)
        else:
            self.feedinfo = None
            self.SetLabel(self._("str_add_feed_dialog"))
            self.feedwinurl.SetValue(newfeed)
            self.feedwintitle.SetValue("")
            #self.feedwinusername.SetValue("")
            #self.feedwinpassword.SetValue("")
            self.feedwincleanup.SetValue(False)
            self.feedwincleanupdays.SetValue("14")
            self.feedwincleanupdays.Enable(False)
        self.feedwingotosubs.Enable(not self.parent.IsSubscriptionsTabSelected())
        self.GetSizer().Fit(self)
        self.feedwintitle.SetEditable(False) #temporary
        self.feedwintitle.Enable(False) #temporary
        self.feedwinurl.SetFocus()
        self.ShowModal()

    def OnSaveSettings(self,event):
        url = self.feedwinurl.GetValue().strip()
        title = self.feedwintitle.GetValue().strip()
        #username = self.feedwinusername.GetValue().strip()
        #password = self.feedwinpassword.GetValue().strip()
        cleanup_enabled = self.feedwincleanup.GetValue()
        daystxt = self.feedwincleanupdays.GetValue().strip()
        
	# validation
        try:
            cleanup_max_days = int(daystxt)
        except ValueError:
            alert = wx.MessageDialog(self, "Please set the days old value to a number", style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()
            self.feedwincleanup.SetValue(True)
            self.feedwincleanupdays.Enable(True)
            self.feedwincleanupdays.SetFocus()
            return
        # end validation

        if self.feedinfo and ['disabled','unsubscribed'].count(self.feedinfo.sub_state) == 0:
            self.feedinfo.url = url
            #self.feedinfo.username = username
            #self.feedinfo.password = password
            self.feedinfo.cleanup_enabled = cleanup_enabled
            self.feedinfo.cleanup_max_days = cleanup_max_days
            self.parent.UpdateFeedsListItem(self.feedinfo)
            self.parent.RefreshFeedWindowData(self.feedinfo)
        else:
            self.parent.AddFeed(url,title=url,raise_tab=self.feedwingotosubs.IsChecked())
        self.Show(0)

class MyURLDropTarget(wx.PyDropTarget):
    def __init__(self, window):
        wx.PyDropTarget.__init__(self)
        self.window = window
        self.data = wx.URLDataObject();
        self.SetDataObject(self.data)

    def OnDragOver(self, x, y, d):
        return wx.DragLink

    def OnData(self, x, y, d):
        if not self.GetData():
            return wx.DragNone
        url = self.data.GetURL()
        self.window.AppendText(url + "\n")
        return d

class PrefsDialog(wx.Dialog):
    def __init__(self):
        p = wx.PreDialog()
        self.PostCreate(p)

    def _(self,key):
        return self.m_stringtable.GetText(self.m_currentlanguage,key)
        
    def ValueControl(self, id, label):
        xrc.XRCCTRL(self, id).SetLabel(self._(label))
        
        
    def SetLanguages(self):
        GENERAL = 0
        THREADS = 1
        NETWORKING = 2
        PLAYER = 3
        FEEDMANAGER = 4
        ADVANCED = 5
        
        self.SetLabel(self._("str_preferences"))
        
        tabsdict = {
            FEEDMANAGER : "str_feed_manager",
            GENERAL : "str_general",
            THREADS : "str_threads",
            NETWORKING : "str_networking",
            PLAYER : "str_player",
            ADVANCED : "str_advanced"
        }
        en_loaded = False
        for key in tabsdict.keys():
            try:
                self.notebook.SetPageText(key, self._(tabsdict[key]))
            except AssertionError:
                """Unfortunately wide characters and Notebooks don't mix well
                on Mac, so we fall back to English."""
                if not en_loaded:
                    self.m_stringtable.LoadLanguage(LanguageModule.ENGLISH)
                    en_loaded = True
                self.notebook.SetPageText(key,self.m_stringtable.GetText(LanguageModule.ENGLISH,tabsdict[key]))

        self.ValueControl("PRF_FEEDMANAGER_BTN_PODNOVA", "str_feedmanager_btn_podnova")
        self.ValueControl("PRF_FEEDMANAGER_BTN_GIGADIAL", "str_feedmanager_btn_gigadial")
        self.ValueControl("PRF_TXT_FEEDMANAGER", "str_txt_feedmanager")
        self.ValueControl("PRF_FEEDMANAGER_ENABLE", "str_feedmanager_enable")
        self.ValueControl("PRF_LBL_GEN_OPTIONS", "str_gen_options_expl")
        self.ValueControl("HIDE_ON_STARTUP", "str_hide_on_startup")
        self.ValueControl("HIDE_TRAY_ICON", "str_hide_tray_icon")
        self.ValueControl("SCAN_ON_STARTUP", "str_run_check_startup")
        self.ValueControl("CHKUPDATE_ON_STARTUP", "str_chkupdate_on_startup")
        self.ValueControl("PLAY_ON_DOWNLOAD", "str_play_after_download")
        self.ValueControl("PRF_PLAYER", "str_choose_a_player")
        self.ValueControl("PRF_LBL_STORAGE_LOC_STORAGE", "str_location_and_storage")
        self.ValueControl("PRF_LBL_STORAGE_STOP", "str_stop_downloading")
        self.ValueControl("PRF_LBL_DOWNLOAD_FOLDER", "str_download_folder")
        self.ValueControl("PREFSBROWSE", "str_browse")
        
        self.ValueControl("PRF_MULTIPLE_DOWNLOAD", "str_multiple_download")
        self.ValueControl("PRF_MAX_FEEDSCANS", "str_max_feedscans")
        self.ValueControl("PRF_MAX_DOWNLOADS", "str_max_downloads")

        self.ValueControl("PRFCORALIZING", "str_coralize_urls")
        self.ValueControl("PRFUSEPROXY", "str_proxy_server")
        self.ValueControl("PRF_PROXY_ADDRESS", "str_proxy_address")
        self.ValueControl("PRF_PROXY_PORT", "str_proxy_port")
        self.ValueControl("PRF_PROXY_USERNAME", "str_username")	
        self.ValueControl("PRF_PROXY_PASSWORD", "str_password")

        self.ValueControl("PRF_POWER_USER", "str_options_power_users")
        self.ValueControl("DLCOMMANDENABLE", "str_run_command_download")
        self.ValueControl("PRF_RCMD_FULL_PATH", "str_rcmd_full_path")
        self.ValueControl("PRF_RCMD_PODCAST_NAME", "str_rcmd_podcast_name")

        self.ValueControl("PRF_OTHER_ADV_OPTION", "str_other_advanced_options")
        self.ValueControl("SHOWLOGPAGE", "str_show_log")

        self.ValueControl("PREFSSAVE", "str_save")
        self.ValueControl("PREFSCANCEL", "str_cancel")
        

        #"No player"
	# Not needed anymore -- DO NOT USE
        #self.playerbox.SetItemLabel(1,self.m_stringtable.GetText(self.m_currentlanguage,"str_no_player"))
        
    def OnEnableProxy(self, event):
        if self.enableProxy.IsChecked()==True:
            self.proxyPort.Enable(True)
            self.proxyHost.Enable(True)
            self.proxyUsername.Enable(True)	
            self.proxyPassword.Enable(True)
        else:
            self.proxyPort.Enable(False)
            self.proxyHost.Enable(False)
            self.proxyUsername.Enable(False)	
            self.proxyPassword.Enable(False)	
        self.OnPrefChange(event)
    
    def HideOnStartup(self, event):
	#shade the hide tray icon or not
        if self.hideOnStartup.IsChecked()==True:
            self.hideTrayIcon.Enable(False)
        else:
            self.hideTrayIcon.Enable(True)
        self.OnPrefChange(event)
    
    def OnBtnPodNova(self, event):
        webbrowser.open("http://my.podnova.com")
    
    def OnBtnGigaDial(self, event):
        webbrowser.open("http://www.gigadial.net/public")
    
    def Init(self,ipodder,gui):
        self.ipodder = ipodder
        self.gui = gui
        self.m_currentlanguage = self.ipodder.config.screen_language
        self.m_stringtable = LanguageModule.StringTable(self.m_currentlanguage)

        self.player_types = ["XMMSPlayer", "BMPPlayer", "NoPlayer"]
        self.notebook = xrc.XRCCTRL(self, "NOTEBOOK")
        self.hideOnStartup = xrc.XRCCTRL(self, "HIDE_ON_STARTUP")
        self.hideTrayIcon = xrc.XRCCTRL(self, "HIDE_TRAY_ICON")
        self.scanOnStartup = xrc.XRCCTRL(self, "SCAN_ON_STARTUP")
        self.chkupdateOnStartup = xrc.XRCCTRL(self, "CHKUPDATE_ON_STARTUP")
        self.playOnDownload = xrc.XRCCTRL(self, "PLAY_ON_DOWNLOAD")
        self.dlCommandEnable = xrc.XRCCTRL(self, "DLCOMMANDENABLE")
        self.dlCommand = xrc.XRCCTRL(self, "DLCOMMAND")
        self.showLogPage = xrc.XRCCTRL(self, "SHOWLOGPAGE")
        self.prefsSave = xrc.XRCCTRL(self, "PREFSSAVE")
        self.prefsCancel = xrc.XRCCTRL(self, "PREFSCANCEL")
        self.downloaddir = xrc.XRCCTRL(self, "PREFSDOWNLOADDIR")
        self.browse = xrc.XRCCTRL(self,"PREFSBROWSE")
        self.numFeedScanThreads = xrc.XRCCTRL(self, "NUMFEEDSCANTHREADS")
        self.numDownloadThreads = xrc.XRCCTRL(self, "NUMDOWNLOADTHREADS")
        self.maxHarddiscSizeMB = xrc.XRCCTRL(self, "MAX_HARDDISC_SIZE_MB")
        self.playerbox = xrc.XRCCTRL(self, "PRF_PLAYER")
        self.feedmanager_btn_podnova = xrc.XRCCTRL(self, "PRF_FEEDMANAGER_BTN_PODNOVA")
        self.feedmanager_btn_gigadial = xrc.XRCCTRL(self, "PRF_FEEDMANAGER_BTN_GIGADIAL")
        self.feedmanager_enable = xrc.XRCCTRL(self, "PRF_FEEDMANAGER_ENABLE")
        self.feedmanagerOPML = xrc.XRCCTRL(self, "PRF_FEEDMANAGER_OPML")
        self.feedmanagerLbl = xrc.XRCCTRL(self, "LBL_FEEDMANAGER_OPML_URL")
        self.feedmanagerOPML.SetDropTarget(MyURLDropTarget(self.feedmanagerOPML))

        # Networking
        self.corlizeUrls = xrc.XRCCTRL(self, "PRFCORALIZING")
        self.corlizeUrls.SetValue(self.ipodder.config.coralize_urls)

        self.enableProxy = xrc.XRCCTRL(self, "PRFUSEPROXY")
        self.proxyHost = xrc.XRCCTRL(self, "TXTPRFPROXYHOST")
        self.proxyPort = xrc.XRCCTRL(self, "TXTPRFPROXYPORT")
        self.proxyUsername = xrc.XRCCTRL(self, "TXTPRFPROXYUSERNAME")	
        self.proxyPassword = xrc.XRCCTRL(self, "TXTPRFPROXYPASSWORD")

        self.Bind(wx.EVT_CHECKBOX, self.HideOnStartup, self.hideOnStartup)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.hideTrayIcon)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.scanOnStartup)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.chkupdateOnStartup)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.playOnDownload)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.dlCommandEnable)
        self.Bind(wx.EVT_COMBOBOX, self.OnPrefChange, self.numFeedScanThreads)
        self.Bind(wx.EVT_COMBOBOX, self.OnPrefChange, self.numDownloadThreads)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.maxHarddiscSizeMB)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.dlCommand)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.showLogPage)
        self.Bind(wx.EVT_BUTTON, self.OnPrefsSave, self.prefsSave)
        self.Bind(wx.EVT_BUTTON, self.OnPrefsCancel, self.prefsCancel)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.downloaddir)
        self.Bind(wx.EVT_BUTTON, self.OnPrefsBrowse, self.browse)
        self.Bind(wx.EVT_CHECKBOX, self.OnPrefChange, self.corlizeUrls)
        self.Bind(wx.EVT_RADIOBOX, self.OnPrefChange, self.playerbox)
        self.Bind(wx.EVT_CHECKBOX, self.OnEnableProxy, self.enableProxy)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.proxyHost)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.proxyPort)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.proxyUsername)	
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.proxyPassword)
        self.Bind(wx.EVT_TEXT, self.OnPrefChange, self.feedmanagerOPML)
        self.Bind(wx.EVT_CHECKBOX, self.OnFeedmanagerEnableChk, self.feedmanager_enable)
        self.Bind(wx.EVT_BUTTON, self.OnBtnPodNova, self.feedmanager_btn_podnova)
        self.Bind(wx.EVT_BUTTON, self.OnBtnGigaDial, self.feedmanager_btn_gigadial)
        self.feedmanagerOPML.SetDropTarget(MyURLDropTarget(self.feedmanagerOPML))

        self.ResetPrefs()        
        self.SetLanguages()

        self.SetAcceleratorTable(
            wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, xrc.XRCID("PREFSCANCEL"))
            ]))
            
    def ResetPrefs(self):
        self.hideOnStartup.SetValue(self.ipodder.config.hide_on_startup)
        if self.hideOnStartup is True:
	    self.hideTrayIcon.Enable(False)
        self.scanOnStartup.SetValue(self.ipodder.config.scan_on_startup)
        self.chkupdateOnStartup.SetValue(self.ipodder.config.chkupdate_on_startup)
        self.playOnDownload.SetValue(self.ipodder.config.play_on_download)
        self.dlCommandEnable.SetValue(self.ipodder.config.dl_command_enable)
        self.dlCommand.SetValue(self.ipodder.config.dl_command)
        self.showLogPage.SetValue(self.ipodder.config.show_log_page)
        self.downloaddir.SetValue(unicode(self.ipodder.config.download_dir))
        self.corlizeUrls.SetValue(self.ipodder.config.coralize_urls)
        self.feedmanager_enable.SetValue(self.ipodder.config.feedmanager_enable)
        self.feedmanagerOPML.SetValue(self.ipodder.config.feedmanager_opml_url)
        self.feedmanagerOPML.Enable(self.ipodder.config.feedmanager_enable)
        self.feedmanagerLbl.Enable(self.ipodder.config.feedmanager_enable)
        self.enableProxy.SetValue(self.ipodder.config.use_proxy_server)
        self.proxyPort.SetValue(self.ipodder.config.http_proxy_port)
        self.proxyHost.SetValue(self.ipodder.config.http_proxy_server)
        self.proxyUsername.SetValue(self.ipodder.config.http_proxy_username)	
        self.proxyPassword.SetValue(self.ipodder.config.http_proxy_password)
        if self.ipodder.config.use_proxy_server is False:
            self.proxyPort.Enable(False)
            self.proxyHost.Enable(False)
            self.proxyUsername.Enable(False)	
            self.proxyPassword.Enable(False)
        self.numFeedScanThreads.SetSelection(self.BestComboIntegerIndex(self.numFeedScanThreads,self.ipodder.config.max_scan_jobs))
        self.numDownloadThreads.SetSelection(self.BestComboIntegerIndex(self.numDownloadThreads,self.ipodder.config.max_download_jobs)) 
        self.maxHarddiscSizeMB.SetValue(str(self.ipodder.config.min_mb_free))
        self.SetPlayerBox()
        if platform.system()=='Darwin':
            self.hideOnStartup.Enable(False)
            self.playerbox.EnableItem(0,False) #XMMS
            self.playerbox.EnableItem(1,False) #Beep-Media-Player
        self.prefsSave.Enable(False)

    def BestComboIntegerIndex(self,combo,desired):
        """Return the index of the closest-valued integer.
        Useful when defaulting the selectlist to a possibly non-matching
        desired value."""
        idx = 0
        diff = None
        for i in range(0,combo.GetCount()):
            if diff == None or \
               abs(int(combo.GetString(i)) - desired) < diff:
                idx = i
                diff = abs(int(combo.GetString(i)) - desired)

        return idx
    
    def SetPlayerBox(self):
        """for each player increment +1 starting from 0"""
        player_type = self.ipodder.config.player_type
        if player_type == "XMMSPlayer":
            self.playerbox.SetSelection(0)
        elif player_type == "BMPPlayer":
            self.playerbox.SetSelection(1)
        else: #No Player by default
            self.playerbox.SetSelection(2)

    def OnFeedmanagerEnableChk(self, event):
        self.feedmanagerOPML.Enable(event.IsChecked())
        self.feedmanagerLbl.Enable(event.IsChecked())
        self.OnPrefChange(event)

    def OnShowLogPage(self, event):
        """Adjust the configuration and hide or show the log page."""
        if event.IsChecked(): 
            self.ipodder.config.show_log_page = True
        else: 
            self.ipodder.config.show_log_page = False
        self.ipodder.config.flush()

    def OnPrefsSave(self, event):
        #validate the download directory
        if not os.path.isdir(self.downloaddir.GetValue()):
            message1 = self._("str_bad_directory_pref_1")
            message2 = self._("str_bad_directory_pref_2")
            alert = wx.MessageDialog(self, "%s (%s).  %s" % (message1,self.downloaddir.GetValue(),message2) , style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()
            return

        #validate the integer-valued configuration options
        try:
            int(self.maxHarddiscSizeMB.GetValue())    
        except ValueError:
            message1 = self._("str_bad_megabyte_limit_1")
            message2 = self._("str_bad_megabyte_limit_2")
            alert = wx.MessageDialog(self, "%s (%s).  %s" % (self._("str_bad_megabyte_limit_1"), self.maxHarddiscSizeMB.GetValue(), self._("str_bad_megabyte_limit_2")), style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()            
            return

        #validate the proxy settings
        if self.enableProxy.IsChecked() and (
            self.proxyHost.GetValue().strip() == '' or
            self.proxyHost.GetValue().strip() == 'http://' or
            self.proxyPort.GetValue().strip() == ''):
            alert = wx.MessageDialog(self, self._("str_bad_proxy_pref"), style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()
            return

        if self.enableProxy.IsChecked() and (
            self.proxyUsername.GetValue().strip() != '' and
            self.proxyPassword.GetValue().strip() == '' ):
            alert = wx.MessageDialog(self, self._("str_missing_proxy_password"), style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()
            return
 

        #validate the feed manager url
        if self.feedmanager_enable.IsChecked() and not \
           self.feedmanagerOPML.GetValue().strip().startswith('http://'):
            alert = wx.MessageDialog(self, self._("str_bad_feedmanager_url"), style=wx.OK)
            response = alert.ShowModal()
            alert.Destroy()
            self.feedmanagerOPML.SetValue(self.ipodder.config.feedmanager_opml_url)
            self.feedmanagerOPML.SetFocus()
            self.feedmanagerOPML.SelectAll()
            return

        new_manager = False
        if self.feedmanager_enable.IsChecked() and \
            ( (self.ipodder.config.feedmanager_opml_url != self.feedmanagerOPML.GetValue().strip()) or \
              not self.ipodder.config.feedmanager_enable
              ):
            new_manager = True

        if self.feedmanager_enable.IsChecked() and \
            ( (self.ipodder.config.feedmanager_opml_url != self.feedmanagerOPML.GetValue().strip()) or \
              not self.ipodder.config.feedmanager_enable
              ):
            new_manager = True

        if (self.ipodder.config.feedmanager_enable and \
            not self.feedmanager_enable.IsChecked()):
            self.gui.RemoveManagedFeeds()
        
        self.ipodder.config.download_dir = self.downloaddir.GetValue()
        
        self.ipodder.config.hide_on_startup = self.hideOnStartup.IsChecked()
        self.ipodder.config.hide_tray_icon = self.hideTrayIcon.IsChecked()
        self.ipodder.config.scan_on_startup = self.scanOnStartup.IsChecked()
        self.ipodder.config.chkupdate_on_startup = self.chkupdateOnStartup.IsChecked()
        self.ipodder.config.play_on_download = self.playOnDownload.IsChecked()
        self.ipodder.config.dl_command_enable = self.dlCommandEnable.IsChecked()
        self.ipodder.config.dl_command = self.dlCommand.GetValue()
        self.ipodder.config.show_log_page = self.showLogPage.IsChecked()            
        self.ipodder.config.max_scan_jobs = int(self.numFeedScanThreads.GetValue())
        self.ipodder.config.max_download_jobs = int(self.numDownloadThreads.GetValue())
        self.ipodder.config.min_mb_free = int(self.maxHarddiscSizeMB.GetValue())
        self.ipodder.config.coralize_urls = self.corlizeUrls.IsChecked()

        self.ipodder.config.use_proxy_server = self.enableProxy.IsChecked()
        self.ipodder.config.http_proxy_server = self.proxyHost.GetValue().strip()
        self.ipodder.config.http_proxy_port =  self.proxyPort.GetValue().strip()
        self.ipodder.config.http_proxy_username = self.proxyUsername.GetValue().strip()
        self.ipodder.config.http_proxy_password = self.proxyPassword.GetValue().strip()

        self.ipodder.config.feedmanager_enable = self.feedmanager_enable.IsChecked()
        self.ipodder.config.feedmanager_opml_url = self.feedmanagerOPML.GetValue().strip()
        self.ipodder.config.player_type = self.player_types[self.playerbox.GetSelection()]
        self.ipodder.config.determine_player()
        self.ipodder.config.flush()
        if self.ipodder.config.feedmanager_enable and new_manager:
            self.gui.ReplaceManagedFeeds()
        self.gui.showlogpage(self.ipodder.config.show_log_page)
        self.ipodder.init_proxy_config()
        self.prefsSave.Enable(False)
        self.Show(0)
        
    def OnPrefChange(self, event):
        if not self.prefsSave.IsEnabled():
            self.prefsSave.Enable(True)
    
    def OnPrefsCancel(self,event):
        self.Show(0)
        self.ResetPrefs()

    def OnPrefsBrowse(self,event):
        self.OnPrefChange(event)
        dlg = wx.DirDialog(self,"Choose download directory",self.downloaddir.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.downloaddir.SetValue(dlg.GetPath())
        dlg.Destroy()       


class EncodingDialog(wx.Dialog):
    def __init__(self):
        p = wx.PreDialog()
        self.PostCreate(p)
        self.codecs = [('ascii','English'),\
            ('latin_1','West Europe'),\
            ('utf_8','all languages'),\
            ('cp037','English'),\
            ('cp424','Hebrew'),\
            ('cp437','English'),\
            ('cp500','Western Europe'),\
            ('cp737','Greek'),\
            ('cp775','Baltic languages'),\
            ('cp850','Western Europe'),\
            ('cp852','Central and Eastern Europe'),\
            ('cp855','Bulgarian, Byelorussian, Macedonian, Russian, Serbian'),\
            ('cp856','Hebrew'),\
            ('cp857','Turkish'),\
            ('cp860','Portuguese'),\
            ('cp861','Icelandic'),\
            ('cp862','Hebrew'),\
            ('cp863','Canadian'),\
            ('cp864','Arabic'),\
            ('cp865','Danish, Norwegian'),\
            ('cp869','Greek'),\
            ('cp874','Thai'),\
            ('cp875','Greek'),\
            ('cp1006','Urdu'),\
            ('cp1026','Turkish'),\
            ('cp1140','Western Europe'),\
            ('cp1250','Central and Eastern Europe'),\
            ('cp1251','Bulgarian, Byelorussian, Macedonian, Russian, Serbian'),\
            ('cp1252','Western Europe'),\
            ('cp1253','Greek'),\
            ('cp1254','Turkish'),\
            ('cp1255','Hebrew'),\
            ('cp1256','Arabic'),\
            ('cp1257','Baltic languages'),\
            ('cp1258','Vietnamese'),\
            ('iso8859_2','Central and Eastern Europe'),\
            ('iso8859_3','Esperanto, Maltese'),\
            ('iso8859_4','Baltic languagues'),\
            ('iso8859_5','Bulgarian, Byelorussian, Macedonian, Russian, Serbian'),\
            ('iso8859_6','Arabic'),\
            ('iso8859_7','Greek'),\
            ('iso8859_8','Hebrew'),\
            ('iso8859_9','Turkish'),\
            ('iso8859_10','Nordic languages'),\
            ('iso8859_13','Baltic languages'),\
            ('iso8859_14','Celtic languages'),\
            ('iso8859_15','Western Europe'),\
            ('koi8_r','Russian'),\
            ('koi8_u','Ukrainian'),\
            ('mac_cyrillic','Bulgarian, Byelorussian, Macedonian, Russian, Serbian'),\
            ('mac_greek','Greek'),\
            ('mac_iceland','Icelandic'),\
            ('mac_latin2','Central and Eastern Europe'),\
            ('mac_roman','Western Europe'),\
            ('mac_turkish','Turkish'),\
            ('utf_16','all languages'),\
            ('utf_16_be','all languages'),\
            ('utf_16_le','all languages'),\
            ('utf_7','all languages'),\
        ]
	
    def Init(self,gui):
        self.gui = gui
        self.encodingok = xrc.XRCCTRL(self, "ENCODINGOK")
        self.encodingskip = xrc.XRCCTRL(self, "ENCODINGSKIP")
        self.encodingenc = xrc.XRCCTRL(self, "ENCODINGENC")
        wx.EVT_LISTBOX(self, xrc.XRCID("ENCODINGENC"),self.OnEncoding)
        wx.EVT_BUTTON(self, xrc.XRCID("ENCODINGSKIP"),self.OnSkip)
        wx.EVT_BUTTON(self, xrc.XRCID("ENCODINGOK"),self.OnOk)
        self.encodingtext = xrc.XRCCTRL(self, "ENCODINGTEXT")
        if wx.Platform != '__WXMAC__':
            #Throws an error on Mac for some reason.
            self.encodingtext.SetFont(wx.Font(-1,wx.MODERN,wx.NORMAL,wx.NORMAL))
        self.teststr = None
        self.testenc = None
        self.encodingenc.Clear()
        for enc in self.codecs:
            self.encodingenc.Append("%s (%s)" % enc)
        self.SetAutoLayout(True)
        self.GetSizer().Fit(self)

    def ShowModal(self, teststr, testenc):
        self.SelectEncoding(testenc)
        self.ResetText(teststr, testenc)
        wx.Dialog.ShowModal(self)
        codec = self.codecs[self.encodingenc.GetSelection()]
        return codec[0]
    
    def OnOk(self, event):
        self.EndModal(0)

    def OnSkip(self, event):
        self.SelectEncoding(sys.getdefaultencoding())
        self.EndModal(0)
        
    def OnEncoding(self, event):
        codec = self.codecs[self.encodingenc.GetSelection()]
        self.ResetText(self.teststr,codec[0])
	
    def ResetText(self, teststr, testenc):
        self.teststr = teststr
        self.testenc = testenc
        badbyte = self.badbyte(self.teststr, self.testenc)
        if badbyte == -1:
            self.encodingtext.SetLabel(unicode(self.teststr,self.testenc,'replace'))
            self.encodingok.Enable(True)
        else:            
            format = "%%s\n%%%ds" % (badbyte+2)
            self.encodingtext.SetLabel(format %
                (unicode(self.teststr,self.testenc,'replace'),"^^^"))
            self.encodingok.Enable(False)
        self.GetSizer().Fit(self)

    def SelectEncoding(self, testenc):
        i = 0
        for codec in self.codecs:
            if codec[0] == testenc:
                self.encodingenc.Select(i)
                return
            i += 1

    def badbyte(self,teststr,testenc):
        i=0
        for c in teststr:
            try:
                unicode(c,testenc)
                i += 1
            except UnicodeDecodeError:
                return i
        return -1
