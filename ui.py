# ui.py
import tkinter as tk
import socket

def run_cli(node):
    print(f"FractalMind node started on port {node.port}. Type 'HELP' for commands.")
    while True:
        cmd = input("> ").strip()
        if cmd == "STOP":
            node.stop()
            print("Node stopped.")
            break
        response = send_command(node, cmd)
        print(response)

def run_gui(node):
    root = tk.Tk()
    root.title("FractalMind Node")
    tk.Label(root, text=f"Node ID: {node.node_id}").pack()
    
    cmd_entry = tk.Entry(root, width=50)
    cmd_entry.pack()
    
    output_text = tk.Text(root, height=10, width=50)
    output_text.pack()
    
    def execute_command():
        cmd = cmd_entry.get()
        response = send_command(node, cmd)
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, response)
    
    tk.Button(root, text="Run", command=execute_command).pack()
    tk.Button(root, text="Stop", command=lambda: [node.stop(), root.quit()]).pack()
    
    root.mainloop()

def send_command(node, command):
    """Send command to node and get response."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)  # Bumped to 10s
        local_ip = socket.gethostbyname(socket.gethostname())
        try:
            s.connect((local_ip, node.port))
            s.send(command.encode())
            response = s.recv(4096)
            return response.decode() if response else "No response—check command syntax."
        except:
            return f"Error: Node busy or not responding—try port {node.port + 1} or kill process on {node.port} (e.g., 'fuser -k {node.port}/tcp')."
