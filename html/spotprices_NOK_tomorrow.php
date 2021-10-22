<?php

// This script is called by (and used to) update all fields in
// webpage file spotprices_NOK_tomorrow.html.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myFile = fopen("data/prices_NOK_tomorrow.data", "r") or die("Unable to open file!");
  $prices = fread($myFile,filesize("data/prices_NOK_tomorrow.data"));
  fclose($myFile);

  $priceArray = explode(',', $prices);
  echo "data: ".json_encode($priceArray)."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  sleep(1000);
}

?>
