#!/usr/bin/python

import os
import paho.mqtt.client as mqtt
import syslog
import time


def DI(x):
	with open(f'/sys/class/gpio/gpio{18 + x}/value') as f:
		ans = f.read(1) == '0'
	return ans


def DO(x, value):
	with open(f'/sys/class/gpio/gpio{22 + x}/value', 'w') as f:
		f.write(value)


def DIO(x, value):
	with open(f'/sys/class/gpio/gpio{496 + x}/value', 'w') as f:
		f.write(value)
	with open(f'/sys/class/gpio/gpio{500 + x}/value') as f:
		ans = f.read(1) == '0'
	return ans


def LED_RED(value):
	with open('/sys/devices/platform/leds/leds/LED1/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/LED1/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def LED_GREEN(value):
	with open('/sys/devices/platform/leds/leds/LED2/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/LED2/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def BEEP(value):
	with open('/sys/devices/platform/leds/leds/BUZZER/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/BUZZER/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def AI(x):
	with open(f'/sys/bus/iio/devices/iio:device0/in_voltage{x}_raw') as f:
		ans = f.readline()
	return float(ans) / 2816


def on_connect(client, userdata, flags, rc):
	client.subscribe('LED_VPN')


def on_message(client, userdata, message):
	LED_GREEN(f'{message.payload.decode()}')


try:
	# init io ##########################################
	for x in [18, 19, 20, 21, 500, 501, 502, 503]:  # DI
		if not os.path.exists(f'/sys/class/gpio/gpio{x}/value'):
			with open('/sys/class/gpio/export', 'w') as f:
				f.write(str(x))
		with open(f'/sys/class/gpio/gpio{x}/direction', 'w') as f:
			f.write('in')
	for x in [22, 23, 24, 25, 496, 497, 498, 499]:  # DO
		if not os.path.exists(f'/sys/class/gpio/gpio{x}/value'):
			with open('/sys/class/gpio/export', 'w') as f:
				f.write(str(x))
		with open(f'/sys/class/gpio/gpio{x}/direction', 'w') as f:
			f.write('out')
	# Skalierung #####################################
	# 28160 raw = 10V --> faktor = 1/2816
	with open('/sys/bus/iio/devices/iio:device0/in_voltage_sampling_frequency', 'w') as f:
		f.write('15')
	# mqtt-subscribe #################################
	mqttc = mqtt.Client()
	mqttc.on_connect = on_connect
	mqttc.on_message = on_message
	mqttc.connect_async('localhost')
	# puls blinker ###################################
	while True:
		mqttc.loop_start()
		LED_RED('1')
		time.sleep(0.2)
		LED_RED('0')
		time.sleep(1.8)
except Exception as e:
	syslog.syslog(syslog.LOG_WARNING, f'KbwIO: {type(e)}: e')