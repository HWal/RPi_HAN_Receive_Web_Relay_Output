# Generate log files and save on USB stick
# To be executed as cron job every day at 23:55

import datetime
import time
import sys
import shutil

# Extract today's date as string
toDay = datetime.date.today()
shortDateToday = toDay.strftime("%Y") + toDay.strftime("%m") + toDay.strftime("%d")

# Save file for long term logging of EUR price data to log folder
source = '/var/www/html/data/prices_EUR_today.data'
destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_EUR.data'
shutil.copy(source, destination)

# Save file for long term logging of NOK price data to log folder
source = '/var/www/html/data/prices_NOK_today.data'
destination = '/media/pi/D8AF-261F/prices/' + shortDateToday + '_NOK.data'
shutil.copy(source, destination)

sys.exit()
