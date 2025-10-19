#include <BluetoothSerial.h>
#include <ESP32Servo.h>
#include <Stepper.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to enable it
#endif

BluetoothSerial SerialBT;
Servo myservo;
//Stepper myStepper(2048, 22, 21, 19, 18);
int servoPos;
static const int servoPin = 4;



void setup() 
{
  Serial.begin(115200);
  SerialBT.begin("Playstation 6");
  Serial.println("The device has started, bluetooth pairing is enabled");

  myservo.attach(servoPin, 500, 2400);
  myservo.setPeriodHertz(50);
}

void loop() 
{
  //myStepper.setSpeed(10);
  //myStepper.step(2048);
  //delay(1000);

  if (SerialBT.available()) 
  {
    Serial.write(SerialBT.read());
  }
  //myservo.writeMicroseconds(servoPos);
  
  /*
  for (int i = 0; i <= 180; i++)
  {
    myservo.write(i);
    SerialBT.println(i);
    delay(20);
  }
  for (int i = 180; i >= 0; i--)
  {
    myservo.write(i);
    SerialBT.println(i);
    delay(20);
  }
  */
}
