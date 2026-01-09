import json
from data import Extractor, Constants
import csv
from flask import Flask, Response, render_template, jsonify, request, send_file
from flask_cors import CORS
import io

app = Flask(__name__)
# CORS(app, resources={
#     r"/api/*": {
#         "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
#         "methods": ["GET", "POST"],
#         "allow_headers": ["Content-Type"]
#     }
# })
CORS(app, resources={r"/api/*": {"origins": "https://briannalewis7.github.io"}})

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
    
    # Add any keys that weren't in COLUMN_ORDER (just in case)
    for key in data:
        if key not in ordered:
            ordered[key] = data[key]
    
    return ordered

# ============ API ROUTES ============

@app.route('/api/schools', methods=['POST'])
def get_schools():
    """Get data for multiple schools"""
    data = request.json
    schools = data.get('schools', [])
    test_option = data.get('test_pref', '3')  # Default to both
    
    # Convert frontend value to Constants
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
            # Reorder the data to maintain consistent column order
            ordered_data = reorder_columns(school_data)
            results.append(ordered_data)
        else:
            skipped.append(school)
    
        # Use Response with json.dumps to preserve order
    response_data = {
        'data': results,
        'skipped': skipped,
        'count': len(results)
    }
    
    return Response(
        json.dumps(response_data),
        mimetype='application/json'
    )


@app.route('/api/export', methods=['POST'])
def export_csv():
    """Export schools to CSV and return the file"""
    data = request.json
    schools_data = data.get('data', [])
    
    if not schools_data:
        return jsonify({'error': 'No data to export'}), 400
    
    # Reorder each school's data
    ordered_schools_data = [reorder_columns(school) for school in schools_data]
    
    # Create CSV in memory with explicit field order
    output = io.StringIO()
    
    # Use COLUMN_ORDER but filter to only fields that exist
    fieldnames = [col for col in COLUMN_ORDER if col in ordered_schools_data[0]]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ordered_schools_data)
    
    # Convert to bytes for download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='college_data.csv'
    )

