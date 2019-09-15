# MAIN README

The programs in this folder will be upgraded for Python 3 in the future.

About the programs
==================
* Present log data from AMS meter graphically with the Python matplotlib module.

Get started (Windows 10)
------------------------
Install the latest Python 2.7 from here: https://www.python.org/downloads/
Remember to check the box for installing the Path Environment variable for Python 2.7.

If you installed version 2.7.9 or later, you should already have the pip package installer on your PC.
Now check if pip installer needs upgrading by running: python -m pip install --upgrade pip
If necessary pip can be istalled from here: https://www.makeuseof.com/tag/install-pip-for-python/

Check the already installed packages by running: pip list
Eventually you should have these packages:

backports.functools-lru-cache 1.5, beautifulsoup4 4.7.1, cycler 0.10.0, html5lib 1.0.1, kiwisolver 1.0.1, lxml 4.3.0, matplotlib 2.2.3, numpy 1.15.4, pandas 0.23.4, pip 19.0.1, pyparsing 2.3.1, python-dateutil 2.7.5, pytz 2018.9, setuptools 39.0.1, six 1.12.0, soupsieve 1.7, webencodings 0.5.1

If some package is missing in your list, you can install it with this command: pip install <package name>

You should now have all needed packages to view log data on PC. To transfer log data from Raspberry Pi 3 B+ to the laptop, pcsp.exe should be the preferred program.

Plot recorded data on the laptop screen:
----------------------------------------
* It is assumed that you have already copied the logfiles from RPi to the laptop.
* On the laptop, open main_prog_en.py (or main_prog_no.py) in the IDLE editor.
* Edit the variable named folder, to point to your chosen logs folder.
* Start the program with f5. An entry window should appear.
* Select up to two dates, and which graphs you want to be shown, then click Ok.
* The graphs should show, and you can now manipulate them by zooming, panning etc.
