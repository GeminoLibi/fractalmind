# main.py
import sys
from node import FractalNode
from lessons import load_initial_lessons
from ui import run_cli, run_gui

def main(port=5000, use_gui=False):
    node = FractalNode(node_id=cogito_hash(str(time.time())), port=port)
    node.start()
    load_initial_lessons(node)
    if use_gui:
        run_gui(node)
    else:
        run_cli(node)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    use_gui = "--gui" in sys.argv
    main(port, use_gui)
