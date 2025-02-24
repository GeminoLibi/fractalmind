# ui.py
import tkinter as tk
import socket

def run_cli(node):
    print(f"FractalMind node started on port {node.port}. Type 'HELP' for commands.")
    state = "start"  # Track CLI state: start, add_name, add_data
    lesson_name = None
    while True:
        cmd = input("> ").strip()
        if cmd == "STOP":
            node.stop()
            print("Node stopped.")
            break
        if state == "start":
            if cmd == "ADD":
                state = "add_name"
                response = send_command(node, cmd)
                print(response)
            else:
                response = send_command(node, cmd)
                print(response)
        elif state == "add_name":
            response = send_command(node, f"NAME \"{cmd}\"")
            lesson_name = cmd
            state = "add_data"
            print(response)
        elif state == "add_data":
            response = send_command(node, f"DATA \"{lesson_name}:{cmd}\"")
            state = "start"
            lesson_name = None
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
        s.settimeout(5)
        local_ip = socket.gethostbyname(socket.gethostname())
        try:
            s.connect((local_ip, node.port))
            s.send(command.encode())
            try:
                response = s.recv(4096).decode()
                return response if response else "No response—check command syntax."
            except socket.timeout:
                return "Timeout—node may be busy."
        except:
            return "Error: Node busy or not responding."
