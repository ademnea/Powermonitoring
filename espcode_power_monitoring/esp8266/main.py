import urequests
import network
import machine
import time

SSID    :str = 'IoT-ra'
PASSWORD:str = 'P9$y#F5x!b&'
SERVER  :str = 'api.thingspeak.com'
THINGSPEAK_WRITE_API_KEY :str = 'K496XGBKTQEOF2C6'
HTTP_HEADERS = {'Content-Type': 'application/json'} 

RELAY_PIN: int        = 4 # d2 is pin 4
LED_PIN: int          = 2 # GPIO 2 is on board LED
ANALOGIN : int        = 0
CALIBRATION: float    = 0.39

sendDataIntervalSeconds = 14
relayOnTimeSeconds      = 5*60
delayTimeMiliSeconds    = 21_600_000
wifiRetries             = 60
#relayPin = RELAY_PIN
#relayPin.value(1) # since the esp is active high

def connect_wifi() -> bool:  
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
                count += 1
                print('Connected to Network')        
                print('network config:', sta_if.ifconfig())
                return True
        except Exception as e:
            time.sleep(1)
            count += 1
            print(e)
            continue
    return False
            
def scale_value(value, in_min, in_max, out_min, out_max):
  scaled_value = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  return scaled_value

def sendDataAndMeasurement(dummy = None) -> bool:
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
    if request.status_code == 200: 
        print('successfully')
        return True
    else: 
        print('Data not sent')
        return False
    
def main():    
    adc      = machine.ADC(ANALOGIN)
    relayPin = machine.Pin(RELAY_PIN,machine.Pin.OUT)
    ledPin = machine.Pin(LED_PIN,machine.Pin.OUT)
    relayPin.value(0)
    ledPin.value(1)
    
    is_connected = connect_wifi()
    currentMillis = time.ticks_ms()
    
    while True:
        if time.ticks_ms() - currentMillis < relayOnTimeSeconds*1_000:
            
            relayPin.value(1)
            ledPin.value(0)
            t = machine.Timer(1)
            if is_connected: 
                t.init(period=sendDataIntervalSeconds ,callback = sendDataAndMeasurement)
            else:
                t.init(period=sendDataIntervalSeconds, callback = lambda x: print((time.ticks_ms()-currentMillis)/1000,'seconds elapsed'))
            time.sleep(relayOnTimeSeconds)
            t.deinit()
        else:
            relayPin.value(0)
            ledPin.value(1)
            print()
            print()
            print()
            print('Delay')
            # time.sleep(delayTimeSeconds)
            machine.deepsleep(delayTimeMiliSeconds)
        
    
if __name__ == '__main__':
    main()
