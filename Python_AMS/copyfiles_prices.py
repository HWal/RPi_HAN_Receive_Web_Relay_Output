# Save Day-Ahead price per hour file on USB stick
# To be executed as cron job every day at 00:20

import datetime
import time
import sys
import shutil

# Extract today's date as string
toDay = datetime.date.today()
shortDateToday = toDay.strftime("%Y") + toDay.strftime("%m") + toDay.strftime("%d")

# Save file per day to usb stick, averaged per hour
source = '/var/www/html/data/prices_PT15M_NOK_24.data'
destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_PT15M_NOK_24.data'
shutil.copy(source, destination)

# Save file per day to usb stick, 15 min resolution (96 prices)
source = '/var/www/html/data/prices_PT15M_NOK_96.data'
destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_PT15M_NOK_96.data'
shutil.copy(source, destination)

sys.exit()
