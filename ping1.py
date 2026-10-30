# import os
# # google_dns = '8.8.8.8'
# # result = os.system(f"ping {google_dns}")
# # print(result)

# with open("SWs.txt", "r") as file:
#     for line in file:
#         IP = line.strip()
#         ping = os.system(f"ping {IP}")
#         # if (f"Reply from") in ping:
#         #     print(f"{IP} is up")
#         # else:
#         #     print(f"{IP} is down")

import platform
import subprocess
open(r"task\ping result.txt", "w").close()
open(r"task\pingoffline_switches.txt", "w").close()
def ping_ip(ip_address):
    """Pings an IP address. Returns True if active, False otherwise."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip_address]

    try:
        # Timeout prevents the script from hanging forever on dead IPs
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
        return result.returncode == 0
    except Exception:
        return False

with open(r"task\SW_IPs.txt", "r", encoding="utf-8") as file:
    for line in file:
        ip = line.strip()
        with open(r"task\ping result.txt", "a") as res:
            if ping_ip(ip):
                res.write(f"[ ONLINE ] {ip}\n")
            else:
                res.write(f"[ OFFLINE] {ip}\n")
                with open(r"task\pingoffline_switches.txt", "a") as fail:
                    fail.write(f"{ip}\n")
