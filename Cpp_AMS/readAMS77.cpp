//***************************************************************************
// READ MESSAGES FROM HAN PORT ON KAIFA MA304H3E 3-PHASE ELECTRICITY METER.
// THIS PROGRAM ALSO HANDLES MESSAGES FROM 1-PHASE METER OF THE SAME BRAND.
// WRITE DATA FROM ALL MESSAGES (LISTS 1, 2, 3) TO WEBPAGE: amsdata.html
// APPEND LIST2 AND LIST3 MESSAGES TO LOGFILE: yyyy-mm-dd.txt
// WRITE LATEST ACT POWER FROM ALL MESSAGES TO FILE: currentactivepower.data
// WRITE LATEST TIME FROM ALL MESSAGES TO FILE: currenttime.data
// WRITE LATEST LIST2 AND LIST3 MESSAGE TO FILE: currentlog.data
//***************************************************************************

#include <iostream>  // Standard input output library
#include <string.h>  // Allow string methods
#include <unistd.h>  // read, write, close
#include <fcntl.h>   /* open, O_RDONLY, O_RDWR, O_WRONLY, O_NOCTTY, O_NDELAY (O_NONBLOCK)
                        Note: O_NDELAY and O_NONBLOCK might override VMIN and VTIME */
#include <termios.h> /* tcgetattr, B9600, CS8, CLOCAL, CREAD, CSTOPB, IGNPAR,
                        TCIFLUSH, TCOFLUSH, VTIME, VMIN, tcflush, TCSANOW, tcsetattr */
#include <fstream>   // Filestream for writing data to file

using namespace std;

// On Raspberry Pi pins 8 and 10 are UART0_TXD and UART0_RXD respectively

// Declare and initialize a file descriptor with integer value
int uart0_filestream = -1; // -1=error, positive value=normal opening

// Variables for extracting values from the buffer
string obis_list_version = "0";
string meterId = "0";
string meterModel = "0";
int act_pow_pos;             // Active Power +
int act_pow_neg;             // Active Power -
int react_pow_pos;           // Reactive Power +
int react_pow_neg;           // Reactive Power -
int curr_L1;                 // Current Phase L1 mA
int curr_L2;                 // Current Phase L2 mA
int curr_L3;                 // Current Phase L3 mA
int volt_L1;                 // Voltage L1
int volt_L2;                 // Voltage L2
int volt_L3;                 // Voltage L3
int act_energy_pos;          // Active Energy +
int act_energy_neg;          // Active Energy -
int react_energy_pos;        // Reactive Energy +
int react_energy_neg;        // Reactive Energy -
// date-time variables (..0) used in this program
int year0;
int month0;
int day0;
int hour0;
int min0;
int sec0;
// date-time variables (..1) NOT used in this program
int year1;
int month1;
int day1;
int hour1;
int min1;
int sec1;
int num_items;

// Other variables
string listType = "0";               // Type of the last read HAN message
string msgDate = "0";                // HAN field - all list types
string msgTime = "0";                // HAN field - all list types
string actPowerPlus = "0";           // HAN field - all list types
string actPowerMinus = "0";          // HAN field - list types 2 and 3 - 1&3 phase
string reactPowerPlus = "0";         // HAN field - list types 2 and 3 - 1&3 phase
string reactPowerMinus = "0";        // HAN field - list types 2 and 3 - 1&3 phase
string currentL1 = "0";              // HAN field - list types 2 and 3 - 1&3 phase
string currentL2 = "0";              // HAN field - list types 2 and 3 - 3 phase
string currentL3 = "0";              // HAN field - list types 2 and 3 - 3 phase
string voltageL1 = "0";              // HAN field - list types 2 and 3 - 1&3 phase
string voltageL2 = "0";              // HAN field - list types 2 and 3 - 3 phase
string voltageL3 = "0";              // HAN field - list types 2 and 3 - 3 phase
string activeEnergyPlus = "0";       // HAN field - list type 3 - 1&3 phase
string activeEnergyMinus = "0";      // HAN field - list type 3 - 1&3 phase
string reactiveEnergyPlus = "0";     // HAN field - list type 3 - 1&3 phase
string reactiveEnergyMinus = "0";    // HAN field - list type 3 - 1&3 phase
bool debugHex = true;                /* Set true to display telegram length
                                        and HEX values on serial monitor */
