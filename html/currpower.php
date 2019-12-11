<?php

// This script is called by (and used to) update active power+ in
// webpage file amsdata.html, without updating the whole page.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

$currentpowerold = "0";
$currentpowernew = "0";

while (true) {
  $myfile = fopen("data/currentactivepower.data", "r") or die("Unable to open file!");
  $currentpowernew = fread($myfile,filesize("data/currentactivepower.data"));
  fclose($myfile);

  if ($currentpowernew != $currentpowerold) {
    echo "data: $currentpowernew"."\n\n";
    ob_flush(); // Flushes PHP buffer to Apache
    flush();    // Tells Apache to send its buffered content to the client
    $currentpowerold = $currentpowernew;
  }
  sleep(2);
}

?>
