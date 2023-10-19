from os.path import isfile
import paho.mqtt.publish as publish
import psutil
import requests
import subprocess

wv = isfile("/etc/wvdial.conf")

def get_ssid():
    try:
        return subprocess.check_output(["iwgetid", "-r"]).decode().strip()
    except:
        return "no"

if 200 == requests.get("http://10.8.0.1:8055", timeout=5).status_code:
    publish.single("LED_VPN", 1, hostname="localhost")
    vpn_addr = psutil.net_if_addrs().get("tun0", [""])[0].address
    if wv:
        subprocess.run(
            "if ping 1.1.1.1 -c 1 -W 5 -I wlan0 || ping 1.1.1.1 -c 1 -W 5 -I eth0 || ping 1.1.1.1 -c 1 -W 5 -I eth1; then systemctl stop wvdial; fi",
            shell=True, stdout=subprocess.DEVNULL
        )
else:
    publish.single("LED_VPN", 0, hostname="localhost")
    vpn_addr = ""
    if wv:
        subprocess.run("systemctl restart wvdial", shell=True, stdout=subprocess.DEVNULL)

with open("/proc/stat", "r") as f:
    for line in f:
        if line.startswith("cpu "):
            values = line.split()
            print({"IP VPN": vpn_addr,
"WLAN LTE Status": get_ssid(),
"Free RAM, b": psutil.virtual_memory().free,
"Free Disk, b": psutil.disk_usage(".").free,
"CPU Temperatur, °C": subprocess.check_output(["vcgencmd", "measure_temp"]).decode()[5:-3],
"CPU Usage, %": round((int(values[1]) + int(values[3])) * 100 / (int(values[1]) + int(values[3]) + int(values[4])), 1)})
            break