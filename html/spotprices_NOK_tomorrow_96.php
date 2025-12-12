<?php

// This script is called by (and used to) update all fields in
// webpage file spotprices_NOK_tomorrow_96.html.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myFile0 = fopen("data/zonechoice.data", "r") or die("Unable to open file!");
  $zone = fread($myFile0,filesize("data/zonechoice.data"));
  fclose($myFile0);

  $fileToOpen = "data/prices_PT15M_NOK_96_".$zone.".data";
  $myFile1 = fopen($fileToOpen, "r") or die("Unable to open file!");
  $prices1 = fread($myFile1,filesize($fileToOpen));
  fclose($myFile1);

  $priceArray = explode(',', $prices1);
  echo "data: ".json_encode($priceArray)."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  sleep(1000);
}

?>
