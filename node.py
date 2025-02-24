import socket
import threading
import time
import os
import bluetooth  # Requires `pybluez`—pip install pybluez
from fractal import fractal_hash, fractal_compress, pack_data, unpack_data, fractal_decompress

class FractalNode:
    def __init__(self, node_id, tcp_port=5000, bt_port=1):
        self.node_id = node_id
        self.tcp_port = tcp_port
        self.bt_port = bt_port
        self.data_store = {}  # hash: (packed_data, metadata)
        self.peers = set()    # TCP peers
        self.bt_peers = set() # Bluetooth peers
        self.running = True

    def start(self):
        """Start TCP and Bluetooth listeners."""
        threading.Thread(target=self.listen_tcp, daemon=True).start()
        threading.Thread(target=self.listen_bluetooth, daemon=True).start()
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def listen_tcp(self):
        """Listen for TCP packets."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.tcp_port))
            s.listen()
            while self.running:
                try:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(4096).decode()
                        if data:
                            self.process_packet(data, addr[0], conn)
                except:
                    pass

    def listen_bluetooth(self):
        """Listen for Bluetooth packets."""
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", self.bt_port))
        server_sock.listen(1)
        while self.running:
            try:
                conn, addr = server_sock.accept()
                data = conn.recv(4096).decode()
                if data:
                    self.process_packet(data, addr, conn)
                conn.close()
            except:
                pass
        server_sock.close()

    def discover_peers(self):
        """Discover TCP and Bluetooth peers."""
        local_ip = socket.gethostbyname(socket.gethostname())
        subnet = ".".join(local_ip.split(".")[:-1]) + "."
        while self.running:
            # TCP discovery
            for i in range(1, 255):
                ip = f"{subnet}{i}"
                if ip != local_ip:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.1)
                            if s.connect_ex((ip, self.tcp_port)) == 0:
                                self.peers.add(ip)
                    except:
                        pass
            # Bluetooth discovery
            nearby_devices = bluetooth.discover_devices(lookup_names=False)
            for addr in nearby_devices:
                try:
                    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    sock.settimeout(0.1)
                    sock.connect((addr, self.bt_port))
                    self.bt_peers.add(addr)
                    sock.close()
                except:
                    pass
            time.sleep(60)

    def process_packet(self, packet, sender, conn=None):
        """Handle incoming packets."""
        if packet == "HELP":
            if conn:
                conn.send("Commands: ADD <text> <metadata> | GET <hash> | LIST | STOP".encode())
            return
        if packet == "LIST":
            if conn:
                listing = "\n".join(f"{k}: {v[1]}" for k, v in self.data_store.items()) or "No data yet."
                conn.send(listing.encode())
            return
        parts = packet.split("#", 2)
        if len(parts) == 3:
            hash_id, packed_data, metadata = parts
            if hash_id not in self.data_store:
                self.data_store[hash_id] = (packed_data, metadata)
                self.share_packet(packet)

    def share_packet(self, packet):
        """Share with TCP and Bluetooth peers."""
        for peer_ip in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((peer_ip, self.tcp_port))
                    s.send(packet.encode())
            except:
                pass
        for bt_addr in self.bt_peers:
            try:
                sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                sock.settimeout(1)
                sock.connect((bt_addr, self.bt_port))
                sock.send(packet.encode())
                sock.close()
            except:
                pass

    def add_data(self, text, metadata=""):
        """Add and share data."""
        compressed = fractal_compress(text)
        packed = pack_data(compressed)
        hash_id = fractal_hash(text)
        packet = f"{hash_id}#{packed}#{metadata}"
        self.data_store[hash_id] = (packed, metadata)
        self.share_packet(packet)
        return hash_id

    def get_data(self, hash_id):
        """Retrieve data by hash."""
        if hash_id in self.data_store:
            packed, metadata = self.data_store[hash_id]
            compressed = unpack_data(packed)
            return fractal_decompress(compressed), metadata
        return None, None

    def stop(self):
        """Stop the node."""
        self.running = False
