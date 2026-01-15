import requests
import json
import time
import csv
import os

LEAGUE = "Fate+of+the+Vaal"
BASE_URL = "https://poe.ninja/poe2/api/economy/exchange/current"

SLEEP = 0.3
TIMEOUT = 10

DICT = {
    "Currency" : ["mirror-of-kalandra", "hinekoras-lock", "fracturing-orb", "vaal-cultivation-orb", "divine-orb", "perfect-chaos-orb", "crystallised-corruption", "architects-orb", "orb-of-extraction", "vaal-infuser", "ancient-infuser", "perfect-jewellers-orb", "perfect-exalted-orb", "greater-chaos-orb", "perfect-orb-of-augmentation", "orb-of-annulment", "core-destabiliser", "chaos-orb", "perfect-regal-orb", "arcanists-etcher", "armourers-scrap", "gemcutters-prism", "orb-of-chance", "greater-exalted-orb", "transmutation-shard", "greater-regal-orb", "glassblowers-bauble", "orb-of-alchemy", "vaal-orb", "artificers-orb", "perfect-orb-of-transmutation", "exalted-orb", "artificers-shard", "vaal-siphoner", "chance-shard", "greater-jewellers-orb", "blacksmiths-whetstone", "regal-shard", "regal-orb", "orb-of-transmutation", "greater-orb-of-augmentation", "orb-of-augmentation", "lesser-jewellers-orb", "scroll-of-wisdom", "greater-orb-of-transmutation"],
    "Fragments" : ["azmeri-reliquary-key", "the-trialmasters-reliquary-key", "zarokhs-reliquary-key:-against-the-darkness", "tangmazus-reliquary-key", "olroths-reliquary-key", "the-arbiters-reliquary-key", "primary-calamity-fragment", "secondary-calamity-fragment", "xeshts-reliquary-key", "tertiary-calamity-fragment", "victorious-fate", "deadly-fate", "cowardly-fate", "ancient-crisis-fragment", "weathered-crisis-fragment", "faded-crisis-fragment", "ritualistic-reliquary-key", "runic-splinter", "simulacrum-splinter", "twilight-reliquary-key"],
    "Abyss" : ["tecrods-gaze", "ancient-collarbone", "ancient-jawbone", "ancient-rib", "amanamus-gaze", "kurgals-gaze", "preserved-cranium", "preserved-collarbone", "ulamans-gaze", "kulemaks-invitation", "gnawed-jawbone", "gnawed-collarbone", "ulamans-gaze", "kulemaks-invitation", "gnawed-jawbone", "gnawed-collarbone", "preserved-jawbone", "preserved-rib", "gnawed-rib"],
    "UncutGems" : ["uncut-spirit-gem-level-20", "uncut-skill-gem-level-20", "uncut-spirit-gem-level-8", "uncut-spirit-gem-level-9", "uncut-spirit-gem-level-19", "uncut-spirit-gem-level-14", "uncut-spirit-gem-level-15", "uncut-spirit-gem-level-16", "uncut-spirit-gem-level-4", "uncut-skill-gem-level-1", "uncut-spirit-gem-level-7", "uncut-spirit-gem-level-10", "uncut-spirit-gem-level-5", "uncut-spirit-gem-level-13", "uncut-skill-gem-level-7", "uncut-spirit-gem-level-17", "uncut-spirit-gem-level-6", "uncut-spirit-gem-level-18", "uncut-spirit-gem-level-11", "uncut-spirit-gem-level-12", "uncut-skill-gem-level-8", "uncut-skill-gem-level-3", "uncut-skill-gem-level-11", "uncut-skill-gem-level-5", "uncut-support-gem-level-3", "uncut-skill-gem-level-15", "uncut-skill-gem-level-9", "uncut-support-gem-level-4", "uncut-skill-gem-level-4", "uncut-skill-gem-level-2", "uncut-skill-gem-level-12", "uncut-skill-gem-level-10", "uncut-skill-gem-level-19", "uncut-skill-gem-level-16", "uncut-skill-gem-level-6", "uncut-support-gem-level-5", "uncut-skill-gem-level-13", "uncut-support-gem-level-1", "uncut-skill-gem-level-14", "uncut-support-gem-level-2", "uncut-skill-gem-level-17", "uncut-skill-gem-level-18"],
    "LineageSupportGems" : ["uhtreds-augury", "uhtreds-omen", "uul-netols-embrace", "rakiatas-flow", "garukhans-resolve", "tuls-stillness", "eshs-radiance", "rigwalds-ferocity", "ixchels-torment", "uhtreds-exodus", "ataluis-bloodletting", "xophs-pyre", "arbiters-ignition", "atziris-impatience", "diallas-desire", "khatals-rejuvenation", "dominus-grasp", "amanamus-tithe", "hayoxis-fulmination", "zarokhs-revolt", "zerphis-infamy", "tecrods-revenge", "arjuns-medal", "siones-temper", "atziris-allure", "doedres-undoing", "brutus-brain", "rathas-assault", "kulemaks-dominion", "ailiths-chimes", "zarokhs-refrain", "kurgals-leash", "ahns-citadel", "kalisas-crescendo", "kaoms-madness", "xibaquas-rending", "oisins-oath", "arakaalis-lust", "uruks-smelting", "einhars-beastrite", "bhatairs-vengeance", "morganas-tempest", "tasalios-rhythm", "vilentas-propulsion", "cirels-cultivation", "paquates-pact", "tawhoas-tending", "varashtas-blessing", "romiras-requital", "guatelitzis-ablation", "daressos-passion", "tacatis-ire"],
    "Essences" : ["perfect-essence-of-seeking", "perfect-essence-of-insulation", "perfect-essence-of-the-body", "greater-essence-of-alacrity", "perfect-essence-of-grounding", "perfect-essence-of-thawing", "greater-essence-of-grounding", "essence-of-the-mind", "perfect-essence-of-ruin", "lesser-essence-of-ruin", "lesser-essence-of-command", "essence-of-electricity", "essence-of-flames", "greater-essence-of-abrasion", "greater-essence-of-haste", "lesser-essence-of-the-body", "lesser-essence-of-sorcery", "greater-essence-of-enhancement", "greater-essence-of-command", "greater-essence-of-sorcery", "essence-of-battle", "essence-of-ice", "essence-of-the-infinite", "lesser-essence-of-flames", "lesser-essence-of-ice", "lesser-essence-of-seeking", "lesser-essence-of-the-infinite", "greater-essence-of-battle", "greater-essence-of-the-infinite", "greater-essence-of-the-body", "greater-essence-of-electricity", "lesser-essence-of-thawing", "greater-essence-of-ice", "greater-essence-of-the-mind", "greater-essence-of-flames", "essence-of-horror", "essence-of-command", "essence-of-hysteria", "greater-essence-of-opulence", "perfect-essence-of-battle", "perfect-essence-of-haste", "perfect-essence-of-alacrity", "essence-of-the-abyss", "essence-of-delirium", "essence-of-opulence", "lesser-essence-of-opulence", "essence-of-abrasion", "perfect-essence-of-sorcery", "perfect-essence-of-the-infinite", "perfect-essence-of-opulence", "perfect-essence-of-the-mind", "lesser-essence-of-enhancement", "essence-of-alacrity", "essence-of-insanity", "essence-of-sorcery", "essence-of-enhancement", "lesser-essence-of-insulation", "lesser-essence-of-abrasion", "essence-of-seeking", "perfect-essence-of-enhancement", "essence-of-thawing", "greater-essence-of-seeking", "perfect-essence-of-abrasion", "essence-of-insulation", "lesser-essence-of-alacrity", "perfect-essence-of-ice", "essence-of-grounding", "essence-of-haste", "lesser-essence-of-grounding", "essence-of-ruin" , "lesser-essence-of-haste", "perfect-essence-of-electricity", "greater-essence-of-ruin", "perfect-essence-of-flames", "perfect-essence-of-command", "lesser-essence-of-the-mind", "essence-of-the-body", "greater-essence-of-insulation", "greater-essence-of-thawing"],
    "SoulCores" : ["guatelitzis-thesis", "jiquanis-thesis", "soul-core-of-jiquani", "soul-core-of-zalatl", "quipolatls-thesis", "soul-core-of-azcapa", "tzamotos-soul-core-of-ferocity", "soul-core-of-quipolatl", "quipolatls-soul-core-of-flow", "soul-core-of-zantipi", "soul-core-of-citaqualotl", "xopecs-soul-core-of-power", "citaqualotls-thesis", "soul-core-of-tacati", "estazuntis-soul-core-of-convalescence", "atmohuas-soul-core-of-retreat", "guatelitzis-soul-core-of-endurance", "soul-core-of-ticaba", "soul-core-of-cholotl", "topotantes-soul-core-of-dampening", "soul-core-of-atmohua", "hayoxis-soul-core-of-heatproofing", "soul-core-of-puhuarte", "citaqualotls-soul-core-of-foulness", "opilotis-soul-core-of-assault", "xipocados-soul-core-of-dominion", "soul-core-of-topotante", "uromotis-soul-core-of-attenuation", "soul-core-of-tzamoto", "tacatis-soul-core-of-affliction", "soul-core-of-opiloti", "soul-core-of-xopec", "zalatls-soul-core-of-insulation", "cholotls-soul-core-of-war"],
    "Idols" : ["idol-of-eeshta", "rabbit-idol", "idol-of-sirrius", "fox-idol", "idol-of-ralakesh", "idol-of-egrin", "idol-of-thruldana", "snake-idol", "primate-idol", "idol-of-grold", "bear-idol", "stag-idol", "idol-of-maxarius", "owl-idol", "boar-idol", "ox-idol", "cat-idol", "wolf-idol"],
    "Runes" : ["hedgewitch-assandras-rune-of-wisdom", "greater-rune-of-alacrity", "greater-rune-of-tithing", "countess-seskes-rune-of-archery", "inspiration-rune", "iron-rune", "storm-rune", "lesser-iron-rune", "farruls-rune-of-the-chase", "lesser-robust-rune", "saqawals-rune-of-the-sky", "adept-rune", "lesser-adept-rune", "glacial-rune", "lesser-storm-rune", "robust-rune", "resolve-rune", "lesser-body-rune", "the-greatwolfs-rune-of-willpower", "lesser-resolve-rune", "lesser-inspiration-rune", "greater-rune-of-leadership", "saqawals-rune-of-memory", "fenumus-rune-of-agony", "thane-girts-rune-of-wildness", "body-rune", "craiceanns-rune-of-warding", "vision-rune", "thane-grannells-rune-of-mastery", "courtesan-mannans-rune-of-cruelty", "fenumus-rune-of-spinning", "lesser-glacial-rune", "thane-lelds-rune-of-spring", "desert-rune", "farruls-rune-of-the-hunt", "the-greatwolfs-rune-of-claws", "lesser-desert-rune", "lady-hestras-rune-of-winter", "thane-myrks-rune-of-summer", "greater-iron-rune"],
    "Ritual" : ["omen-of-sinistral-annulment", "omen-of-whittling", "omen-of-dextral-annulment", "omen-of-light", "omen-of-dextral-erasure", "omen-of-chance", "omen-of-sanctification", "omen-of-the-blessed", "omen-of-sinistral-crystallisation", "omen-of-dextral-crystallisation", "omen-of-abyssal-echoes", "omen-of-corruption", "omen-of-sinistral-exaltation", "omen-of-recombination", "omen-of-the-hunt", "omen-of-dextral-exaltation", "omen-of-catalysing-exaltation", "omen-of-chaotic-monsters", "omen-of-greater-exaltation", "omen-of-amelioration", "omen-of-chaotic-rarity", "omen-of-chaotic-quantity", "omen-of-reinforcements", "omen-of-answered-prayers", "omen-of-bartering", "omen-of-secret-compartments", "omen-of-the-blackblooded", "omen-of-resurgence", "omen-of-the-ancients", "omen-of-refreshment", "petition-splinter", "omen-of-sinistral-necromancy", "omen-of-dextral-necromancy", "omen-of-the-sovereign", "omen-of-putrefaction", "omen-of-gambling", "omen-of-the-liege", "omen-of-sinistral-erasure"],
    "Expedition" : ["exotic-coinage", "black-scythe-artifact", "sun-artifact", "broken-circle-artifact", "order-artifact"],
    "Delirium" : ["concentrated-liquid-isolation", "concentrated-liquid-suffering", "concentrated-liquid-fear", "liquid-despair", "liquid-disgust", "liquid-envy", "liquid-paranoia", "diluted-liquid-greed", "diluted-liquid-guilt", "diluted-liquid-ire"],
    "Breach" : ["neural-catalyst", "sibilant-catalyst", "skittering-catalyst", "reaver-catalyst", "eshs-catalyst", "tuls-catalyst", "xophs-catalyst", "breach-splinter", "flesh-catalyst", "carapace-catalyst", "chayulas-catalyst", "adaptive-catalyst", "adaptive-catalyst", "uul-netols-catalyst"]
    }

