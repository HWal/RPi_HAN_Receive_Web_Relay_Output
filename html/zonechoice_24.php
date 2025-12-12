<!DOCTYPE html>

<!-- Enter or edit zone (Norway) for displaying El-spotprices -->

<html lang=en-EN>

    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content ="width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1">
        <meta http-equiv="refresh" content="1200">
        <title>Select zone</title>
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

    <center><H3>At the moment only Norway zones<br><br>are available, with prices in NOK</H3></center>

        <table align="center" border="1" height="180" width="300" cellpadding="2" bgcolor="#F5F9FA"><tr><td>

        <?php
        $path = '/var/www/html/data/zonechoice.data';

        // Data has been entered and form submitted
        if (isset($_POST['newzone'])) {
            $fh = fopen($path,"wa");
            $string = $_POST['newzone'];
            // Correct the entry if user has entered an illegal zone
            if ($string != 'NO1' && $string != 'NO2' && $string != 'NO3' && $string != 'NO4' && $string != 'NO5') {
                $string = 'NO5';
                echo "<center><b>No valid zone Entered. Corrected to NO5</b><br><br>";
            }
            fwrite($fh,$string); // Write to file
            fclose($fh);         // Close file
            echo "<center><b>Price zone updated</b><br><br>";
            echo "New value: ".$string."<br><br>";
            echo "<b><a href=\"spotprices_NOK_tomorrow_24.html\">Back</a></b></center>";

        // Data has not yet been entered and submitted
        } else {
            ?>
            <?php
            // Read from file and display the current zone
            $fh = fopen($path,"r");
            $current = fread($fh, filesize($path));
            echo "<font color=\"red\">";
            echo "<center>Current zone: ".$current."<br><br></center>";
            echo "</font>";
            fclose($fh);
            ?>
            <center>
            <!-- Get user data and submit the form
            A filename.php between the action= quotes: php is in a separate file
            Nothing between the action= quotes: php code is in the same file
            Here the input is submitted to the php on this url (page) -->
            <form action="" method="POST">
                Enter new: (NO1 ... NO5)<br><br>
                <input type="text" name="newzone" value="NO_" size="3" maxlength="3"><br><br>
                <input type="submit" value="Submit">
            </form>
            <br><b><a href="spotprices_NOK_tomorrow_24.html">Back</a></b>
            </center>
        <?php } ?>

        </td></tr></table>
    </body>

</html>
