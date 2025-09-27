############################################################
# Plot spotprice data from Entso_e,                        #
# saved  to disk on Raspberry Pi.                          #
# This module performs the actual plot.                    #
############################################################

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as md

# Read file from selected date containing NOK spotprices
def main(fileName):

  # Extract string for chosen currency
  currency = fileName[-8:][0:3]

  with open (fileName, "r") as fp:
    # rwList contains only one line
    # readLines() returns a list with one element per line
    rwList = fp.readlines()

  priceList = []
  tmList = []
  tmLabels = []

  # Split the single line file into a commaseparated list
  spltList = rwList[0].split(",")

  # The list should contain 24 price elements, but may not be complete
  # First element is a date string, last element is EUR <> NOK exchange rate
  # in the NOK list, and time resolution in the EUR list.
  # If price element(s) are marked "unavailable", replace with "0.0"
  for index, element in enumerate(spltList):
    if element == "unavailable":
      spltList[index] = "0.0"

  # Remove last element of the list
  del spltList[-1]

  # Extract date from the first element of spltList
  dateString = spltList[0][0:4] + "-" + spltList[0][4:6] + "-" + spltList[0][6:8]

  # Remove the first (date) element from the list
  spltList.pop(0)

  # Format labels of the x axis
  for p in range(24):
    tmList.append(p)
  for q in range(24):
    tmLabels.append(f'{q:02d}' + '-' + f'{(q + 1):02d}')

  # Generate the 24 spotprices
  for r in range(24):
    priceList.append(float(spltList[r]))

  fig = plt.figure()
  ax = fig.add_subplot(1,1,1)

  plt.title("SPOT PRICES IN " + currency + " FROM ENTSO-E, " + dateString \
  + "\n Note: Price 0.0 means 0.0 or not available")
  plt.xticks(rotation=90)
  plt.xticks(tmList, tmLabels)

  if currency == "NOK":
    ax.plot(tmList, priceList, "b", label="Price per kWh (NOK)")
  if currency == "EUR":
    ax.plot(tmList, priceList, "g", label="Price per MWh (EUR)")
  # ax.xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d"))
  # ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M:%S"))
  ax.grid(which='both')
  ax.legend()
  plt.show(block=False)

if __name__ == '__main__':
  main()
