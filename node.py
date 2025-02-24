# node.py
import socketserver
import threading
import time
import pickle
import os
import socket
from fractal import cogito_hash, pack_packet, unpack_packet, fractal_decompress, fractal_compress

class FractalRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(4096).decode()
        if data:
            self.server.node.process_packet(data, self.client_address[0], self.request)

class FractalNode:
    def __init__(self, node_id, port=5000, bt_port=1):
        self.node_id = node_id
        self.port = port
        self.bt_port = bt_port
        self.data_store = {}  # name: (packet, metadata, hash)
        self.peers = set()
        self.bt_peers = set()
        self.running = True
        self.server = None
        self.store_file = f"fractalmind_store_{port}.pkl"
        self.load_store()

    def start(self):
        self.server = socketserver.ThreadingTCPServer(('0.0.0.0', self.port), FractalRequestHandler)
        self.server.node = self
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        self.peer_thread = threading.Thread(target=self.discover_peers, daemon=True)
        self.peer_thread.start()

    def load_store(self):
        if os.path.exists(self.store_file):
            with open(self.store_file, 'rb') as f:
                self.data_store = pickle.load(f)

    def save_store(self):
        with open(self.store_file, 'wb') as f:
            pickle.dump(self.data_store, f)

    def discover_peers(self):
        local_ip = socket.gethostbyname(socket.gethostname())
        subnet = ".".join(local_ip.split(".")[:-1]) + "."
        while self.running:
            for i in range(1, 255):
                ip = f"{subnet}{i}"
                if ip != local_ip and ip not in self.peers:
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.1)
                            if s.connect_ex((ip, self.port)) == 0:
                                self.peers.add(ip)
                                # Request sync from peer
                                self.share_packet("SYNC_REQUEST", ip)
                    except:
                        pass
            time.sleep(10)  # Faster sync—10s vs. 60s

    def process_packet(self, packet, sender, conn=None):
        if packet == "HELP":
            if conn:
                conn.send("ADD <name> <text> | GET <name/hash> | LIST | STOP".encode())
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
                        try:
                            compressed, chunk_dict, _ = unpack_packet(packed)
                            text = fractal_decompress(compressed, chunk_dict)
                            conn.send(f"{name}: {text}".encode())
                        except ValueError as e:
                            conn.send(f"Error unpacking {name}: {str(e)}".encode())
                        return
                conn.send(f"Error: {name_or_hash} not found.".encode())
            return
        if packet.startswith("ADD "):
            try:
                if conn:
                    parts = packet.split(" ", 2)
                    if len(parts) == 3:
                        _, name, text = parts
                        compressed, chunk_dict = fractal_compress(text)
                        hash_id = cogito_hash(text)
                        packed = pack_packet(compressed, chunk_dict, name)
                        self.data_store[name] = (packed, name, hash_id)
                        self.share_packet(packed)
                        conn.send(f"Added {name}: {hash_id}".encode())
                    else:
                        conn.send("Error: Use ADD <name> <text> (e.g., ADD Test Hello)".encode())
            except Exception as e:
                if conn:
                    conn.send(f"Error: Invalid ADD format - {str(e)}".encode())
            return
        if packet == "SYNC_REQUEST":
            if conn and sender not in self.peers:
                self.peers.add(sender)
                # Send full store to requesting peer
                for name, (packed, _, hash_id) in self.data_store.items():
                    self.share_packet(packed, sender)
            return
        if packet == "SYNC_RESPONSE":
            return  # Placeholder for peer response handling
        parts = packet.split("#", 2)
        if len(parts) == 3:
            hash_id, packed_data, metadata = parts
            if metadata not in self.data_store:
                self.data_store[metadata] = (packed_data, metadata, hash_id)
                self.share_packet(packed_data)

    def share_packet(self, packet, specific_peer=None):
        target_peers = [specific_peer] if specific_peer else self.peers
        for peer_ip in target_peers:
            if peer_ip:  # Avoid None
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
        packed = pack_packet(compressed, chunk_dict, metadata)
        self.data_store[metadata] = (packed, metadata, hash_id)
        self.share_packet(packed)
        return hash_id

    def get_data(self, name_or_hash):
        for name, (packet, metadata, hash_id) in self.data_store.items():
            if name == name_or_hash or hash_id == name_or_hash:
                compressed, chunk_dict, _ = unpack_packet(packet)
                return fractal_decompress(compressed, chunk_dict), metadata
        return None, None

    def stop(self):
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join(timeout=2)  # Wait for server thread
        self.peer_thread.join(timeout=2)  # Wait for peer thread
        self.save_store()
