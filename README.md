# FractalMind

A decentralized, fractal-powered knowledge network.

## Why?
FractalMind frees knowledge—education, tools, solutions—across any device, anywhere. No servers, just peers—online or off, low-power, unstoppable.

## Setup
- **Requirements**: Python 3.x
- **Clone**: `git clone <url>`
- **Run**: 
  - CLI: `python3 main.py [port]` (e.g., `python3 main.py 5000`)
  - GUI: `python3 main.py [port] --gui` (e.g., `python3 main.py 5000 --gui`)

## Usage
- **CLI**:
  - `HELP`: Show commands.
  - `ADD <text> <metadata>`: Share—e.g., `ADD "Hello world" "Test101"`.
  - `GET <hash>`: Retrieve—e.g., `GET <hash-from-add>`.
  - `LIST`: List data—hash and metadata.
  - `STOP`: Shut down.
- **GUI**: Type commands, click "Run", see output—same as CLI.
- **Multi-Node**: Run on devices—LAN auto-connects (Bluetooth disabled by default).

## Features
- **Fractal Compression**: Adaptive, pattern-based—tiny, efficient packets.
- **P2P**: TCP—resilient, scales infinitely (Bluetooth optional, requires `pybluez`).
- **Lessons**: Math, farming, emergency, science, health, code, culture—pre-loaded, expandable.
