from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Overpass API URL
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save_polygons', methods=['POST'])
def save_polygons():
    data = request.json
    polygons = data.get('polygons')

    if not polygons:
        return jsonify({"error": "No polygons provided"}), 400

    # Generate Overpass QL query to get streets within the polygons
    overpass_query = generate_overpass_query(polygons)

    # Query Overpass API
    try:
        response = requests.get(OVERPASS_URL, params={'data': overpass_query})
        response.raise_for_status()
        streets = response.json()

        all_street_names = set()

        # Print the streets to the console
        print("Received streets:")
        for element in streets.get("elements", []):
            if element["type"] == "way":
                print(f"Street: {element['tags'].get('name', 'Unnamed')} - {element['id']}")
                name = element['tags'].get('name', 'Unnamed')
                all_street_names |= {name}


        print(all_street_names)

        return jsonify({"message": "Polygons processed and streets printed to console."}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Overpass API request failed: {str(e)}"}), 500


def generate_overpass_query(polygons):
    """
    Generate an Overpass QL query for querying streets (highways) within given polygons.
    """
    polygon_str = " ".join(f"{lat} {lon}" for lat, lon in polygons[0])  # Taking the first polygon for this example
    return f"""
    [out:json];
    (
      way["highway"](poly:"{polygon_str}");
    );
    out body;
    """


if __name__ == '__main__':
    app.run(debug=True)
