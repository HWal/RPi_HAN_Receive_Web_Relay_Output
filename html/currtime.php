<?php

// This script is called by (and used to) update time in webpage
// file amsdata.html, without updating the whole page.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

$currenttimeold = "0";
$currenttimenew = "0";

while (true) {
  $myfile = fopen("data/currenttime.data", "r") or die("Unable to open file!");
  $currenttimenew = fread($myfile,filesize("data/currenttime.data"));
  fclose($myfile);

  if ($currenttimenew != $currenttimeold) {
    echo "data: $currenttimenew"."\n\n";
    ob_flush(); // Flushes PHP buffer to Apache
    flush();    // Tells Apache to send its buffered content to the client
    $currenttimeold = $currenttimenew;
  }
  sleep(2);
}

?>
