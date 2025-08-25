<?php

// This script is called by (and used to) update active power+ in
// webpage file amsdata.html, without updating the whole page.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myfile = fopen("data/currentactivepower.data", "r") or die("Unable to open file!");
  $currentpower = fread($myfile,filesize("data/currentactivepower.data"));
  fclose($myfile);

  echo "data: $currentpower"."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  clearstatcache();
  sleep(2);
}

?>
