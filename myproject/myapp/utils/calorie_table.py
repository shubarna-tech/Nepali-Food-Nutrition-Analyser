# File: myapp/utils/calorie_table.py
"""
Map each food class to an approximate calories per serving.
Adjust values to suit your dataset.
"""
CALORIE_TABLE = {
    "burger": 500,
    "chiya": 120,
    "dalbhat": 450,
    "friedrice": 300,
    "jeri": 160,
    "momo": 300,
    "omelette": 150,
    "pakoda": 180,
    "panipuri": 100,
    "pizza": 285,
    "roti": 120,
    "samosa": 150,
    "selroti": 200,
    "yomari": 250,
    "chatamari": 180,
    "chhoila": 280,
    "dhindo": 300,
    "gundruk": 65,
    "kheer": 200,
    "sekuwa": 250,
}


def get_calories_for_class(food_class: str) -> float:
    return CALORIE_TABLE.get(food_class.lower(), 0.0)
