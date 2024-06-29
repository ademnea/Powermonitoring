from machine import Pin, ADC, RTC
import time

adc = ADC(Pin(26))
r = RTC()
with open("data.csv", "w") as f:
    f.write("time,voltage\r\n")
while True:
    v = adc.read_u16()
    voltage = v*3.3*2/65535
    
    with open("data.csv", "a") as f:
        f.write(str(time.time_ns()))
        f.write(",")
        f.write(str(voltage))
        f.write("\r\n")
        