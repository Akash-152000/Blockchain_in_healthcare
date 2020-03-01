float temp;



void setup()
{
  Serial.begin(9600);
   Serial.println("Date & Time, Temperature *C");

  }

void loop() {
  delay(1000);
  // put your main code here, to run repeatedly:
temp = analogRead(A1);
temp = temp * 0.48828125;
Serial.print(",");
Serial.print(temp);
Serial.print("*C");
Serial.println();

}
