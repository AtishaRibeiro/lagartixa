import copy
import json


PROVINCE_INCLUDE_FILTER = [
    # "Région de Bruxelles-Capitale - Brussels Hoofdstedelijk Gewest",
    # "Vlaams-Brabant",
    # "Antwerpen",
    # "Oost-Vlaanderen",
    # "Limburg",
    # "Brabant wallon",
    # "Hainaut",
    # "West-Vlaanderen",
    # "Namur",
    # "Liège",
    # "Luxembourg",
    # None
]

EXCLUDE_FILTER = [
    "n°",
    "nᵒ",
    "/",
    "(",
    "nr.",
    ">",
    " — ",
    " - ",
    "- ",
    " -",
    ";",
    '"',
    "chemin priv",
    "parking",
    "train vicinal",
    "chemin vicinal",
    "driveway",
    "vzw",
    "toegangsweg",
    "bedrijvenzone",
    "industrieterrein",
    "industriepark",
    "zoning industriel",
    "zone industrielle",
    "parc industriel",
    "koppelingsgebieden",
    "dit stuk verharding",
    "toegangsweg",
    "werfweg",
    "road",
    "ravel ",
    "parcours",
    "chemin de fer",
    "sncb",
    "nmbs",
    "voetgangerstunnel",
    "spoorwegbedding",
    "parc d'activités",
    "éco-pédagogique",
    "pieds nus",
    "numéro",
    "chemin traversant",
    "zone piétonne",
    "chemein d'accès",
    "chemin d'accès",
    # Specific "streets"
    "avenue marie-thérèse et andré dujardin-simoenslaan",
    "1000 bornes à vélo région hainaut-est",
    " ",
    "-",
]


def filter(
    node,
    exclude: list | None = None,
    include: list | None = None,
    province_include: list | None = None,
) -> bool:
    if province_include is not None:
        if node["province"] not in province_include:
            return False
    if node["highway"] in [
        "path",
        "footway",
        # "service",
        "track",
        "services",
        "cycleway",
        "steps",
    ]:
        return False

    name = node["name"]
    if exclude is not None:
        for f in exclude:
            if f in name.lower():
                return False
    if include is not None:
        for f in include:
            if f not in name.lower():
                return False
    return True


def print_list(l: list):
    for i in l:
        print(i)


def main():
    with open("/home/atisha/Downloads/res.json", "r") as f:
        data = json.load(f)

    new_data = []
    for d in data:
        n = d["name"]
        split1 = n.split(" / ")
        for s in split1:
            split2 = s.split(" - ")
            for s2 in split2:
                new_d = copy.deepcopy(d)
                new_d["name"] = s2
                new_data.append(new_d)

    data = new_data
    # Filter out specific words/characters
    data = [x for x in data if filter(x, exclude=EXCLUDE_FILTER)]

    unique_data_dict = {}
    for x in data:
        # Remove spaces from beginning and end
        x["name"] = x["name"].strip(" ")
        unique_data_dict[x["name"]] = x

    unique_data = list(unique_data_dict.values())
    unique_data.sort(key=lambda x: len(x["name"]))
    final_output = [
        {"name": x["name"], "highway": x.get("highway")} for x in unique_data[-1000:]
    ]
    print_list(final_output)

    avg_len = sum(len(x["name"]) for x in unique_data) / len(unique_data)
    print(f"Average length: {avg_len}")


if __name__ == "__main__":
    main()
