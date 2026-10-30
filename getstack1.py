from netmiko import ConnectHandler
import socket
import re
import time
import logging
import os

start_time = time.perf_counter()
# logging file
# logging.basicConfig(
#     filename=r'temp\logbackup.log', 
#     level=logging.INFO, 
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
def check_port(switch_ip, port):
    """Returns True if the specific port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex((switch_ip, port)) == 0
    
with open(r'task\SW_IPs.txt', 'r') as ips:
    switch_list = [line.strip() for line in ips if line.strip()]
unique_switches = set()

for switch_ip in switch_list:
    switch = {
        'host': switch_ip,
        'username': 'noc',
        'password': 'N)c#6^2',
        'secret': 'N)c#6^2',
        # 'session_log': r'temp\temp_session.log'
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
        with ConnectHandler(**switch) as connection:
            print(f"Connecting to switch {switch['host']}")
            connection.enable()
            hostname = connection.find_prompt().strip("#")#.strip(">")
            int_sta = connection.send_command("sh int status")
            match = re.findall(r"Gi(\d+)/", int_sta)
            unique_switches = set(match)
            connection.disconnect()
            print(unique_switches)
            total_switches = len(unique_switches)
            print(f"Total number of {switch_ip} / {hostname} switches: {total_switches}")

    except Exception as e:
        print(f"Connection failed to {switch_ip}: {e}")


