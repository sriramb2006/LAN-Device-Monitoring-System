from scapy.all import ARP, Ether, srp
import socket
import sqlite3
import time
from datetime import datetime

# ---------------- DATABASE CONNECTION ---------------- #

conn = sqlite3.connect("network_devices.db")
cursor = conn.cursor()

# ---------------- CREATE TABLE ---------------- #

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

# ---------------- NETWORK SCAN FUNCTION ---------------- #

def scan_network(ip_range):

    arp = ARP(pdst=ip_range)

    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether / arp

    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []

    for sent, received in result:

        ip = received.psrc
        mac = received.hwsrc

        # GET DEVICE NAME
        try:
            hostname = socket.gethostbyaddr(ip)[0]

        except:
            hostname = socket.getfqdn(ip)

        # IF NO VALID NAME FOUND
        if hostname == ip:
            hostname = "Unknown"

        devices.append({
            "device_name": hostname,
            "ip_address": ip,
            "mac_address": mac
        })

    return devices

# ---------------- DATABASE UPDATE FUNCTION ---------------- #

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

        # EXISTING DEVICE
        if existing:

            old_ip = existing[2]

            # CHECK IP CHANGE
            if old_ip != ip:

                print(f"[IP CHANGED] {mac}: {old_ip} -> {ip}")

            cursor.execute("""
            UPDATE devices
            SET device_name=?,
                ip_address=?,
                status=?,
                last_seen=?
            WHERE mac_address=?
            """, (
                name,
                ip,
                "Connected",
                current_time,
                mac
            ))

        # NEW DEVICE
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

    # CHECK DISCONNECTED DEVICES
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

# ---------------- MAIN PROGRAM ---------------- #

if __name__ == "__main__":

    # YOUR NETWORK RANGE
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

            # SCAN EVERY 5 SECONDS
            time.sleep(5)

        except KeyboardInterrupt:

            print("\nProgram Stopped")

            conn.close()

            break

        except Exception as e:

            print("Error:", e)

            time.sleep(5)