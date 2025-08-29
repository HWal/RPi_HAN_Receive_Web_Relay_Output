# MAIN README

HAN reader with relay control for Raspberry Pi 3B+
==================================================

Brief description
-----------------
This project for the Raspberry Pi has the following functions:
* Read and decode data from the HAN-port on Kaifa (MA304H3E 3-phase) smart electricity meter. It also reads data from Kaifa 1-phase meter, but this has not been tested.
* Present live data from the meter on a traditional webpage, based on Apache2 webserver.
* Control two output relays.
* Download and view el-spotprices for the user's local area. Note, the program spotprices.py needs to be edited accordingly. 
* Send email to a specified address when Watt hours used during one hour exceeds a limit set by the user.
* Analyze log files on a Windows laptop.

Hardware
--------
* One Raspberry Pi 3 B+ with Raspbian (Buster) installed
* 5V power supply and USB cable
* TSS721 Module Board M-BUS To TTL converter (AliExpress)
* Two 3.3V relay boards that will drain less than 12mA from RPi gpio output
* Some connecting wire
* A laptop, in my project one that is running Windows 10

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

Continue to prepare RPi in Headless mode
----------------------------------------
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

Permissions and ownership shown above is like I have it on my RPi. Data security has not been considered so far.

Now copy the files from github into the corresponding directories on RPi listed above.

Edit a cronjob as your pi user, with crontab -e, with the following content:

05 00 * * * /usr/bin/python3 /home/pi/Python_AMS/copyprices_1.py<br>
10 00 * * * /home/pi/Cpp_AMS/copyFiles_meter<br>
00 15 * * * /usr/bin/python3 /home/pi/Python_AMS/spotprices.py<br>
55 23 * * * /usr/bin/python3 /home/pi/Python_AMS/copyprices_2.py<br>

Connect the equipment as shown in schematic.jpg

Goto folder Cpp_AMS and compile the source code with: g++ -W readAMSxx.cpp. Then start reading messages by typing: ./a.out

NOTE: After upgrading from RPi Operating system stretch to buster I experienced problems while reading the meter. readAMS66.cpp has now been adapted to the newer buster release, and latest version is now readAMS77.cpp. In case of problems it is suggested that you try both program versions to determine what works best for you.

Goto folder Python_AMS and start the notification app with: python3 maxpowermonitor.py

When you see the two programs working in their respective terminal windows, you may open the website. From the laptop, when connected to the same local network, open the browser and enter the IP address of the Raspberry pi. The website is very simple, and should be self explanatory. Test that values are being updated in the "View current data from the meter" page. <br>

Note: I have a water meter as well, which has an entry in the webpage. Details about this is currently not covered in this project.

For presentation of log data on laptop, please see the Readme file in the python folder.

To connect to the website from the outside world, you should open port 80 in your firewall. Beware the risk of getting the RPi hacked by outside users. You should therefore password protect the website. Information about how to do this is found on the internet.<br>

LIST OF FILES<br>
/home/pi/Cpp_AMS/readAMS77.cpp                  C++ source code<br>
/home/pi/Cpp_AMS/copyFiles_meter                bash script<br>
/home/pi/Cpp_AMS/a.out                          executable, reads meter<br>
/home/pi/Python_AMS/copyprices_1.py<br>
/home/pi/Python_AMS/copyprices_1.py<br>
/home/pi/Python_AMS/spotprices.py<br>
/home/pi/Python_AMS/maxpowermonitor.py<br>
/var/www/html/currtime.php<br>
/var/www/html/gpio.php<br>
/var/www/html/notificationlimit.php<br>
/var/www/html/schematic.html<br>
/var/www/html/schematic.jpg<br>
/var/www/html/spotprices_EUR_today.php<br>
/var/www/html/spotprices_EUR_today.html<br>
/var/www/html/spotprices_EUR_tomorrow.php<br>
/var/www/html/spotprices_EUR_tomorrow.html<br>
/var/www/html/spotprices_NOK_today.php<br>
/var/www/html/spotprices_NOK_today.html<br>
/var/www/html/spotprices_NOK_tomorrow.php<br>
/var/www/html/spotprices_NOK_tomorrow.html<br>
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
/var/www/html/data/prices_EUR_today.data<br>
/var/www/html/data/prices_NOK_today.data<br>
/var/www/html/data/prices_EUR_tomorrow.xml<br>
/var/www/html/data/prices_EUR_tomorrow.data<br>
/var/www/html/data/currencyconversions.xml<br>
/var/www/html/data/prices_NOK_tomorrow.data<br>
/var/www/html/data/currentlog.data<br>
/var/www/html/data/currentactivepower.data<br>
/var/www/html/data/currenttime.data<br>
/var/meter_log/20xx-yy-zz.txt                    Prepare meter log files for permanent storage on usb stick<br>
/media/pi/D8AF-261F/meter/20xx-yy-zz.txt<br>
/media/pi/D8AF-261F/prices/20xxyyzz_EUR.data<br>
/media/pi/D8AF-261F/prices/20xxyyzz_NOK.data<br>
