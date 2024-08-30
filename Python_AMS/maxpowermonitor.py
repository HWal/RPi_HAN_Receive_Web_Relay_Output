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
from_email_addr ="helge5895@gmail.com"
from_email_pass ="plxwxihtiaddnaum"
to_email_addr ="helgewal@gmail.com"

ok1 = False
ok2 = False
ok3 = False

yearNew = ""
monthNew = ""
dayNew = ""
hourNew = ""
minuteNew = ""
secondNew = ""
yearOld = ""
monthOld = ""
dayOld = ""
hourOld = ""
minuteOld = ""
secondOld = ""

energyNew = 0
energyOld = 0
wattHourDiff = 0
wattHourDiffMax = 0
maxWattHour1 = 1
maxWattHour2 = 1
maxWattHour3 = 1
wattHourAverage = 1
wattHourSamples = 3

print("Program startet...\n")

# Read three previously stored max values from file
try:
  with open ("/var/www/html/data/threemaxes.data", "r") as fp3:
    threeMaxString = fp3.read()
    if (len(threeMaxString) > 0):
      values = threeMaxString.split(",")
      if len(values) == 3:
        maxWattHour1 = int(values[0])
        maxWattHour2 = int(values[1])
        maxWattHour3 = int(values[2])
        wattHourAverage = (maxWattHour1 + maxWattHour2 + maxWattHour3) / wattHourSamples
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
          yearNew = now.strftime("%Y")
          monthNew = now.strftime("%m")
          dayNew = now.strftime("%d")
          hourNew = now.strftime("%H")
          minuteNew = now.strftime("%M")
          secondNew = now.strftime("%S")
          ok2 = True
    except:
      print("Could not open or read file: currentlog.data")

  # Cut first iteration short
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
 
  # New energy value is sent from the meter 10 seconds after each top of hour
  # Used Wh in one hour is the difference in energy between two tops of hour
  # The difference in Wh is calculated for every 10s cycle anyway
  wattHourDiff = energyNew - energyOld

  # Check if we have got a new energy value different from the old one
  if ok1 == True and ok2 == True and energyOld != energyNew:

    # We want to find the highest hourly Wh value within the day
    if wattHourDiff > wattHourDiffMax:
      wattHourDiffMax = wattHourDiff

    # We want to keep the three highest Wh values in three different
    # days within one month - The next 16 lines below take care of that
    if dayNew != dayOld:
      # Compare the day max with already stored values
      diff1 = wattHourDiffMax - maxWattHour1
      diff2 = wattHourDiffMax - maxWattHour2
      diff3 = wattHourDiffMax - maxWattHour3

      # Debug
      # print("Positiv diff betyr en ny max i dag")
      # print("diff1 =", diff1, " diff2 =", diff2, " diff3 =", diff3)

      # Determine the largest diff and update stored values
      if (diff1 >= diff2) and (diff1 >= diff3):
        if (diff1 > 0):
          maxWattHour1 = wattHourDiffMax
      elif (diff2 >= diff1) and (diff2 >= diff3):
        if (diff2 > 0):
          maxWattHour2 = wattHourDiffMax
      elif (diff3 >= diff1) and (diff3 >= diff2):
        if (diff3 > 0):
          maxWattHour3 = wattHourDiffMax

      wattHourAverage = (maxWattHour1 + maxWattHour2 + maxWattHour3) / wattHourSamples

      # Debug
      # print("maxWattHour1 =", maxWattHour1, " maxWattHour2 =", maxWattHour2, " maxWattHour3 =", maxWattHour3)

      # Store the maximum values to file 10s after each midnight
      saveFileString_maxes = str(maxWattHour1) + ',' + str(maxWattHour2) + ',' + str(maxWattHour3)
      with open('/var/www/html/data/threemaxes.data', 'w') as fp4:
        fp4.write(saveFileString_maxes)

    # Print status hourly (when there is a new Wh reading from the meter)
    print("År: ", yearOld, "Måned: ", monthOld, " Dag: ", dayOld)
    print("Timen mellom kl: ", hourOld, " og ", hourNew)
    print("Forbruk denne timen: ", wattHourDiff, "Wh")
    print("Maks Wh time hittil i dag", wattHourDiffMax)
    print("Varselgrense: ", limit, "Wh")
    print("Snitt 3 høyeste døgn Wh hittil denne mnd: ", wattHourAverage, "Wh")
    print()

    # Print status daily
    if dayNew != dayOld:
      print("NY DAG")
      print("Tre høyeste døgnmakser hittil i måneden (Wh) År ", yearOld, " Måned ", monthOld, " ", maxWattHour1, "  ", maxWattHour2, "  ", maxWattHour3, "\n")
      print("Snitt av de tra døgnmaksene: ", wattHourAverage, "Wh")

    # Print status monthly
    if monthNew != monthOld:
      print("Ny måned")
      print("Tre høyeste månedsmakser i måneden (Wh) År ", yearOld, " Måned ", monthOld, " ", maxWattHour1, "  ", maxWattHour2, "  ", maxWattHour3, "\n")

    # Reset max energy during one hour within one day
    if dayNew != dayOld:
      wattHourDiffMax = 0

    # Reset the three largest max hour energy values on three
    # different days within one month
    if monthNew != monthOld:
      maxWattHour1 = 0
      maxWattHour2 = 0
      maxWattHour3 = 0

    # Send email if Wh during one hour is greater than the limit
    if wattHourAverage > limit:

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
