import board
import neopixel
import time

# Neopixel setup (pin 4, number of leds)
pixels = neopixel.NeoPixel(board.D4, 8)

# Turn off all the leds
def leds_off():
    pixels.fill((0, 0, 0))

# Blink frequency and timer
BLINK = .1
t1 = time.monotonic()

# Needed variables
shift_changed = 10

def action(rpm, STEP, END, br):
    global shift_changed
    global t1
    # If shift light is needed
    if rpm > END - STEP * 5:
        shift = (END - rpm) // STEP + 1
        # Blinker
        if rpm > END + STEP:
            if t1 + BLINK < time.monotonic():
                pixels.fill((0, br, br))
            if t1 + BLINK * 2 < time.monotonic():
                pixels.fill((0, 0, 0))
                t1 = time.monotonic()
            # print("Blinker on")
        # Check if status has changed
        elif shift_changed != shift:
            # LED steps control
            print("Shift:", shift)
            print("Shift_changed:", shift_changed)
            if shift <= 3:
                pixels[0] = (0, br, 0)
                pixels[7] = (0, br, 0)
                if shift <= 2:
                    pixels[1] = (0, br, 0)
                    pixels[6] = (0, br, 0)
                    if shift <= 1:
                        pixels[2] = (br, br, 0)
                        pixels[5] = (br, br, 0)
                        if shift <= 0:
                            pixels[3] = (0, br, br)
                            pixels[4] = (0, br, br)
            # If rpm goes down
            if shift > shift_changed:
                # if shift_changed >= 0 and shift_changed < 4:
                print("Rpm goes down")
                if shift == 0:
                    pixels[3] = ((0, 0, 0))
                    pixels[4] = ((0, 0, 0))
                elif shift == 1:
                    pixels[2] = ((0, 0, 0))
                    pixels[5] = ((0, 0, 0))
                elif shift == 2:
                    pixels[1] = ((0, 0, 0))
                    pixels[6] = ((0, 0, 0))
                elif shift == 3:
                    pixels[0] = ((0, 0, 0))
                    pixels[7] = ((0, 0, 0))
        # Save the new state
        shift_changed = shift
