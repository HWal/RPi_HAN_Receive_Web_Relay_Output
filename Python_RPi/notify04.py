#!/usr/bin/env python3

# Imports
from math import ceil
import time
import requests

# Variables
MakerIFTTT_Event = 'Kaifa_notify'
MakerIFTTT_Key = 'ddx5za5xy1fMGfxQcKn4I6'
info1 = {"value1" : "Grense overskredet!"}
limit = 12000
power = 0
ok1 = False
ok2 = False
ok3 = False
counter = 0
powerSum = 0
powerAvg = 0
avgTime = 10
nbSamples = 5

# Eternal loop
while True:
  time.sleep(2)

  if ok1 == False:
    try:
      with open ("/var/www/kaifaweb/data/notificationlimit.data", "r") as fp2:
        limitString = fp2.read()
        if (len(limitString) < 6 and len(limitString) > 2 and limitString.isdigit()):
          limit = int(limitString)
          ok1 = True
        else:
          print("Invalid notification limit: ", end = '')
          print(limitString)
    except:
      print("Could not open or read file: notificationlimit.data")

  if ok2 == False:
    try:
      with open ("/var/www/kaifaweb/data/averagingtime.data", "r") as fp2:
        averageString = fp2.read()
        if (len(averageString) < 4 and len(averageString) > 0 and averageString.isdigit()):
          avgTime = int(averageString)
          # If divisjon below gives a decimal number, raise nbSamples to the nearest integer
          nbSamples = ceil(avgTime / 2)
          ok2 = True
        else:
          print("Invalid average time: ", end = '')
          print(averageString)
    except:
      print("Could not open or read file: notificationlimit.data")

  try:
    with open ("/var/www/kaifaweb/data/currentactivepower.data", "r") as fp1:
      powerString = fp1.read()
      if (len(powerString) < 6 and len(powerString) > 0 and powerString.isdigit()):
        power = int(powerString)
        counter += 1
        powerSum += power
        ok3 = True
      else:
        print("Invalid current power: ", end = '')
        print(powerString)
  except:
    print("Could not open or read file: currentactivepower.data")
  
  # Print counter value and number of samples
  print("Counter = ", end = '')
  print(counter, end = '')
  print(", Samples = ", end = '')
  print(nbSamples)

  if counter >= nbSamples:
    # Calculate average power
    powerAvg = powerSum / nbSamples

    # Print information to terminal
    print(time.strftime("%Y-%m-%d %H:%M"), end = '')
    print(", Avg power in ", end = '')
    print(nbSamples * 2, end = '')
    print(" seconds, ", end = '')
    print("%d" % powerAvg, end = '')
    print("W", end = '')
    print(", Notify limit = ", end = '')
    print(limit, end = '')
    print("W")

    # Send notification if average power exceeds limit
    if powerAvg > limit and ok1 == True and ok2 == True and ok3 == True:
      # IFTTT URL with event name, key and json parameters (values)
      r = requests.post('https://maker.ifttt.com/trigger/' + MakerIFTTT_Event + '/with/key/' + MakerIFTTT_Key, data=info1)
      print(r)

    # Reset values
    counter = 0
    powerSum = 0
    ok1 = False
    ok2 = False

  ok3 = False
