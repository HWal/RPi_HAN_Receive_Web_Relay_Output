# TO BE EXECUTED AS CRON JOB EVERY DAY AT 15:00
# This program can exit at several points without notice if necessary
# data is not successfully obtained from the internet.
#
# Download el-spotprices in EUR from entso-e and save as xml file
# Download currency conversion data from DNB and save as xml file
# Read the xml files into xml strings and parse
# Build commaseparated string with day-ahead date and prices in EUR
# Save the string to file /var/www/html/data/prices_EUR_tomorrow.data,
# presented in the following webpage: spotprices_EUR_tomorrow.html.
# Build commaseparated string with day-ahead date and prices in NOK
# Save the string to file /var/www/html/data/prices_NOK_tomorrow.data,
# presented in the following webpage: spotprices_NOK_tomorrow.html.

import xml.etree.ElementTree as ET # Process xml documents
import re                          # Process regex
import datetime
import requests                    # For downloading Url
import time
import sys



# Extract tomorrow's date as string
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
shortDateTomorrow = tomorrow.strftime("%Y") + tomorrow.strftime("%m") + tomorrow.strftime("%d")
# print(shortDateTomorrow)

# Sections of search string with Domain code for Market Balance Area N05 (includes Bergen)
a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10Y1001A1001A48H&out_Domain=10Y1001A1001A48H&periodStart='
b = '0000&periodEnd='
c = '2300&securityToken=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'



# url search string combined for download of price data from entso-e website
url1 = a + shortDateTomorrow + b + shortDateTomorrow + c
# print(url1)

# Download and save price data in EUR as xml file
counter = 0
searchFinished = False
while searchFinished == False:
    r = requests.get(url1)
    # Write result to file
    if r.status_code == 200:
        with open('/var/www/html/data/prices_EUR_tomorrow.xml', 'w') as file:
            file.write(r.text)
            searchFinished = True
    # Limit number of tries to 5
    counter += 1
    if counter >= 5:
        sys.exit()
    # Wait 10 seconds before next try
    time.sleep(10)

# Read xml file into an xml string
with open('/var/www/html/data/prices_EUR_tomorrow.xml') as f1:
    xmlstring1 = f1.read()

# The root1 tag '..._MarketDocument' has a namespace definition,
# (xmlns="...") which is removed with the statement below
xmlstring1 = re.sub('\\sxmlns="[^"]+"', '', xmlstring1, count=1)

# Parse the XML string
root1 = ET.fromstring(xmlstring1)

# Replace the tagname price.amount with priceamount
for element in root1.iter('price.amount'):
    element.tag = 'priceamount'



# url search string for conversion of currencies found at the DNB website
url2 = 'https://www.dnb.no/portalfront/datafiles/miscellaneous/csv/kursliste_over_NOK.xml'
# print(url2)

# Download and save conversion data as xml file
counter = 0
searchFinished = False
while searchFinished == False:
    s = requests.get(url2)
    # Write result to file
    if s.status_code == 200:
        with open('/var/www/html/data/currencyconversions.xml', 'w') as file:
            file.write(s.text)
            searchFinished = True
    # Limit number of tries to 5
    counter += 1
    if counter >= 5:
        sys.exit()
    # Wait 10 seconds before next try
    time.sleep(10)

# Read xml file into an xml string
with open('/var/www/html/data/currencyconversions.xml') as f2:
    xmlstring2 = f2.read()

# Parse the XML string
root2 = ET.fromstring(xmlstring2)

# Find the sell price for EUR (the price we we have to pay when we buy)
here = False
for elem in root2.iter():
    if elem.tag == 'code' and elem.text == 'EUR':
       here = True
    if here == True and elem.tag == 'sell':
       eurInNok = elem.text
       break



