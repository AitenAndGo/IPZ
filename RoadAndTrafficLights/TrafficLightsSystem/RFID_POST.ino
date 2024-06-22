#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFiMulti.h>
#include <TimeLib.h>

#define SS_PIN_1 21
#define SS_PIN_2 2
#define SS_PIN_3 16
#define SS_PIN_4 5

#define RST_PIN_1 4
#define RST_PIN_2 15
#define RST_PIN_3 14
#define RST_PIN_4 2

MFRC522 rfid_1(SS_PIN_1, RST_PIN_1); // Instance of the class
MFRC522 rfid_2(SS_PIN_2, RST_PIN_2);
MFRC522 rfid_3(SS_PIN_3, RST_PIN_3); // Corrected RST_PIN for this instance
MFRC522 rfid_4(SS_PIN_4, RST_PIN_4);
WiFiMulti wifiMulti;
//connecting to WiFi w domu
/**/
const char* ssid = "HH71V1_3A49_2.4G";
const char* password = "pYRyNYde";

MFRC522::MIFARE_Key key; 

// Init arrays to store new NUID for each RFID reader
byte nuidPICC_1[4];
byte nuidPICC_2[4];
byte nuidPICC_3[4];
byte nuidPICC_4[4];

void setup() { 
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus

  rfid_1.PCD_Init(); // Init MFRC522 
  rfid_2.PCD_Init();
  rfid_3.PCD_Init(); // Init MFRC522 
  rfid_4.PCD_Init();

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  Serial.println(F("This code scans the MIFARE Classic NUID."));
  Serial.print(F("Using the following key:"));
  printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
  wifiMulti.addAP(ssid, password);
}

String byteToHex(byte *buffer, byte bufferSize)
 {
  String hexString = "";
  char tmp[3];
  for (byte i = 0; i < bufferSize; i++) {
  sprintf(tmp, "%02X", buffer[i]);
  hexString += String(tmp);
  }
  return hexString;
}


void readRFID(MFRC522& rfid, byte* nuidPICC, int ss_pin) {
  // Activate the RFID module
  digitalWrite(ss_pin, LOW);
  String nuid;
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (rfid.PICC_IsNewCardPresent()) {
    // Verify if the NUID has been read
    if (rfid.PICC_ReadCardSerial()) {
      Serial.print(F("PICC type: "));
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      Serial.println(rfid.PICC_GetTypeName(piccType));

      // Check if the PICC is of Classic MIFARE type
      if (piccType == MFRC522::PICC_TYPE_MIFARE_MINI || 
          piccType == MFRC522::PICC_TYPE_MIFARE_1K ||
          piccType == MFRC522::PICC_TYPE_MIFARE_4K) {

          Serial.println(F("A new card has been detected."));

          // Store NUID into nuidPICC array
          for (byte i = 0; i < 4; i++) {
            nuidPICC[i] = rfid.uid.uidByte[i];
          }

          Serial.println(F("The NUID tag is:"));
          Serial.print(F("In hex: "));
          printHex(rfid.uid.uidByte, rfid.uid.size);
          nuid = byteToHex(rfid.uid.uidByte, rfid.uid.size);
          Serial.println();
          Serial.print(F("In dec: "));
          printDec(rfid.uid.uidByte, rfid.uid.size);
          //Serial.println();
          //Serial.println(nuid);

      } else {
        Serial.println(F("Your tag is not of type MIFARE Classic."));
      }
      String name = "Północ";
      postDataToServer(nuid, name);
      // Halt PICC
      rfid.PICC_HaltA();

      // Stop encryption on PCD
      rfid.PCD_StopCrypto1();
    }
  }

  // Deactivate the RFID module
  digitalWrite(ss_pin, HIGH);
}

void postDataToServer(String dane, String sensor_id) {

Serial.println(F("Posting JSON data to server..."));
// Block until we are able to connect to the WiFi access point
if (wifiMulti.run() == WL_CONNECTED) {
  HTTPClient http;   
  //Serial.println(F("Here1"));
  http.begin("https://miszczak13.eu.pythonanywhere.com/postTrafic");  
  http.addHeader("Content-Type", "application/json");         
  //Serial.println(F("Here2"));
  StaticJsonDocument<200> doc;

  doc["car_id"] = dane;
  doc["timeofstop"] = now();
  doc["sensor_id"] =  sensor_id;

  //Serial.println(F("Here3"));
  String requestBody;
  serializeJson(doc, requestBody);

  Serial.println(requestBody);
  Serial.println(F("Wyslany"));
  
  int httpResponseCode = http.POST(requestBody);

  delay(100);

  if(httpResponseCode>0){
    
    String response = http.getString();                       
    
    Serial.println(httpResponseCode);   
    Serial.println(response);
  }
  else {
    Serial.println(F("Error occurred while sending HTTP POST"));
  }
}
}
bool connected_to_wifi = false;

void loop() {
  readRFID(rfid_1, nuidPICC_1, SS_PIN_1);
  readRFID(rfid_2, nuidPICC_2, SS_PIN_2);
  readRFID(rfid_3, nuidPICC_3, SS_PIN_3);
  readRFID(rfid_4, nuidPICC_4, SS_PIN_4);

  
// wifi connection
WiFi.mode(WIFI_STA); //Optional
WiFi.begin(ssid, password);

while(WiFi.status() != WL_CONNECTED){
  if(!connected_to_wifi){
    Serial.println(F("\nConnecting....."));
    delay(3000);
  }
}

if(!connected_to_wifi)
{
Serial.println(F("\nConnected to the WiFi network"));
Serial.print("Local ESP32 IP: ");
Serial.println(WiFi.localIP());
delay(100);
connected_to_wifi = true;
}
}

/**
 * Helper routine to dump a byte array as hex values to Serial. 
 */
void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}

/**
 * Helper routine to dump a byte array as dec values to Serial.
 */
void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}