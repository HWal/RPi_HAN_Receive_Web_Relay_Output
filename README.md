# MAIN README

HAN reader with relay control for Raspberry Pi 3 B+
===================================================

Brief description
-----------------
This project for the Raspberry Pi has the following functions:
* Read and decode data from the HAN-port on Kaifa (MA304H3E 3-phase) smart electricity meter. It also reads data from Kaifa 1-phase meter, but this has not been tested.
* Present live data from the meter on a simple webpage, based on Apache2 webserver.
* Control two output relays.
* Send notification to mobile phone via the IFTTT service when averaged active power (user defined averaging period) exceeds a limit set by the user.
* Analyze log files on a Windows 10 laptop.

Hardware
--------
* One Raspberry Pi 3 B+ with Raspbian (stretch) installed
* 5V power supply and USB cable
* TSS721 Module Board M-BUS To TTL converter (AliExpress)
* Two 3.3V relay boards that will drain less than 12mA from RPi gpio output
* Some connecting wire
* A laptop, in my project one that is running Windows 10

Preparation of RPi while powered up and connectected directly to a screen (TV)
------------------------------------------------------------------------------
Activate VNC here: sudo raspi-config -> Interfacing Options -> VNC -> Enable VNC server <br>
Activate SSH here: sudo raspi-config -> Interfacing Options -> SSH -> Enable SSH server

Open a terminal window, note the IP number of the RPi returned from the command: hostname -I

Prepare a laptop for remote control of the RPi
----------------------------------------------
Download VNC viewer: https://www.realvnc.com/en/connect/download/viewer/ <br>
Download putty.exe and pscp.exe: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html <br>
You should now be able to control RPi from the laptop on your local network, both via the GUI (VNC viewer) and terminal window (putty.exe). Also you can copy files between RPi and the laptop with pscp.exe. To connect, use the IP number noted above.

From now on a separate screen should rarely be necessary, and the RPi will be working in "Headless mode".

Continue to prepare RPi in Headless mode
----------------------------------------
Preferably, give RPi a static IP address, see: https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address/74428#74428

Install Apache2 webserver: sudo apt-get update , sudo apt-get upgrade , sudo apt-get install apache2 -y <br>
Make user pi the owner of /var/www/html: sudo chown pi: -R html <br>
Install PHP for the relay control script: sudo apt-get install php libapache2-mod-php -y <br>

Make a "clean" UART port on the RPi 3. For reference, see: https://www.raspberrypi.org/documentation/configuration/uart.md and https://spellfoundry.com/2016/05/29/configuring-gpio-serial-port-raspbian-jessie-including-pi-3-4/ <br>
We want these pins to communicate with the M-BUS To TTL converter:  <br>
Physical pin 8 = gpio 14 = Tx <br>
Physical pin 10 = gpio 15 = Rx

sudo apt-get update , sudo apt-get upgrade <br>

Disable console and activate serial: sudo raspi-config -> Interfacing Options -> Serial <br>
Login shell accessible over serial: No <br>
Serial port hardware enabled: Yes <br>
The system asks for a reboot: Yes

We can stop the getty service, as long as the console is not used: <br>
sudo systemctl stop serial-getty@ttyS0.service <br>
sudo systemctl disable serial-getty@ttyS0.service <br>

We don't need to use the Bluetooth modem at this time. <br>
sudo systemctl disable hciuart  // Disables the Bluetooth modem <br>

We want to swap the serial ports, please see the relevant lines in the file /boot/overlays/README. <br>
sudo nano /boot/config.txt, and add at the bottom: dtoverlay=pi3-disable-bt <br>
sudo reboot <br>
Now ttyAMA0 / PL011 / UART0 is connected to gpio 14 / 15 which are the physical pins 8 / 10 <br>

Make some directories on the Raspberry Pi: <br>
Command - Owner - Group - View - Change - Access <br>
mkdir /home/pi/Cpp_AMS - pi - pi - Anyone - Only owner - Anyone <br>
mkdir /home/pi/Python_AMS - pi - pi - Anyone - Only owner - Anyone <br>
mkdir /var/kaifalog - root - root - Anyone - Anyone - Anyone <br>
mkdir /var/www/html/data - pi - pi - Anyone - Only owner - Anyone <br>
mkdir /var/www/html/img - pi - pi - Anyone - Only owner - Anyone

Permissions and ownership shown above is like I have it on my RPi. root as owner/group of /var/kaifalog is related to the fact that I run a cron job just after midnight, to copy the completed logfiles to a USB stick. Not described here.

Now copy the files from github into the corresponding directories on RPi listed above.

Goto folder Cpp_AMS and start reading messages with: ./a.out . If you are not permitted to run the program, recompile the source code with: g++ -W readAMS58.cpp

Goto folder Python_AMS and start the notification app with: python3 notify04.py

When you see the two programs working in their respective terminal windows, you may open the website. From the laptop, when connected to the same local network, open the browser and enter the IP address of the Raspberry pi. The website is very simple, and should be self explanatory. Test that messages are shown in the messages page. Also, edit the user settings suited to your application.

Configuring notifications in IFTTT is outside the scope of this Readme, but it is quite easy to get working if you spend a little time looking into it. When that is done, you may test the functionality of the notification service. See: https://ifttt.com

For presentation of log data, please check the Readme in the python folder.

To connect to the website from the outside world, you should open port 80 in your firewall. Beware the risk of getting the RPi hacked by outside users.
