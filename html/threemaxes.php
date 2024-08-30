<?php

// This script is called by (and used to) present
// the tree highest Wh maxes in the current month.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myFile = fopen("data/threemaxes.data", "r") or die("Unable to open file!");
  $maxes = fread($myFile,filesize("data/threemaxes.data"));
  fclose($myFile);

  $maxesArray = explode(',', $maxes);
  echo "data: ".json_encode($maxesArray)."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  sleep(1000);
}

?>
