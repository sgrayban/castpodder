<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<!--                                                       -->
<!--          CastPodder project                           -->
<!--          ==========================================   -->
<!--          programming: Scott Grayban                   -->
<!--          programming: Andrew Grumet                   -->
<!--          GUI/design:                                  -->
<!--          Content Strategist:                          -->
<!--          Based on the idea of Adam Curry & Dave Winer -->
<!--                                                       -->
<!-- $Id: thank_you.php 3 2005-10-20 07:57:14Z sgrayban $ -->
<!--                                                       -->
  <head>
    <title>CastPodder - A Linux podcast agregrator</title>

  <?php require("../includes/metatags.php");?>
  </head>
  <body>
    <table cellpadding="0" cellspacing="0" border="0" width="100%">
      <tbody>
        <tr>
          <td class="column_left" valign="top" align="right">
            <!-- left side -->
            <div class="navigation">
              <?php require("../includes/menu.php");?>
              <br />
              <br />
              <?php require("../includes/developers.php");?>
              <br />
              <br />
              <?php require("../includes/subscription.php");?>
              <br />
              <br />
              <?php require("../includes/resources.php");?>
            </div>
          </td>
          <td width="50%" valign="top" align="center">
            <!-- body -->
            <br>
            <center>
              <img src="/images/splashscreen.png">
              <br>
              <small> CastPodder&reg;&trade; is a Registered Trademark<br> CastPodder&reg;&trade; is Copyright &copy; 2005 CastPodder Team</small>
              <h3>
                 Thank you for donating to CastPodder. Your contributions will help keep the project alive.
              </h3>
              <br>
<?php
// ===== Configure Script ==========

// The email address where you want the order information to be sent to

$toEmail = "sgrayban@castpodder.net";

// The email address you want the order email to be sent from

$fromEmail = "sgrayban@castpodder.net";

// ===== Do Not Edit Below This Line ==========

$body1 =

    "Subscription Receipt\n\n" .
    "Credit Card Status ... $credit_card_processed" . "<br>" .
    "Total Billed ............... " . "$" . $total . " USD<br>" .
    "Order Number .......... $order_number" . "<br>" .
    "Product ID ............... $merchant_product_id" . "<br>" .
    "Card Holder Name .... $card_holder_name" . "<br>" .
    "Email Address ........... $email" . "<br>" .
    "Phone Number .......... $phone" . "<br>" .
    "Street Address .......... $street_address" . "<br>" .
    "City, State Zip ........... $city, $state $zip" . "<br>" .
    "Country .................... $country" . "<br>" .
    "MD5 Key ................... $key" . "<br>";

$body2 =

    "Dear $card_holder_name,\n\n" .
    "Here is your Subscription Receipt\n\n" .
    "Credit Card Status .. $credit_card_processed \n" .
    "Total Billed ........ " . "$" . $total . " USD \n" .
    "Order Number ........ $order_number \n" .
    "Product ID .......... $merchant_product_id \n\n" .
    "Card Holder Name .... $card_holder_name \n" .
    "Email Address ....... $email \n" .
    "Phone Number ........ $phone \n" .
    "Street Address ...... $street_address \n" .
    "City, State Zip ..... $city, $state $zip \n" .
    "Country ............. $country \n" .
    "MD5 Key ............. $key \n\n" .

    "Thank you for making a subscription donation to CastPodder. We really appreciate it!\n\nThe CastPodder Team.\n\n";

//Send me a copy
 mail("$toEmail", "New Order: $merchant_product_id", $body2, "FROM: $fromEmail");

//Send a copy to the donator
 mail("$email", "Castpodder Subscription: $merchant_product_id", $body2, "FROM: $fromEmail");
?>
              <u>Your 2Checkout Reciept will be emailed to you.</u>
              <table>
                <tbody>
                  <tr>
                    <td>
                      <!-- 2co passback -->
<?php echo $body1;?>
                    </td>
                  </tr>
                </tbody>
              </table>
               You can return to the project website<a href="http://www.castpodder.net/">here</a>.
              <br>
              <br>
               Thanks !! The CastPodder Team
            </center>
          </td>
          <!-- End main content -->
          <td class="column_right" valign="top" align="left">
            <!-- right side -->
<?php require("../includes/news.php");?>
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
