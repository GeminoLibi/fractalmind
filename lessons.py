def load_initial_lessons(node):
    """Load diverse, practical lessons."""
    lessons = {
        "Math101": "Math Basics: 1+1=2, 2+2=4—addition builds step by step.",
        "Farm101": "Crop Rotation: Corn, beans, squash—cycle yearly for soil health.",
        "Emergency101": "Water Safety: Boil water 1 minute to purify—use in floods.",
        "Science101": "Photosynthesis: Plants use sunlight, CO2, water—make oxygen, sugar.",
        "Health101": "Hygiene: Wash hands 20s with soap—stops germs spreading.",
        "Code101": "Python: print('Hello')—outputs text to screen."
    }
    for metadata, text in lessons.items():
        hash_id = node.add_data(text, metadata)
        print(f"Added {metadata}: {hash_id}")
