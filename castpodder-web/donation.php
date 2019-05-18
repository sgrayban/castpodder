<?php
header("Cache-Control: no-cache, must-revalidate");
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");
header('HTTP/1.0 301 Moved Permanently');
header('Location: http://forum.castpodder.net/index.php?pid=3');
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<html>
<!--                                                       -->
<!--          CastPodder project                              -->
<!--          ==========================================   -->
<!--          programming: Scott Grayban                   -->
<!--          programming: Andrew Grumet                   -->
<!--          GUI/design:                                  -->
<!--          Content Strategist:                          -->
<!--          Based on the idea of Adam Curry & Dave Winer -->
<!--                                                       -->
<!-- $Id: donation.php 356 2006-08-01 10:08:29Z sgrayban $ -->

  <head>
    <title>CastPodder - Donate</title>
  <?php require("includes/metatags.php");?>
 </head>
  <body>
    <table cellpadding="0" cellspacing="0" border="0" width="100%">
      <tbody>
        <tr>
          <td class="column_left" valign="top" align="right">
            <!-- left side -->
            <div class="navigation">
              <b>Users online</b>: <font color="#8B0000"><?php include("includes/onlinesql.php"); ?></font>
              <br />
              <?php require("includes/menu.php");?>
              <br /><br />
              <?php require("includes/developers.php");?>
              <br /><br />
              <?php require("includes/resources.php");?>
            </div>
          </td>
          <td width="50%" valign="top" align="center">
            <!-- body -->
<?php require("includes/donations.php");?>
<br /><br /><br />
<?php require("includes/supporters.php");?>
            </center>
          </td>
          <!-- End main content -->
          <td class="column_right" valign="top" align="left">
            <!-- right side -->
<?php require("includes/news.php");?>
<?php require("includes/rss-feed.php");?>
          </td>
        </tr>
        <tr>
          <td class="footer" rowSpan="1" colspan="3" valign="top" align="center">
            <!-- footer -->
<?php require("includes/footer.php");?>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
