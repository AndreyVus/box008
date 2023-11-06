#!/bin/bash
if [ -f KbwIO.py ]; then
  if [ ! -x KbwIO.py ]; then chmod 755 KbwIO.py; fi
  FILE=/etc/systemd/system/kbwio.service
  if [ ! -f $FILE ]; then
    echo '[Unit]
Description=kbwio
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot
ExecStart=/home/kbwiot/KbwIO.py

[Install]
WantedBy=default.target
'>$FILE
  fi
  systemctl enable kbwio.service
  systemctl start kbwio.service
  systemctl status kbwio.service
else
  echo 'KbwIO.py fehlt'
fi