# -------------------------------------
# ---------- Project BLE-SPY ----------
# -------- Michael Lacock, 2022 -------
# -------------------------------------

import pygame
import random
import sqlite3
import os
import time
from datetime import datetime,date,timedelta
import random

resolution = (900, 600)

def Print_header():
    print ("-----------------------------------------")
    print ("------------ Project BLE-SPY ------------")
    print ("---------- Michael Lacock, 2022 ---------")
    print ("-----------------------------------------")
    print (" ")
    return()

def Clear_screen():
    if (os.name == 'nt'):
        os.system('cls')
    else:
        os.system('clear')
    return()

Min_color_value = 50

Append_mode = 0
Process_mode = 0
Visualization_mode = 0

db_dir = ("BLE-SPY.db")

while True:
    Clear_screen()
    Print_header()
    print ('Pick an option: ')
    print ("1 - Append data to database file.")
    print ("2 - Process data-set.")
    print ("3 - View visualization of data-set.")
    print ("4 - All of the above.")
    print (" ")
    option = input('')
    Clear_screen()
    if (option == "1"):
        Append_mode = 1

    if (option == "2"):
        Process_mode = 1

    if (option == "3"):
        Visualization_mode = 1

    if (option == "4"):
        Append_mode = 1
        Process_mode = 1
        Visualization_mode = 1

    if (Append_mode == 1):
        Clear_screen()
        Print_header()
        print ('Enter filename of log file: ')
        filename = input('')

        Clear_screen()
        Print_header()

        try:
            log_file = open(filename, "r+") # File in same directory.
            print ('[-] Entering data... Please wait.')
        except:
            print ('[x] Error, could not open log file.')
            break

        try:
            connect_DB = sqlite3.connect(db_dir, timeout=10)
            DB = connect_DB.cursor ()
        except:
            Clear_screen()
            Print_header()
            print ('[x] Error, failed to open database file.')
            break

        Log_lines = log_file.readlines()
        for line in Log_lines:
            if not ("Node_ID Scans DateTime Address Name TX_power RSSI" in line):
                split_line = line.split(" ")
                Node_ID = int(split_line[0])
                Scans = int(split_line[1])
                DateTime = str(split_line[2])
                Address = str(split_line[3])
                Name = str(split_line[4])
                TX_power = str(split_line[5])
                RSSI = int(split_line[6])

                DB.execute('INSERT INTO data (Node_ID, Scans, DateTime, Address, Name, TX_power, RSSI) VALUES (?, ?, ?, ?, ?, ?, ?)', (Node_ID, Scans, DateTime, Address, Name, TX_power, RSSI))
                connect_DB.commit()

        connect_DB.close()

        Clear_screen()
        Print_header()
        print ('[-] Data inserted.')
        time.sleep(4)


    if (Process_mode == 1):
        Clear_screen()
        Print_header()

        try:
            connect_DB = sqlite3.connect(db_dir, timeout=10)
            DB = connect_DB.cursor ()
            print ('[-] Processing data-set... Please wait.')
        except:
            Clear_screen()
            Print_header()
            print ('[x] Error, failed to open database file.')
            break

        DB.execute('SELECT Address FROM data')
        data_Addresses = DB.fetchall()

        for Current_adress in data_Addresses:
            Current_adress = str(Current_adress)
            Current_adress = Current_adress.replace("('", "")
            Current_adress = Current_adress.replace("',)", "")
            #print (Current_adress)

            DB.execute('SELECT Address FROM interpret')
            interpret_Addresses = DB.fetchall()
            clean_interpret_Addresses = []
            for current_interpret_Addresses in interpret_Addresses:
                current_interpret_Addresses = str(current_interpret_Addresses)
                current_interpret_Addresses = current_interpret_Addresses.replace("('", "")
                current_interpret_Addresses = current_interpret_Addresses.replace("',)", "")
                clean_interpret_Addresses.append(current_interpret_Addresses)

            if not Current_adress in clean_interpret_Addresses:
                color_loop = 1
                while (color_loop == 1):
                    r = random.randint(Min_color_value, 255)
                    g = random.randint(Min_color_value, 255)
                    b = random.randint(Min_color_value, 255)
                    color = str((r, g, b))
                    color = color.replace(")", "")
                    color = color.replace("(", "")
                    color = color.replace("'", "")

                    DB.execute('SELECT Color_ID FROM interpret')
                    interpret_Color_ID = DB.fetchall()

                    if not color in interpret_Color_ID:
                        color_loop = 0

                DB.execute('SELECT Name FROM data WHERE Address = ?', [Current_adress])
                all_names = DB.fetchall()
                final_name = "null"
                for name in all_names:
                    name = str(name)
                    name = name.replace("('", "")
                    name = name.replace("',)", "")
                    if not (name == "null"):
                        final_name = name

                DB.execute('SELECT Number_ID FROM interpret')
                total_Number_ID = DB.fetchall()
                entry_ammout = len(total_Number_ID)
                Number_ID = (entry_ammout + 1)

                DB.execute('SELECT DateTime FROM data WHERE Address = ?', [Current_adress])
                all_DateTime = DB.fetchall()

                DB.execute('SELECT Node_ID FROM data WHERE Address = ?', [Current_adress])
                all_Nodes = DB.fetchall()

                Placement = ""
                for i in range(len(all_DateTime)):
                    Number_ID_str = str(Number_ID)
                    current_Node = str(all_Nodes[(i - 1)])
                    current_Node = current_Node.replace("(", "")
                    current_Node = current_Node.replace(",)", "")
                    current_DateTime = str(all_DateTime[(i - 1)])
                    current_DateTime = current_DateTime.replace("('", "")
                    current_DateTime = current_DateTime.replace("',)", "")
                    if (i == 0):
                        combine_str = str(Number_ID_str + "_" + current_Node + "_" + current_DateTime)
                    else:
                        combine_str = str(", " + Number_ID_str + "_" + current_Node + "_" + current_DateTime)

                    Placement = (Placement + combine_str)

                DB.execute('INSERT INTO interpret (Address, Name, Number_ID, Color_ID, Placement) VALUES (?, ?, ?, ?, ?)', (str(Current_adress), str(final_name), Number_ID, str(color), str(Placement)))
                connect_DB.commit()

        connect_DB.close()

        Clear_screen()
        Print_header()
        print ('[-] Data processed.')
        time.sleep(4)

    if (Visualization_mode == 1):
        Clear_screen()
        Print_header()

        try:
            connect_DB = sqlite3.connect(db_dir, timeout=10)
            DB = connect_DB.cursor ()
        except:
            Clear_screen()
            Print_header()
            print ('[x] Error, failed to open database file.')
            break

        try:
            pygame.init()
            screen = pygame.display.set_mode(resolution)
            pygame.display.set_caption('Project BLE-SPY')
            screen.fill((0,0,0))
            print ('[-] Starting data visualization.')
        except:
            Clear_screen()
            Print_header()
            print ('[x] Error, failed to load PyGame.')
            break

        pygame.init()
        screen = pygame.display.set_mode(resolution)
        pygame.display.set_caption('Project BLE-SPY')

        DB.execute('SELECT Placement FROM interpret')
        all_Placement = DB.fetchall()

        Placement_list = []
        for i in range(len(all_Placement)):
            current_Placement = str(all_Placement[(i - 1)])
            current_Placement = current_Placement.replace("('", "")
            current_Placement = current_Placement.replace("',)", "")
            current_Placement = current_Placement.split(", ")
            for i in range(len(current_Placement)):
                current_Placement_data = str(current_Placement[(i - 1)])
                current_Placement_data = current_Placement_data.replace("('", "")
                current_Placement_data = current_Placement_data.replace("',)", "")
                current_Placement_data = current_Placement_data.replace('"', '')
                Placement_list.append(current_Placement_data)

        Placement_list.sort(key=lambda x: x[-19:])

        for i in range(len(Placement_list)):
            items = Placement_list[(i - 1)]
            items = items.split("_")
            Number_ID = items[0]
            current_Node = items[1]
            current_DateTime = items[2]

            DB.execute('SELECT Color_ID FROM interpret WHERE Number_ID = ?', [int(Number_ID)])
            Color = DB.fetchone()
            Color = str(Color)
            Color = Color.replace("('", "")
            Color = Color.replace("',)", "")
            Color = Color.split(", ")
            r = int(Color[0])
            g = int(Color[1])
            b = int(Color[2])

            screen.fill((0,0,0))
            font = pygame.font.Font('/Users/michaellacock/Library/Fonts/ufohunterai.ttf', 50) #Directory path for MacOS.
            text = font.render(current_DateTime, True, (255,255,255), (30,30,30))
            textRect = text.get_rect()
            textRect.center = (450, 400)
            screen.blit(text, textRect)

            pygame.draw.circle(screen, (r,g,b), ((random.randint(30, (resolution[0] - 30))), (random.randint(30, (resolution[1] - 30)))), 10)
            pygame.display.update()

            print (Number_ID + " - " + current_Node)

            time.sleep(0.001)

        screen.fill((0,0,0))
        font = pygame.font.Font('/Users/michaellacock/Library/Fonts/ufohunterai.ttf', 50) #Directory path for MacOS.
        text = font.render("DONE.", True, (255,255,255), (30,30,30))
        textRect = text.get_rect()
        textRect.center = (450, 400)
        screen.blit(text, textRect)
        pygame.display.update()

    Append_mode = 0
    Process_mode = 0
    Visualization_mode = 0
