import sys
import tkinter as tk
from node import FractalNode
from lessons import load_initial_lessons

def run_node(port=5000, use_gui=False):
    """Run a FractalMind node with CLI or GUI."""
    node = FractalNode(node_id=cogito_hash(str(time.time())), port=port)
    node.start()
    load_initial_lessons(node)
    print(f"FractalMind node started on port {port}. Type 'HELP' for CLI or use GUI.")

    def send_command(command):
        """Send command to node and get response."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            local_ip = socket.gethostbyname(socket.gethostname())
            try:
                s.connect((local_ip, node.port))
                s.send(command.encode())
                return s.recv(4096).decode()
            except:
                return "Error: Node busy."

    if use_gui:
        root = tk.Tk()
        root.title("FractalMind Node")
        tk.Label(root, text=f"Node ID: {node.node_id}").pack()
        
        cmd_entry = tk.Entry(root, width=50)
        cmd_entry.pack()
        
        output_text = tk.Text(root, height=10, width=50)
        output_text.pack()
        
        def execute_command():
            cmd = cmd_entry.get()
            response = send_command(cmd)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, response)
        
        tk.Button(root, text="Run", command=execute_command).pack()
        tk.Button(root, text="Stop", command=lambda: [node.stop(), root.quit()]).pack()
        
        root.mainloop()
    else:
        while True:
            cmd = input("> ").strip()
            if cmd == "STOP":
                node.stop()
                print("Node stopped.")
                break
            print(send_command(cmd))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    use_gui = "--gui" in sys.argv
    run_node(port, use_gui)
