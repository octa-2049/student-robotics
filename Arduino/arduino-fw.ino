#include <Arduino.h>
#include <PinChangeInterrupt.h>

// We communicate with the Arduino at 115200 baud.
#define SERIAL_BAUD 115200

#define FW_VER 2

// Define encoder pins
const int encoder0PinA = 2; // Interrupt pin
const int encoder0PinB = 3; // Digital pin
const int encoder1PinA = 4; // Interrupt pin
const int encoder1PinB = 5; // Digital pin

volatile long encoder0Ticks = 0; // Track encoder ticks
long previous0Ticks = 0;
long ticks0 = 0;
float motor0Speed = 0.0; // Motor speed in RPM
float motor0Position = 0.0; // Motor position in revolutions

volatile long encoder1Ticks = 0; // Track encoder ticks
long previous1Ticks = 0;
long ticks1 = 0;
float motor1Speed = 0.0; // Motor speed in RPM
float motor1Position = 0.0; // Motor position in revolutions

unsigned long lastTime = 0;
const unsigned long interval = 100; // Interval in milliseconds
const int encoderResolution0 = 700; // Encoder resolution in ticks per revolution (gearbox)
const int encoderResolution1 = 700; // Encoder resolution in ticks per revolution (gearbox)

void setup() {
  pinMode(encoder0PinA, INPUT);
  pinMode(encoder0PinB, INPUT);
  pinMode(encoder1PinA, INPUT);
  pinMode(encoder1PinB, INPUT);

  // Attach interrupt for encoder pin A
  attachInterrupt(digitalPinToInterrupt(encoder0PinA), update0Encoder, RISING);
  attachPCINT(digitalPinToPCINT(encoder1PinA), update1Encoder, RISING);
  Serial.begin(SERIAL_BAUD);
}

int read_pin() {
  // Convert the ASCII character to a pin number.
  // a -> 0, b -> 1, c -> 2, etc.
  while (!Serial.available());
  int pin = Serial.read();
  return (int)(pin - 'a');
}

void command_read() {
  int pin = read_pin();
  // Read from the expected pin.
  int level = digitalRead(pin);
  // Send back the result indicator.
  if (level == HIGH) {
    Serial.write('h');
  } else {
    Serial.write('l');
  }
}

void command_analog_read() {
  int pin = read_pin();
  int value = analogRead(pin);
  Serial.print(value);
}

void command_write(int level) {
  int pin = read_pin();
  digitalWrite(pin, level);
}

void command_mode(int mode) {
  int pin = read_pin();
  pinMode(pin, mode);
}

void command_ultrasound() {
  int pulse = read_pin();
  int echo = read_pin();

  // config pins to correct modes
  pinMode(pulse, OUTPUT);
  pinMode(echo, INPUT);

  // provide pulse to trigger reading
  digitalWrite(pulse, LOW);
  delayMicroseconds(2);
  digitalWrite(pulse, HIGH);
  delayMicroseconds(5);
  digitalWrite(pulse, LOW);

  // measure the echo time on the echo pin
  int duration = pulseIn(echo, HIGH, 60000);
  Serial.print(microsecondsToMm(duration));
}

long microsecondsToMm(long microseconds) {
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance we need half
  // 10 x (us / 29 / 2)
  return (5 * microseconds / 29);
}

void command_motor0_speed(float s) {
  float speed = s;
   Serial.print(speed);
}

void command_motor0_position(float p) {
  float position = p;
  Serial.print(position);
}

void command_motor1_speed(float s) {
  float speed = s;
   Serial.print(speed);
}

void command_motor1_position(float p) {
  float position = p;
  Serial.print(position);
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastTime >= interval) {
    noInterrupts(); // Temporarily disable interrupts to read encoderTicks safely
    ticks0 = encoder0Ticks;
    interrupts(); // Re-enable interrupts

    // Calculate speed (RPM)
    motor0Speed = (ticks0 - previous0Ticks) * (60000.0 / (interval * encoderResolution0));
    previous0Ticks = ticks0;

    // Calculate position (revolutions)
    motor0Position = ticks0 / (float)encoderResolution0;

    noInterrupts(); // Temporarily disable interrupts to read encoderTicks safely
    ticks1 = encoder1Ticks;
    interrupts(); // Re-enable interrupts

    // Calculate speed (RPM)
    motor1Speed = (ticks1 - previous1Ticks) * (60000.0 / (interval * encoderResolution0));
    previous1Ticks = ticks1;

    // Calculate position (revolutions)
    motor1Position = ticks1 / (float)encoderResolution0;

    lastTime = currentTime;
  }
  while (Serial.available()) {
    // Fetch all commands that are in the buffer
    int selected_command = Serial.read();
    // Do something different based on what we got:
    switch (selected_command) {
      case 'a':
        command_analog_read();
        break;
      case 'r':
        command_read();
        break;
      case 'l':
        command_write(LOW);
        break;
      case 'h':
        command_write(HIGH);
        break;
      case 'i':
        command_mode(INPUT);
        break;
      case 'o':
        command_mode(OUTPUT);
        break;
      case 'p':
        command_mode(INPUT_PULLUP);
        break;
      case 'u':
        command_ultrasound();
        break;
      case 'v':
        Serial.print("SRcustom:");
        Serial.print(FW_VER);
        break;
      case 'm':
        command_motor0_speed(motor0Speed);
        break;
      case 'n':
        command_motor0_position(motor0Position);
        break;
      case 'x':
        command_motor1_speed(motor1Speed);
        break;
      case 'y':
        command_motor1_position(motor1Position);
        break;
      default:
        // A problem here: we do not know how to handle the command!
        // Just ignore this for now.
        break;
    }
    Serial.print("\n");
  }
}

void update0Encoder() {
    int stateB0 = digitalRead(encoder0PinB);
    // Determine direction based on encoder signals
    if (stateB0 == HIGH) {
        encoder0Ticks++;
    } else {
        encoder0Ticks--;
    }
}

void update1Encoder() {
    int stateB1 = digitalRead(encoder1PinB);

    // Determine direction based on encoder signals
    if (stateB1 == HIGH) {
        encoder1Ticks++;
    } else {
        encoder1Ticks--;
    }
}
