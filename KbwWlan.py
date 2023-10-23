#!/bin/python
import cryptocode
import re
import subprocess
import syslog
import yaml


def decode(passw):
    if len(passw) > 20:
        passw = cryptocode.decrypt(passw, 'Kbwiot2022!')
    return passw


def nmcli_c():
    return subprocess.check_output("nmcli c | awk '/wifi/ {print $1}'", shell=True).decode().split()


def nmcli_add(ssid, passw):
    subprocess.run(['nmcli', 'con', 'add', 'ifname', 'wlan0', 'con-name', f'{ssid}', 'type', 'wifi',
                             'ssid', f'{ssid}', 'ipv4.route-metric', '150', 'wifi-sec.key-mgmt', 'wpa-psk',
                             'wifi-sec.psk', f'{passw}'])


def nmcli_del(datei):
    subprocess.run(['nmcli', 'connection', 'delete', datei])


def hat(datei, ssid, passw):
    pat = re.compile(f"(ssid={ssid}$).+(psk={passw}$)", re.M+re.S)
    try:
        with open(f"/etc/NetworkManager/system-connections/{datei}.nmconnection") as file:
            return pat.findall(file.read())
    except:
        return []


if __name__ == '__main__':
    try:
        with open("/home/kbwiot/settings.yaml") as file:
            wifi = yaml.safe_load(file)['wifi']
        for datei in set(nmcli_c()).difference(set(wifi.keys())):
            nmcli_del(datei)
        for datei in nmcli_c():
            flag = True
            for ssid, passw in wifi.items():
                if hat(datei, ssid, decode(passw)):
                    flag = False
                    break
            if flag:
                nmcli_del(datei)
        for ssid in set(wifi.keys()).difference(set(nmcli_c())):
            nmcli_add(ssid, decode(wifi[ssid]))
    except Exception as e:
        syslog.syslog(syslog.LOG_WARNING, f"KbwWlan.py: {e}")