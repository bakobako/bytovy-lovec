from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Overpass API URL
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@app.route('/')
def index():
    return render_template('index.html')


def generate_overpass_query(polygon):
    """
    Generate an Overpass QL query for querying streets (highways) within given polygons.
    """
    polygon_str = " ".join(f"{lat} {lon}" for lat, lon in polygon)  # Taking the first polygon for this example
    return f"""
    [out:json];
    (
      way["highway"](poly:"{polygon_str}");
    );
    out body;
    """


def get_streets_within_polygon(polygon):
    overpass_query = generate_overpass_query(polygon)
    try:
        response = requests.get(OVERPASS_URL, params={'data': overpass_query})
        response.raise_for_status()
        streets = response.json()

        all_street_names = set()

        for element in streets.get("elements", []):
            if element["type"] == "way":
                name = element['tags'].get('name', 'Unnamed')
                all_street_names |= {name}

        return all_street_names

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error querying Overpass API: {e}")


@app.route('/save_polygons', methods=['POST'])
def save_polygons():
    print("Received request to save polygons.")
    data = request.json
    polygons = data.get('polygons')
    dispozice = data.get('dispozice')
    price_from = data.get('priceFrom')
    price_to = data.get('priceTo')
    floor_from = data.get('floorFrom')
    floor_to = data.get('floorTo')
    ownership = data.get('ownership')

    # add area m2 from and to
    # add numer of bedrooms
    # add is walkthrough
    # add ownership
    # add building type
    # add condition
    # add is rooftop apartment
    # add is mezonet
    # add has balcony
    # add has terrace
    # add has elevator
    # add has garage
    # add has cellar
    # add has parking_lot




    # Print the received data
    print("Received data:")
    print(f"Polygons: {polygons}")
    print(f"Dispozice: {dispozice}")
    print(f"Price from: {price_from}")
    print(f"Price to: {price_to}")
    print(f"Floor from: {floor_from}")
    print(f"Floor to: {floor_to}")
    print(f"Ownership: {ownership}")

    if not polygons:
        return jsonify({"error": "No polygons provided"}), 400

    # Generate Overpass QL query to get streets within the polygons
    all_streets = set()
    for polygon in polygons:
        streets = get_streets_within_polygon(polygon)
        all_streets |= streets

    print("Streets within the polygons: ", all_streets)

    return jsonify({"streets": list(all_streets)})

    # Query Overpass API


if __name__ == '__main__':
    app.run(debug=True)
