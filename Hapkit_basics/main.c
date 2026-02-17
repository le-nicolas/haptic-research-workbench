#include <Servo.h>

Servo hapticMotor;

const int joystickX = A0;
const int joystickY = A1;
const int potPin = A2;
const int motorPin = 9;

float Kp = 1.5;  // Proportional gain for force feedback
float damping = 0.5;  // Damping coefficient
float targetPosition = 0;  // Target position from joystick

void setup() {
  Serial.begin(9600);
  hapticMotor.attach(motorPin);
  pinMode(joystickX, INPUT);
  pinMode(potPin, INPUT);
}

void loop() {
  // Read joystick input
  int joystickValue = analogRead(joystickX);
  targetPosition = map(joystickValue, 0, 1023, -50, 50);  // Map joystick range to position

  // Read Hapkit arm position
  int potValue = analogRead(potPin);
  float currentPosition = map(potValue, 0, 1023, -50, 50);

  // Compute force feedback
  float error = targetPosition - currentPosition;  // Error between target and current position
  float force = Kp * error - damping * (currentPosition);  // Proportional and damping

  // Generate haptic feedback
  int motorSpeed = constrain(force, 0, 180);  // Map force to motor speed range
  hapticMotor.write(motorSpeed);

  // Debugging output
  Serial.print("Joystick: ");
  Serial.print(targetPosition);
  Serial.print("\tPosition: ");
  Serial.print(currentPosition);
  Serial.print("\tForce: ");
  Serial.println(force);

  delay(10);
}
