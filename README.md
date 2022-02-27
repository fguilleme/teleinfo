# teleinfo
A Linky information grabber running on raspberry with an ePaper display

Requirements
- influxdb

The data is stored in an influxdb that can be accessed by grafana dashboard.
It is also displayed on an ePaped 2.13 inches display

Installation:
sudo apt install influxdb

sudo make

check grabbing is fine with sudo tail -f /var/log/teleinfo/teleinfo.log
