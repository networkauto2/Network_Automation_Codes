import os
import time
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import socket
import re
import time
import logging

# ==================== CONFIGURATION ====================
TEXT_FILE_PATH = r'task\SW_IPs.txt'

# Shared credentials for all switches
SSH_USER = "noc"           # Replace with your username
SSH_PASS = "N)c#6^2"     # Replace with your password
DEVICE_TYPE = "cisco_ios"    # Use 'cisco_xe' if running IOS-XE
MAC = input("Please enter MAC address: ")


# Global flag to signal background threads to exit
STOP_STREAM = False
# =======================================================

def load_ips_from_file(file_path):
    """Reads IP addresses from a text file, skipping empty lines and comments."""
    ip_list = []
    if not os.path.exists(file_path):
        print(f"[X] Error: The file '{file_path}' was not found.")
        return ip_list

    with open(file_path, "r") as file:
        for line in file:
            clean_line = line.strip()
            # Skip empty lines and lines starting with '#'
            if clean_line and not clean_line.startswith("#"):
                ip_list.append(clean_line)
    return ip_list

def check_port(ip_address, port):
    """Returns True if the specific port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex((ip_address, port)) == 0

def monitor_switch(ip_address):
    """Worker function handled by each thread for a specific switch."""
    global STOP_STREAM
    
    # Construct the device dictionary dynamically for Netmiko

    device_info = {
        'host': ip_address,
        'username': SSH_USER,
        'password': SSH_PASS,
    }
    if check_port(ip_address, 23):
        device_info["device_type"] = "cisco_ios_telnet"
        device_info["port"] = 23
    elif check_port(ip_address, 22):
        device_info["device_type"] = "cisco_ios"
        device_info["port"] = 22
    
    ssh = None
    try:
        print(f"[*] [{ip_address}] Connecting...")
        ssh = ConnectHandler(**device_info)
        
        print(f"[*] [{ip_address}] Enabling Terminal Monitor...")
        ssh.send_command("terminal monitor", expect_string=r"#")
        hostname = ssh.find_prompt().strip("#")#.strip(">")
        sh_mac = ssh.send_command(f"show mac address-table | i {MAC}")
        sh_log = ssh.send_command(f"show logg | i {MAC}")
        print(f'{device_info["host"]} {hostname} {sh_mac} at ')
        print(sh_log)
        
        time.sleep(1)
        ssh.clear_buffer()
        print(f"[+] [{ip_address}] Successfully streaming live logs...")

        line_buffer = ""

        # Loop until global STOP_STREAM variable becomes True
        while not STOP_STREAM:
            output = ssh.read_channel()
            if output:
                line_buffer += output
                # Process complete lines that end with a newline character
                if "\n" in line_buffer:
                    lines = line_buffer.split("\n")
                    # If the last element isn't terminated by \n, keep it in buffer
                    line_buffer = lines.pop()
                    
                    for line in lines:
                        clean_line = line.strip("\r\n")
                        if clean_line:
                            print(f"[{ip_address}] {clean_line}", flush=True)
                            
            time.sleep(0.2)

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(f"[X] [{ip_address}] Connection Error: {error}")
    except Exception as e:
        print(f"[X] [{ip_address}] Unexpected Error: {e}")
    finally:
        if ssh:
            print(f"[*] [{ip_address}] Disabling Terminal Monitor & Disconnecting...")
            try:
                ssh.send_command("terminal no monitor", expect_string=r"#")
                ssh.disconnect()
            except Exception:
                pass 
            print(f"[-] [{ip_address}] Disconnected cleanly.")

def main():
    global STOP_STREAM
    
    # Load IPs from the text file
    switch_ips = load_ips_from_file(TEXT_FILE_PATH)
    
    if not switch_ips:
        print("[X] No valid IP addresses found in the text file. Exiting.")
        return

    print(f"[*] Found {len(switch_ips)} switches in '{TEXT_FILE_PATH}'. Starting simultaneous connections...")
    
    # Max_workers matches the total number of IPs pulled from the file
    with ThreadPoolExecutor(max_workers=len(switch_ips)) as executor:
        # Submit all tasks to the background thread pool using the IP list
        futures = [executor.submit(monitor_switch, ip) for ip in switch_ips]
        
        try:
            # Keep main thread alive while threads run background monitoring
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[!] Ctrl+C detected. Signalling background threads to stop...")
            STOP_STREAM = True
            
    print("[*] All threads finished executing. Execution complete.")

if __name__ == "__main__":
    main()
