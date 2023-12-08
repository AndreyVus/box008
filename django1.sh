#!/bin/bash
if [ "$1" == "start" ]; then
  cd /home/kbwiot/django1
  python -m venv venv
  source venv/bin/activate
  python -m pip install Django pyyaml
  deactivate
  cd ..

  if [ ! -x django1/manage.py ]; then chmod 755 django1/manage.py; fi
  if [ ! -f /etc/systemd/system/django1.service ]; then
    echo '[Unit]
Description=Django App
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot/django1
ExecStart=/bin/bash -c "source venv/bin/activate && ./manage.py runserver 0:8000"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
'>/etc/systemd/system/django1.service
  fi
  systemctl enable django1.service
  systemctl start django1.service
  systemctl status django1.service

elif [ "$1" == "stop" ]; then
  systemctl stop django1.service
  systemctl disable django1.service
  rm /etc/systemd/system/django1.service

  #rm -rf /home/kbwiot/django1/venv

else
  echo "Unbekannter Parameter: $1. Bitte verwenden Sie 'start' oder 'stop'."
fi
