# -------------------------------
# ------- BLE Scan Logger -------
# ---- Michael Lacock, 2022 -----
# -------------------------------

#-- Hardware used: "Adafruit Glasses Driver Board (Product 5217)" and
#--        "Adafruit PCF8523 Real Time Clock (Product 5189 or 3295)".

import busio
import adafruit_pcf8523
import time
from adafruit_datetime import datetime, date
import math
from math import ceil, floor
import board
import storage
import microcontroller
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from rainbowio import colorwheel
from adafruit_ble import BLERadio

Node_ID = 1 # Change for each node.

debug = 0 #-- Debug mode dose not log, but instead prints out the data.
manual_scan = 0 #-- When enabled, it only scans/logs when the on-board button is pressed.
                #--                 This mode has priority over other modes when enabled.

interval_mode = 1 #-- Only scans after a specified amount of time.
interval_length = 5 #-- Length in minutes.

boardI2C = busio.I2C(board.SCL, board.SDA)
rtc = adafruit_pcf8523.PCF8523(boardI2C)

radio = BLERadio()

button = DigitalInOut(board.SWITCH)
button.direction = Direction.INPUT
button.pull = Pull.UP

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.3, auto_write=False)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(1):
            rc_index = (i * 256 // 1) + j
            pixel[i] = colorwheel(rc_index & 255)
        pixel.show()
        time.sleep(wait)

clear = (0, 0, 0)

if (debug == 0):
    storage.remount("/") #-- NRF52840 can't be plugged into USB for this to work. Disable debug and unplug USB for it to work.

    try:
        with open("/local/log.txt", "a") as log:
            log.write("Node_ID Scans DateTime Address Name TX_power RSSI\n")
            time.sleep(1)
        with open("/local_backup/backup_log.txt", "a") as log:
            log.write("Node_ID Scans DateTime Address Name TX_power RSSI\n")
            time.sleep(1)
    except OSError as e: #-- For NRF52840, it isn't writable when plugged into USB.
        print("Filesystem isn't writable.")

for i in range(2):
    rainbow_cycle(0)

scan_now = 0
scan_ammount = 1

t = rtc.datetime
current_min = t.tm_min
next_min = current_min

while True:
    pixel.fill(clear)
    pixel.show()

    if (manual_scan == 1):
        if not button.value:
            scan_now = 1
            for i in range(2):
                rainbow_cycle(0)
            pixel.fill(clear)
            pixel.show()
        else:
            scan_now = 0
    else:
        if (interval_mode == 1):
            t = rtc.datetime
            current_min = t.tm_min

            if (current_min == next_min):
                scan_now = 1

                next_min = (interval_length * ceil(current_min / interval_length))
                if (current_min >= next_min):
                    next_min = (next_min + interval_length)
                if (next_min > 59):
                    next_min = (next_min - 59)
            else:
                scan_now = 0
                time.sleep(15)

        else:
            scan_now = 1

    if (scan_now == 1):
        try:
            found = set()
            for entry in radio.start_scan(timeout=60, minimum_rssi=-99):
                addr = entry.address
                strength = entry.rssi

                if addr not in found:
                    t = rtc.datetime
                    dt = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                    dt = (str(dt)).replace(" ", "T")

                    export_addr = (str(addr)).replace("<Address ", "")
                    export_addr = export_addr.replace(">", "")

                    if ("complete_name=" in str(entry)):
                        export_name = (str(entry)).split("complete_name=")
                        export_name = (export_name[1]).split(" ")
                        export_name = str(export_name[0])
                    else:
                        export_name = "null"

                    if ("tx_power=" in str(entry)):
                        export_txpower = (str(entry)).split("tx_power=")
                        export_txpower = (export_txpower[1]).split(" ")
                        export_txpower = str(export_txpower[0])
                    else:
                        export_txpower = "null"

                    if (debug == 1):
                        print("-----------------------------------")
                        print("[-] Node_ID:  ", Node_ID)
                        print("[-] Total_scans: ", scan_ammount)
                        print("[-] DateTime: ", dt)
                        print("[-] Address:  ", export_addr)
                        print("[-] Name:     ", export_name)
                        print("[-] TX_power: ", export_txpower)
                        print("[-] RSSI:     ", strength)

                    else:
                        try:
                            with open("/local/log.txt", "a") as log:
                                log.write("{} {} {} {} {} {} {}\n".format(
                                    str(Node_ID), str(scan_ammount), str(dt), export_addr, export_name, export_txpower, str(strength)))
                                time.sleep(1)
                            with open("/local_backup/backup_log.txt", "a") as log:
                                log.write("{} {} {} {} {} {} {}\n".format(
                                    str(Node_ID), str(scan_ammount), str(dt), export_addr, export_name, export_txpower, str(strength)))
                                time.sleep(1)
                        except OSError as e: #-- For NRF52840, it isn't writable when plugged into USB.
                            print("Filesystem isn't writable.")

                    #scan_ammount = (scan_ammount + 1)

                found.add(addr)

            scan_ammount = (scan_ammount + 1)

            for i in range(5):
                rainbow_cycle(0)

        except OSError:
            pass
        except RuntimeError:
            pass
