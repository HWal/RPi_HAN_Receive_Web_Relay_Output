# TO BE EXECUTED AS CRON JOB EVERY DAY AT 14:00
# This program may exit early if necessary data is not successfully
# obtained from entso-e. If that happens, run the program from
# terminal and see messages to determine where the process stops.
# Downloads el-spotprices in EUR from entso-e and saves as xml file
# Downloads currency conversion data from DNB and saves as xml file
# Reads the xml files into xml strings and parses
# Builds commaseparated string with day-ahead date and prices in NOK
# Saves to files:
# /var/www/html/data/prices_PT15M_NOK_96_zone.data   96  15m values
# /var/www/html/data/prices_PT15M_NOK_24_zone.data   24  60m values

import xml.etree.ElementTree as ET # Process xml documents
import re                          # Process regex
import datetime
import requests                    # For downloading Url
import time
import sys


# Open and read file containing chosen prize zone
# with open ("/var/www/html/data/zonechoice.data", "r") as fp1:
#     choiceString = fp1.read()
#     fp1.close()
# print(choiceString)


# INFO:
# Price Area	EIC Code
# NO1	        10YNO-1--------2 
# NO2           10YNO-2--------T 
# NO3	        10YNO-3--------J 
# NO4	        10YNO-4--------9 
# NO5	        10Y1001A1001A48H 


# Extract tomorrow's date as string
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
shortDateTomorrow = tomorrow.strftime("%Y") + tomorrow.strftime("%m") + tomorrow.strftime("%d")
# print(shortDateTomorrow)





norwayZones = ["NO1", "NO2", "NO3", "NO4", "NO5"]
for zone in norwayZones:

    # Section of search string with Domain code for Market Balance Area (N05 includes Bergen)
    if zone == "NO1":
        a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10YNO-1--------2&out_Domain=10YNO-1--------2&periodStart='
    elif zone == "NO2":
        a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10YNO-2--------T&out_Domain=10YNO-2--------T&periodStart='
    elif zone == "NO3":
        a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10YNO-3--------J&out_Domain=10YNO-3--------J&periodStart='
    elif zone == "NO4":
        a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10YNO-4--------9&out_Domain=10YNO-4--------9&periodStart='
    elif zone == "NO5":
        a = 'https://web-api.tp.entsoe.eu/api?documentType=A44&processType=A01&in_Domain=10Y1001A1001A48H&out_Domain=10Y1001A1001A48H&periodStart='
    else:
        print("No valid Domain found")
        sys.exit()
    
    b = '0000&periodEnd='
    c = '2359&securityToken=5415fd5e-908a-43b7-a5ab-920ebf5735e3'

    # Build search string combined for downloading price data from entso-e website
    url1 = a + shortDateTomorrow + b + shortDateTomorrow + c
    # print(url1)
    # print()

    # Download and save price data in EUR as xml file
    counter = 0
    searchFinished = False
    while searchFinished == False:
        r = requests.get(url1)
        # Write result to file
        if r.status_code == 200:
            with open('/var/www/html/data/prices_EUR_tomorrow_' + zone + '.xml', 'w') as file:
                file.write(r.text)
                searchFinished = True
        # Limit number of tries to 5
        counter += 1
        if counter >= 5:
            print("Could not open url for dowloading prices after 5 tries.")
            sys.exit()
        # Wait 10 seconds before next try
        time.sleep(10)

    # Read xml file into an xml string
    with open('/var/www/html/data/prices_EUR_tomorrow_' + zone + '.xml') as f1:
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
            print("Could not open url for dowloading EUR to NOK conversion after 5 tries.")
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
        print("Could not find the correct resolution PT15M for prizes after 5 tries.")
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





    # Read existing "/var/www/html/data/prices_PT15M_NOK_96" + zone + ".data". This
    # file must always exist for the program to work. The new version of the file is
    # made by replacing values in the old (existing) version.
    with open ("/var/www/html/data/prices_PT15M_NOK_96_" + zone + ".data", "r") as fp1:
        chString_NOK = fp1.readlines()
        fp1.close()
    # Break it down into a list with 98 elements like below where:
    # element[0]=zone, [1]=YYYYMMDD, [2]-->[97]=prices, element[98]=eurInNok
    spltlist_NOK_96 = chString_NOK[0].split(",")

    # Iterate through all Points of the xml file and update the full 15m price list
    # Note: The new xml file may not be complete with all points and prices. So, it
    # is assumed that only prices that have changed, are present in the new xml file
    for point in root1.findall('.//Point'):
        position = point.find('position').text
        price = point.find('priceamount').text
        # Convert each priceamount to NOK
        spltlist_NOK_96[int(position)] = (str(float(price) * float(eurInNok) / 1000))[0:6]





    # Build a commaseparated text string with zone, date, 96 NOK prices and exchange rate
    saveFileString_NOK_96 = zone + ',' + shortDateTomorrow + ','

    # Add the 96 prices
    for i in range(1, 97):
        saveFileString_NOK_96 += spltlist_NOK_96[i] + ','

    # Add the sell price for EUR
    saveFileString_NOK_96 += eurInNok

    # Save the 96 price commaseparated string to file
    file96 = "/var/www/html/data/prices_PT15M_NOK_96_" + zone + ".data"
    with open(file96, 'w') as file:
        file.write(saveFileString_NOK_96)





    # Build a commaseparated text string with date, 24 NOK prices and exchange rate
    saveFileString_NOK_24 = zone + ',' + shortDateTomorrow + ','

    # Add 24 prices, each one is the average of 4 prices given for every hour
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
    file24 = "/var/www/html/data/prices_PT15M_NOK_24_" + zone + ".data"
    with open(file24, 'w') as file:
        file.write(saveFileString_NOK_24)





# If everything was successful - exit program
sys.exit()