bool debugText = true;               // Set true to display telegrams in clear text
unsigned char buf[255];              // Buffer array for complete message
unsigned char buf1[10];              // Receive buffer used in read statement
int rx_length = 0;                   // Length of the last read char buffer, 1 or 0
int n_bytes = 0;                     // Length of message

// FORWARD DECLARATIONS
void receive_bytes();
bool validate_msg();
int decodeMessage();
int printData();



int main() {
  // Open filestream in non blocking r/w mode (O_NDELAY loads CPU to 99,9% !)
  // uart0_filestream = open("/dev/ttyAMA0", O_RDWR | O_NOCTTY | O_NDELAY);
  // Open filestream in blocking read only mode (waits for bytes, saves CPU %)
  uart0_filestream = open("/dev/ttyAMA0", O_RDONLY | O_NOCTTY);
  if (uart0_filestream == -1) {
    printf("Error - Unable to open UART.\n");
  }
  // Set communication options
  struct termios options;
  tcgetattr(uart0_filestream, &options);
  options.c_cflag = B2400 | CS8 | CLOCAL | CREAD | PARENB;
  options.c_iflag = IGNPAR;
  options.c_oflag = 0;
  options.c_lflag = 0;
  options.c_cc[VTIME] = 2; /* read returns 2 * 0.1s after the read call
                              if no data is received. */
  options.c_cc[VMIN] = 0;  // This is a pure timed read, see explanation below
  tcflush(uart0_filestream, TCIFLUSH);
  tcsetattr(uart0_filestream, TCSANOW, &options);

  // Call never ending read function
  receive_bytes();

  // CLOSE THE UART - the program probably never gets here
  cout << "Closing uart...\n";
  close(uart0_filestream);
  cout << "uart closed\n";

  return 0;
}



void receive_bytes() {
  if (uart0_filestream != -1) {
    /* This is a pure timed read. If data is available in the input queue,
    it is transferred to the calling program up to a maximum of 1 byte per
    read operation, and returned immediately to the program. Otherwise the
    driver blocks until data arrives, OR when VTIME tenths has expired
    from the read call. If the timer expires without data, zero is returned.
    Note that this is an overall timer, not an intercharacter one.

    The messages from Kaifa MA304H3E 3-phase meter are 41 bytes,
    123 bytes and 157 bytes respectively. There is an estimated 1.3s
    pause after the longest message, before start of the next message.
    VTIME determines when a message is complete.*/

    while (1) {
      // Do the reading
      rx_length = read(uart0_filestream, (void*)buf1, 1);

      if ((rx_length < 0) || (rx_length == 0)) {
        // No byte received on the last read, test if we have a message
        if (n_bytes > 0) {
          // Test if the message satisfies needed criteria
          if (validate_msg()) {
            // We have a proper message
            if (debugHex) {
              // Print message header and hex values
              cout << "Message length = " << n_bytes << endl;
              for (int i = 0; i < n_bytes; i++) {
                cout << hex << (int)buf[i] << " ";
                cout << dec;
              }
              cout << endl << endl;
            }

            // Call decoding of message
            decodeMessage();
            // Convert all values to strings and print
            printData();
            cout << endl;
          }
          // Reset the bytes counter
          n_bytes = 0;
        }
      } else {
        // One byte is received
        buf[n_bytes] = buf1[0];
        n_bytes++;
        /* buf[] should start with one char 126 and end with 126. The
        content part of the message is between these flags.*/
      }
    }
  }
}



// Check some key values to check that the buffer contains a proper message
bool validate_msg() {
  if (((int)buf[17] == 9) &&
     ((int)buf[0] == 126) &&
     ((int)buf[n_bytes - 1] == 126) &&
     ((int)((buf[1] & 7) << 8 | buf[2]) == (n_bytes - 2)))
  {
    return true;
  } else {
    return false;
  }
}



