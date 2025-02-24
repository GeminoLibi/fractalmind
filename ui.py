# ui.py
import tkinter as tk
import socket

def run_cli(node):
    print(f"FractalMind node started on port {node.port}. Type 'HELP' for commands.")
    last_cmd = None
    while True:
        cmd = input("> ").strip()
        if cmd == "STOP":
            node.stop()
            print("Node stopped.")
            break
        response = send_command(node, cmd, last_cmd)
        print(response)
        if cmd.startswith("ADD ") or cmd.startswith("NAME "):
            last_cmd = cmd
        else:
            last_cmd = None

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

def send_command(node, command, last_cmd=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        local_ip = socket.gethostbyname(socket.gethostname())
        try:
            s.connect((local_ip, node.port))
            if last_cmd and last_cmd.startswith("ADD "):
                command = f"NAME \"{command}\""
            elif last_cmd and last_cmd.startswith("NAME "):
                name = last_cmd.split(" ", 1)[1].strip('"')
                command = f"DATA \"{name}:{command}\""
            s.send(command.encode())
            response = s.recv(4096).decode()
            return response if response else "No response—check command syntax."
        except:
            return "Error: Node busy or not responding."
