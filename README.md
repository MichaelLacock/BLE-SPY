# BLE-SPY

The primary goal for this project was to create both hardware nodes and software that would scan/log available Bluetooth devices in a public environment; this is with the intent to create a data visualization and spread awareness that something as simple as the Bluetooth radio on our devices can be used to track us.

The computer-side application software I made using python.  Step one appends line by line the data that was logged to the text file from the Circuit Python hardware.  This data is organized into a SQLite local database.  Step two processes the data and prepares it for the next step.  Step three is the direct data visualization using PyGame.

![Alt Text](https://raw.githubusercontent.com/MichaelLacock/BLE-SPY/main/examples/application_step1.gif)

Regarding the visualization of the data, in this example a color is assigned to each Bluetooth Mac-Address.  Each color takes form as a dot randomly places in sequence from the recorded timestamp in the log.

Data Visualization Example Output:
![Alt Text](https://raw.githubusercontent.com/MichaelLacock/BLE-SPY/main/examples/output_example.gif)

Hardware (required):
- Adafruit NRF52840 Glasses Driver Board (https://www.adafruit.com/product/5217)
- Adafruit PCF8523 RTC (https://www.adafruit.com/product/5189 or https://www.adafruit.com/product/3295)
- Battery for RTC (https://www.adafruit.com/product/380)

Hardware (recommended):
- STEMMA QWIIC Cable (https://www.adafruit.com/product/4399)
- 500mah rechargeable battery (https://www.adafruit.com/product/1578)

I am making all the software I wrote for this project open source; please use this code responsibly and not for malicious purposes.
 
-	Project BLE-SPY made by Michael Lacock, 2022

![image](https://user-images.githubusercontent.com/71791024/152244504-39619c2b-4bdb-427f-8589-d7472dfb9e7d.png)
