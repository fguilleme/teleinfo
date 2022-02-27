# teleinfo
A Linky information grabber running on raspberry with an ePaper display

![ePaper display](https://github.com/fguilleme/teleinfo/blob/1fd800b61a76f14ee4aec7abdc50fd364f969db1/epaper/linky.png)

Requirements
- influxdb

The data is stored in an influxdb that can be accessed by grafana dashboard.
It is also displayed on an ePaped 2.13 inches display

Installation:

sudo pip install pyserial
sudo apt install influxdb

sudo make

check grabbing is fine with sudo tail -f /var/log/teleinfo/teleinfo.log
