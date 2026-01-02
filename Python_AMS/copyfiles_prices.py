# Save Day-Ahead price per hour file on USB stick
# To be executed as cron job every day at 00:20

import datetime
import time
import sys
import shutil

# INFO:
# Price Area	EIC Code
# NO1	        10YNO-1--------2 
# NO2           10YNO-2--------T 
# NO3	        10YNO-3--------J 
# NO4	        10YNO-4--------9 
# NO5	        10Y1001A1001A48H 

# Extract today's date as string
toDay = datetime.date.today()
shortDateToday = toDay.strftime("%Y") + toDay.strftime("%m") + toDay.strftime("%d")


norwayZones = ["NO1", "NO2", "NO3", "NO4", "NO5"]
for zone in norwayZones:
    # Save file per day to usb stick, averaged per hour
    source = '/var/www/html/data/prices_PT15M_NOK_24_' + zone + '.data'
    destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_PT15M_NOK_24_' + zone + '.data'
    shutil.copy(source, destination)

    # Save file per day to usb stick, 15 min resolution (96 prices)
    source = '/var/www/html/data/prices_PT15M_NOK_96_' + zone + '.data'
    destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_PT15M_NOK_96_' + zone + '.data'
    shutil.copy(source, destination)

sys.exit()
