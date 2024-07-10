from machine import Pin, ADC, RTC
import time

filename = "data08"
adc = ADC(Pin(26))
start_time = time.time_ns()
window_size = 10  
voltage_window = []

def moving_average(window):
    return sum(window) / len(window)

with open(f"{filename}.csv", "w") as f:
    f.write("time,voltage,average_voltage\r\n")

while True:
    v = adc.read_u16()
    voltage = v * 3.3 * 2 / 65535
    elapsed_time = time.time_ns() - start_time
    print(elapsed_time)
    voltage_window.append(voltage)
    if len(voltage_window) > window_size:
        voltage_window.pop(0)
    
    average_voltage = moving_average(voltage_window)
    
    with open(f"{filename}.csv", "a") as f:
        f.write(f"{elapsed_time},{voltage},{average_voltage}\r\n")
    # time.sleep(0.00000001)
    

