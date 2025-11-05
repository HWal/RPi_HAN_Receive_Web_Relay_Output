#!/usr/bin/env python3

# Calculate energy difference between each top of hour
# Determine the highest Wh value for each day
# Keep the three highest day values within the month

from datetime import datetime
import time
import csv
import sys
import smtplib
from email.message import EmailMessage


# Initialization of variables
from_email_addr ="xxxxxxxxx5@xxxxx.com"
from_email_pass ="xxxxxxxxxxxxxxxx"
to_email_addr ="xxxxxxxx@xxxxx.xxx"

ok1 = ok2 = ok3 = False

yearNew = monthNew = dayNew = hourNew = minuteNew = secondNew = " "
yearOld = monthOld = dayOld = hourOld = minuteOld = secondOld = " "

energyNew = energyOld = 0
wattHourDiff = wattHourDiffMax = 0

d1 = m1 = y1 = h11 = h12 = " "
d2 = m2 = y2 = h21 = h22 = " "
d3 = m3 = y3 = h31 = h32 = " "
maxWattHour1 = maxWattHour2 = maxWattHour3 = 1

wattHourAverage = 1
wattHourSamples = 3

print("Program startet...\n")


# Read 3 previously stored max values from file
try:
  with open ("/var/www/html/data/threemaxes.data", "r") as fp3:
    threeMaxString = fp3.read()
    if (len(threeMaxString) > 0):
      values = threeMaxString.split(",")
      if len(values) == 18:
        d1 = values[0]
        m1 = values[1]
        y1 = values[2]
        h11 = values[3]
        h12 = values[4]
        maxWattHour1 = int(values[5])
        d2 = values[6]
        m2 = values[7]
        y2 = values[8]
        h21 = values[9]
        h22 = values[10]
        maxWattHour2 = int(values[11])
        d3 = values[12]
        m3 = values[13]
        y3 = values[14]
        h31 = values[15]
        h32 = values[16]
        maxWattHour3 = int(values[17])
        wattHourAverage = int((maxWattHour1 + maxWattHour2 + maxWattHour3) / wattHourSamples)
      else:
        print("Could not read three max values")
    else:
      print("No data was read ", end = '')
except:
  print("Could not open or read file: threemaxes.data")



