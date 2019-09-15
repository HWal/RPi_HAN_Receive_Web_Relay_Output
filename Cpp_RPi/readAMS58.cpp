//**************************************************************************
// READ MESSAGES FROM HAN PORT ON KAIFA MA304H3E 3-PHASE ELECTRICITY METER.
// THIS PROGRAM ALSO HANDLES MESSAGES FROM 1-PHASE METER OF THE SAME TYPE.
// WRITE DATA FROM ALL MESSAGES (LISTS 1, 2, 3) TO WEBPAGE: amsdata.html
// WRITE LIST2 AND LIST3 TO LOGFILE: yyyy-mm-dd.txt
// WRITE ACTIVE POWER FROM ALL MESSAGES TO FILE: currentactivepower.data
//**************************************************************************

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
unsigned char buf[255];              // Buffer array to receive message
int rx_length = 0;                   // Length of the last read char buffer

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
  options.c_cc[VTIME] = 3;  /* read returns after an interval of
                               3*0.1s between two characters */
  options.c_cc[VMIN] = 255; // read returns after 255 chars
  tcflush(uart0_filestream, TCIFLUSH);
  tcsetattr(uart0_filestream, TCSANOW, &options);

  // Call never ending read function
  receive_bytes();

  // CLOSE THE UART - the program never gets here
  cout << "Closing uart...\n";
  close(uart0_filestream);
  cout << "uart closed\n";

  return 0;
}



