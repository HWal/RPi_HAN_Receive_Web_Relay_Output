# Copy prices Day-Ahead => Today
# To be executed as cron job every day at 00:05

import sys
import shutil

# Copy file to show today's EUR prices available on website
source = '/var/www/html/data/prices_EUR_tomorrow.data'
destination = '/var/www/html/data/prices_EUR_today.data'
shutil.copy(source, destination)

# Copy file to show today's NOK prices available on website
source = '/var/www/html/data/prices_NOK_tomorrow.data'
destination = '/var/www/html/data/prices_NOK_today.data'
shutil.copy(source, destination)

sys.exit()
