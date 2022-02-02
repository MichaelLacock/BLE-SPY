//---------------------------------------------
//---------------- ML-Watch OS ----------------
//----------------- RTC SETUP -----------------
//---------------------------------------------
//----- Made by Michael Lacock, 2019-2022 -----
//  *** Use of example code from Adafruit ***
//---------------------------------------------

#include <bluefruit.h>
#include "RTClib.h"
#include <Adafruit_NeoPixel.h>

RTC_PCF8523 rtc;
BLEClientCts  bleCTime;

#define LED_PIN     3
#define LED_COUNT  1
#define BRIGHTNESS 50

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRBW + NEO_KHZ800);

int rainbow = 0;

const int BUTTON_PIN = 4;
int lastState = HIGH;
int currentState;

int Day = 21;
int Month = 4;
int Year = 2000;

int Hour = 21;
int Min = 48;
int Sec = 31;

void setup() {
  
  Serial.begin(115200);
  Serial.print("----on----");

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  //_BLUETOOTH_SETUP_
  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);

  Bluefruit.begin();
  Bluefruit.setTxPower(4);
  Bluefruit.setName("RTC-Setup");
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  bleCTime.begin();
  bleCTime.setAdjustCallback(cts_adjust_callback);

  startAdv();

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    Serial.flush();
    while (1) delay(10);
  }

  rtc.start();

  strip.begin();
  strip.show();
  strip.setBrightness(BRIGHTNESS);

}

void loop() {

  bleCTime.getCurrentTime();
  
  Day = bleCTime.Time.day;
  Month = bleCTime.Time.month;
  Year = bleCTime.Time.year;
  
  Hour = bleCTime.Time.hour;
  Min = bleCTime.Time.minute;
  Sec = bleCTime.Time.second;

  Serial.println("   ");
  Serial.printf("%04d-%02d-%02d ", bleCTime.Time.year, bleCTime.Time.month, bleCTime.Time.day);
  Serial.printf("%02d:%02d:%02d ", bleCTime.Time.hour, bleCTime.Time.minute, bleCTime.Time.second);

  rtc.adjust(DateTime(Year, Month, Day, Hour, Min, Sec));

  currentState = digitalRead(BUTTON_PIN);

  if (lastState == HIGH && currentState == LOW) {
      rtc.adjust(DateTime(Year, Month, Day, Hour, Min, Sec));
      Serial.println("--------------------");
      Serial.println("[-] RTC setup complete.");
      Serial.println("--------------------");

      rainbow = 1;
  }
      
  lastState = currentState;

  if (rainbow == 1) {
      rainbowFade2White(3, 3, 1);
  }
  
}

//_CODE_FROME_ADAFRUIT_
void startAdv(void)
{
  // Advertising packet
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addAppearance(BLE_APPEARANCE_GENERIC_CLOCK);

  // Include CTS client UUID
  Bluefruit.Advertising.addService(bleCTime);

  // Includes name
  Bluefruit.Advertising.addName();
  
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);      // number of seconds in fast mode
  Bluefruit.Advertising.start(0);                // 0 = Don't stop advertising after n seconds
}

void connect_callback(uint16_t conn_handle)
{
  BLEConnection* conn = Bluefruit.Connection(conn_handle);

  Serial.println("Connected");
  
  Serial.print("Discovering CTS ... ");
  if ( bleCTime.discover(conn_handle) )
  {
    Serial.println("Discovered");
    
    // Current Time Service requires pairing to work
    // request Pairing if not bonded
    Serial.println("Attempting to PAIR with the iOS device, please press PAIR on your phone ... ");
    conn->requestPairing();
  }
}

void cts_adjust_callback(uint8_t reason)
{
  const char * reason_str[] = { "Manual", "External Reference", "Change of Time Zone", "Change of DST" };

  Serial.println("iOS Device time changed due to ");
  Serial.println( reason_str[reason] );
}

void printTime(void)
{
  const char * day_of_week_str[] = { "n/a", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };
  
  Serial.printf("%04d-%02d-%02d ", bleCTime.Time.year, bleCTime.Time.month, bleCTime.Time.day);
  Serial.printf("%02d:%02d:%02d ", bleCTime.Time.hour, bleCTime.Time.minute, bleCTime.Time.second);
  Serial.print(day_of_week_str[bleCTime.Time.weekday]);
  
  int utc_offset =  bleCTime.LocalInfo.timezone*15; // in 15 minutes unit
  Serial.printf(" (UTC %+d:%02d, ", utc_offset/60, utc_offset%60);
  Serial.printf("DST %+.1f)", ((float) bleCTime.LocalInfo.dst_offset*15)/60 );
  Serial.println();
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) reason;

  //Disconnect = 1;

  Serial.println();
  Serial.print("Disconnected, reason = 0x"); Serial.println(reason, HEX);
}

void rainbowFade2White(int wait, int rainbowLoops, int whiteLoops) {
  int fadeVal=0, fadeMax=100;

  // Hue of first pixel runs 'rainbowLoops' complete loops through the color
  // wheel. Color wheel has a range of 65536 but it's OK if we roll over, so
  // just count from 0 to rainbowLoops*65536, using steps of 256 so we
  // advance around the wheel at a decent clip.
  for(uint32_t firstPixelHue = 0; firstPixelHue < rainbowLoops*65536;
    firstPixelHue += 256) {

    for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...

      // Offset pixel hue by an amount to make one full revolution of the
      // color wheel (range of 65536) along the length of the strip
      // (strip.numPixels() steps):
      uint32_t pixelHue = firstPixelHue + (i * 65536L / strip.numPixels());

      // strip.ColorHSV() can take 1 or 3 arguments: a hue (0 to 65535) or
      // optionally add saturation and value (brightness) (each 0 to 255).
      // Here we're using just the three-argument variant, though the
      // second value (saturation) is a constant 255.
      strip.setPixelColor(i, strip.gamma32(strip.ColorHSV(pixelHue, 255,
        255 * fadeVal / fadeMax)));
    }

    strip.show();
    delay(wait);

    if(firstPixelHue < 65536) {                              // First loop,
      if(fadeVal < fadeMax) fadeVal++;                       // fade in
    } else if(firstPixelHue >= ((rainbowLoops-1) * 65536)) { // Last loop,
      if(fadeVal > 0) fadeVal--;                             // fade out
    } else {
      fadeVal = fadeMax; // Interim loop, make sure fade is at max
    }
  }

  for(int k=0; k<whiteLoops; k++) {
    for(int j=0; j<256; j++) { // Ramp up 0 to 255
      // Fill entire strip with white at gamma-corrected brightness level 'j':
      strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
      strip.show();
    }
    delay(1000); // Pause 1 second
    for(int j=255; j>=0; j--) { // Ramp down 255 to 0
      strip.fill(strip.Color(0, 0, 0, strip.gamma8(j)));
      strip.show();
    }
  }

  delay(500); // Pause 1/2 second
}
