# lessons.py
from fractal import fractal_compress, pack_packet, fractal_hash

def load_initial_lessons(node):
    """Load pre-encoded lessons."""
    lessons = [
        ("Math Basics: 1+1=2, 2+2=4—addition builds step by step.", "Math101"),
        ("Crop Rotation: Corn, beans, squash—cycle yearly for soil health.", "Farm101"),
        ("Water Safety: Boil water 1 minute to purify—use in floods.", "Emergency101"),
        ("Photosynthesis: Plants use sunlight, CO2, water—make oxygen, sugar.", "Science101"),
        ("Hygiene: Wash hands 20s with soap—stops germs spreading.", "Health101"),
        ("Python: print('Hello')—outputs text to screen.", "Code101"),
        ("Greetings: Hola (Spanish), Nihao (Chinese)—say hi anywhere.", "Culture101")
    ]
    for text, metadata in lessons:
        compressed, chunk_dict = fractal_compress(text)
        packet = pack_packet(compressed, chunk_dict, metadata)
        hash_id = fractal_hash(text)
        node.data_store[hash_id] = (packet, metadata)
        node.share_packet(packet)
        print(f"Loaded {metadata}: {hash_id}")
