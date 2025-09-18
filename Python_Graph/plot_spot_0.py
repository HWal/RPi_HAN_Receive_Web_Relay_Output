############################################################
# Plot spotprice data from Entso_e,                        #
# saved  to disk by Raspberry Pi.                          #
#                                                          #
# Plot shows active power during one day and night (date). #
############################################################

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as md

def main(fileName, hour1, hour2):
  with open (fileName, "r") as fp:
    rwList = fp.readlines()

  # spltList = []
  # tmList = []
  priceList = []

  spltList = rwList[0].split(",")

  del spltList[-1]

  dateString = spltList[0][0:4] + "-" + spltList[0][4:6] + "-" + spltList[0][6:8]
  tmString = dateString + " 00:00:00"
  tmObject = datetime.strptime(tmString, '%Y-%m-%d %H:%M:%S')
  tmObject = tmObject.date()

  spltList.pop(0)

  tmList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
  tmLabels = ["00-01", "01-02", "02-03", "03-04", "04-05", "05-06", "06-07", "07-08", "08-09", \
              "09-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", \
              "18-19", "19-20","20-21", "21-22", "22-23", "23-24"]

  for x in range(24):
    priceList.append(float(spltList[x]))

  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)

  plt.title("SPOT PRICE DATA FROM ENTSO-E, " + dateString)
  plt.xticks(rotation=90)
  plt.xticks(tmList, tmLabels)

  ax.plot(tmList, priceList, "b", label="Price per kWh (NOK)")
  # ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
  # ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
  ax.grid(which='both')
  ax.legend()
  plt.show(block=False)

if __name__ == '__main__':
  main()
