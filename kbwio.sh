#!/bin/bash
echo "[Unit]
Description=kbwio
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot
ExecStart=/home/kbwiot/KbwIO.py

[Install]
WantedBy=default.target
">kbwio.service
mv kbwio.service /etc/systemd/system/
systemctl enable kbwio.service
systemctl start kbwio.service
systemctl status kbwio.service