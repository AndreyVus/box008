#!/bin/bash

# Digital Input (DI) GPIO pins
DI_PINS=(18 19 20 21 500 501 502 503)

# Digital Output (DO) GPIO pins
DO_PINS=(22 23 24 25 496 497 498 499)

# Export DI GPIO pins
for x in "${DI_PINS[@]}"; do
    if [ ! -e "/sys/class/gpio/gpio$x/value" ]; then
        echo $x > /sys/class/gpio/export
    fi
    echo "in" > "/sys/class/gpio/gpio$x/direction"
done

# Export DO GPIO pins
for x in "${DO_PINS[@]}"; do
    if [ ! -e "/sys/class/gpio/gpio$x/value" ]; then
        echo $x > /sys/class/gpio/export
    fi
    echo "out" > "/sys/class/gpio/gpio$x/direction"
done

# Set analog input sampling frequency
echo "15" > "/sys/bus/iio:device0/in_voltage_sampling_frequency"

chmod 777 -R /sys/devices/platform/leds/leds/* /sys/class/gpio/* /sys/bus/iio:device0/*

logger "Konfiguration LEDs, GPIO-Pins und Sampling-Frequenz abgeschlossen."