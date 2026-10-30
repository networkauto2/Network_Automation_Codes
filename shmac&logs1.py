from netmiko import ConnectHandler
import socket
import re
import time
import logging
import os
MAC = input("Please enter MAC address: ")
def check_port(switch_ip, port):
    """Returns True if the specific port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex((switch_ip, port)) == 0
    
with open(r'task\SW_IPs.txt', 'r') as ips:
    switch_list = [line.strip() for line in ips if line.strip()]

for switch_ip in switch_list:
    switch = {
        'host': switch_ip,
        'username': 'noc',
        'password': 'N)c#6^2',
        'secret': 'N)c#6^2',
        }
    if check_port(switch_ip, 23):
        switch["device_type"] = "cisco_ios_telnet"
        switch["port"] = 23
    elif check_port(switch_ip, 22):
        switch["device_type"] = "cisco_ios"
        switch["port"] = 22
    else:
        print("No port open")
        continue
    
    try:
        with ConnectHandler(**switch) as ssh:
            print(f"Connecting to switch {switch['host']}")
            ssh.enable()
            hostname = ssh.find_prompt().strip("#")#.strip(">")
            sh_mac = ssh.send_command(f"show mac address-table | i {MAC}")
            sh_log = ssh.send_command(f"show logg | i {MAC}")
            print(f'{switch["host"]} {sh_mac}')
            print(f'{switch["host"]} {sh_log}')

    except Exception as e:
        print(f"Connection failed to {switch_ip}: {e}")


