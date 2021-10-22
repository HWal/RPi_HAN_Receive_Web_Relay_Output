# To be executed as cron job every day at 15:00
#
# Download el-spotprices from entso-e and save as xml file
# Read the xml file into xml string and parse it
# Build commaseparated string with day-ahead date and prices in EUR
# Save the string to file /var/www/html/data/prices_EUR_tomorrow.data,
# which is used by the following webpage: elspotprices_EUR_tomorrow.html
# Download currency conversion data from DNB and save as xml file
# Build commaseparated string with day-ahead date and prices in NOK
# Save the string to file /var/www/html/data/prices_EUR_tomorrow.data,
# which is used by the following webpage: elspotprices_NOK_tomorrow.html

import xml.etree.ElementTree as ET # Process xml documents
import re                          # Process regex
import datetime
import requests                    # For downloading Url
import time
import sys

# Extract tomorrow's date as string
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
shortDateTomorrow = tomorrow.strftime("%Y") + tomorrow.strftime("%m") + tomorrow.strftime("%d")

# Build Url search string with Domain code for Market Balance Area N05 (includes Bergen)
a = 'https://transparency.entsoe.eu/api?documentType=A44&in_Domain=10Y1001A1001A48H&out_Domain=10Y1001A1001A48H&periodStart='
b = '0000&periodEnd='
c = '2300&securityToken=5415fd5e-908a-43b7-a5ab-920ebf5735e3'

url1 = a + shortDateTomorrow + b + shortDateTomorrow + c
# print(url1)

# Download and save price data as xml file
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

# Build a commaseparated text string with date and EUR prices
saveFileString_EUR = shortDateTomorrow + ','
for priceamount in root1.iter('priceamount'):
    saveFileString_EUR += priceamount.text
    saveFileString_EUR += ','
# Remove the last comma
saveFileString_EUR = saveFileString_EUR[:-1]

# Save the commaseparated string to file
with open('/var/www/html/data/prices_EUR_tomorrow.data', 'w') as file:
    file.write(saveFileString_EUR)


# url search string for conversion of currencies found at the DNB website
url2 = 'https://www.dnb.no/portalfront/datafiles/miscellaneous/csv/kursliste_over_NOK.xml'
# print(url2)

# Save conversion data as xml file
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

# Build a commaseparated text string with date and NOK prices
saveFileString_NOK = shortDateTomorrow + ','
for priceamount in root1.iter('priceamount'):
#for i in range(len(price_NOK)):
    saveFileString_NOK += (str(float(priceamount.text) * float(eurInNok) / 1000))[0:6]
    saveFileString_NOK += ','
# Add the sell price for EUR
saveFileString_NOK += eurInNok

# Save the commaseparated string to file
with open('/var/www/html/data/prices_NOK_tomorrow.data', 'w') as file:
    file.write(saveFileString_NOK)

# If everything was successful so far - exit program
sys.exit()