def get_next_filename(base_name):
    """
    poe2_all_details.json
    poe2_all_details_001.json
    poe2_all_details_002.json
    """
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    i = 1
    while True:
        new_name = f"{name}_{i:03d}{ext}"
        if not os.path.exists(new_name):
            return new_name
        i += 1

def get_details(type_name, details_id):
    url = (
        f"{BASE_URL}/details"
        f"?league={LEAGUE}"
        f"&type={type_name}"
        f"&id={details_id}"
    )

    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"❌ {type_name} | {details_id} → {e}")
        return None


all_details = {}

for type_name, details_ids in DICT.items():
    print(f"\n📦 {type_name}")
    all_details[type_name] = {}

    for details_id in details_ids:
        data = get_details(type_name, details_id)

        if not data:
            continue

        all_details[type_name][details_id] = data

        print(f"✔ {details_id}")
        time.sleep(SLEEP)

# Sauvegarde finale
output_file = get_next_filename("poe2_all_details.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_details, f, indent=2, ensure_ascii=False)

print(f"\n💾 Sauvegardé dans {output_file}")


# Sauvegarde en CSV
with open("currencies.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "details_id",
        "name",
        "type",
        "category",
        "primary",
        "secondary"
    ])

    for type_name, items in all_details.items():
        for details_id, data in items.items():
            item = data.get("item", {})
            core = data.get("core", {})

            writer.writerow([
                details_id,
                item.get("name"),
                type_name,
                item.get("category"),
                core.get("primary"),
                core.get("secondary")
            ])

with open("prices_history.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "details_id",
        "pair",
        "timestamp",
        "rate",
        "volume"
    ])

    for type_name, items in all_details.items():
        for details_id, data in items.items():
            for pair in data.get("pairs", []):
                pair_id = pair.get("id")

                for h in pair.get("history", []):
                    writer.writerow([
                        details_id,
                        pair_id,
                        h.get("timestamp"),
                        h.get("rate"),
                        h.get("volumePrimaryValue")
                    ])
