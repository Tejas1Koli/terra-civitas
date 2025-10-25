
# Local crime detection labels
LABELS = [
    "Abuse", "Arrest", "Arson", "Assault", "Burglary", 
    "Explosion", "Fighting", "Normal", "RoadAccidents", 
    "Robbery", "Shooting", "Shoplifting", "Stealing", "Vandalism"
]

LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for i, label in enumerate(LABELS)}
