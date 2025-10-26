#!/usr/bin/python3

import matplotlib
matplotlib.use('Agg')
# from datetime import datetime
# import matplotlib.pyplot as plt
import plot_volts
import plot_currents
import plot_power
import os
# import sys

def main():

    # Delete existing plots
    if os.path.exists("power.png"):
        os.remove("power.png")
    if os.path.exists("volts.png"):
        os.remove("volts.png")
    if os.path.exists("currents.png"):
        os.remove("currents.png")

    with open ("/var/www/html/data/amsplotchoices.data", "r") as fp1:
        choicesString = fp1.readlines()
        fp1.close()

    # spltlist[0] -> [8] is: log files path, year, month, day, Watt, Volt, Amp, hr start, hr stop
    spltlist = choicesString[0].split(",")
    # choicesString = spltlist[0] + "," + spltlist[1] + "," + spltlist[2] + "," + spltlist[3] + "," \
    # + spltlist[4] + "," + spltlist[5] + "," + spltlist[6] + "," + spltlist[7] + "," + spltlist[8]

    # Call plot
    path_file = spltlist[0] + spltlist[1] + "-" + spltlist[2] + "-" + spltlist[3] + ".txt"
    starthour = spltlist[7]
    endhour = spltlist[8]

    if starthour < endhour:
        if spltlist[4] == "Y" or spltlist[4] == "y":
            plot_power.main(path_file, starthour, endhour)
        if spltlist[5] == "Y" or spltlist[5] == "y":
            plot_volts.main(path_file, starthour, endhour)
        if spltlist[6] == "Y" or spltlist[6] == "y":
            plot_currents.main(path_file, starthour, endhour)

    # input()

if __name__ == "__main__":
    main()
