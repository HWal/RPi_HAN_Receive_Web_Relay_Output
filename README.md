# MAIN README

HAN reader with relay control for Raspberry Pi 3B+
==================================================

Brief description
-----------------
This project for the Raspberry Pi has the following functions:
* Read and decode data from the HAN-port on Kaifa (MA304H3E 3-phase) smart electricity meter. It also works with Kaifa 1-phase meter, but this has not been tested.
* Present live data from the meter on a simple webpage, based on Apache2 webserver.
* Control two output relays.
* Download and view el-spotprices for the user's local area. Note, the program spotprices.py needs to be edited accordingly. 
* Send email to a specified address when Watt hours used during one hour exceeds a limit set by the user.
* Analyze log files from the meter on the website.

Hardware
--------
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
mkdir /home/pi/Cpp_AMS - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /home/pi/Python_AMS - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /var/meter_log - root - root - Anyone - Anyone - Anyone<br>
mkdir /var/www/html/data - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /var/www/html/img - pi - pi - Anyone - Only owner - Anyone<br>
mkdir /media/pi/name-of-usb-stick/meter - pi - pi - Anyone - Only owner - Anyone (for usb stick)<br>
mkdir /media/pi/name-of-usb-stick/prices - pi - pi - Anyone - Only owner - Anyone (for usb stick)<br>

Permissions and ownership shown above is like I have it on my RPi. Use a strong password, see below.
To give Apache permission to read /media/pi, edit pi to root - root- Anyone - Only owner and group - Anyone

Now copy the files from github into the corresponding directories on RPi listed above.

Edit a cronjob as your pi user, with crontab -e, with the following content:

10 00 * * * /home/pi/Cpp_AMS/copyFiles_meter<br>
20 00 * * * /usr/bin/python3 /home/pi/Python_AMS/copyfiles_prices.py<br>
00 14 * * * /usr/bin/python3 /home/pi/Python_AMS/spotprices.py<br>

Connect the equipment as shown in schematic.jpg

Goto folder Cpp_AMS and compile the source code with: g++ -W readAMS77.cpp. Then start reading messages by typing: ./a.out

NOTE: After upgrading from RPi Operating system stretch to buster I experienced problems while reading the meter. readAMS66.cpp has now been adapted to the newer buster release, and latest version is now readAMS77.cpp. In case of problems it is suggested that you try both program versions to determine what works best for you.

Goto folder Python_AMS and start the notification app with: python3 maxpowermonitor.py

When you see the two programs working in their respective terminal windows, you may open the website. From the laptop, when connected to the same local network, open the browser and enter the IP address of the Raspberry pi. The website is very simple, and should be self explanatory. Test that values are being updated in the "View current data from the meter" page. <br>

For presentation of log data on a laptop, please see the Readme file in the python folder.

To connect to the website from the outside world, you should open port 80 in your firewall. Beware the risk of getting the RPi hacked by outside users. You should therefore password protect the website. Information about how to do this is found on the internet.<br>

LIST OF FILES<br>
/home/pi/Cpp_AMS/readAMS77.cpp
/home/pi/Cpp_AMS/copyFiles_meter
/home/pi/Cpp_AMS/a.out
/home/pi/Python_AMS/copyfiles_prices.py<br>
/home/pi/Python_AMS/spotprices.py<br>
/home/pi/Python_AMS/maxpowermonitor.py<br>

ALLE FILER FOR PLOTTING HER

/var/www/html/currtime.php<br>
/var/www/html/gpio.php<br>
/var/www/html/notificationlimit.php<br>
/var/www/html/schematic.html<br>
/var/www/html/schematic.jpg<br>
/var/www/html/spotprices_NOK_tomorrow_24.php<br>
/var/www/html/spotprices_NOK_tomorrow_24.html<br>
/var/www/html/spotprices_NOK_tomorrow_96.php<br>
/var/www/html/spotprices_NOK_tomorrow_96.html<br>
/var/www/html/relaycontrol.php<br>
/var/www/html/threemaxes.php<br>
/var/www/html/threemaxes.html<br>
/var/www/html/amsdata.html<br>
/var/www/html/currpower.php<br>
/var/www/html/currlog.php<br>
/var/www/html/index.html<br>
/var/www/html/img/green_0.jpg<br>
/var/www/html/img/green_1.jpg<br>
/var/www/html/img/red_0.jpg<br>
/var/www/html/img/red_1.jpg<br>
/var/www/html/data/notificationlimit.data<br>
/var/www/html/data/threemaxes.data<br>

SJEKK UNDER HER OM PRICES FILENE I .data
HUSK OGSÅ PLOT CHOICES I .data

