from netmiko import ConnectHandler
import socket
import re
import time
import logging
import os

start_time = time.perf_counter()

logging.basicConfig(
    filename=r'SW_Backup\logbackup.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

total_sum = 0
def check_port(switch_ip, port):
    """Returns True if the specific port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex((switch_ip, port)) == 0
    
with open(r'Switches_IP.txt', 'r') as ips:
    switch_list = [line.strip() for line in ips if line.strip()]

for switch_ip in switch_list:
    switch = {
        'host': switch_ip,
        'username': 'noc',
        'password': 'N)c#6^2',
        'secret': 'N)c#6^2',
        'session_log': 'temp_session.log'
        }
    if check_port(switch_ip, 23):
        switch["device_type"] = "cisco_ios_telnet"
        switch["port"] = 23
        logging.info(f"Connecting to {switch_ip} by telnet successed")
    elif check_port(switch_ip, 22):
        switch["device_type"] = "cisco_ios"
        switch["port"] = 22
        logging.info(f"Connecting to {switch_ip} by ssh successed")
    else:
        print("No port open")
        continue

    try:
        with ConnectHandler(**switch) as connection:
            connection.enable()
            print(f"Connecting to switch {switch['host']}")
            hostname = connection.find_prompt().strip("#")
            sh_version = connection.send_command('sh version')
            pattern3560 = re.search(r'Model number.+(C3560.+)', sh_version)
            pattern3850 = re.search(r'Model Number.+(C3850.+)', sh_version)
            pattern9300 = re.search(r'Model Number.+(C9300.+)', sh_version)
            sw_version = pattern.group(1)
            if sw_version:
                sw_ip = print(f"Connecting to switch {switch['host']}")
                print(sw_version)
                open(r'sw_versions.txt', 'w').close()
                with open(r"sw_versions.txt", "a") as file:
                    file.write(switch_ip + "\n")
                    file.write(sw_version + "\n")
                    file.write("---------------------------\n")
                    file.write("---------------------------\n")
    except Exception as e:
        logging.error(f"Connection failed to {switch_ip}: {e}")
print(total_sum)