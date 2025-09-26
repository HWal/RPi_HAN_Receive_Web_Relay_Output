############################################################
# Plot spotprice data from Entso_e,                        #
# saved  to disk on Raspberry Pi.                          #
# Main program for entry of plot choices                   #
############################################################

from datetime import datetime
import matplotlib.pyplot as plt
from graphics import *
import plot_spot
import sys

def input_values(folder, date1, date2, date3, choice_1_1, choice_1_2, choice_2_1, choice_2_2, choice_3_1, choice_3_2, win_in):
    # Create entry fields and show current values
    folder_entry = Entry(Point(505, 120), 50)
    folder_entry.setText(folder)
    folder_entry.draw(win_in)
    date_entry1 = Entry(Point(324, 215), 10)
    date_entry1.setText(date1)
    date_entry1.draw(win_in)
    date_entry2 = Entry(Point(324, 265), 10)
    date_entry2.setText(date2)
    date_entry2.draw(win_in)
    date_entry3 = Entry(Point(324, 315), 10)
    date_entry3.setText(date3)
    date_entry3.draw(win_in)
    choice_entry1_1 = Entry(Point(660, 215), 2)
    choice_entry1_1.setText(choice_1_1)
    choice_entry1_1.draw(win_in)
    choice_entry1_2 = Entry(Point(706, 215), 2)
    choice_entry1_2.setText(choice_1_1)
    choice_entry1_2.draw(win_in)
    choice_entry2_1 = Entry(Point(660, 265), 2)
    choice_entry2_1.setText(choice_2_1)
    choice_entry2_1.draw(win_in)
    choice_entry2_2 = Entry(Point(706, 265), 2)
    choice_entry2_2.setText(choice_1_1)
    choice_entry2_2.draw(win_in)
    choice_entry3_1 = Entry(Point(660, 315), 2)
    choice_entry3_1.setText(choice_3_1)
    choice_entry3_1.draw(win_in)
    choice_entry3_2 = Entry(Point(706, 315), 2)
    choice_entry3_2.setText(choice_1_1)
    choice_entry3_2.draw(win_in)
    # Get mouse click and position
    click = win_in.getMouse()
    a = click.getX()
    b = click.getY()
    # Get values from entry fields
    folder = folder_entry.getText()
    date1 = date_entry1.getText()
    date2 = date_entry2.getText()
    date3 = date_entry3.getText()
    choice_1_1 = choice_entry1_1.getText()
    choice_1_2 = choice_entry1_2.getText()
    choice_2_1 = choice_entry2_1.getText()
    choice_2_2 = choice_entry2_2.getText()
    choice_3_1 = choice_entry3_1.getText()
    choice_3_2 = choice_entry3_2.getText()
    # Check if user wants to quit the app
    if (a > 620 and a < 730) and (b > 389 and b < 410):
        win_in.close()
        plt.close('all')
        sys.exit()
    return folder, date1, date2, date3, choice_1_1, choice_1_2, choice_2_1, choice_2_2, choice_3_1, choice_3_2


def main():
    # Create initial window
    win_in = GraphWin("Control window", 800, 450)
    info_text1 = Text(Point(400, 55), "SPOT PRICES IN NOK FROM ENTSO-E")
    info_text1.draw(win_in)
    folder_text = Text(Point(98, 120), "Path to log files:")
    folder_text.draw(win_in)
    currency_text = Text(Point(684, 185), "NOK   EUR")
    currency_text.draw(win_in)
    date_text1 = Text(Point(120, 215), "Date (YYYY-MM-DD):")
    date_text1.draw(win_in)
    date_text2 = Text(Point(120, 265), "Date (YYYY-MM-DD):")
    date_text2.draw(win_in)
    date_text3 = Text(Point(120, 315), "Date (YYYY-MM-DD):")
    date_text3.draw(win_in)
    choice_text1 = Text(Point(549, 215), "Price graph (Y/N):")
    choice_text1.draw(win_in)
    choice_text2 = Text(Point(549, 265), "Price graph (Y/N):")
    choice_text2.draw(win_in)
    choice_text3 = Text(Point(549, 315), "Price graph (Y/N):")
    choice_text3.draw(win_in)
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
    folder = "/media/pi/D8AF-261F/prices/"
    date1 = "2025-08-13"
    date2 = "2025-08-17"
    date3 = "2025-08-19"
    choice_1_1 = choice_1_2 = choice_2_1 = choice_2_2 = choice_3_1 = choice_3_2 = "N"

    # Eternal loop
    while True:
        # Send current values and get new input values
        folder, date1, date2, date3, choice_1_1, choice_1_2, choice_2_1, choice_2_2, \
        choice_3_1, choice_3_2 = input_values(folder, date1, date2, date3, choice_1_1, \
        choice_1_2, choice_2_1, choice_2_2, choice_3_1, choice_3_2, win_in)
        if choice_1_1 == "Y" or choice_1_1 == "y":
            plot_spot.main(folder + date1[0:4] + date1[5:7] + date1[8:11] + "_NOK.data")
        if choice_1_2 == "Y" or choice_1_2 == "y":
            plot_spot.main(folder + date1[0:4] + date1[5:7] + date1[8:11] + "_EUR.data")
        if choice_2_1 == "Y" or choice_2_1 == "y":
            plot_spot.main(folder + date2[0:4] + date2[5:7] + date2[8:11] + "_NOK.data")
        if choice_2_2 == "Y" or choice_2_2 == "y":
            plot_spot.main(folder + date2[0:4] + date2[5:7] + date2[8:11] + "_EUR.data")
        if choice_3_1 == "Y" or choice_3_1 == "y":
            plot_spot.main(folder + date3[0:4] + date3[5:7] + date3[8:11] + "_NOK.data")
        if choice_3_2 == "Y" or choice_3_2 == "y":
            plot_spot.main(folder + date3[0:4] + date3[5:7] + date3[8:11] + "_EUR.data")
        if date1 == "2099-12-31" or date2 == "2099-12-31" or date3 == "2099-12-31":
            win_in.close()
            plt.close('all')
            sys.exit()
        # Reset plot choices to default values
        # price_nok = "N"

if __name__ == "__main__":
    main()
