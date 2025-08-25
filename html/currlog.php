<?php

// This script is called by (and used to) update all fields in
// webpage file amsdata.html, except for time and active power+.

header("Cache-Control: no-cache");
header("Content-Type: text/event-stream");

while (true) {
  $myfile = fopen("data/currentlog.data", "r") or die("Unable to open file!");
  $currentlog = fread($myfile,filesize("data/currentlog.data"));
  fclose($myfile);

  $currentlogarray = explode(',', $currentlog);
  echo "data: ".json_encode($currentlogarray)."\n\n";
  ob_flush(); // Flushes PHP buffer to Apache
  flush();    // Tells Apache to send its buffered content to the client
  clearstatcache();
  sleep(10);
}

?>
