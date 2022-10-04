# Version 2
# Dimmer improved by slower reaction to ambient light change. 

import board
import busio
import time
import digitalio
import canio
import struct
import adafruit_ds3231
import analogio
import shift_light

# RTC communication
myI2C = board.I2C()
rtc = adafruit_ds3231.DS3231(myI2C)

if False:   # change to True if you want to write the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = time.struct_time((2021,  3,   16,   10,  30,  00,    0,   -1,    -1))
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but
    # we don't do anything with it at this time

    print('Setting time to:', t)     # uncomment for debugging
    rtc.datetime = t
    print()

# UART settings
# uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=1)
uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=1)

# Message sending to Nextion
def message_send(message):
    ending = 0xFF, 0xFF, 0xFF
    uart.write(message.encode('ascii'))
    uart.write(bytes(ending))

# Nextion baudrate change
if False:
    # To make sure Nextion is ready
    time.sleep(1)
    message_send('bauds=115200')

# Error flags
ERRORFLAGS = ("", "OILP", "EWG", "DSG", "DIFFCTRL", "FPR", "DBW", "FF_SENSOR",
              "KNOCKING", "EGT_ALARM", "EGT2", "EGT1", "WBO", "MAP", "IAT", "CLT")
def error_flags(number):
    # Convert to bit list
    bit_list = [x - ord("0") for x in b"{:016b}".format(number)]
    # To boolean
    boolean = list(map(bool, bit_list))
    # Get the errors that are on
    errors_on = []
    for x in range(len(boolean)):
        if boolean[x] is True:
            errors_on.append(ERRORFLAGS[x])
    print(errors_on)
    # Send error count
    data_s = 'er_c.val=' + str(len(errors_on))
    message_send(data_s)
    # Send error codes
    if len(errors_on) == 1:
        message_send('er_1.txt=' + '"' + errors_on[0] + '"')
    elif len(errors_on) > 1:
        message_send('er_1.txt=' + '"' + errors_on[0] + '"')
        message_send('er_2.txt=' + '"' + errors_on[1] + '"')

# Light sensor
ADC = analogio.AnalogIn(board.A0)
def is_dark():
    a_val = ADC.value
    # print(a_val)
    if a_val > 35000:
        return True
    else:
        return False

# dimmer
def dimmer(value):
    global led_br
    # Dark
    if value is True:
        message_send('dim=50')
        led_br = 20
        # print("dim=50")
    # Bright
    else:
        message_send('dim=100')
        led_br = 80
        # print("dim=100")

# Run at startup
dimmer(is_dark())

# CAN BUS
# The CAN transceiver has a standby pin, bring it out of standby mode
if hasattr(board, 'CAN_STANDBY'):
    standby = digitalio.DigitalInOut(board.CAN_STANDBY)
    standby.switch_to_output(False)

# The CAN transceiver is powered by a boost converter, turn on its supply
# if hasattr(board, 'BOOST_ENABLE'):
#    boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
#    boost_enable.switch_to_output(True)

# Can Bus pins
can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=500_000, auto_restart=True)

# CAN listener 0x600 - 0x607
listener = can.listen(matches=[canio.Match(0x600, mask=0x608)], timeout=.9)

# Shift light
# SETUP
END = 8600
STEP = 100

# Make sure the leds are off
shift_light.leds_off()

# Needed variables
old_clock = None
timer_needed = False
old_bus_state = None
shift_light_off = False
rpm = 0
old_errors = 0
old_dark = is_dark()
t1 = time.monotonic()
dim_counter = 0
# counter = 0

while True:
    # Debug
    # counter += 1
    # if counter > 1000:
    #    break
    # rpm -= 1
    # print(rpm)

    # Uart message receiving
    receiving_data = False
    buffer = uart.in_waiting
    if buffer != 0:
        data_r = uart.read(1)
        receiving_data = True
        received = []
        received.append(data_r)

    while receiving_data is True:
        data_r = uart.read(1)
        # print("Receiving")
        if data_r == b'\xff':
            data_r = uart.read(1)
            if data_r == b'\xff':
                data_r = uart.read(1)
                if data_r == b'\xff':
                    # Message ended
                    receiving_data = False
                    if received == [b'\x00', b'\x00', b'\x00']:
                        print("Nextion Startup")
                    elif received == [b'\x88']:
                        print("Nextion Ready")
                    elif received == [b'\x1a']:
                        print("Invalid variable")
                    else:
                        print('Message: ', received)
        else:
            received.append(data_r)
    # Clock
    t = rtc.datetime
    clock = "%02d:%02d" % (t.tm_hour, t.tm_min)
    # clock = '%02d:%02d' % (5, 23)   # debugging
    if clock != old_clock:
        data_s = 'cl.txt="'+clock+'"'
        message_send(data_s)
        old_clock = clock

    # Dimmer
    dark = is_dark()

    if dark is not old_dark and time.monotonic() > t1:
        dim_counter += 1
        t1 = time.monotonic() + 0.5
    elif dark is old_dark:
        dim_counter = 0

    if dim_counter > 6:
        dimmer(dark)
        old_dark = dark

    # CAN BUS
    # Bus state information
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state
    message = listener.receive()

    # Message handling
    if message is None:
        print("No message received within timeout")
        # time.sleep(1)
        continue

    data = message.data
    if len(data) != 8:
        print(f"Unusual message length {len(data)}")
        # time.sleep(1)
        continue

    id = message.id

    # Printing received messages
    # print("Received a message with id:", (hex(id)))

    if id == 0x600:
        # Unpack message
        message = struct.unpack("<HBbHH", data)
        rpm = message[0]
    elif id == 0x602:
        message = struct.unpack("<HBBBBh", data)
        # Oil temperature
        oil_t = message[2]
        # Build the message
        data_s = 'ot.val='+str(oil_t)
        # Send it to Nextion
        message_send(data_s)
        # Oil pressure
        oil_p = int(message[3] * 0.625)
        data_s = 'op.val='+str(oil_p)
        message_send(data_s)
        # Fuel pressure
        fuel_p = int(message[4] * 0.625)
        data_s = 'fp.val='+str(fuel_p)
        message_send(data_s)
    elif id == 0x603:
        message = struct.unpack("<bBBBHH", data)
        # Lambda
        lambda_value = int(message[2] * 0.78125)
        data_s = 'la.val='+str(lambda_value)
        message_send(data_s)
    elif id == 0x604:
        message = struct.unpack("<BbHHBB", data)
        # Battery voltage
        battery_v = int(message[2] * 0.27)
        data_s = 'ba.val='+str(battery_v)
        message_send(data_s)
        # Error flags
        errors = message[3]
        if errors != old_errors:
            # No errors any more
            if errors == 0:
                message_send('er_c.val=0')
            # Error found
            else:
                error_flags(errors)
            old_errors = errors

    # Shift light
    if rpm > END - STEP * 5:
        shift_light.action(rpm, STEP, END, led_br)
        shift_light_off = False
        # Make sure all leds are off
    elif rpm < END - STEP * 5 and shift_light_off is False:
        shift_light.leds_off()
        shift_light_off = True
