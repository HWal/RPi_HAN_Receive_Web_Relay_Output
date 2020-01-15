<?php

// This script is called by (and used to) update all fields in
// webpage file spotprices.html.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myFile = fopen("data/prices.data", "r") or die("Unable to open file!");
  $prices = fread($myFile,filesize("data/prices.data"));
  fclose($myFile);

  $priceArray = explode(',', $prices);
  echo "data: ".json_encode($priceArray)."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  sleep(1000);
}

?>
