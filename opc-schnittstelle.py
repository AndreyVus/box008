import xmltodict


with (open("opc.xml", encoding = 'utf8') as f):
	d = xmltodict.parse(f.read())
l = d['UANodeSet']['UAVariable']
for l1 in l:
	if l1['@DataType'] in ['REAL', 'DINT', 'LDT']:
		name1 = l1['DisplayName']#[4:]
		id1 = l1['@NodeId'].split('=')[-1]
		print(f'"{name1}": {id1},')