void receive_bytes() {
  while(1) {
    if (uart0_filestream != -1) {
      /* read returns if 255 characters are read from the port (never
         happens in this program).
         read returns if there is a > 3*0.1s interval between two characters.
         The messages from Kaifa MA304H3E 3-phase meter are 41 bytes,
         123 bytes and 157 bytes respectively. There is an estimated 1.3s
         pause after the longest message, before start of the next message.
         This means that VMIN never kicks in, but VTIME determines when a
         message is complete. */
      rx_length = read(uart0_filestream, (void*)buf, 255);
      if ((rx_length < 0) || (rx_length == 0)) {
        // No byte received
      } else {
        /* Bytes are received.
           The buf array starts with one char 126 and ends with one char 126.
           The content part of the message is between these flags. */

        if (validate_msg()) {
          if (debugHex) {
            // Print message header and hex values
            cout << "Message length = " << rx_length << endl;
            for (int i = 0; i < rx_length; i++) {
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
      }
    }
  }
}



// Check some key values to check that the buffer contains a proper message
bool validate_msg() {
  if (((int)buf[17] == 9) &&
     ((int)buf[0] == 126) &&
     ((int)buf[rx_length - 1] == 126) &&
     ((int)((buf[1] & 7) << 8 | buf[2]) == (rx_length - 2)))
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

  // Write all messages to webpage: amsdata.html
  string page = "";
  // Header
  page += "<!DOCTYPE html>";
  page += "<html lang=en-EN>";
  page += "<head>";
  page += "<meta name=\"viewport\" content =\"width=device-width, initial-scale=1.0, maximum-scale=4.0, minimum-scale=.5, user-scalable=1\">";
  page += "<meta http-equiv=\"refresh\" content=\"2\">";
  page += "<title>Web page</title>";
  page += "<style> body { background-color: #fffff; font-family: Arial, Helvetica, Sans-Serif; Color: #000088; }</style>";
  page += "</head>";
  page += "<body>";
  page += "<center>";
  page += "<center><H2>Messages from Kaifa AMS meter</center></H2></center>";
  page += "<table align=\"center\" border=\"1\" width=\"350\" cellpadding=\"2\">";
  // Data
  page += "<tr><td><b>LAST READ LIST TYPE</b></td><td align=\"right\"><b><font color=\"red\">";
  page += listType;
  page += "</font></b></td></tr>";
  page += "<tr><td><b>DATE</b></td><td align=\"right\">";
  page += msgDate;
  page += "</td></tr>";
  page += "<tr><td><b>TIME</b></td><td align=\"right\">";
  page += msgTime;
  page += "</td></tr>";
  page += "<tr><td><b>LIST VERSION</b></td><td align=\"right\">";
  page += obis_list_version;
  page += "</td></tr>";
  page += "<tr><td><b>METER ID</b></td><td align=\"right\">";
  page += meterId;
  page += "</td></tr>";
  page += "<tr><td><b>METER MODEL</b></td><td align=\"right\">";
  page += meterModel;
  page += "</td></tr>";
  page += "<tr><td><b>ACT POWER+ (W)</b></td><td align=\"right\">";
  page += actPowerPlus;
  page += "</td></tr>";
  page += "<tr><td><b>ACT POWER- (W)</b></td><td align=\"right\">";
  page += actPowerMinus;
  page += "</td></tr>";
  page += "<tr><td><b>REA POWER+ (VAR)</b></td><td align=\"right\">";
  page += reactPowerPlus;
  page += "</td></tr>";
  page += "<tr><td><b>REA POWER- (VAR)</b></td><td align=\"right\">";
  page += reactPowerMinus;
  page += "</td></tr>";
  page += "<tr><td><b>CURR L1 (A * 1000)</b></td><td align=\"right\">";
  page += currentL1;
  page += "</td></tr>";
  page += "<tr><td><b>CURR L2 (A * 1000)</b></td><td align=\"right\">";
  page += currentL2;
  page += "</td></tr>";
  page += "<tr><td><b>CURR L3 (A * 1000)</b></td><td align=\"right\">";
  page += currentL3;
  page += "</td></tr>";
  page += "<tr><td><b>VOLT L1 (V * 10)</b></td><td align=\"right\">";
  page += voltageL1;
  page += "</td></tr>";
  page += "<tr><td><b>VOLT L2 (V * 10)</b></td><td align=\"right\">";
  page += voltageL2;
  page += "</td></tr>";
  page += "<tr><td><b>VOLT L3 (V * 10)</b></td><td align=\"right\">";
  page += voltageL3;
  page += "</td></tr>";
  page += "<tr><td><b>ACT ENERGY+ (Wh)</b></td><td align=\"right\">";
  page += activeEnergyPlus;
  page += "</td></tr>";
  page += "<tr><td><b>ACT ENERGY- (Wh)</b></td><td align=\"right\">";
  page += activeEnergyMinus;
  page += "</td></tr>";
  page += "<tr><td><b>REA ENERGY+ (VARh)</b></td><td align=\"right\">";
  page += reactiveEnergyPlus;
  page += "</td></tr>";
  page += "<tr><td><b>REA ENERGY- (VARh)</b></td><td align=\"right\">";
  page += reactiveEnergyMinus;
  page += "</td></tr>";
  // End of data
  page += "</table>";
  page += "<br>";
  page += "<b><center><a href=\"index.html\">Back</a></center></b>";
  page += "</body>";
  page += "</html>";
  // End of page
  try {
    ofstream ofs1;
    ofs1.open("/var/www/kaifaweb/amsdata.html", ofstream::out | ofstream::trunc);
    ofs1 << page;
    ofs1.close();
  } catch(...) {
    cout << "Something went wrong on open/write/close file amsdata.html\n";
  }

  // Write List2 and List3 to logfile: yyyy-mm-dd.txt
  if ((num_items == 9) || (num_items == 13) || (num_items == 14) || (num_items == 18)) {
    try {
      ofstream ofs2;
      string logData = "/var/kaifalog/" + msgDate + ".txt";
      ofs2.open(logData, ofstream::out | ofstream::app);
      ofs2 << msgDate << "," << msgTime << "," << obis_list_version << "," << meterId << ","
           << meterModel << "," << actPowerPlus << "," << actPowerMinus << "," << reactPowerPlus << ","
           << reactPowerMinus << "," << currentL1 << "," << currentL2 << "," << currentL3 << ","
           << voltageL1 << "," << voltageL2 << "," << voltageL3 << "," << activeEnergyPlus << ","
           << activeEnergyMinus << "," << reactiveEnergyPlus << "," << reactiveEnergyMinus << "\n";
      ofs2.close();
    } catch(...) {
      cout << "Something went wrong on open/write/close file msgDate.txt\n";
    }
  }

  // Write current active power value from every message to file: currentactivepower.data
  try {
    ofstream ofs3;
    ofs3.open("/var/www/kaifaweb/data/currentactivepower.data", ofstream::out | ofstream::trunc);
    ofs3 << actPowerPlus;
    ofs3.close();
  } catch(...) {
    cout << "Something went wrong on open/write/close file currentactivepower.data\n";
  }
  return 1;
}
