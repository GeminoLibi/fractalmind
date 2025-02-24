# node.py
import socket
import threading
import time
import bluetooth
from fractal import cogito_hash, pack_packet, unpack_packet, fractal_decompress

class FractalNode:
    def __init__(self, node_id, port=5000, bt_port=1):  # Changed tcp_port to port
        self.node_id = node_id
        self.port = port  # Unified to port
        self.bt_port = bt_port
        self.data_store = {}
        self.peers = set()
        self.bt_peers = set()
        self.running = True

    def start(self):
        threading.Thread(target=self.listen_tcp, daemon=True).start()
        # threading.Thread(target=self.listen_bluetooth, daemon=True).start()  # Commented out per your setup
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def listen_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.port))  # Updated to self.port
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

    # ... (rest of listen_bluetooth unchanged, commented out in your run)
    def discover_peers(self):
        local_ip = socket.gethostbyname(socket.gethostname())
        subnet = ".".join(local_ip.split(".")[:-1]) + "."
        while self.running:
            for i in range(1, 255):
                ip = f"{subnet}{i}"
                if ip != local_ip:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.1)
                            if s.connect_ex((ip, self.port)) == 0:  # Updated to self.port
                                self.peers.add(ip)
                    except:
                        pass
            # Bluetooth discovery commented out per your setup
            time.sleep(60)
            
    def process_packet(self, packet, sender, conn=None):
        if packet == "HELP":
            if conn:
                conn.send("ADD <text> <metadata> | GET <hash> | LIST | STOP".encode())
            return
        if packet == "LIST":
            if conn:
                listing = "\n".join(f"{k}: {v[1]}" for k, v in self.data_store.items()) or "No data yet."
                conn.send(listing.encode())
            return
        if packet.startswith("GET "):
            if conn:
                hash_id = packet.split(" ", 1)[1]
                text, metadata = self.get_data(hash_id)
                if text:
                    conn.send(f"{metadata}: {text}".encode())
                else:
                    conn.send(f"Error: Hash {hash_id} not found.".encode())
            return
        if packet.startswith("ADD "):
            try:
                parts = packet.split(" ", 2)
                if len(parts) == 3:
                    _, text, metadata = parts
                    hash_id = self.add_data(text, metadata)
                    if conn:
                        conn.send(f"Added: {hash_id}".encode())
            except:
                if conn:
                    conn.send("Error: Invalid ADD format. Use ADD <text> <metadata>".encode())
            return
        parts = packet.split("#", 2)
        if len(parts) == 3:
            hash_id, packed_data, metadata = parts
            if hash_id not in self.data_store:
                self.data_store[hash_id] = (packed_data, metadata)
                self.share_packet(packet)
                
    def share_packet(self, packet):
        for peer_ip in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((peer_ip, self.port))  # Updated to self.port
                    s.send(packet.encode())
            except:
                pass
        # Bluetooth sharing commented out per your setup

    def add_data(self, text, metadata=""):
        compressed, chunk_dict = fractal_compress(text)
        packet = pack_packet(compressed, chunk_dict, metadata)
        hash_id = cogito_hash(text)
        self.data_store[hash_id] = (packet, metadata)
        self.share_packet(packet)
        return hash_id

    def get_data(self, hash_id):
        if hash_id in self.data_store:
            packet, metadata = self.data_store[hash_id]
            compressed, chunk_dict, _ = unpack_packet(packet)
            return fractal_decompress(compressed, chunk_dict), metadata
        return None, None

    def stop(self):
        self.running = False
