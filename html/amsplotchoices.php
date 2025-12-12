<!DOCTYPE html>

<!-- Enter or edit choices for plotting of stored AMS meter data -->

<html lang=en-EN>

    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content ="width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1">
        <meta http-equiv="refresh" content="1200">
        <title>Ams plot parameters input</title>
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

    <center><H3>Plot data from the AMS meter</H3></center>
    <!-- <center>Enter plot parameters:<br><br></center> -->

        <?php
        // Location for storage of plot choices
        $choicespath = '/var/www/html/data/amsplotchoices.data';

        // Data has been entered and form submitted
        if ($_SERVER["REQUEST_METHOD"] == "POST") {
            $string1 = $_POST['string1'];
            $string2 = $_POST['string2'];
            $string3 = $_POST['string3'];
            $string4 = $_POST['string4'];
            $string5 = $_POST['string5'];
            $string6 = $_POST['string6'];
            $string7 = $_POST['string7'];
            $string8 = $_POST['string8'];
            $string9 = $_POST['string9'];

            // Validate the entered date and write to file if valid
            if (checkdate((int)$string3, (int)$string4, (int)$string2) && ((int)$string9 > (int)$string8)) {
                $combinedstring = $string1.','.$string2.','.$string3.','.$string4.','.$string5.','.$string6.','.$string7.','.$string8.','.$string9;
                $fh = fopen($choicespath,"wa");                // Open file
                fwrite($fh,$combinedstring);                   // Write to file
                fclose($fh);                                   // Close file
                echo "<center>Parameters set.</center>";
                // echo "<b>Current values: </b>$combinedstring<br><br>";
                echo "<center><b><a href=\"plot.php\"><br>Click here and wait for graph...</a></b></center>";
                echo "<br>or<br>";
                echo "<center><b><a href=\"amsplotchoices.php\"><br>Go back</a></b></center>";
            } else {
                echo "<center>Invalid date and/or hour interval entered! Parameters not changed.</center><br>";
                echo "<center><b><a href=\"index.html\">Go back</a></b></center>";
            }
        } else {
            // Read already stored parameters to be shown as defaults in the html form
            $fh = fopen($choicespath,"r");                     // Open file
            $currchoices = fread($fh, filesize($choicespath)); // Read file
            fclose($fh);                                       // Close file
            $choicesarray = explode(',', $currchoices);
        ?>

            <center>
            <!-- Get user data and submit the form
            A filename.php between the action= quotes: php code is in a separate file
            Nothing between the action= quotes: php code is in the same (this) file -->
            <table align="center" border="1" height="180" width="420" cellpadding="2" bgcolor="#F5F9FA">
            <form action="" method="POST">
                <tr height="20"><td colspan="2" ><center><b>Enter plot parameters:</b></center></td></tr>
                <tr height="20"><td><label for="string1">Path to log files:</label></td>
                <td align="center"><input type="text" value="<?php echo $choicesarray[0]; ?>" size="25" maxlength="50" id="path" name="string1"></td></tr>
                <tr height="20"><td><label for="string2">Year (YYYY):</label></td>
                <td align="center"><input type="number" style="width: 50px;" value="<?php echo $choicesarray[1]; ?>" min="2000" max="2100" id="year" name="string2"></td></tr>
                <tr height="20"><td><label for="string3">Month (MM):</label></td>
                <td align="center"><input type="number" style="width: 50px;" value="<?php echo $choicesarray[2]; ?>" min="1" max="12" id="month" name="string3"></td></tr>
                <tr height="20"><td><label for="string4">Day (DD):</label></td>
                <td align="center"><input type="number" style="width: 50px;" value="<?php echo $choicesarray[3]; ?>" min="1" max="31" id="day" name="string4"></td></tr>
                <tr height="20"><td><label for="string5">Power graph (Y/y/N/n):</label></td>
                <td align="center"><input type="text" value="<?php echo $choicesarray[4]; ?>" size="1" maxlength="1" id="powergraph" name="string5"></td></tr>
                <tr height="20"><td><label for="string6">Volt graph (Y/y/N/n):</label></td>
                <td align="center"><input type="text" value="<?php echo $choicesarray[5]; ?>" size="1" maxlength="1" id="voltgraph" name="string6"></td></tr>
                <tr height="20"><td><label for="string7">Current graph (Y/y/N/n):</label></td>
                <td align="center"><input type="text" value="<?php echo $choicesarray[6]; ?>" size="1" maxlength="1" id="currentgraph" name="string7"></td></tr>
                <tr height="20"><td><label for="string8">Start hour (00-23):</label></td>
                <td align="center"><input type="number" style="width: 50px;" value="<?php echo $choicesarray[7]; ?>" min="0" max="23" id="starthour" name="string8"></td></tr>
                <tr height="20"><td><label for="string9">End hour (01-24):</label></td>
                <td align="center"><input type="number" style="width: 50px;" value="<?php echo $choicesarray[8]; ?>" min="1" max="24" id="endthour" name="string9"></td></tr>
                <tr height="20"><td align="center" colspan="2"><input type="submit" value="Submit"></td></tr>
            </form>
            </table>
            <br><b><a href="index.html">Go back without changes</a></b>
            </center>

        <?php } ?>
    </body>
</html>
