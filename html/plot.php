<!DOCTYPE html>

<!-- Plot graphs -->

<html lang=en-EN>

  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content ="width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1">
    <meta http-equiv="refresh" content="1200">
    <title>Ams plot input</title>
    <style>
    body {
      background-color: white;
      text-align:center;
      font-family: Arial, Helvetica, Sans-Serif;
      Color: #000088;
    }
    img {
      max-width: 70%;  /* Ensures the image doesn't exceed its parent's width */
      height: auto;    /* Maintains the aspect ratio */
      display: block;  /* Optional: removes extra space below the image */
    }
    </style>
  </head>

  <body>

    <!-- Call Python to make the plot files -->
    <?php
    $output = shell_exec('python3 /var/www/html/plotmain.py 2>&1');
    echo"<pre>$output</pre>";
    // echo"$output";
    ?>

  <!-- Show the plots in html page -->
  <center><img src="power.png" align="bottom" alt="Image" onerror="this.style.display='none';"></center>
  <br><br>
  <center><img src="volts.png" align="bottom" alt="Image" onerror="this.style.display='none';"></center>
  <br><br>
  <center><img src="currents.png" align="bottom" alt="Image" onerror="this.style.display='none';"></center>
  <center><H3>Your chosen plots are shown on this page</center></H3>
  <center><b><a href="index.html">Back</a></b></center>

  </body>
</html>
