# MAIN README

HAN reader with relay control for Raspberry Pi 3B+
==================================================

Brief description
-----------------
This project for the Raspberry Pi has the following functions:
* Read and decode data from the HAN-port on Kaifa (MA304H3E 3-phase) smart electricity meter. This also works with Kaifa 1-phase meter, but has not been tested.
* Present live data from the meter on a simple webpage, based on Apache2 webserver.
* Control two output relays.
* Download and view el-spotprices for selectable Norwegian price zones. 
* Send email to a specified address when Watt hours used during one hour exceeds a limit set by the user.
* Plot log files from the meter on the website.

Hardware (see connection diagram)
---------------------------------
* One Raspberry Pi 3 B+ with Raspbian (Buster) installed
* 5V power supply and USB cable
* TSS721 Module Board M-BUS To TTL converter (AliExpress)
* Two 3.3V relay boards that will drain less than 12mA from RPi gpio output
* One usb stick, preferably 16GB, for permanent storage
* Some connecting wire
* A laptop, in my project one that is running Windows 11

Preparation of RPi while powered up and connectected directly to a screen (TV)
------------------------------------------------------------------------------
Activate VNC: sudo raspi-config -> Interfacing Options -> VNC -> Enable VNC server<br>
Activate SSH: sudo raspi-config -> Interfacing Options -> SSH -> Enable SSH server

Open a terminal window, note the IP number of the RPi returned from the command: hostname -I

Prepare a laptop for remote control of the RPi
----------------------------------------------
Download VNC viewer: https://www.realvnc.com/en/connect/download/viewer/ <br>
Download putty.exe and pscp.exe: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html<br>
You should now be able to control RPi from the laptop on your local network, both via the GUI (VNC viewer) and terminal window (putty.exe). Also you can copy files between RPi and the laptop with pscp.exe. To connect, use the IP number noted above.

From now on a separate screen should rarely be necessary. The RPi will be working in "Headless mode".

Continue preparing RPi in Headless mode
---------------------------------------
Preferably, give RPi a static IP address, see: https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address/74428#74428

Install Apache2 webserver: sudo apt-get update , sudo apt-get upgrade , sudo apt-get install apache2 -y<br>
Make user pi the owner of /var/www/html: sudo chown pi: -R html<br>
Install PHP for the relay control script: sudo apt-get install php libapache2-mod-php -y<br>

Make a "clean" UART port on the RPi 3. For reference, see: https://www.raspberrypi.org/documentation/configuration/uart.md and https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/<br>
We want these pins to communicate with the M-BUS To TTL converter:<br>
Physical pin 8 = gpio 14 = Tx<br>
Physical pin 10 = gpio 15 = Rx

sudo apt-get update , sudo apt-get upgrade<br>

Disable console and activate serial: sudo raspi-config -> Interfacing Options -> Serial<br>
Login shell accessible over serial: No<br>
Serial port hardware enabled: Yes<br>
The system asks for a reboot: Yes

We can stop and deactivate the getty service, as long as the console is not used: <br>
sudo systemctl stop serial-getty@ttyS0.service<br>
sudo systemctl disable serial-getty@ttyS0.service<br>

We don't need to use the Bluetooth modem at this time.<br>
sudo systemctl disable hciuart  // Disables the Bluetooth modem<br>

We want to swap the serial ports, please see the relevant lines in the file /boot/overlays/README.<br>
sudo nano /boot/config.txt, and add at the bottom: dtoverlay=pi3-disable-bt<br>
sudo reboot <br>

Now ttyAMA0 / PL011 / UART0 is connected to gpio 14 / 15 which are the physical pins 8 / 10<br>

Make some directories on the Raspberry Pi (Command - Owner - Group - View - Change - Access):<br>
mkdir /home/pi/Cpp_AMS/ - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /home/pi/Python_AMS/ - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /var/meter_log/ - root - root - Anyone - Anyone - Anyone<br>
Edit/check /var/www/html/ - pi - pi - Anyone - Anyone - Anyone<br>
mkdir /var/www/html/data/ - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /var/www/html/img/ - pi - pi - Anyone - Only owner - Anyone<br>
Edit/check /media/pi/ - root - root - Anyone - Only owner and group - Anyone<br>
Edit/check /media/pi/name-of-usb-stick/ - pi - pi - Anyone - Only owner - Anyone (for usb stick)<br>
mkdir /media/pi/name-of-usb-stick/meter/ - pi - pi - Anyone - Only owner - Anyone (for usb stick)<br>
mkdir /media/pi/name-of-usb-stick/prices/ - pi - pi - Anyone - Only owner - Anyone (for usb stick)<br>

Permissions and ownership shown above is like I have it on my RPi. Use a strong password, see below.

Now copy the files from github into the corresponding directories on RPi listed above.
Don't mind about existing data on the files, they will be overwritten with correct data.

Edit a cronjob as your pi user, with crontab -e, with the following content:

10 00 * * * /home/pi/Cpp_AMS/copyFiles_meter<br>
20 00 * * * /usr/bin/python3 /home/pi/Python_AMS/copyfiles_prices.py<br>
00 14 * * * /usr/bin/python3 /home/pi/Python_AMS/spotprices.py<br>
00 22 * * * /usr/bin/python3 /home/pi/Python_AMS/spotprices.py<br>
The last line is present to secure that late incoming spotprices are registered. 

Connect the equipment as shown in schematic.jpg

Goto folder Cpp_AMS and compile the source code with: g++ -W readAMSxx.cpp. Then start reading messages by typing: ./a.out

NOTE: After upgrading from RPi Operating system stretch to buster I experienced problems while reading the meter. readAMS66.cpp has now been adapted to the newer buster release, and latest version is now readAMS77.cpp. In case of problems it is suggested that you try both program versions to determine what works best for you.

Goto folder Python_AMS and start the notification app with: python3 maxpowermonitor.py

When you see the two programs working in their respective terminal windows, you may open the website. From the laptop, when connected to the same local network, open the browser and enter the IP address of the Raspberry pi. The website is very simple, and should be self explanatory. Test that values are being updated in the "View current data from the meter" page. <br>

For presentation of log data on a laptop, please see the Readme file in the python folder.

To connect to the website from the outside world, you should open port 80 in your firewall. Beware the risk of getting the RPi hacked by outside users. You should therefore password protect the website. Information about how to do this is found on the internet.<br>

LIST OF FILES AND HOW THEY ARE USED
-----------------------------------

/var/www/html/index.html<br>
Main menu. Links all programs and scripts. The page also contains links to the NORD POOL power exchange, and an in-house water meter web camera.

/var/www/html/amsdata.html<br>
Shows live data from the AMS electricity meter. Calls currtime.php, currpower.php, currlog.php, which in turn reads data from the files currenttime.data, currentactivepower.data, currentlog.data.

/var/www/html/spotprices_NOK_tomorrow_96.html<br>
Shows Day-Ahead el-spotprices with 15m resolution. Calls spotprices_nok_tomorrow_96.php.

/var/www/html/spotprices_NOK_tomorrow_96.php<br>
Prepares data to be shown on spotprices_nok_tomorrow_96.html. Reads data from prices_PT15M_NOK_96_NOx.data (x = 1 ...5) and zonechoice.data.

/var/www/html/zonechoice_96.php<br>
Called by spotprices_nok_tomorrow_96.html, for choosing zone to display. Edits zonechoice.data.

/var/www/html/spotprices_NOK_tomorrow_24.html<br>
Shows Day-Ahead el-spotprices with 60m resolution. Calls spotprices_nok_tomorrow_24.php.

/var/www/html/spotprices_NOK_tomorrow_24.php<br>
Prepares data to be shown on spotprices_NOK_tomorrow_24.html. Reads data from prices_PT15M_NOK_24_NOx.data (x = 1 ...5) and zonechoice.data.

/var/www/html/zonechoice_24.php<br>
Called by spotprices_nok_tomorrow_24.html, for choosing zone to display. Edits zonechoice.data.

/var/www/html/threemaxes.html<br>
Shows the three highest day maxes in current month. Calls threemaxes.php.

/var/www/html/threemaxes.php<br>
Reads data from threemaxes.data, to show on threemaxes.html page.

/var/www/html/relaycontrol.php<br>
GUI for control of two output relays. This script calls gpio.php.

/var/www/html/gpio.php<br>
Controls two output relays, driven from output pins on Raspberry Pi 3B+.

/var/www/html/notificationlimit.php<br>
Edit kWh/h that triggers sending an email to specified email address. Stores user defined kWh/h trigger value in  notificationlimit.data. maxpowermonitor.py monitors the kWh/h value and sends email when applicable.

/var/www/html/schematic.html<br>
Shows schematic of the equipment connected to Raspberry Pi 3B+.

/var/www/html/schematic.jpg<br>
Image containing the schematic.

/var/www/html/zonemap.html<br>
Shows nordic el price zones.

/var/www/html/zonemap.jpg<br>
Image containing the zone map.

/var/www/html/amsplotchoices.php<br>
Edits parameter file amsplotchoices.data for plotting data from the AMS meter.

/var/www/html/plot.php<br>
Starts main python script plotmain.py for plotting of currents, power, voltages.

/var/www/html/plotmain.py<br>
Main python script for running the plot scripts. Deletes old plot images, reads amsplotchoices.data, calls functions according to choices made by user.

/var/www/html/plot_volts.py<br>
Plots two voltages (third not available for tech reasons).

/var/www/html/volts.png<br>
Latest voltages plot image. Gets overwritten by next plot.

/var/www/html/plot_currents.py<br>
Plots three currents.

/var/www/html/currents.png<br>
Latest currents plot image. Gets overwritten by next plot.

/var/www/html/plot_power.py<br>
Plots active power.

/var/www/html/power.png<br>
Latest power plot image. Gets overwritten by next plot.

/var/www/html/currlog.php<br>
Reads currentlog.data every 10s, values are shown on amsdata.html page. Currentlog.data file is updated by program readAMSxx.cpp.