// Decode message from HEX telegram
int decodeMessage() {

  year0 = buf[19]<<8 | buf[20];
  month0 = buf[21];
  day0 = buf[22];
  hour0 = buf[24];
  min0 = buf[25];
  sec0 = buf[26];

  // Determine number of items in telegram
  int offset = 17 + 2 + buf[18];
  if (buf[offset]== 0x02) {
    num_items = buf[offset+1];
  }
  offset+=2;

  // List1 for 1 and 3 phase meters - 1 item
  if (num_items == 1) { /* Num Records: 1 */
    if (buf[offset]==0x06) { /* Item 1 */
      act_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
  }
  // List2 for 1 phase meter - 9 items
  else if (num_items==9) { /* Num records: 9 */
    unsigned int num_bytes=0;
    if (buf[offset]==0x09) { /* Item 1 */
      num_bytes = buf[offset+1];
      obis_list_version.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 2 */
      num_bytes = buf[offset+1];
      meterId.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 3 */
      num_bytes = buf[offset+1];
      meterModel.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 4 */
      act_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 5 */
      act_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 6 */
      react_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 7 */
      react_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 8 */
      curr_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 9 */
      volt_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
  }
  // List2 for 3 phase meter - 13 items
  else if (num_items==13) { /* Num records: 13 */
    unsigned int num_bytes = 0;
    if (buf[offset]==0x09) { /* Item 1 */
      num_bytes = buf[offset+1];
      obis_list_version.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 2 */
      num_bytes = buf[offset+1];
      meterId.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 3 */
      num_bytes = buf[offset+1];
      meterModel.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 4 */
      act_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 5 */
      act_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 6 */
      react_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 7 */
      react_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 8 */
      curr_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 9 */
      curr_L2 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 10 */
       curr_L3 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 11 */
      volt_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 12 */
      volt_L2 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 13 */
      volt_L3 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
  }
  // List3 for 1 phase meter - 14 items
  else if (num_items==14) { /* Num records: 14 */
    unsigned int num_bytes = 0;
    if (buf[offset]==0x09) { /* Item 1 */
      num_bytes = buf[offset+1];
      obis_list_version.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 2 */
      num_bytes = buf[offset+1];
      meterId.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 3 */
      num_bytes = buf[offset+1];
      meterModel.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 4 */
      act_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 5 */
      act_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 6 */
      react_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 7 */
      react_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 8 */
      curr_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 9 */
      volt_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x09) { /* Item 10 */
      num_bytes = buf[offset+1];
      year1 = buf[offset+2]<<8 | buf[offset+3];
      month1 = buf[offset+4];
      day1 = buf[offset+5];
      hour1 = buf[offset+7];
      min1 = buf[offset+8];
      sec1 = buf[offset+9];
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 11 */
      act_energy_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 12 */
      act_energy_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 13 */
      react_energy_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 14 */
      react_energy_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
  }
  // List3 for 3 phase meter - 18 items
  else if (num_items==18) { /* Num records: 18 */
    unsigned int num_bytes = 0;
    if (buf[offset]==0x09) { /* Item 1 */
      num_bytes = buf[offset+1];
      obis_list_version.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 2 */
      num_bytes = buf[offset+1];
      meterId.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x09) { /* Item 3 */
      num_bytes = buf[offset+1];
      meterModel.assign((const char *) buf + offset+2, num_bytes);
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 4 */
      act_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 5 */
      act_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 6 */
      react_pow_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 7 */
      react_pow_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 8 */
      curr_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 9 */
      curr_L2 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 10 */
      curr_L3 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 11 */
      volt_L1 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 12 */
      volt_L2 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 13 */
      volt_L3 = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x09) { /* Item 14 */
      num_bytes = buf[offset+1];
      year1 = buf[offset+2]<<8 | buf[offset+3];
      month1 = buf[offset+4];
      day1 = buf[offset+5];
      hour1 = buf[offset+7];
      min1 = buf[offset+8];
      sec1 = buf[offset+9];
    }
    offset+=2+num_bytes;
    if (buf[offset]==0x06) { /* Item 15 */
      act_energy_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 16 */
      act_energy_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 17 */
      react_energy_pos = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
    offset+=1+4;
    if (buf[offset]==0x06) { /* Item 18 */
      react_energy_neg = buf[offset+1]<<24 | buf[offset+2]<<16 | buf[offset+3]<<8 | buf[offset+4];
    }      
  } else {
    cout << "Unknown message\n";
  }
  return 1;
}



// Convert all values from decode function to strings
int printData() {

  // Format date and time fields
  // Insert leading zero(s) in date/time as needed
  string a = ""; if (buf[21] < 10) {a = "0";}
  string b = ""; if (buf[22] < 10) {b = "0";}
  string c = ""; if (buf[24] < 10) {c = "0";}
  string d = ""; if (buf[25] < 10) {d = "0";}
  string e = ""; if (buf[26] < 10) {e = "0";}
  
  msgDate = to_string(year0) + "-" + a + to_string(month0) + "-" + b
  + to_string(day0);
  msgTime = c + to_string(hour0) + ":" + d + to_string(min0) + ":" + e
  + to_string(sec0);

  // Check which list type that was last read and update web fields
  switch (num_items) {
    
  // List1 for 1 and 3 phase meters - 1 item
  case 1:
    listType = "List 1, 1&3-phase";
    actPowerPlus = to_string(act_pow_pos);
    break;
    
  // List2 for 1 phase meter - 9 items
  case 9:
    listType = "List 2, 1-phase";
    actPowerPlus = to_string(act_pow_pos);
    actPowerMinus = to_string(act_pow_neg);
    reactPowerPlus = to_string(react_pow_pos);
    reactPowerMinus = to_string(react_pow_neg);
    currentL1 = to_string(curr_L1);
    voltageL1 = to_string(volt_L1);
    break;
    
  // List2 for 3 phase meter - 13 items
  case 13:
    listType = "List 2, 3-phase";
    actPowerPlus = to_string(act_pow_pos);
    actPowerMinus = to_string(act_pow_neg);
    reactPowerPlus = to_string(react_pow_pos);
    reactPowerMinus = to_string(react_pow_neg);
    currentL1 = to_string(curr_L1);
    currentL2 = to_string(curr_L2);
    currentL3 = to_string(curr_L3);
    voltageL1 = to_string(volt_L1);
    voltageL2 = to_string(volt_L2);
    voltageL3 = to_string(volt_L3);
    break;
    
  // List3 for 1 phase meter - 14 items
  case 14:
    listType = "List 3, 1-phase";
    actPowerPlus = to_string(act_pow_pos);
    actPowerMinus = to_string(act_pow_neg);
    reactPowerPlus = to_string(react_pow_pos);
    reactPowerMinus = to_string(react_pow_neg);
    currentL1 = to_string(curr_L1);
    voltageL1 = to_string(volt_L1);
    activeEnergyPlus = to_string(act_energy_pos);
    activeEnergyMinus = to_string(act_energy_neg);
    reactiveEnergyPlus = to_string(react_energy_pos);
    reactiveEnergyMinus = to_string(react_energy_neg);
    break;
    
  // List3 for 3 phase meter - 18 items
  case 18:
    listType = "List 3, 3-phase";
    actPowerPlus = to_string(act_pow_pos);
    actPowerMinus = to_string(act_pow_neg);
    reactPowerPlus = to_string(react_pow_pos);
    reactPowerMinus = to_string(react_pow_neg);
    currentL1 = to_string(curr_L1);
    currentL2 = to_string(curr_L2);
    currentL3 = to_string(curr_L3);
    voltageL1 = to_string(volt_L1);
    voltageL2 = to_string(volt_L2);
    voltageL3 = to_string(volt_L3);
    activeEnergyPlus = to_string(act_energy_pos);
    activeEnergyMinus = to_string(act_energy_neg);
    reactiveEnergyPlus = to_string(react_energy_pos);
    reactiveEnergyMinus = to_string(react_energy_neg);
    break;
  }

  // Optional print values to terminal
  if (debugText) {
    cout << "msgDate: " << msgDate << " " << "msgTime: " << msgTime << endl;
    cout << "listType: " << listType << endl;
    cout << "obis_list_version: " << obis_list_version << endl;
    cout << "meterId: " << meterId << endl;
    cout << "meterModel: " << meterModel << endl;
    cout << "actPowerPlus: " << actPowerPlus << endl;
    cout << "actPowerMinus: " << actPowerMinus << endl;
    cout << "reactPowerPlus: " << reactPowerPlus << endl;
    cout << "reactPowerMinus: " << reactPowerMinus << endl;
    cout << "currentL1: " << currentL1 << endl;
    cout << "currentL2: " << currentL2 << endl;
    cout << "currentL3: " << currentL3 << endl;
    cout << "voltageL1: " << voltageL1 << endl;
    cout << "voltageL2: " << voltageL2 << endl;
    cout << "voltageL3: " << voltageL3 << endl;
    cout << "activeEnergyPlus: " << activeEnergyPlus << endl;
    cout << "activeEnergyMinus: " << activeEnergyMinus << endl;
    cout << "reactiveEnergyPlus: " << reactiveEnergyPlus << endl;
    cout << "reactiveEnergyMinus: " << reactiveEnergyMinus << endl;
  }

  // Write List2 and List3 to logfile: yyyy-mm-dd.txt
  if ((num_items == 9) || (num_items == 13) || (num_items == 14) || (num_items == 18)) {
    try {
      ofstream ofs1;
      string logData = "/var/meter_log/" + msgDate + ".txt";
      ofs1.open(logData, ofstream::out | ofstream::app);
      ofs1 << msgDate << "," << msgTime << "," << obis_list_version << "," << meterId << ","
           << meterModel << "," << actPowerPlus << "," << actPowerMinus << "," << reactPowerPlus << ","
           << reactPowerMinus << "," << currentL1 << "," << currentL2 << "," << currentL3 << ","
           << voltageL1 << "," << voltageL2 << "," << voltageL3 << "," << activeEnergyPlus << ","
           << activeEnergyMinus << "," << reactiveEnergyPlus << "," << reactiveEnergyMinus << "\n";
      ofs1.close();
    } catch(...) {
      cout << "Something went wrong on open/write/close file msgDate.txt\n";
    }
  }

  // Write current active power value from every message to file: currentactivepower.data
  try {
    ofstream ofs2;
    ofs2.open("/var/www/html/data/currentactivepower.data", ofstream::out | ofstream::trunc);
    ofs2 << actPowerPlus;
    ofs2.close();
  } catch(...) {
    cout << "Something went wrong on open/write/close file currentactivepower.data\n";
  }

  // Write current time from every message to file: currenttime.data
  try {
    ofstream ofs3;
    ofs3.open("/var/www/html/data/currenttime.data", ofstream::out | ofstream::trunc);
    ofs3 << msgTime;
    ofs3.close();
  } catch(...) {
    cout << "Something went wrong on open/write/close file currenttime.data\n";
  }

  // Write newest version of List2 or List3 to file: currentlog.data
  if ((num_items == 9) || (num_items == 13) || (num_items == 14) || (num_items == 18)) {
    try {
      ofstream ofs4;
      ofs4.open("/var/www/html/data/currentlog.data", ofstream::out | ofstream::trunc);
      ofs4 << msgDate << "," << msgTime << "," << obis_list_version << "," << meterId << ","
           << meterModel << "," << actPowerPlus << "," << actPowerMinus << "," << reactPowerPlus << ","
           << reactPowerMinus << "," << currentL1 << "," << currentL2 << "," << currentL3 << ","
           << voltageL1 << "," << voltageL2 << "," << voltageL3 << "," << activeEnergyPlus << ","
           << activeEnergyMinus << "," << reactiveEnergyPlus << "," << reactiveEnergyMinus << "\n";
      ofs4.close();
    } catch(...) {
      cout << "Something went wrong on open/write/close file currentlog.data\n";
    }
  }
  return 1;
}
