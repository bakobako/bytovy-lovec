from flask import Flask, render_template, request, jsonify
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_polygons', methods=['POST'])
def save_polygons():
    data = request.json
    polygons = data.get('polygons')

    if not polygons:
        return jsonify({"error": "No polygons provided"}), 400

    # Print each polygon to the console
    print("Received polygons:")
    for i, polygon in enumerate(polygons, start=1):
        print(f"Polygon {i}:")
        for coord in polygon:
            print(coord)

    return jsonify({"message": "Polygons received and printed to console."}), 200

if __name__ == '__main__':
    app.run(debug=True)
