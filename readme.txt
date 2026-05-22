LAN Device Monitoring System
Mini Project
Project Title
LAN Device Monitoring System using Python and SQLite

LAN Device Monitoring System
Professional Project Documentation

1. Introduction
The LAN Device Monitoring System is a Python-based network monitoring application developed to identify and track all devices connected to the same Local Area Network (LAN).
The system continuously scans the network and collects:
Device Name
IP Address
MAC Address
The collected information is stored inside a SQLite database. The database updates automatically whenever:
A new device joins the network
A device disconnects from the network
A device's IP address changes
This project demonstrates concepts of:
Computer Networking
ARP Protocol
Python Programming
Database Management
Real-Time Monitoring

2. Objective
The main objective of this project is:
To monitor devices connected to a LAN network
To automatically detect network changes
To maintain updated records of connected devices
To store device information using SQLite database

3. Technologies Used
Technology
Purpose
Python
Main programming language
Scapy
Network scanning and ARP requests
SQLite3
Database storage
Socket Programming
Device hostname detection
VS Code
Development environment


4. Python Libraries Used
from scapy.all import ARP, Ether, srp
import socket
import sqlite3
import time
from datetime import datetime


5. System Requirements
Hardware Requirements
Laptop/Desktop
WiFi or LAN connection
Minimum 4GB RAM
Software Requirements
Python 3.x
VS Code / PyCharm
Windows/Linux/macOS

6. Working Principle
The project works using ARP (Address Resolution Protocol).
Steps:
The program sends ARP broadcast packets to all devices in the LAN.
Devices connected to the network respond with:
MAC Address
IP Address
The system resolves hostnames using socket programming.
Device information is stored in SQLite database.
The network is rescanned continuously.
Any change in network devices updates the database automatically.

7. Database Design
Database Name
network_devices.db

Table Name
devices

Table Structure
Column Name
Data Type
Description
mac_address
TEXT
Primary Key
device_name
TEXT
Device hostname
ip_address
TEXT
Current IP address
status
TEXT
Connected/Disconnected
last_seen
TEXT
Timestamp


8. SQL Queries Used
Create Table
CREATE TABLE IF NOT EXISTS devices (
    mac_address TEXT PRIMARY KEY,
    device_name TEXT,
    ip_address TEXT,
    status TEXT,
    last_seen TEXT
)

Insert Device
INSERT INTO devices
(device_name, ip_address, mac_address, status, last_seen)
VALUES (?, ?, ?, ?, ?)

Update Device
UPDATE devices
SET device_name=?, ip_address=?, status=?, last_seen=?
WHERE mac_address=?

Mark Disconnected Device
UPDATE devices
SET status='Disconnected'
WHERE mac_address=?


9. Full Python Code
from scapy.all import ARP, Ether, srp
import socket
import sqlite3
import time
from datetime import datetime

# DATABASE CONNECTION
conn = sqlite3.connect("network_devices.db")
cursor = conn.cursor()

# CREATE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS devices (
    mac_address TEXT PRIMARY KEY,
    device_name TEXT,
    ip_address TEXT,
    status TEXT,
    last_seen TEXT
)
""")

conn.commit()

# SCAN NETWORK

def scan_network(ip_range):

    arp = ARP(pdst=ip_range)

    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether / arp

    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []

    for sent, received in result:

        ip = received.psrc
        mac = received.hwsrc

        try:
            hostname = socket.gethostbyaddr(ip)[0]

        except:
            hostname = socket.getfqdn(ip)

        if hostname == ip:
            hostname = "Unknown"

        devices.append({
            "device_name": hostname,
            "ip_address": ip,
            "mac_address": mac
        })

    return devices

# UPDATE DATABASE

def update_database(devices):

    current_macs = []

    for device in devices:

        name = device["device_name"]
        ip = device["ip_address"]
        mac = device["mac_address"]

        current_macs.append(mac)

        cursor.execute(
            "SELECT * FROM devices WHERE mac_address=?",
            (mac,)
        )

        existing = cursor.fetchone()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if existing:

            old_ip = existing[2]

            if old_ip != ip:
                print(f"[IP CHANGED] {mac}: {old_ip} -> {ip}")

            cursor.execute("""
            UPDATE devices
            SET device_name=?, ip_address=?, status=?, last_seen=?
            WHERE mac_address=?
            """, (
                name,
                ip,
                "Connected",
                current_time,
                mac
            ))

        else:

            print(f"[NEW DEVICE] {name} - {ip}")

            cursor.execute("""
            INSERT INTO devices
            (
                device_name,
                ip_address,
                mac_address,
                status,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                ip,
                mac,
                "Connected",
                current_time
            ))

    cursor.execute("SELECT mac_address FROM devices")

    all_macs = [row[0] for row in cursor.fetchall()]

    for mac in all_macs:

        if mac not in current_macs:

            print(f"[DISCONNECTED] {mac}")

            cursor.execute("""
            UPDATE devices
            SET status='Disconnected'
            WHERE mac_address=?
            """, (mac,))

    conn.commit()

# MAIN PROGRAM

if __name__ == "__main__":

    ip_range = "192.168.1.1/24"

    print("LAN Device Monitoring Started...\n")

    while True:

        print(f"\nScanning at: {datetime.now()}")

        try:

            devices = scan_network(ip_range)

            print(f"\nDevices Found: {len(devices)}\n")

            for d in devices:

                print(
                    f"Device Name : {d['device_name']}\n"
                    f"IP Address  : {d['ip_address']}\n"
                    f"MAC Address : {d['mac_address']}\n"
                )

            update_database(devices)

            time.sleep(5)

        except KeyboardInterrupt:

            print("\nProgram Stopped")

            conn.close()

            break

        except Exception as e:

            print("Error:", e)

            time.sleep(5)


10. Output
Example Output
LAN Device Monitoring Started...

Scanning at: 2026-05-22 18:59:41

Devices Found: 7

Device Name : Acer.hgu_lan
IP Address  : 192.168.1.38
MAC Address : A4:B1:C1:A1:6D:19

[NEW DEVICE] Unknown - 192.168.1.44
[DISCONNECTED] C0:51:7E:C6:D9:BB


11. Advantages
Lightweight and simple
Real-time monitoring
Automatic database updates
Easy deployment
No external database server required
Tracks devices using MAC addresses

12. Limitations
Only works inside same LAN network
Some devices may not expose hostnames
Requires administrator privileges for ARP scanning

13. Future Enhancements
GUI Dashboard
Email alerts
CSV Export
Device manufacturer identification
Web dashboard
Network usage monitoring

14. Conclusion
The LAN Device Monitoring System successfully detects and monitors all devices connected to a local network. The project demonstrates real-time device tracking using ARP scanning and SQLite database integration.
The system automatically updates whenever devices join, disconnect, or change IP addresses, making it useful for network monitoring and management applications.

15. Project Structure
LAN_Device_Monitor/
│
├── network_monitor.py
├── network_devices.db
└── README.md


17. Author
Sriram Jayaraj Bommannan

