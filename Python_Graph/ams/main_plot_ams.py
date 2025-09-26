###############################################################
# Plot data collected from AMS smart electricity meter        #
###############################################################

from datetime import datetime
import matplotlib.pyplot as plt
from graphics import *
import plot_power
import plot_voltage
import plot_current
import sys

def input_values(folder, date, power, volt, current, hour1, hour2, win_in):
    # Create entry fields and show current values
    folder_entry = Entry(Point(505, 85), 50)
    folder_entry.setText(folder)
    folder_entry.draw(win_in)
    date_entry = Entry(Point(324, 150), 10)
    date_entry.setText(date)
    date_entry.draw(win_in)
    power_entry = Entry(Point(720, 150), 2)
    power_entry.setText(power)
    power_entry.draw(win_in)
    volt_entry = Entry(Point(720, 180), 2)
    volt_entry.setText(volt)
    volt_entry.draw(win_in)
    current_entry = Entry(Point(720, 210), 2)
    current_entry.setText(current)
    current_entry.draw(win_in)
    hour_entry1 = Entry(Point(720, 260), 2)
    hour_entry1.setText(hour1)
    hour_entry1.draw(win_in)
    hour_entry2 = Entry(Point(720, 290), 2)
    hour_entry2.setText(hour2)
    hour_entry2.draw(win_in)
    # Get mouse click and position
    click = win_in.getMouse()
    a = click.getX()
    b = click.getY()
    # Get values from entry fields
    folder = folder_entry.getText()
    date = date_entry.getText()
    power = power_entry.getText()
    volt = volt_entry.getText()
    current = current_entry.getText()
    hour1 = hour_entry1.getText()
    hour2 = hour_entry2.getText()
    # Check if user wants to quit the app
    if (a > 620 and a < 730) and (b > 389 and b < 410):
        win_in.close()
        plt.close('all')
        sys.exit()
    return folder, date, power, volt, current, hour1, hour2


def main():
    # Create initial window
    win_in = GraphWin("Control window", 800, 450)
    info_text1 = Text(Point(400, 35), "PLOT DATA FROM KAIFA MA304H3E SMART METER")
    info_text1.draw(win_in)
    folder_text = Text(Point(98, 85), "Path to log files:")
    folder_text.draw(win_in)
    date_text = Text(Point(120, 150), "Date (YYYY-MM-DD):")
    date_text.draw(win_in)
    power_text1 = Text(Point(583, 150), "Power graph (Y/N):")
    power_text1.draw(win_in)
    volt_text1 = Text(Point(588, 180), "Voltage graph (Y/N):")
    volt_text1.draw(win_in)
    current_text1 = Text(Point(586, 210), "Current graph (Y/N):")
    current_text1.draw(win_in)
    hour_text1 = Text(Point(583, 260), "Start hour (00 - 23):")
    hour_text1.draw(win_in)
    hour_text2 = Text(Point(581, 290), "End hour (01 - 24):")
    hour_text2.draw(win_in)
    info_text2 = Text(Point(124, 400), "Enter values and click:")
    info_text2.draw(win_in)
    ok_text = Text(Point(270, 400), "Ok")
    ok_text.draw(win_in)
    p1 = Point(240, 410)
    p2 = Point(300, 389)
    rect1 = Rectangle(p1, p2)
    rect1.draw(win_in)
    finish_text = Text(Point(675, 400), "Exit")
    finish_text.draw(win_in)
    p3 = Point(620, 410)
    p4 = Point(730, 389)
    rect2 = Rectangle(p3, p4)
    rect2.draw(win_in)
    
    # set default values
    # folder = "C:\\Users\\HelgeN550JK\\Desktop\\Raspberry_Pi\\RPi_HAN_Receive_Web_Relay_Output\\python_Laptop\\logs\\"
    folder = "/media/pi/D8AF-261F/meter/"
    date = "2025-04-27"
    power = volt = current = "N"
    hour1 = "00"
    hour2 = "24"

    # Eternal loop
    while True:
        # Send current values and get new input values
        folder, date, power, volt, current, hour1, hour2 = input_values(folder, date, power, volt, current, hour1, hour2, win_in)
        if int(hour1) < int(hour2) and int(hour1) >= 0 and int(hour1) <= 23 and int(hour2) >= 1 and int(hour2) <= 24:
            if power == "Y" or power == "y":
                plot_power.main(folder + date + ".txt", hour1, hour2)
            if volt == "Y" or volt == "y":
                plot_voltage.main(folder + date + ".txt", hour1, hour2)
            if current == "Y" or current == "y":
                plot_current.main(folder + date + ".txt", hour1, hour2)
        if date == "2099-12-31":
            win_in.close()
            plt.close('all')
            sys.exit()
        # Reset plot choices to default values
        # power = volt = current = "N"
        # hour1 = "00"
        # hour2 = "24"

if __name__ == "__main__":
    main()
