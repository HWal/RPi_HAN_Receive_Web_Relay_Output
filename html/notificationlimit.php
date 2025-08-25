<!DOCTYPE html>

<!-- Enter or edit active power limit for triggering mobile notification -->

<html lang=en-EN>

    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content ="width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1">
        <meta http-equiv="refresh" content="1200">
        <title>Limit input</title>
        <style>
        body {
            background-color: white;
            text-align:center;
            font-family: Arial, Helvetica, Sans-Serif;
            Color: #000088;
        }
        </style>
    </head>

    <body>

    <center><H3>Enter the preferred notification limit.</center></H3></center>
    <center><H3>If Watt hours used during one hour</center></H3></center>
    <center><H3>exceeds the limit, an email reminder</center></H3></center>
    <center><H3>is sent to the address given in</center></H3></center>
    <center><H3>.../pi/Python_AMS/threemaxes.py</H3></center>

        <table align="center" border="1" height="180" width="300" cellpadding="2" bgcolor="#F5F9FA"><tr><td>

        <?php
        $path = '/var/www/html/data/notificationlimit.data';
        // Data has been entered and form submitted
        if (isset($_POST['newval'])) {
            $fh = fopen($path,"wa");
            $string = $_POST['newval'];
            // Correct the input if user has entered illegal value < 100
            if (($string < 100) || ($string == '')) {
                $string = '100';
            }
            fwrite($fh,$string); // Write to file
            fclose($fh);         // Close file
            echo "<center><h3>Limit updated</h3>";
            echo "New value: ".$string."Wh<br><br>";
            echo "<b><a href=\"index.html\">Back</a></b></center>";

        // Data has not yet been entered and submitted
        } else {
            ?>
            <?php
            // Read and display the current limit
            $fh = fopen($path,"r");
            $current = fread($fh, filesize($path));
            echo "<font color=\"red\">";
            echo "<center>Current limit: ".$current."Wh<br><br></center>";
            echo "</font>";
            fclose($fh);
            ?>
            <center>
            <!-- Get user data and submit the form
            A filename.php between the action= quotes: php is in a separate file
            Nothing between the action= quotes: php code is in the same file
            Here the input is submitted to the php on this url (page) -->
            <form action="" method="POST">
                Enter new: (100-99999)<br>
                <!-- <input type="number" name="newval" value="0" min="100" max="99999" maxlength="5"><br><br> -->
                <input type="text" name="newval" pattern="[0]*[1-9][0-9]*" title="Kun heltall 100-99999" maxlength="5">
                <input type="submit" value="Submit">
            </form>
            <br><b><a href="index.html">Back</a></b>
            </center>
        <?php } ?>

        </td></tr></table>
    </body>

</html>
