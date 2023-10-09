#!/usr/bin/python

from os.path import isfile
import requests
import subprocess
import syslog
import sqlite3
import time


settings = {
    "SW Versionen": "01.01",
    "Seriennummer": "008",
    "token": "http://thingsboard.kbw-cloud.de/api/v1/box008/telemetry",
    "wifi": {
        "FB-Gast": "Fierthbauer930807!",
        "GastTest": "sch1ll3r",
        "KBWIIOT": "Kbwiot2022!",
        "Schi01": "sch1ll3r",
        "matrixSCI": "dirkjuliasch1ll3r",
        "NETFMB": "7M8b1ck73",
        "Besucher": "Willkommen!"
    }
}


# tasks = {
"""
from os.path import isfile
import paho.mqtt.publish as publish
import psutil
import requests
import subprocess

wv = "/etc/wvdial.conf"
pingVPN = "http://10.8.0.1:8055"

def req_get(r, t=5):
        try:
            return 200 == requests.get(r, timeout=t).status_code
        except:
            return False

if req_get(pingVPN):
    publish.single("LED_VPN", 1, hostname="localhost")
    vpn_addr = psutil.net_if_addrs().get('tun0', [''])[0].address
    if isfile(wv):
        subprocess.run(
            "if ping 1.1.1.1 -c 1 -W 5 -I wlan0 || ping 1.1.1.1 -c 1 -W 5 -I eth0 || ping 1.1.1.1 -c 1 -W 5 -I eth1; then systemctl stop wvdial; fi",
            shell=True, stdout=subprocess.DEVNULL
        )
else:
    publish.single("LED_VPN", 0, hostname="localhost")
    vpn_addr = ''
    if isfile(wv):
        subprocess.run("systemctl restart wvdial", shell=True, stdout=subprocess.DEVNULL)

with open("/proc/stat", "r") as f:
    for line in f:
        if line.startswith("cpu "):
            values = line.split()
            print({"IP VPN": vpn_addr,
"WLAN LTE Status": subprocess.check_output(["iwgetid", "-r"]).decode().strip(),
"Free RAM, b": psutil.virtual_memory().free,
"Free Disk, b": psutil.disk_usage(".").free,
"CPU Temperatur, °C": subprocess.check_output(["vcgencmd", "measure_temp"]).decode()[5:-3],
"CPU Usage, %": round((int(values[1]) + int(values[3])) * 100 / (int(values[1]) + int(values[3]) + int(values[4])), 1)})
            break
"""

# "OPC":
"""
opcuaClient = "opc.tcp://10.49.150.123:4840"
node = {
  "Tanktemp": "ns=4;i=2",
  "Tankniveau": "ns=4;i=3",
  "Volumenstrom": "ns=4;i=4",
  "Systemdruck_ok": "ns=4;i=5",
}
import opcua
names = list(node.keys())
client = opcua.Client(opcuaClient)
client.session_timeout = 6000
client.connect()
vals = [client.get_node(val).get_value() for val in node.values()]
client.disconnect()
print(dict(zip(names, vals))) # dies muss man prüfen
"""


# init WLAN #################################
def wlan_init(settings):
    for ssid, passw in settings['wifi'].items():
        # wenn Box keine ssid.nmconnection hat, der in settings.ini gibt,
        if not isfile(f"/etc/NetworkManager/system-connections/{ssid}.nmconnection"):
            # dann schreiben
            subprocess.run(['nmcli', 'con', 'add', 'ifname', 'wlan0', 'con-name', f'{ssid}', 'type', 'wifi',
                            'ssid', f'{ssid}', 'ipv4.route-metric', '150', 'wifi-sec.key-mgmt', 'wpa-psk',
                            'wifi-sec.psk', f'{passw}'])


if __name__ == '__main__':
    wlan_init(settings) # netze und Kennworts
    while True:
        # get joblist from db
        with sqlite3.connect('db.sqlite3') as conn:
            c = conn.cursor()
            c.execute('SELECT id, Name, Periode, start, skript FROM home_home1Item WHERE Berechtigen = 1;')
            joblist = {
                Nr: {'Name': Name, 'Periode': Periode, 'start': start, 'skript': skript}
                for (Nr, Name, Periode, start, skript) in c.fetchall()
            }
        # print(joblist)
        if joblist:
            # Zyklus 1 Minute
            endTime = time.time() + 60
            while time.time() < endTime:
                for job in joblist.values():
                    if job['start'] <= time.time():
                        # nächste Startzeit
                        job['start'] = time.time() + job['Periode']
                        try:
                            data = subprocess.check_output(['python', '-c', job['skript']]).decode().strip()
                        except Exception as e:
                            syslog.syslog(syslog.LOG_WARNING, f"tasks.py: {job['Name']}, {e}")
                            data = {job['Name']: 'error'}
                        # send json to ThingsBoard
                        response = requests.post(settings['token'], data=data, timeout=5)
                        if response.status_code != 200:
                            syslog.syslog(syslog.LOG_WARNING, f"tasks.py: Error sending telemetry {response.status_code}")
                # positive pause bis nächstes job
                time.sleep(max(0, min([job['start'] for job in joblist.values()]) - time.time()))
            # save start Werte
            with sqlite3.connect('db.sqlite3') as conn:
                c = conn.cursor()
                for Nr, values in joblist.items():
                    c.execute(
                        'UPDATE home_home1Item SET start=? WHERE id=?;',
                        (values['start'], Nr)
                    )
        else:
            time.sleep(60)