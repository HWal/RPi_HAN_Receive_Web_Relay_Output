<!DOCTYPE html>
<!-- Control relays for water and panel heaters -->

<html lang=en-EN>

    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content ="width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1">
        <meta http-equiv="refresh" content="60">
        <title>Raspberry Pi gpio</title>
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
    <table align="center" border="1" height="200" width="300" cellpadding="2" bgcolor="#F5F9FA"><tr><td>
        <b>Heater control relays</b><br><br>
        <table align="center" border="1" height= 80 width="200" cellpadding="2" bgcolor="#F5F8FA"><tr><td>

        <!-- php code to generate the initial page -->
        <?php
        $val_array = array(0,0);

        for ( $i= 0; $i<2; $i++) {
            //set the pin's mode to output and read them
            system("gpio mode ".$i." out");
            exec ("gpio read ".$i, $val_array[$i], $return );
        }
        echo("<br>");
        //for loop to read values and display
        $i =0;
        for ($i = 0; $i < 2; $i++) {
            // Relay
            if ($i == 0 ) {
                echo("<b>Panel: </b>");
            }
            if ($i == 1 ) {
                echo("<b>Water: </b>");
            }
            //if off
            if ($val_array[$i][0] == 0 ) {
                echo ("<img id='button_".$i."' src='img/green_".$i.".jpg'.' width=36 height=14' onclick='change_pin (".$i.");'/>");
                echo "<br><br>";
            }
            //if on
            if ($val_array[$i][0] == 1 ) {
                echo ("<img id='button_".$i."' src='img/red_".$i.".jpg'.' width=36 height=13' onclick='change_pin (".$i.");'/>");
                echo "<br><br>";
            }	 
        }
        ?>

        </td></tr></table>


        <!-- javascript inside the webpage -->
        <script>
﻿        //TheFreeElectron 2015, http://www.instructables.com/member/TheFreeElectron/
        //JavaScript, uses pictures as buttons, sends and receives values to/from the Rpi
        //These are all the buttons
        var button_0 = document.getElementById("button_0");
        var button_1 = document.getElementById("button_1");

        //Create an array for easy access later
        var Buttons = [ button_0, button_1];

        //This function is asking for gpio.php, receiving datas and updating the index.php pictures
        function change_pin ( pic ) {
        var data = 0;

        //send request with the pic number to gpio.php for changes
            var request = new XMLHttpRequest();
            request.open( "GET" , "gpio.php?pic=" + pic, true);
            request.send(null);

            //receive information
            request.onreadystatechange = function () {

            if (request.readyState == 4 && request.status == 200) {
                data = request.responseText;
                //update the index pic
                if ( !(data.localeCompare("0")) ){
                    Buttons[pic].src = "img/green_"+pic+".jpg";
                    Buttons[pic].width = 36;
                    Buttons[pic].height = 14;
                }
                else if ( !(data.localeCompare("1")) ) {
                    Buttons[pic].src = "img/red_"+pic+".jpg";
                    Buttons[pic].width = 36;
                    Buttons[pic].height = 13;
                }
                else if ( !(data.localeCompare("fail"))) {
                    alert ("Something went wrong!" );
                    return ("fail");			
                }
                else {
                    alert ("Something went wrong!" );
                    return ("fail"); 
                }
            }
            //test if fail
            else if (request.readyState == 4 && request.status == 500) {
                alert ("server error");
                return ("fail");
            }
            else if (request.readyState == 4 && request.status != 200 && request.status != 500 ) { 
                alert ("Something went wrong!");
                return ("fail"); }
            }	

        return 0;
        }
        </script>




        <script type = "text/javascript">
        if(typeof(EventSource) !== "undefined") {
          var eSource1 = new EventSource("currpower.php");
          eSource1.onmessage = function(event) {
            document.getElementById("actPowerPlus_SSE").innerHTML = event.data;
          }
        } else {
          document.getElementById("msgDate_SSE").innerHTML = "No browser support."
        }
        </script>



        <br><b><i>Total active power+ (W):</b><div id = "actPowerPlus_SSE"></div></i>
        <br>To operate, click on the green (On) <br> or red (Off) status indicator.<br>
        <br><b>Panel heater:</b><br>Controls power to panel heater in the east wall of the living room. Status <b>On</b> indicates the heater is powered.<br>
        <br><b>Water heater:</b><br>Controls 2000W power to the 200L water heater in the laundry room. Status <b>On</b> indicates the heater is powered.<br>

        <br><b><center><a href="index.html">Back</a></center></b>
    </td></tr></table>
    </body>

</html>