# Eternal loop
while True:
  time.sleep(10)

  # Extract today's date and time
  now = datetime.now()

  # Read in Wh limit to generate email notification
  if ok1 == False:
    try:
      with open ("/var/www/html/data/notificationlimit.data", "r") as fp2:
        limitString = fp2.read()
        if (len(limitString) < 6 and len(limitString) > 2 and limitString.isdigit()):
          limit = int(limitString)
          ok1 = True
        else:
          print("Invalid notification limit: ", end = '')
          print(limitString)
    except:
      print("Could not open or read file: notificationlimit.data")

  # Read the logged Wh value from the meter
  if ok2 == False:
    try:
      with open ("/var/www/html/data/currentlog.data", "r") as fp:
        powerString = fp.read()
        energyField = powerString.split(",")
        # print(energyField[15])
        if energyField[15].isdigit():
          energyNew = int(energyField[15])
          # We need a valid energyNew value greater than zero
          # The value is 0 after restart of meter, until it is
          # updated 10s past top of hour. 100 is just symbolic
          if (energyNew < 100):
            continue
          yearNew = now.strftime("%Y")
          monthNew = now.strftime("%m")
          dayNew = now.strftime("%d")
          hourNew = now.strftime("%H")
          minuteNew = now.strftime("%M")
          secondNew = now.strftime("%S")
          ok2 = True
    except:
      print("Could not open or read file: currentlog.data")
      print()

  # Cut first iteration with valid active energy short
  # This is because we need an updated energyOld value
  if ok3 == False:
    ok3 = True
    energyOld = energyNew
    yearOld = yearNew
    monthOld = monthNew
    dayOld = dayNew
    hourOld = hourNew
    minuteOld = minuteNew
    secondOld = secondNew
    continue
 
  # New energy value is sent from the meter 10 seconds after top of the hour
  # Used Wh in one hour is the difference in energy between two tops of hour
  # The difference in Wh is calculated for every 10s cycle anyway
  wattHourDiff = energyNew - energyOld

  # The active energy Wh value is updated hourly, 10s past top of the hour
  # Check if the Wh value is different from the old one
  if ok1 == True and ok2 == True and energyOld != energyNew:


    # Send email if Wh during one hour is greater than the limit
    if wattHourDiff > limit:

      # Create a message object
      msg = EmailMessage()

      # Set your email subject
      msg['Subject'] = 'VARSEL OM OVERSKREDET GRENSE FOR ENERGI PR TIME'

      # Set the email body
      msg.set_content("År: " + yearOld + " Måned: " + monthOld + " Dag: " + dayOld + "\n" +
                      "Timen mellom kl: " + hourOld + " og " + hourNew + "\n" +
                      "Varselgrense: " + limitString + " Wh/h" + "\n" +
                      "Forbruk: " + str(wattHourDiff) + " Wh\n")

      # Set sender and recipient
      msg['From'] = from_email_addr
      msg['To'] = to_email_addr

      # Connecting to server and sending email
      # Edit the following line with your provider's SMTP server details
      server = smtplib.SMTP('smtp.gmail.com', 587)

      # gmail wants to use Transport Layer Security
      server.starttls()

      # Login to the SMTP server
      server.login(from_email_addr, from_email_pass)

      # Send the message
      server.send_message(msg)

      print('Email sent')
      print()


    # We want to find the highest hourly Wh value within the day
    if wattHourDiff > wattHourDiffMax:
      wattHourDiffMax = wattHourDiff
      hOldDiffMax = hourOld
      hNewDiffMax = hourNew

    # Print status hourly (if the Wh reading from the meter has changed)
    print("NY TIME")
    print("År: ", yearOld, "Måned: ", monthOld, " Dag: ", dayOld)
    print("Timen mellom kl: ", hourOld, " og ", hourNew)
    print("Forbruk denne timen: ", wattHourDiff, "Wh")
    print("Maks Wh time hittil i dag", wattHourDiffMax)
    print("Varselgrense: ", limit, "Wh")
    print()


    # We want to keep the 3 highest Wh values in 3 different days
    # within the current month. The next 16 lines take care of that
    if dayNew != dayOld:
      # Compare the day max with already stored values
      diff1 = wattHourDiffMax - maxWattHour1
      diff2 = wattHourDiffMax - maxWattHour2
      diff3 = wattHourDiffMax - maxWattHour3

      # Determine the largest diff and update stored values
      if (diff1 >= diff2) and (diff1 >= diff3):
        if (diff1 > 0):
          d1 = dayOld
          m1 = monthOld
          y1 = yearOld
          h11 = hOldDiffMax
          h12 = hNewDiffMax
          maxWattHour1 = wattHourDiffMax
      elif (diff2 >= diff1) and (diff2 >= diff3):
        if (diff2 > 0):
          d2 = dayOld
          m2 = monthOld
          y2 = yearOld
          h21 = hOldDiffMax
          h22 = hNewDiffMax
          maxWattHour2 = wattHourDiffMax
      elif (diff3 >= diff1) and (diff3 >= diff2):
        if (diff3 > 0):
          d3 = dayOld
          m3 = monthOld
          y3 = yearOld
          h31 = hOldDiffMax
          h32 = hNewDiffMax
          maxWattHour3 = wattHourDiffMax

      wattHourAverage = int((maxWattHour1 + maxWattHour2 + maxWattHour3) / wattHourSamples)
      # print("maxes =", maxWhattHour1, " ", maxWattHour2, " ", maxWattHour3)

      # Store the maximum values to file
      saveFileString_maxes = \
      d1 + ',' + m1 + ',' + y1 + ',' + h11 + ',' + h12 + ',' + str(maxWattHour1) + ',' + \
      d2 + ',' + m2 + ',' + y2 + ',' + h21 + ',' + h22 + ',' + str(maxWattHour2) + ',' + \
      d3 + ',' + m3 + ',' + y3 + ',' + h31 + ',' + h32 + ',' + str(maxWattHour3)
      with open('/var/www/html/data/threemaxes.data', 'w') as fp4:
        fp4.write(saveFileString_maxes)

      # Print status daily
      print("NY DAG")
      print("3 høyeste døgnmakser hittil denne mnd (Wh): År", yearOld, "Måned", monthOld, " ", maxWattHour1, maxWattHour2, maxWattHour3)
      print("Snitt av de 3 døgnmaksene (Wh): ", wattHourAverage, "\n")
      wattHourDiffMax = 0
      print()


    # Print status monthly
    if monthNew != monthOld:
      print("NY MÅNED")
      print("3 høyeste døgnmakser denne mnd (Wh): År", yearOld, "Måned", monthOld, " ", maxWattHour1, maxWattHour2, maxWattHour3)
      print("Snitt av de 3 døgnmaksene (Wh): ", wattHourAverage, "\n")

      # Reset the 3 largest max hour energy values on 3 different days within one month
      d1 = m1 = y1 = h11 = h12 = " "
      d2 = m2 = y2 = h21 = h22 = " "
      d3 = m3 = y3 = h31 = h32 = " "
      maxWattHour1 = maxWattHour2 = maxWattHour3 = 1
      print()

    # Update Old values
    energyOld = energyNew
    yearOld = yearNew
    monthOld = monthNew
    dayOld = dayNew
    hourOld = hourNew
    minuteOld = minuteNew
    secondOld = secondNew

  ok1 = False
  ok2 = False
