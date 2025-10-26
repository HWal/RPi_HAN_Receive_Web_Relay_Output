# TO BE EXECUTED AS CRON JOB EVERY DAY AT 15:00
# This program may exit early if necessary data is not successfully
# obtained from entso-e.
# Download el-spotprices in EUR from entso-e and save as xml file
# Download currency conversion data from DNB and save as xml file
# Read the xml files into xml strings and parse
# Build commaseparated string with day-ahead date and prices in NOK
# Save to files:
# /var/www/html/data/prices_PT15M_NOK_96.data   96  15m values
# /var/www/html/data/prices_PT15M_NOK_24.data   24  60m values
# Show 24 values in the following webpage: spotprices_NOK_tomorrow.html.

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
c = '2300&securityToken=5415fd5e-908a-43b7-a5ab-920ebf5735e3'





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





# Find the resolution of XML data
for period in root1.findall('.//Period'):
    timeInterval = period.find('resolution').text

# For the time being we only want to process PT15M xml files
# This is the one we get from entso-e when using the url above
if timeInterval != 'PT15M':
    sys.exit()





# Possible resolutions
# timeInterval = 'PT15M'
# firstPos = 1
# lastPos = 96
# timeInterval = 'PT30M':
# firstPos = 1
# lastPos = 48
# timeInterval = 'PT60M':
# firstPos = 1
# lastPos = 24





# Read existing /var/www/html/data/prices_PT15M_NOK_96.data
with open ("/var/www/html/data/prices_PT15M_NOK_96.data", "r") as fp1:
    chString_NOK = fp1.readlines()
    fp1.close()
# Break it down into a list with 98 elements like below where:
# element[0]=YYYYMMDD, element[1]-->[96]=prices, element[97]=eurInNok
spltlist_NOK_96 = chString_NOK[0].split(",")

# Iterate through all Points of the xml file and update the full 15m price list
# Note: The new xml file may not be complete with all points and prices
# It is assumed that only prices that have changed, are present in the xml file
for point in root1.findall('.//Point'):
    position = point.find('position').text
    price = point.find('priceamount').text
    # Use the EUR price
    # spltlist_NOK_96[int(position)] = price
    # Or convert priceamount to NOK
    spltlist_NOK_96[int(position)] = (str(float(price) * float(eurInNok) / 1000))[0:6]





# Build a commaseparated text string with date, 96 NOK prices and exchange rate
saveFileString_NOK_96 = shortDateTomorrow + ','

# Add the 96 prices
for i in range(1, 97):
    saveFileString_NOK_96 += spltlist_NOK_96[i] + ','

# Add the sell price for EUR
saveFileString_NOK_96 += eurInNok

# Save the 96 price commaseparated string to file
with open('/var/www/html/data/prices_PT15M_NOK_96.data', 'w') as file:
    file.write(saveFileString_NOK_96)





# Build a commaseparated text string with date, 24 NOK prices and exchange rate
saveFileString_NOK_24 = shortDateTomorrow + ','

# Add 24 prices, each one the average of 4 prices given for every hour
for z in range(1, 97, 4):
    avgprice = 0
    if z < 96:
        for q in range(z, z+4):
            avgprice += float(spltlist_NOK_96[q])
        avgprice /= 4
    saveFileString_NOK_24 += str(avgprice)[0:6] + ','

# Add the sell price for EUR
saveFileString_NOK_24 += eurInNok

# Save the 24 price commaseparated string to file
with open('/var/www/html/data/prices_PT15M_NOK_24.data', 'w') as file:
    file.write(saveFileString_NOK_24)





# If everything was successful - exit program
sys.exit()
