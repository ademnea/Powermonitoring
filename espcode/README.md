To upload data to the ESP 32

- flash micropython to the esp 32 instructions can be found on micropython website

install esptool 
```bash
sudo pip install esptool
```
and erase the old flash
```bash
esptool.py --port /dev/ttyUSB0 erase_flash
```

for esp8266

```bash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dout 0 ESP8266_GENERIC-20240602-v1.23.0.bin
```
where `ESP8266_GENERIC-20240602-v1.23.0.bin` is the micropython binary from the site

for esp 32

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
```
where `ESP32_GENERIC-20240602-v1.23.0.bin` is the micropython binary from the site

- create two files on the esp 32 using thonny `boot.py` and `main.py` then the logic runs with deep sleep

Thingspeak channel
https://thingspeak.com/channels/2488885
