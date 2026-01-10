import json
import csv
from flask import Flask, Response, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import io
import os
from data import Extractor, Constants

app = Flask(__name__, 
            static_folder='../public',
            static_url_path='')
CORS(app)

COLUMN_ORDER = [
    'University',
    'Location',
    'Number of Undergraduates',
    'Test Policy',
    'SAT Range',
    'ACT Range',
    'Avg GPA',
    'Acceptance Rate',
    'Cost of Attendance',
    'Merit Aid',
    'Likely/Target/Reach',
    'ED/EA/Rolling',
    'Application Deadlines'
]

def reorder_columns(data):
    """Reorder dictionary keys to maintain consistent column order"""
    ordered = {}
    for key in COLUMN_ORDER:
        if key in data:
            ordered[key] = data[key]

    for key in data:
        if key not in ordered:
            ordered[key] = data[key]

    return ordered

# Serve the frontend
@app.route('/')
def serve_index():
    return send_from_directory('../public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../public', path)

@app.route('/api/schools', methods=['POST', 'OPTIONS'])
def get_schools():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    schools = data.get('schools', [])
    test_option = data.get('test_pref', '3')

    if test_option in ['1', 1]:
        test_pref = Constants.ACT
    elif test_option in ['2', 2]:
        test_pref = Constants.SAT
    else:
        test_pref = Constants.BOTH

    if not schools:
        return jsonify({'error': 'No schools provided'}), 400

    results = []
    skipped = []

    for school in schools:
        extractor = Extractor(school.strip())
        school_data = extractor.get_full_data(test_pref)

        if school_data:
            ordered_data = reorder_columns(school_data)
            results.append(ordered_data)
        else:
            skipped.append(school)

    response_data = {
        'data': results,
        'skipped': skipped,
        'count': len(results)
    }

    return Response(
        json.dumps(response_data),
        mimetype='application/json'
    )

@app.route('/api/export', methods=['POST', 'OPTIONS'])
def export_csv():
    if request.method == 'OPTIONS':
        return '', 204
        
    data = request.json
    schools_data = data.get('data', [])

    if not schools_data:
        return jsonify({'error': 'No data to export'}), 400

    ordered_schools_data = [reorder_columns(school) for school in schools_data]

    output = io.StringIO()
    fieldnames = [col for col in COLUMN_ORDER if col in ordered_schools_data[0]]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ordered_schools_data)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='college_data.csv'
    )