# Find resolution of XML data, initialize variables
for period in root1.findall('.//Period'):
    timeInterval = period.find('resolution').text
    if timeInterval == 'PT15M':
        divFactor = 4
        firstPos = 1
        lastPos = 93
        # print(divFactor, firstPos, lastPos)
    elif timeInterval == 'PT30M':
        divFactor = 2
        firstPos = 1
        lastPos = 47
        # print(divFactor, firstPos, lastPos)
    elif timeInterval == 'PT60M':
        divFactor = 1
        firstPos = 1
        lastPos = 24
        # print(divFactor, firstPos, lastPos)
    else:
        sys.exit()



# Build a commaseparated text string with date and EUR prices
saveFileString_EUR = shortDateTomorrow + ','

oldPosition = 0
newPosition = 0
OldPrice = 0.0
newPrice = 0.0

# Indicator for checking if last point is present
lastOk = False

# Iterate through all Points
for point in root1.findall('.//Point'):
    position = point.find('position').text
    price = point.find('priceamount').text

    # Check if the Point with position lastPos is present
    if int(position) == lastPos:
        lastOk = True

    newPosition = int(position)
    newPrice = float(price)

    # Check if Point is missing, if so, how many
    diff = newPosition - oldPosition - 1
    if diff >= divFactor:
        division = diff // divFactor
        for i in range(division):
            saveFileString_EUR += "unavailable"
            saveFileString_EUR += ','
            # Print to terminal
            # print("Unavailable")

    saveFileString_EUR += price
    saveFileString_EUR += ','
    # Print to terminal
    # print(f"Position: {newPosition}, Price: {newPrice}")

    oldPosition = newPosition
    oldPrice = newPrice

# If the last Point with position lastPos is missing
if lastOk == False:
    diff = lastPos - newPosition
    if diff >= divFactor:
        division = diff // divFactor
    for i in range(division):
        saveFileString_EUR += "unavailable"
        saveFileString_EUR += ','
        # Print to terminal
        # print("Unavailable")

# Print to terminal
# print(f"Resolution: {timeInterval}")

# Add the resolution
saveFileString_EUR += timeInterval

# Save the commaseparated string to file
with open('/var/www/html/data/prices_EUR_tomorrow.data', 'w') as file:
    file.write(saveFileString_EUR)


# Print empty line to terminal
# print()


# Build a commaseparated text string with date and NOK prices
saveFileString_NOK = shortDateTomorrow + ','

oldPosition = 0
newPosition = 0
OldPrice = 0.0
newPrice = 0.0

# Indicator for checking if last point is present
lastOk = False

# Iterate through all Points
for point in root1.findall('.//Point'):
    position = point.find('position').text
    price = point.find('priceamount').text

    # Check if the Point with position lastPos is present
    if int(position) == lastPos:
        lastOk = True

    newPosition = int(position)
    newPrice = float(price)

    # Check if Point is missing, if so, how many
    diff = newPosition - oldPosition - 1
    if diff >= divFactor:
        division = diff // divFactor
        for i in range(division):
            saveFileString_NOK += "unavailable"
            saveFileString_NOK += ','
            # Print to terminal
            # print("Unavailable")

    saveFileString_NOK += (str(float(price) * float(eurInNok) / 1000))[0:6]
    saveFileString_NOK += ','
    # Print to terminal
    # print(f"Position: {newPosition}, Price: {(str(float(price) * float(eurInNok) / 1000))[0:6]}")

    oldPosition = newPosition
    oldPrice = newPrice

# If the last Point with position lastPos is missing
if lastOk == False:
    diff = lastPos - newPosition
    if diff >= divFactor:
        division = diff // divFactor
    for i in range(division):
        saveFileString_NOK += "unavailable"
        saveFileString_NOK += ','
        # Print to terminal
        # print("Unavailable")

# Print to terminal
# print(f"One EUR in NOK: {eurInNok}")

# Add the sell price for EUR
saveFileString_NOK += eurInNok

# Save the commaseparated string to file
with open('/var/www/html/data/prices_NOK_tomorrow.data', 'w') as file:
    file.write(saveFileString_NOK)


# If everything was successful so far - exit program
sys.exit()
