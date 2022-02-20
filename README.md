# teleinfo
A Linky information grabber running on raspberry with an ePaper display

![ePaper display](https://github.com/fguilleme/teleinfo/blob/1fd800b61a76f14ee4aec7abdc50fd364f969db1/epaper/linky.png)

Requirements
- influxdb

The data is stored in an influxdb that can be accessed by grafana dashboard.
It is also displayed on an ePaped 2.13 inches display

Installation:

sudo apt install influxdb

sudo install grabber/teleinfo.py /usr/local/bin/teleinfo

sudo install epaper/main.py /usr/local/bin/linky-epaper

sudo cp epaper/epd*py /usr/local/bin

sudo cp epaper/Font.ttc /usr/local/share

sudo cp grabber/teleinfo.service /etc/systemd/system/

sudo cp epaper/linky-epaper.service /etc/systemd/system/

sudo systemctl enable teleinfo.service

sudo systemctl start teleinfo.service

sudo systemctl enable linky-epaper.service

sudo systemctl start linky-epaper.service

check grabbing is fine with sudo tail -f /var/log/teleinfo/teleinfo.log
