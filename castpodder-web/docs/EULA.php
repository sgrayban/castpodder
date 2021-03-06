<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
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
<title>CastPodder - User Guide</title>
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
<?php require("Software_License_Agreement.html");?>
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