/var/www/html/currpower.php<br>
Reads currentactivepower.data every 2s, values are shown on amsdata.html page. Currentactivepower.data file is updated by program readAMSxx.cpp.

/var/www/html/currtime.php<br>
Reads currenttime.data every 2s, values are shown on amsdata.html page. Currenttime.data file is updated by program readAMSxx.cpp.

/var/www/html/data/amsplotchoices.data<br>
Stores user defined parameters for plot, edited with amsplotchoices.php.

/var/www/html/data/currencyconversions.xml<br>
Conversion of EUR to NOK downloaded, read by spotprices.py.

/var/www/html/data/currentactivepower.data<br>
Holds active power read from the meter by readAMSxx.cpp. Updated every 2s.

/var/www/html/data/currentlog.data<br>
Holds multiple data read from the meter by readAMSxx.cpp. Updated at various intervals every 2s/10s/hourly.

/var/www/html/data/currenttime.data<br>
Holds time updated from the meter by readAMSxx.cpp every 2s. Read by currtime.php, to update time in amsdata.html page.

/var/www/html/data/notificationlimit.data<br>
Holds the kWh/h limit for when notification is sent to email address hardcoded in the maxpowermonitor.py script. The kWh/h value is updated by notificationlimit.php.

/var/www/html/data/prices_EUR_tomorrow_NOx.xml (x = 1 ... 5)<br>
El-price data downloaded from enso-e by spotprices.py each day at 14.00 hrs.

/var/www/html/data/prices_PT15M_NOK_24_NOx.data (x = 1 ... 5)<br>
Parsed .xml for zone NOx. Averaged 15m, shown in spotprices_NOK_tomorrow_24.html.

/var/www/html/data/prices_PT15M_NOK_96_NOx.data (x = 1 ... 5)<br>
Parsed .xml for zone NOx. Price per 15m, shown in spotprices_NOK_tomorrow_96.html.

/var/www/html/data/threemaxes.data<br>
Holds the three max kWh/h values with date and time, during current month. Content updated by maxpowermonitor.py. Read by threemaxes.php, shown i treemaxes.html.

/var/www/html/data/zonechoice.data<br>
Holds the current price zone to be shown. Read by zonechoice_24.php and zonechoice_96.php, to be used by, and shown in, spotprices_NOK_tomorrow_24.html and spotprices_NOK_tomorrow_96.html respectively.

/var/www/html/img/green_0.jpg<br>
Show On/Off condition of output relays.

/var/www/html/img/green_1.jpg<br>
Show On/Off condition of output relays.

/var/www/html/img/red_0.jpg<br>
Show On/Off condition of output relays.

/var/www/html/img/red_1.jpg<br>
Show On/Off condition of output relays.

/home/pi/Cpp_AMS/readAMSxx.cpp<br>
C++ program, source code for a.out. These files are updated by the program: /var/meter_log/yyyy-mm-dd.txt Every 10s, /var/www/html/data/currenttime.data Every 2s, /var/www/html/data/currentactivepower.data Every 2s, /var/www/html/data/currentlog.data various intervals every 2s/10s/hourly.

/home/pi/Cpp_AMS/a.out<br>
Executable version of readAMSxx.cpp . Does the actual reading of the meter.

/home/pi/Cpp_AMS/copyFiles_meter<br>
Copies /var/meter_log/yyyy-mm-dd.txt to usb stick. Cleans /var/meter_log/ of files older than 2 days. Run as cron job 10 minutes past every midnight.

/var/meter_log/yyyy-mm-dd.txt<br>
This file is updated by readAMSxx.cpp Every 10s.

/home/pi/Python_AMS/copyfiles_prices.py<br>
Copies price data per day to usb stick. Run as cron job 20 minutes past midnight. Note: At present only prices for NO5 are saved to the usb stick. prices_PT15M_NOK_24_NO5.data -> yyyymmdd_PT15M_NOK_24_NO5.data. prices_PT15M_NOK_96_NO5.data -> yyyymmdd_PT15M_NOK_96_NO5.data.

/home/pi/Python_AMS/maxpowermonitor.py<br>
Calculates energy difference between each top of hour. Determines the highest Wh value for each day. Keeps the three highest day values within the month. Updates file threemaxes.data.

/home/pi/Python_AMS/spotprices.py<br>
Downloads spotprices and generates price data files for all norwegian price zones. Run as cron job every day at 14.00 hrs. Files: prices_PT15M_NOK_24_NOx.data and prices_PT15M_NOK_96_NOx.data (x = 1 ... 5).

/media/pi/D8AF-261F/meter/yyyy-mm-dd.txt<br>
Log per day of AMS meter, with 10s resolution, copied from folder /var/meter_log.

/media/pi/D8AF-261F/prices/yyyymmdd_PT15M_NOK_24_NOx.data (x = 5)<br>
Log per day of el-spotprices, one price per hour (averaged 15m prices).

/media/pi/D8AF-261F/prices/yyyymmdd_PT15M_NOK_96_NOx.data (x = 5)<br>
Log per day of el-spotprices, one price per 15m.
