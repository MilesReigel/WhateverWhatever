#include <BluetoothSerial.h>
#include <ESP32Servo.h>
#include <Stepper.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to enable it
#endif

BluetoothSerial SerialBT;
Servo myservo;
char c;
static const int servoPin = 14;
int theta = 0, rho = 0, SPin1 = 22, SPin2 = 21, SPin3 = 19, SPin4 = 18;
bool autorunTF = 0;
String input;
Stepper mystepper(2048, SPin1, SPin2, SPin3, SPin4);


void Clockwise() {
  SPin1 = 22;
  SPin2 = 21;
  SPin3 = 19;
  SPin4 = 18;
}

void Counterclockwise() {
  SPin1 = 18;
  SPin2 = 19;
  SPin3 = 21;
  SPin4 = 22;
}

void autoRun() {
  srand(time(NULL));
  rho = (rand() + 10) % 160 + 10;
  theta = rand() % 360;

  myservo.write(rho);
  mystepper.setSpeed(10);
  if (theta >= 180) {
    Clockwise();
  } else {
    Counterclockwise();
  }
  mystepper.step((2048 / 360) * (theta / 2));
  delay(2000);
}

bool inputIsNumber(String inputStr) {
  for (char c : inputStr) {
    if (!(48 <= c && 57 >= c)) {
      return (0);
    } else {
      return (1);
    }
  }
}

int strtoint(String str) {
  int intconverter = (100 * int(str[0] - '0')) + (10 * int(str[1] - '0')) + int(str[2] - '0');
  if (intconverter > 0 && intconverter < 180) {
    return (intconverter);
  } else {
    SerialBT.println("Invalid Input");
    return (0);
  }
}

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32TEST");

  myservo.attach(servoPin, 500, 2400);
  myservo.setPeriodHertz(50);
}

void loop() {
  if (SerialBT.available()) {
    input = SerialBT.readStringUntil('\n');
    c = input[0];
    if (c == 'a' || c == 'A') {
      SerialBT.println("Automatic Mode Activated");
      autorunTF = 1;
    } else if (c == 'm' || c == 'M') {
      SerialBT.println("Manual Mode Activated");
    }
    if (inputIsNumber(input)) {
      myservo.write(strtoint(input));
    }
  }
  if (autorunTF) {
    autoRun();
  }
  delay(20);
}