/var/www/html/data/prices_EUR_today.data<br>
/var/www/html/data/prices_NOK_today.data<br>
/var/www/html/data/prices_EUR_tomorrow.xml<br>
/var/www/html/data/prices_EUR_tomorrow.data<br>
/var/www/html/data/currencyconversions.xml<br>
/var/www/html/data/prices_NOK_tomorrow.data<br>
/var/www/html/data/currentlog.data<br>
/var/www/html/data/currentactivepower.data<br>
/var/www/html/data/currenttime.data<br>
/var/meter_log/20xx-yy-zz.txt<br>
/media/pi/D8AF-261F/meter/20xx-yy-zz.txt<br>
/media/pi/D8AF-261F/prices/20xxyyzz_EUR.data<br>
/media/pi/D8AF-261F/prices/20xxyyzz_NOK.data<br>


# MAIN README

AMS UTILITY - PROGRAMS AND FILES; CONNECTION BETWEEN FILES AND PROGRAMS/SCRIPTS
===============================================================================

Name                             Type              Location                      Purpose
----                             ----              --------                      -------
index.html                       html page         /var/www/html/                Main menu. Links all programs and scripts. The page also contains links
                                                                                 to NORD POOL and an in-house water meter web camera.
amsdata.html                     html page              "                        Shows live data from the AMS electricity meter.
                                                                                 Calls currtime.php, currpower.php, currlog.php, which in turn reads data
                                                                                 from the files currenttime.data, currentactivepower.data, currentlog.data .
spotprices_NOK_tomorrow_96.html  html page              "                        Shows Day-Ahead el-spotprices with 15m resolution. Calls spotprices_nok_tomorrow_96.php .
spotprices_NOK_tomorrow_96.php   php script             "                        Prepares data to be shown on spotprices_nok_tomorrow_96.html .
                                                                                 Reads data from prices_PT15M_NOK_96_NOx.data and zonechoice.data .
zonechoice_96.php                php script             "                        Called by spotprices_nok_tomorrow_96.html, for choosing zone to display.
                                                                                 Edits zonechoice.data .
spotprices_NOK_tomorrow_24.html  html page              "                        Shows Day-Ahead el-spotprices with 60m resolution. Calls spotprices_nok_tomorrow_24.php .
spotprices_NOK_tomorrow_24.php   php script             "                        Prepares data to be shown on spotprices_NOK_tomorrow_24.html .
                                                                                 Reads data from prices_PT15M_NOK_24_NOx.data and zonechoice.data .
zonechoice_24.php                php script             "                        Called by spotprices_nok_tomorrow_24.html, for choosing zone to display.
                                                                                 Edits zonechoice.data .
threemaxes.html                  html page              "                        Shows the three highest day maxes in current month. Calls threemaxes.php .
threemaxes.php                   php script             "                        Reads data from threemaxes.data, to show on threemaxes.html page.
relaycontrol.php                 php script             "                        GUI for control of two output relays. This script calls gpio.php .
gpio.php                         php script             "                        Controls two output relays, driven from output pins on Raspberry Pi 3B+.
notificationlimit.php            php script             "                        Edit kWh/h that triggers sending an email to specified email address.
                                                                                 Stores user defined kWh/h trigger value in  notificationlimit.data.
                                                                                 maxpowermonitor.py monitors the kWh/h value and sends email when applicable.
schematic.html                   html page              "                        Shows schematic of the equipment connected to Raspberry Pi 3B+.
schematic.jpg                    Image file             "                        Image containing the schematic.
zonemap.html                     html page              "                        Shows nordic el price zones.
zonemap.jpg                      Image file             "                        Image containing the zone map.
amsplotchoices.php               php script             "                        Edits parameter file amsplotchoices.data for plotting data from the AMS meter.
plot.php                         php script             "                        Starts main python script plotmain.py for plotting of currents, power, voltages.
plotmain.py                      python script          "                        Main python script for running the plot scripts. Deletes old plot images,
                                                                                 reads amsplotchoices.data, calls functions according to choices made by user.
plot_volts.py                    python script          "                        Plots two voltages (third not available for tech reasons).
volts.png                        Image file             "                        Latest voltages plot image. Gets overwritten by next plot.
plot_currents.py                 python script          "                        Plots three currents.
currents.png                     Image file             "                        Latest currents plot image. Gets overwritten by next plot.
plot_power.py                    python script          "                        Plots active power.
power.png                        Image file             "                        Latest power plot image. Gets overwritten by next plot.
currlog.php                      php script             "                        Reads currentlog.data every 10s, values are shown on amsdata.html page.
                                                                                 Currentlog.data file is updated by program readAMSxx.cpp .
currpower.php                    php script             "                        Reads currentactivepower.data every 2s, values are shown on amsdata.html page.
                                                                                 Currentactivepower.data file is updated by program readAMSxx.cpp .
currtime.php                     php script             "                        Reads currenttime.data every 2s, values are shown on amsdata.html page.
                                                                                 Currenttime.data file is updated by program readAMSxx.cpp .
																				 
amsplotchoices.data              data file         /var/www/html/data/           Stores user defined parameters for plot, edited with amsplotchoices.php .
currencyconversions.xml          xml file               "                        Conversion of EUR to NOK downloaded, read by spotprices.py .
currentactivepower.data          data file              "                        Holds active power read from the meter by readAMSxx.cpp. Updated every 2s.
currentlog.data                  data file              "                        Holds multiple data read from the meter by readAMSxx.cpp .
                                                                                 Updated at various intervals every 2s/10s/hourly.
