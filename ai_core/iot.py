from scapy.all import ARP, Ether, srp
import socket
import threading

class IoTSensor:
    def __init__(self):
        self.local_ip = self._get_local_ip()
        self.devices = []

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def scan_network(self):
        """
        Scans the local subnet for devices using ARP.
        Returns a list of (IP, MAC) tuples.
        """
        print(f"[IoT] Scanning network from {self.local_ip}...")
        try:
            # Assume /24 subnet
            target_ip = ".".join(self.local_ip.split(".")[:3]) + ".1/24"

            # Create ARP request
            arp = ARP(pdst=target_ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            # Send (Timeout 2s)
            result = srp(packet, timeout=2, verbose=0)[0]

            devices = []
            for sent, received in result:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})

            self.devices = devices
            print(f"[IoT] Found {len(devices)} devices nearby.")
            return devices
        except Exception as e: # Permission error usually
            print(f"[IoT] Scan limited (Permission Denied?): {e}")
            return []

if __name__ == "__main__":
    iot = IoTSensor()
    print(iot.scan_network())
