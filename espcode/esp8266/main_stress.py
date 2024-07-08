import urequests
import network
import machine
import time

SSID    :str = 'IoT-ra'
PASSWORD:str = 'P9$y#F5x!b&'
SERVER  :str = 'api.thingspeak.com'
THINGSPEAK_WRITE_API_KEY :str = 'GJ84DDRYWOHWXDH5'
HTTP_HEADERS = {'Content-Type': 'application/json'} 

RELAY_PIN: int        = 2
ANALOGIN : int        = 0
CALIBRATION: float    = 0.39

wifiRetries             = 200
relayOnTimeSeconds      = 5


def scan_wifi(sta_if) -> None:
    for x in sta_if.scan():
        ssid = x[0]
        values = x[1:]
        
def connect_wifi() -> None:  
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    count = 0
    while count < wifiRetries:
        try:
            if not sta_if.isconnected():
                print(f'connecting to network... Retries = {count}')
                sta_if.connect(SSID, PASSWORD)
                time.sleep(1)
                count += 1                
            if sta_if.isconnected():
                print('Connected to Network')        
                print('network config:', sta_if.ifconfig())
                break
        except Exception as e:
            print(e)
            continue
            
def scale_value(value, in_min, in_max, out_min, out_max):
  scaled_value = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  return scaled_value

def sendDataAndMeasurement(dummy = None) -> None:
    print('reading')
    
    adc         = machine.ADC(ANALOGIN)
    sensorValue = adc.read_u16()
    voltage     = ((sensorValue * 3.3) / 65535) * 2 + CALIBRATION
    voltage     = round(voltage,2)
    battery_percentage = scale_value(voltage,2.7,4.0,0,100)
    print('sensor',sensorValue,'voltage',voltage,'percent',battery_percentage)
    
    with open('battery.csv','a') as file:
        file.write(str(time.time_ns()))
        file.write(',')
        file.write('_'.join(list(str(x) for x in time.gmtime())))
        file.write(',')
        file.write(str(voltage))
        file.write(',')
        file.write(str(battery_percentage))
        file.write('\r\n')
        
    print('sending to thingspeak ', end = '')
    data = {'field1':voltage, 'field2':battery_percentage} 
    request = urequests.post(
        'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY,
        json    = data,
        headers = HTTP_HEADERS
    )
    request.close() 
    if request.status_code == 200: print('successfully')
    else: print('Data not sent')
    
def main():  
    connect_wifi()
    adc      = machine.ADC(ANALOGIN)
    relayPin = machine.Pin(RELAY_PIN,machine.Pin.OUT)        
    relayPin.value(1)
    t = machine.Timer(1)
    t.init(period=relayOnTimeSeconds ,callback = sendDataAndMeasurement)
    
if __name__ == '__main__':
    main()
