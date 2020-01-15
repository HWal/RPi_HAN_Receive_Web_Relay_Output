# Download and save pricedata as xml from entsoe
# Parse xml file into string with date and prices
# Save the string, which is used by webpage elspotprices.html
# Info: Updated prices are available after 1300 (GMT+1)

import xml.etree.ElementTree as ET # Process xml documents
import re                          # Process regex
import datetime
import requests                    # For downloading Url
import time
import sys

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
shortDate = tomorrow.strftime("%Y") + tomorrow.strftime("%m") + tomorrow.strftime("%d")

# Build the Url search string
a = 'https://transparency.entsoe.eu/api?documentType=A44&in_Domain=10Y1001A1001A48H&out_Domain=10Y1001A1001A48H&periodStart='
b = '0000&periodEnd='
c = '2300&securityToken=3880e276-5398-4edb-b283-e96b339ea056'
url = a + shortDate + b + shortDate + c

# Download and save price data to file
counter = 0
searchFinished = False
while searchFinished == False:
    r = requests.get(url)
    # Write result to file
    if r.status_code == 200 or r.status_code == 400:
        with open('/var/www/html/data/prices.xml', 'w') as file:
            file.write(r.text)
            searchFinished = True
    # Limit number of tries to 10
    counter += 1
    if counter >= 10:
        # print ('Search ended without success')
        sys.exit()
    # Wait 10 seconds before next try
    time.sleep(10)


# Read xml file into an xml string
with open('/var/www/html/data/prices.xml') as f:
    xmlstring = f.read()

# The root tag '..._MarketDocument' has a namespace definition,
# (xmlns="...") which is removed here
xmlstring = re.sub('\\sxmlns="[^"]+"', '', xmlstring, count=1)

# Parse the XML string
root = ET.fromstring(xmlstring)

# Check if xml file is the correct one with prices
for element in root.iter():
    if element.tag == 'Reason':
        # If the above tag is found, prices are not available
        print ('Day-Ahead-Prices not available yet')
        print ('Normally available after 1300 GMT')
        sys.exit()

# If day-ahead prices are available, the program saves
# date and prices to file as a commaseparated string

# Replace the tagname price.amount with priceamount
for element in root.iter('price.amount'):
    element.tag = 'priceamount'

# Generate a list with hour numbers
pos = []
for position in root.iter('position'):
    pos.append(position.text)

price = []
# Generate a list with prices in EUR per MWh
for priceamount in root.iter('priceamount'):
    price.append(priceamount.text)

# Build a string with price information
saveFileString = shortDate + ','
for i in range(len(price)):
    saveFileString += price[i]
    saveFileString += ','
# Remove the last comma
saveFileString = saveFileString[:-1]

# Save date and price information to file
with open('/var/www/html/data/prices.data', 'w') as file:
    file.write(saveFileString)
    sys.exit()

# Everything was successfuly processed - end program
sys.exit()
