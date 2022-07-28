# Emu_Black_DIY_screen_35
Microcontroller reading sensor values and sending them to LCD screen. Also equipped with shift light and light sensor to control screen and shift light brightness. 

### Parts used (total about 130€):
- Adafruit Feather M4 CAN Express with ATSAME51
- Adafruit DS3231 Precision RTC Breakout (blue one)
- NeoPixel Stick - 8 x 5050 RGB LED
- MPM3610 5V 1.2A Buck Converter Breakout
- Nextion Discovery 3.5" (NX4832F035)
- CR1220 battery
- pcb own desing (from JLCPCB)
- JST-SM 4pin connector pair
- JST-XH female connector
- 2A fast diode
- tantalum capacitor 0,47µF 35V
- 1kohm 0,6W resistor
- photoresistor 200R - 500K
- side actuated tactile switch (TE 1-1825027-1)
- 1row 90 degree pin header 2,54mm
- 2 pin DuPont style housing
- 3 pin DuPont style housing
- 0,22mm2 stranded wire (24 AWG)
- 4x M3x5 button head screws
- 4x M3x10 countersunk screws
- 2x M3x8 countersunk screws
- magnetic car phone holder
- micro SD-card for uploading file to Nextion
- case printed from PETG with Creality Ender 3 V2
- 
### Putting it to together:
One modification is needed for the Feather: Remove resistor next to the EN-pin (R8 on schematic). This disables the battery charger chip and then you can use the BAT-pin for 5v input. With this modification done you can connect it to computer with auxiliar power supply without worries. 
I had to drill bigger mounting holes to the Nextion to rotate the screen slightly, because screen wasn't installed straight to the pcb. Hot glue is used to the photoresistor. 

### Setup
Check Adafruit guide for setting up the Feather. Upload HMI file to sd card and Nextion will upload it when powered, then remove sd card. 
You also need to change the  baudrate to 115200 with code.py. Shift light setup guide is in the code.py. 

### Video of the shift light action
https://youtu.be/XviCfcwE8Wc

### Pictures
![image1](/pictures/IMG_20220728_215339.jpg)
Pcb on this picture is earlier prototype. Feather had a faulty voltage booster so I had to delete it. 
![image1](/pictures/IMG_20220727_231424.jpg)
![image1](/pictures/IMG_20220727_231604.jpg)
![image1](/pictures/IMG_20220727_234645.jpg)
![image1](/pictures/IMG_20220727_234736.jpg)
