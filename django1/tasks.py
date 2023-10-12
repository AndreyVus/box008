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