currenttime.data                 data file              "                        Holds time updated from the meter by readAMSxx.cpp every 2s.
                                                                                 Read by currtime.php, to update time in amsdata.html page.
notificationlimit.data           data file              "                        Holds the kWh/h limit for when notification is sent to email address
                                                                                 given in the maxpowermonitor.py script. The kWh/h value is updated
																				 through notificationlimit.php .
prices_EUR_tomorrow_NO1.xml      xml file               "                        El-price data downloaded from enso-e by spotprices.py each day at 14.00 hrs.
prices_EUR_tomorrow_NO2.xml      xml file               "                                             "
prices_EUR_tomorrow_NO3.xml      xml file               "                                             "
prices_EUR_tomorrow_NO4.xml      xml file               "                                             "
prices_EUR_tomorrow_NO5.xml      xml file               "                                             "
prices_PT15M_NOK_24_NO1.data     data file              "                        Parsed .xml for zone NOx. Averaged 15m, shown in spotprices_NOK_tomorrow_24.html .
prices_PT15M_NOK_24_NO2.data     data file              "                                             "
prices_PT15M_NOK_24_NO3.data     data file              "                                             "
prices_PT15M_NOK_24_NO4.data     data file              "                                             "
prices_PT15M_NOK_24_NO5.data     data file              "                                             "
prices_PT15M_NOK_96_NO1.data     data file              "                        Parsed .xml for zone NOx. Price per 15m, shown in spotprices_NOK_tomorrow_96.html .
prices_PT15M_NOK_96_NO2.data     data file              "                                             "
prices_PT15M_NOK_96_NO3.data     data file              "                                             "
prices_PT15M_NOK_96_NO4.data     data file              "                                             "
prices_PT15M_NOK_96_NO5.data     data file              "                                             "
threemaxes.data                  data file              "                        Holds the three max kWh/h with date and time, during current month.
                                                                                 Content updated by maxpowermonitor.py .
                                                                                 Read by threemaxes.php, shown i treemaxes.html .
zonechoice.data                  data file              "                        Holds the current price zone to be shown.
                                                                                 Read by zonechoice_24.php and zonechoice_96.php, to be used by, and shown in,
                                                                                 spotprices_NOK_tomorrow_24.html and spotprices_NOK_tomorrow_96.html respectively.

green_0.jpg                      Image file        /var/www/html/img/            Show On/Off condition of output relays.
green_1.jpg                      Image file             "                                             "
red_0.jpg                        Image file             "                                             "
red_1.jpg                        Image file             "                                             "

readAMSxx.cpp                    C++ program       /home/pi/Cpp_AMS/             Source code for a.out. These files are updated by the program:
                                                                                 /var/meter_log/yyyy-mm-dd.txt                Every 10s.
                                                                                 /var/www/html/data/currenttime.data          Every 2s.
                                                                                 /var/www/html/data/currentactivepower.data      "
                                                                                 /var/www/html/data/currentlog.data various intervals every 2s/10s/hourly.
a.out                            executable file        "                        Executable version of readAMSxx.cpp . Does the actual reading of the meter.
copyFiles_meter                  shell script           "                        Copy logs to usb stick. Cleans /var/meter_log/ of log files older than 2 days.
                                                                                 Run as cron job 10 minutes past every midnight.
																				 
yyyy-mm-dd.txt                                     /var/meter_log                Updated by readAMSxx.cpp Every 10s.

copyfiles_prices.py              python script     /home/pi/Python_AMS           Copy price data per day to usb stick. Run as cron job 20 minutes past midnight.
                                                                                 Note: At present only prices for NO5 are saved to the usb stick.
                                                                                 prices_PT15M_NOK_24_NO5.data -> yyyymmdd_PT15M_NOK_24_NO5.data .
                                                                                 prices_PT15M_NOK_96_NO5.data -> yyyymmdd_PT15M_NOK_96_NO5.data .
maxpowermonitor.py               python script          "                        Calculate energy difference between each top of hour.
                                                                                 Determines the highest Wh value for each day.
                                                                                 Keeps the three highest day values within the month.
																				 Updates the file threemaxes.data .
spotprices.py                    python script          "                        Downloads spotprices and generates price data files for all norwegian price zones.
                                                                                 Run as cron job every day at 14.00 hrs.
                                                                                 Files: prices_PT15M_NOK_24_NOx.data and prices_PT15M_NOK_96_NOx.data .

yyyy-mm-dd.txt                                     /media/pi/D8AF-261F/meter/    Log per day of AMS meter, with 10s resolution, copied from folder /var/meter_log .

yyyymmdd_PT15M_NOK_24_NO5.data                     /media/pi/D8AF-261F/prices/   Log per day of el-spotprices, one price per hour (averaged 15m prices).
yyyymmdd_PT15M_NOK_96_NO5.data                          "                        Log per day of el-spotprices, one price per 15m.
