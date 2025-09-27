int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "LED ON") {
      digitalWrite(ledPin, HIGH);
    } 
    else if (command == "LED OFF") {
      digitalWrite(ledPin, LOW);
    }
  }
}
// This code is written in C++ and Intended  for the use of the Ardunio platfrom.