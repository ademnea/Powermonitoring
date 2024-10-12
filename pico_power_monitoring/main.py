import urequests
import network
import machine
import time

# SSID    :str = 'IoT-ra'
# PASSWORD:str = 'P9$y#F5x!b&'

SSID    :str = 'netEwaste'
PASSWORD:str = 'net3013P'

SERVER  :str = 'api.thingspeak.com'
THINGSPEAK_WRITE_API_KEY :str = 'K496XGBKTQEOF2C6'
HTTP_HEADERS = {'Content-Type': 'application/json'} 

RELAY_PIN: int           = 4 # GPIO4 pin 6 
LED_PIN: str             =  "LED" # not connected to pin but to wifi
ANALOGIN : int         =  27
CALIBRATION: float  =  0.39

sendDataIntervalSeconds = 15
relayOnTimeSeconds      = 1*60
delayTimeSeconds   = 6*60*60
wifiRetries             = 25

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
    adc         = machine.ADC(machine.Pin(ANALOGIN))
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
    ledPin.value(0)
    
    is_connected = connect_wifi()
    currentMillis  = time.ticks_ms()
    
    while True:
        if time.ticks_ms() - currentMillis < relayOnTimeSeconds*1_000:
            
            relayPin.on()
            ledPin.on()
            
            if is_connected: 
                t = machine.Timer(
                    period=sendDataIntervalSeconds *1000,
                    callback = sendDataAndMeasurement
                )
                time.sleep(relayOnTimeSeconds)
            else:
                t = machine.Timer(
                    period=sendDataIntervalSeconds*1000,
                    callback = lambda x: print((time.ticks_ms()-currentMillis)/1000,'seconds elapsed')
                )
            time.sleep(relayOnTimeSeconds)
            t.deinit()
        else:
            relayPin.off()
            ledPin.off()
            print()
            print()
            print()
            print('light sleep')
            # time.sleep(delayTimeSeconds)
            time.sleep(10)
            print('reset')
            machine.reset()
            
            # machine deep sleep does'nt work for long values
            #print('deep sleep')
            #machine.deepsleep(10*1000) # deep sleep to induce wake up into boot file
        
    
if __name__ == '__main__':
    main()

