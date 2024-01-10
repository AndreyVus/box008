wifi = {
	'Besucher' : 'Willkommen!',
	'FB-Gast'  : 'qsj5eKuabwPuggKj24s0dNMN*UtlbgjgXG5075v0sskZvjA==*FF/odSuopI35zUQEG+kjzg==*d6IzKVchaHY9xcpferDt2A==',
	'GastTest' : 'FjQUFOijPB4=*G6ktgEkXqWboPlDL84vaAw==*QgyI5do8kED4Magjo4aeBg==*LbKgdhhmUF59D8zMUDpP0A==',
	'KBWIIOT'  : 'US9P9PbmMKuibE8=*T/BNGi06TVcyMCRP4pSrHQ==*2KFeDMbJKHCHOOy+r72jRw==*gEjVsLx5AxmdsliFkdLP5A==',
	'Schi01'   : 'FjQUFOijPB4=*G6ktgEkXqWboPlDL84vaAw==*QgyI5do8kED4Magjo4aeBg==*LbKgdhhmUF59D8zMUDpP0A==',
	'matrixSCI': 'mE3nG0o+V7feCyAxDxqVgjQ=*jummKSJRpzClAblFqzjhKA==*H3mj1PZBjvawqwSt2AlgXQ==*RUWfuHFYSh9xMj7xaJZtrg==',
}
from time import sleep
import cryptocode
import re
import subprocess
import sys
import syslog
Periode = int(sys.argv[1])
def decode(passw):
	if len(passw) > 20:
		passw = cryptocode.decrypt(passw, 'Kbwiot2022!')
	return passw
def nmcli_c():
	return subprocess.check_output("nmcli c | awk '/wifi/ {print $1}'", shell=True).decode().split()
def nmcli_add(ssid, passw):
	subprocess.run(['nmcli', 'con', 'add', 'ifname', 'wlan0', 'con-name', ssid, 'type', 'wifi', 'ssid', ssid,
			'ipv4.route-metric', '150', 'wifi-sec.key-mgmt', 'wpa-psk', 'wifi-sec.psk', passw])
def nmcli_del(datei):
	subprocess.run(['nmcli', 'connection', 'delete', datei])
def hat(datei, ssid, passw):
	pat = re.compile(f'(ssid={ssid}$).+(psk={passw}$)', re.M+re.S)
	try:
		with open(f'/etc/NetworkManager/system-connections/{datei}.nmconnection') as file:
			return pat.findall(file.read())
	except:
		return []
while 1:
	#with lock:
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
	sleep(Periode)