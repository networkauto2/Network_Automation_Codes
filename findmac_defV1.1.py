from netmiko import ConnectHandler
import socket
import re
import time
import logging
import os
import re
from paramiko.ssh_exception import SSHException
from datetime import datetime


now = datetime.now().strftime("%m-%d %H-%M")
start_time = time.perf_counter()

logging.basicConfig(
    filename=f'logs/run_findmac_{now}.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

switch_list = []

def ch(switch_ip, TARGET_MAC, VLAN):
    def check_port(switch_ip, port=None):
        """Returns True if the specific port is open."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            return s.connect_ex((switch_ip, port)) == 0
    global switch
    switch = {
    'host': switch_ip,
    'username': 'noc',
    'password': 'N)c#6^2',
    'secret': 'N)c#6^2',
    'session_log': f'logs/temp_session.log'}
    if check_port(switch["host"], 23):
        switch["device_type"] = "cisco_ios_telnet"
        switch["port"] = 23
        logging.info(f"Connecting to {switch["host"]} by telnet successed")
    elif check_port(switch["host"], 22):
        switch["device_type"] = "cisco_ios"
        switch["port"] = 22
        logging.info(f"Connecting to {switch["host"]} by ssh successed")
    with ConnectHandler(**switch) as connection:
        print(f"🔗 Connecting to switch {switch['host']}")
        connection.enable()
        switch_list.append(switch["host"])
        global mode, hostname, output, interface_name
        hostname = connection.find_prompt().strip("#")
        output = connection.send_command(f'show mac address-table | i {TARGET_MAC}')
        interface_match = re.search(r"(Et\w*\d+[\/\d+]*|Gi\w*\d+[\/\d+]*|Fa\w*\d+[\/\d+]*|Te\w*\d+[\/\d+]*|Po\w*\d+)",output)
        interface_name = interface_match.group(1)
        check_cascde = connection.send_command(f"sh run interface {interface_name}")
        match = re.search(r"switchport mode\s+(access|trunk)", check_cascde)
        mode = match.group(1)
        if mode == "access":
            print(f"⇄ The mode is access at {switch['host']}")
            print(f"{hostname}# show run interface {interface_name}")
            print(f'{connection.send_command(f'sh run int {interface_name}')}')
            change = input('change port (y/n)?: ')
            # Req = input("Enter Requster(a/e)?")
            if change == "y":
                full_config_block = [f"interface {interface_name}"] + CLI
                config_output = connection.send_config_set(full_config_block)
                print("\n--- Configuration Output ---")
                print(config_output)
                print(connection.save_config())
            elif change == "n":
                pass
            print(f"The host connected at {switch['host']} and the port is {interface_name}")
            print(f'The path is {switch_list}')
            print('=' * 120)
            print('The ticket is:')
            print(f'''Configure access port on switch: "{hostname}/{switch_list[-1]}"

Interface: {interface_name}
VLAN: {VLAN}''')
            connection.disconnect()

        elif mode == "trunk":
            print(f"-->The mode is trunk at {switch['host']}")
            sh_vlan = connection.send_command(f'sh vlan id  {VLAN}')
            ch_vlan = re.search(r"(not found)", sh_vlan)
            if ch_vlan and ch_vlan.group(0) == 'not found':
                print(f"❌ VLAN id {VLAN} not found in current VLAN database at {switch['host']}")
            else:
                print(f"✅ VLAN {VLAN} is exist at {switch['host']}")
            print('-' * 75)
            ch_po = re.search(r"(Po)(\d+)", interface_name)
            if ch_po and ch_po.group(1).startswith("Po"):
                po_sum = connection.send_command(f"show etherchannel {ch_po.group(2)} summary")
                int_in_po = re.findall(r"((?:Eth|Et|Gi|Fa|Te)\d+(?:/\d+)*)\s*\(P\)", po_sum)
                trunk1 = connection.send_command(f"sh cd ne {int_in_po[0]} det")
            else:
                trunk1 = connection.send_command(f"sh cd ne {interface_name} det")
            ftrunkip = re.search(r"(?:IP address|IPv4 Address):\s*([\d\.]+)",trunk1)
            switch["host"] = ftrunkip.group(1)

switch_ip = input('Enter the switch ip: ')        
TARGET_MAC  = input('The MAC is: ')
VLAN = input('Enter VlAN: ')
    
CLI =[
    "switchport host",
    f"switchport access vlan {VLAN}"
    ]
ch(switch_ip, TARGET_MAC, VLAN)            
       
while True:
    if mode == "access":
        break
    elif mode == "trunk":
        ch(switch["host"],TARGET_MAC,VLAN)
        continue

import datetime
now = datetime.datetime.now().strftime("%I:%M %p")
print(f'''
SEE Action:
- Task done.
- We confirm with CAC.


Status:
-Done@{now}

Best Regards,
Maged Sayed
.........................
Requester: Eng. Ahmed abo Zied
TB1 Network Operation Support Engineer
      ''')
# if Req == "a" else "Emad"