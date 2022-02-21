all: 
	install epaper/main.py /usr/local/bin/linky-epaper
	cp epaper/epd*py /usr/local/bin/
	cp epaper/Font.ttc /usr/local/share
	cp  epaper/linky-epaper.service /etc/systemd/system
	install grabber/teleinfo.py /usr/local/bin/teleinfo
	cp  grabber/teleinfo.service /etc/systemd/system
	systemctl enable linky-epaper.service
	systemctl enable teleinfo.service
	systemctl daemon-reload
	systemctl restart linky-epaper.service
	systemctl restart teleinfo.service

