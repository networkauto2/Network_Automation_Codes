from netmiko import ConnectHandler
import socket
import re
import time
import logging
import os

start_time = time.perf_counter()

# logging.basicConfig(
#     filename=r'task\logbackup.log', 
#     level=logging.INFO, 
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


def check_port(switch_ip, port):
    """Returns True if the specific port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        return s.connect_ex((switch_ip, port)) == 0


with open(r'task\AllSW_IPs.txt', 'r') as ips:
    switch_list = [line.strip() for line in ips if line.strip()]

for switch_ip in switch_list:
    switch = {
        'host': switch_ip,
        'username': 'noc',
        'password': 'N)c#6^2',
        'secret': 'N)c#6^2',
        'session_log': r'SW_Backup\temp_session.log'
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
    
    s_ip = ".".join(switch_ip.split('.')[-2:])    
    try:
        with ConnectHandler(**switch) as connection:
            print(f"Connecting to {switch['host']}")
            connection.enable()
            #safe_hostname = re.sub(r'[^a-zA-Z0-9_\-]', '_', hostname)
            #log_filename = f'logs\{safe_hostname}_{s_ip}.txt'
            # log_filename = f'{switch_ip}.txt'
            hostname = connection.find_prompt().strip("#")#.strip(">")
            runconf = connection.send_command('sh run')
            with open(rf'task\Backup\{s_ip} {hostname}.txt', 'a') as bfile:
                bfile.write(runconf)
                bfile.close()
            connection.disconnect()
    
    except Exception as e:
        logging.error(f"Connection failed to {switch_ip}: {e}")

logging.info("Script execution finished.")
end_time = time.perf_counter()
print(f"Task done & the execution time is: {end_time - start_time:.4f} seconds")
logging.info(f"Task done & the execution time is: {end_time - start_time:.4f} seconds")
