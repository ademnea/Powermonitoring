
// Measure current with ACS712
const int nSamples = 1000;
const float vcc = 5.0;
const int adcMax = 1023;
unsigned long mytime;

const float sens = 0.185;  // 5A

float avg() {
  float val = 0;
  for (int i = 0; i < nSamples; i++) {
    val += analogRead(A0);
    delay(0.5);
  }
  return val / adcMax / nSamples;
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  mytime = millis();
  Serial.print(mytime);
  Serial.print(",");
  // Serial.print("Voltage:");
  Serial.print(avg()*10);
  Serial.print(",");
  float cur = (2.4945 - vcc * avg()) / sens;
  // Serial.print("Current:");
  Serial.println(cur);
}