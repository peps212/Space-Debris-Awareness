#include <SPI.h>
#include <WiFiNINA.h>
#include <ArduinoHttpClient.h>

char ssid[] = "networkname";              // your network SSID (name)
char password[] = "networkpass";                // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;             // the Wi-Fi radio's status
unsigned long previousMillisInfo = 0;     //will store last time Wi-Fi information was updated
const int intervalInfo = 5000;            // interval at which to update the board information
int port = 80;

char server[] = "url"; 

WiFiClient wifiClient;

HttpClient httpClient = HttpClient(wifiClient, server, port);

void setup()

{
 
  //please enter your sensitive data in the Secret tab

  //Initialize serial and wait for port to open:
  Serial.begin(9600);
  while (!Serial);

  // attempt to connect to Wi-Fi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to network: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(ssid, password);

    // wait 10 seconds for connection:
    delay(10000);
  }

  // you're connected now, so print out the data:
  Serial.println("You're connected to the network");
  Serial.println("---------------------------------------");
}
 


void loop() {

  String date = "09102022";
  String key = "2";
  String username = "mikayelsuvaryan" ;

  String datelabel = "&date=";
  String keylabel = "&key=";
  String usernamelabel = "username=";
  String totalpost;
  totalpost = usernamelabel + username + keylabel + key + datelabel + date;


  if (WiFi.status() == WL_CONNECTED) {

    String data = "{\"username\":\"mikayelsuvaryan\", \"key\":\"1\", \"date\" : \"2023\"}";
    httpClient.post("/datatransfer.php","application/json",data);
    int statusCode = httpClient.responseStatusCode();
    String response = httpClient.responseBody();
    Serial.println(statusCode);
    Serial.println(response);
    
  
    delay(1000);

    
  
  }

delay(5000);
}
