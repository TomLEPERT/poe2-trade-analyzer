import json
import csv

# Charger le JSON depuis un fichier (ou depuis une variable)
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Préparer le CSV
csv_file = "output.csv"
csv_columns = [
    "id",
    "name",
    "category",
    "primaryValue",
    "volumePrimaryValue",
    "maxVolumeCurrency",
    "maxVolumeRate",
    "totalChange",
    "sparkline"
]

with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

    # Créer un dictionnaire pour mapper l'id aux noms et catégories
    items_dict = {item["id"]: {"name": item["name"], "category": item["category"]} for item in data["items"]}

    # Parcourir les lignes et écrire dans le CSV
    for line in data["lines"]:
        item_id = line["id"]
        name = items_dict[item_id]["name"] if item_id in items_dict else ""
        category = items_dict[item_id]["category"] if item_id in items_dict else ""
        primaryValue = line.get("primaryValue", "")
        volumePrimaryValue = line.get("volumePrimaryValue", "")
        maxVolumeCurrency = line.get("maxVolumeCurrency", "")
        maxVolumeRate = line.get("maxVolumeRate", "")
        totalChange = line.get("sparkline", {}).get("totalChange", "")
        sparkline = ";".join(str(x) for x in line.get("sparkline", {}).get("data", []))

        writer.writerow({
            "id": item_id,
            "name": name,
            "category": category,
            "primaryValue": primaryValue,
            "volumePrimaryValue": volumePrimaryValue,
            "maxVolumeCurrency": maxVolumeCurrency,
            "maxVolumeRate": maxVolumeRate,
            "totalChange": totalChange,
            "sparkline": sparkline
        })

print(f"CSV généré avec succès : {csv_file}")