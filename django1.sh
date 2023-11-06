#!/bin/bash
echo '[Unit]
Description=Django App
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot/django1
ExecStart=/bin/bash -c "source venv/bin/activate && ./manage.py runserver 0:8000"

[Install]
WantedBy=multi-user.target
'>/etc/systemd/system/django1.service
systemctl enable django1.service
systemctl start django1.service
systemctl status django1.service

echo '[Unit]
Description=Django task
After=network.target
Requires=django1.service

[Service]
Type=simple
WorkingDirectory=/home/kbwiot/django1
ExecStart=python tasks.py
RestartSec = 15
Restart = on-failure

[Install]
WantedBy=multi-user.target
'>/etc/systemd/system/tasks.service
systemctl enable tasks.service
systemctl start tasks.service
systemctl status tasks.service