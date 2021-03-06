<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<!--                                                       -->
<!--          CastPodder project                           -->
<!--          ==========================================   -->
<!--          programming: Scott Grayban                   -->
<!--          GUI/design:                                  -->
<!--          Content Strategist:                          -->
<!--          Based on the idea of Adam Curry & Dave Winer -->
<!--                                                       -->
<!-- $Id: index.php 338 2006-07-23 03:00:09Z sgrayban $ -->
  <head>
    <title>CastPodder - FAQ</title>
  <?php require("../includes/metatags.php");?>
  </head>
  <body>
    <table cellpadding="0" cellspacing="0" border="0" width="100%">
      <tbody>
        <tr>
          <td class="column_left" valign="top" align="right">
            <!-- left side -->
            <div class="navigation">
              <b>Users online</b>: <font color="#8B0000"><?php include("../includes/onlinesql.php"); ?></font>
              <br />
              <?php require("../includes/menu.php");?>
              <br />
              <?php require("../includes/developers.php");?>
              <br /><br />
              <?php require("../includes/resources.php");?>
            </div>
          </td>
          <td width="50%" valign="top" align="center">
            <!-- body -->
<?php require("../includes/translate.php");?>
<?php require("faq.php");?>
            </center>
          </td>
          <!-- End main content -->
          <td class="column_right" valign="top" align="left">
            <!-- right side -->
<?php require("../includes/news.php");?>
<?php require("../includes/rss-feed.php");?>
          </td>
        </tr>
        <tr>
          <td class="footer" rowSpan="1" colspan="3" valign="top" align="center">
            <!-- footer -->
<?php require("../includes/footer.php");?>
          </td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
