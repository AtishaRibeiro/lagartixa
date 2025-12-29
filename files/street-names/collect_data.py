import json
import matplotlib.pyplot as plt
import overpy
import shapely.geometry as geom
import shapely.ops as ops
from shapely.plotting import plot_polygon
import time

api = overpy.Overpass()

PROVINCE_NAMES = [
    "Région de Bruxelles-Capitale - Brussels Hoofdstedelijk Gewest",
    "Vlaams-Brabant",
    "Antwerpen",
    "Oost-Vlaanderen",
    "Limburg",
    "Brabant wallon",
    "Hainaut",
    "West-Vlaanderen",
    "Namur",
    "Liège",
    "Luxembourg",
]


def plot_province_shapely(provinces):
    """Using shapely's plotting function"""
    for name, poly in provinces:
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        plot_polygon(poly, ax=ax, add_points=False, color="lightblue", alpha=0.7)

        ax.set_title(f"{name} Province Boundary (Shapely Plot)")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        plt.tight_layout()
        plt.show()


def get_streets(area: str):
    result = api.query(
        f"""
        [out:json][timeout:500];
        {area}
        way["highway"]["name"](area.searchArea);
        out center tags;
    """
    )
    return result


def get_province_area(admin_level: int, province: str):
    result = api.query(
        f"""
        [out:json][timeout:500];
        (
          relation["boundary"="administrative"]["admin_level"="{admin_level}"]["name"="{province}"];
          way(r);
          node(w);
        );
        out geom;
    """
    )
    return result


def build_polygons_from_ways(province_names, provinces_res):
    provinces = []
    for i, name in enumerate(province_names):
        result = provinces_res[i]

        # Get the relation
        if not result.relations:
            continue

        rel = result.relations[0]

        # Group ways by role
        outer_ways = []
        for member in rel.members:
            if member.role == "outer" or member.role == "":
                # Find the way with this ID
                way = next((w for w in result.ways if w.id == member.ref), None)
                if way:
                    outer_ways.append(way)

        # Build coordinate list from ways (preserves order)
        all_coords = []
        for way in outer_ways:
            way_coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
            all_coords.extend(way_coords)

        if len(all_coords) >= 3:
            try:
                # Remove consecutive duplicates
                coords = [all_coords[0]]
                for coord in all_coords[1:]:
                    if coord != coords[-1]:
                        coords.append(coord)

                # Close polygon
                if coords[0] != coords[-1]:
                    coords.append(coords[0])

                poly = geom.Polygon(coords)

                if poly.is_valid:
                    provinces.append((name, poly))
                    print(f"✓ Created polygon for {name}")
                else:
                    poly = poly.buffer(0)
                    if poly.is_valid:
                        provinces.append((name, poly))
                        print(f"✓ Fixed polygon for {name}")
            except Exception as e:
                print(f"✗ Error: {e}")

    return provinces


def main():
    area = 'area["ISO3166-1"="BE"][admin_level=2]->.searchArea;'
    # area = 'area["name"="Leuven"]["boundary"="administrative"]["admin_level"="8"]->.searchArea;'

    print("Fetching provinces")
    provinces_res = []
    for i, n in enumerate(PROVINCE_NAMES):
        print(n)
        if i == 0:  # Brussels
            provinces_res.append(get_province_area(4, n))
        else:  # Other provinces
            provinces_res.append(get_province_area(6, n))

        # Sleep to prevent timeout
        time.sleep(5)

    print(provinces_res)

    provinces = build_polygons_from_ways(PROVINCE_NAMES, provinces_res)
    plot_province_shapely(provinces)
    print(provinces)

    print("Fetching streets")
    streets_res = get_streets(area)
    # Match each street to a province
    output = []
    for way in streets_res.ways:
        if way.center_lat is None:
            continue
        point = geom.Point(float(way.center_lon), float(way.center_lat))
        province_name = None
        for pname, poly in provinces:
            if poly.contains(point):
                province_name = pname
                break
        output.append(
            {
                "id": way.id,
                "name": way.tags.get("name"),
                "highway": way.tags.get("highway"),
                "center_lat": float(way.center_lat),
                "center_lon": float(way.center_lon),
                "province": province_name,
            }
        )

    with open("res.json", "w", encoding="utf=8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
