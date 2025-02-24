# node.py
import socket
import threading
import time
# import bluetooth
from fractal import cogito_hash, pack_packet, unpack_packet

class FractalNode:
    def __init__(self, node_id, tcp_port=5000, bt_port=1):
        self.node_id = node_id
        self.tcp_port = tcp_port
        self.bt_port = bt_port
        self.data_store = {}
        self.peers = set()
        self.bt_peers = set()
        self.running = True

    def start(self):
        threading.Thread(target=self.listen_tcp, daemon=True).start()
        # threading.Thread(target=self.listen_bluetooth, daemon=True).start()
        threading.Thread(target=self.discover_peers, daemon=True).start()

    def listen_tcp(self):
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
        local_ip = socket.gethostbyname(socket.gethostname())
        subnet = ".".join(local_ip.split(".")[:-1]) + "."
        while self.running:
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
        if packet == "HELP":
            if conn:
                conn.send("ADD <text> <metadata> | GET <hash> | LIST | STOP".encode())
            return
        if packet == "LIST":
            if conn:
                listing = "\n".join(f"{k}: {v[1]}" for k, v in self.data_store.items()) or "No data yet."
                conn.send(listing.encode())
            return
        try:
            compressed, chunk_dict, metadata = unpack_packet(packet)
            hash_id = cogito_hash(fractal_decompress(compressed, chunk_dict))
            if hash_id not in self.data_store:
                self.data_store[hash_id] = (packet, metadata)
                self.share_packet(packet)
        except:
            pass

    def share_packet(self, packet):
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
