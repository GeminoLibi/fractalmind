# lessons.py
from fractal import fractal_compress, pack_data, fractal_hash

def load_initial_lessons(node):
    """Load pre-encoded lessons into the network."""
    # Pre-encoded lessons (compressed and packed)
    lessons = {
        "Math101": {
            "text": "Math Basics: 1+1=2, 2+2=4—addition builds step by step.",
            "packed": pack_data(fractal_compress("Math Basics: 1+1=2, 2+2=4—addition builds step by step.")),
            "hash": fractal_hash("Math Basics: 1+1=2, 2+2=4—addition builds step by step.")
        },
        "Farm101": {
            "text": "Crop Rotation: Corn, beans, squash—cycle yearly for soil health.",
            "packed": pack_data(fractal_compress("Crop Rotation: Corn, beans, squash—cycle yearly for soil health.")),
            "hash": fractal_hash("Crop Rotation: Corn, beans, squash—cycle yearly for soil health.")
        },
        "Emergency101": {
            "text": "Water Safety: Boil water 1 minute to purify—use in floods.",
            "packed": pack_data(fractal_compress("Water Safety: Boil water 1 minute to purify—use in floods.")),
            "hash": fractal_hash("Water Safety: Boil water 1 minute to purify—use in floods.")
        },
        "Science101": {
            "text": "Photosynthesis: Plants use sunlight, CO2, water—make oxygen, sugar.",
            "packed": pack_data(fractal_compress("Photosynthesis: Plants use sunlight, CO2, water—make oxygen, sugar.")),
            "hash": fractal_hash("Photosynthesis: Plants use sunlight, CO2, water—make oxygen, sugar.")
        },
        "Health101": {
            "text": "Hygiene: Wash hands 20s with soap—stops germs spreading.",
            "packed": pack_data(fractal_compress("Hygiene: Wash hands 20s with soap—stops germs spreading.")),
            "hash": fractal_hash("Hygiene: Wash hands 20s with soap—stops germs spreading.")
        },
        "Code101": {
            "text": "Python: print('Hello')—outputs text to screen.",
            "packed": pack_data(fractal_compress("Python: print('Hello')—outputs text to screen.")),
            "hash": fractal_hash("Python: print('Hello')—outputs text to screen.")
        }
    }
    for metadata, info in lessons.items():
        packet = f"{info['hash']}#{info['packed']}#{metadata}"
        node.data_store[info['hash']] = (info['packed'], metadata)
        node.share_packet(packet)
        print(f"Loaded {metadata}: {info['hash']}")
