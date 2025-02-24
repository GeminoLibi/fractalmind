# node.py
import socket
import threading
import time
#import bluetooth
from fractal import cogito_hash, pack_packet, unpack_packet, fractal_decompress, fractal_compress

class FractalNode:
    def __init__(self, node_id, port=5000, bt_port=1):
        self.node_id = node_id
        self.port = port
        self.bt_port = bt_port
        self.data_store = {}  # name: (packet, metadata, hash)
        self.peers = set()
        self.bt_peers = set()
        self.running = True

    def start(self):
        threading.Thread(target=self.listen_tcp, daemon=True).start()
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def listen_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.port))
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
                            if s.connect_ex((ip, self.port)) == 0:
                                self.peers.add(ip)
                    except:
                        pass
            time.sleep(60)
            
    def process_packet(self, packet, sender, conn=None):
        if packet == "HELP":
            if conn:
                conn.send("ADD | GET | LIST | STOP".encode())
            return
        if packet == "LIST":
            if conn:
                listing = "\n".join(f"{name} ({data[2]})" for name, data in self.data_store.items()) or "No data yet."
                conn.send(listing.encode())
            return
        if packet.startswith("GET "):
            if conn:
                name_or_hash = packet.split(" ", 1)[1].strip('"')
                for name, (packed, metadata, hash_id) in self.data_store.items():
                    if name == name_or_hash or hash_id == name_or_hash:
                        compressed, chunk_dict, _ = unpack_packet(packed)
                        text = fractal_decompress(compressed, chunk_dict)
                        conn.send(f"{name}: {text}".encode())
                        return
                conn.send(f"Error: {name_or_hash} not found.".encode())
            return
        if packet == "ADD":
            if conn:
                conn.send("Enter lesson name:".encode())
            return
        if packet.startswith("NAME "):
            if conn:
                name = packet.split(" ", 1)[1].strip('"')
                conn.send(f"Enter lesson data for {name}:".encode())
            return
        if packet.startswith("DATA "):
            try:
                if conn:
                    data_part = packet.split(" ", 1)[1].strip('"')
                    name, text = data_part.split(":", 1)
                    name = name.strip()
                    text = text.strip()
                    compressed, chunk_dict = fractal_compress(text)
                    hash_id = cogito_hash(text)
                    packet = pack_packet(compressed, chunk_dict, name)
                    self.data_store[name] = (packet, name, hash_id)
                    self.share_packet(packet)
                    conn.send(f"Added {name}: {hash_id}".encode())
            except:
                if conn:
                    conn.send("Error: Use DATA \"name:text\" (e.g., DATA \"Test:Hello\")".encode())
            return
        parts = packet.split("#", 2)
        if len(parts) == 3:
            hash_id, packed_data, metadata = parts
            if metadata not in self.data_store:
                self.data_store[metadata] = (packed_data, metadata, hash_id)
                self.share_packet(packet)
                
    def share_packet(self, packet):
        for peer_ip in self.peers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((peer_ip, self.port))
                    s.send(packet.encode())
            except:
                pass

    def add_data(self, text, metadata=""):
        compressed, chunk_dict = fractal_compress(text)
        hash_id = cogito_hash(text)
        packet = pack_packet(compressed, chunk_dict, metadata)
        self.data_store[metadata] = (packet, metadata, hash_id)
        self.share_packet(packet)
        return hash_id

    def get_data(self, name_or_hash):
        for name, (packet, metadata, hash_id) in self.data_store.items():
            if name == name_or_hash or hash_id == name_or_hash:
                compressed, chunk_dict, _ = unpack_packet(packet)
                return fractal_decompress(compressed, chunk_dict), metadata
        return None, None

    def stop(self):
        self.running = False
