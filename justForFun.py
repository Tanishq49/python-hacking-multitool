import pywifi
from pywifi import const
import time
from colorama import Fore,Style,init
import subprocess
import configparser
from pathlib import Path
import re

#Autoresetting the coloring of the colorama
init(autoreset=True)

#Starting of the function areas

def get_clients_by_bssid(interface='wlan0', target_bssid='AA:BB:CC:DD:EE:FF'):
    try:
        result = subprocess.run(
            ['iw', 'dev', interface, 'station', 'dump'],
            capture_output=True,
            text=True,
            check=True
        )
        stations = result.stdout.strip().split('\n\n')  # Each client block is separated by a blank line

        matched_clients = 0

        for block in stations:
            # Check for BSSID reference (if visible)
            if f"connected to {target_bssid.lower()}" in block.lower():
                matched_clients += 1
            elif re.search(r'Station ([0-9a-f:]{17})', block, re.IGNORECASE):
                # If no direct BSSID, you can still count all clients if you're hosting that BSSID
                matched_clients += 1  # All are your clients if you're the AP

        return matched_clients

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return -1

#frecuency to channel converter
def frequency_to_channel(freq):
    if freq == 2484:
        return 14
    elif 2412 <= freq <= 2472:
        return (freq - 2407) // 5
    elif 5170 <= freq <= 5825:
        return (freq - 5000) // 5
    else:
        return "Unknown"

def scan_networks():
    print(f"{Fore.GREEN}Scanning the network..")
    configureWifi = pywifi.PyWiFi()
    wifi = configureWifi.interfaces()[0]
    wifi.scan()
    time.sleep(5)
    result = wifi.scan_results()
    for network in result:
        freq = network.freq
        channel = frequency_to_channel(freq)
        print(f"{Fore.BLUE}ssid: {network.ssid} {Fore.YELLOW}bssid: {network.bssid} {Fore.CYAN}channel: {channel} {Fore.MAGENTA}signal: {network.signal}")
  
def get_current_ssid():
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"], encoding='utf-8').strip()
        return ssid
    except subprocess.CalledProcessError:
        return None

def get_wifi_password(ssid):
    connections_path = Path("/etc/NetworkManager/system-connections/")
    if not connections_path.exists():
        print("Connections path not found.")
        return None

    for file in connections_path.glob("*"):
        try:
            config = configparser.ConfigParser()
            config.read(file)
            if 'wifi' in config and config['wifi'].get('ssid') == ssid:
                password = config.get('wifi-security', 'psk', fallback=None)
                return password
        except Exception as e:
            continue  # skip files that can't be parsed

    return None

def pass_current():
    ssid = get_current_ssid()
    if not ssid:
        print("Not connected to any Wi-Fi network.")
        return

    print(f"Connected SSID: {ssid}")
    password = get_wifi_password(ssid)
    if password:
        print(f"Password: {password}")
    else:
        print("Password not found or permission denied (try running with sudo).")

#End of the function area  
      
helpText = f""" 
{Fore.GREEN}Commands:{Style.RESET_ALL}
[1]Scan Networks        [2]Current connected network password
[3]Connected Clients to the network
"""
print(helpText)

commandNumber = input("Enter the number of the command:")
print("\n")

if commandNumber == "1":
    scan_networks()
elif commandNumber == "2":
    pass_current()
elif commandNumber == "3":
    bssid = input("Enter the bssid of the network:")
    clients = get_clients_by_bssid(interface='wlan0', target_bssid=bssid)
    print(f"Number of clients connected to {bssid}: {clients}")

print("\nThanks for using the programm and this was made by Trifalic Hacker")