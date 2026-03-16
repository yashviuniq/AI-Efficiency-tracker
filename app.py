
from flask import Flask, render_template, request, jsonify
import tracker
import analysis
import database

app = Flask(__name__)

# Ensure DB is initialized
database.init_db()
# Ensure model is ready (try loading)
classifier = analysis.ActivityClassifier()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    report = analysis.calculate_efficiency()
    if report.empty:
        return jsonify([])
    # Convert dataframe to list of dicts
    return jsonify(report.to_dict(orient='records'))

@app.route('/api/log', methods=['POST'])
def log_activity_api():
    data = request.json
    activity = data.get('activity')
    category = data.get('category')
    duration = data.get('duration')
    
    if not all([activity, category, duration]):
        return jsonify({"error": "Missing fields"}), 400
        
    try:
        duration = float(duration)
    except ValueError:
        return jsonify({"error": "Invalid duration"}), 400
        
    tracker.log_activity(activity, category, duration)
    return jsonify({"message": "Logged successfully"})

@app.route('/api/goal', methods=['POST'])
def set_goal_api():
    data = request.json
    category = data.get('category')
    hours = data.get('hours')
    
    if not all([category, hours]):
        return jsonify({"error": "Missing fields"}), 400
        
    try:
        hours = float(hours)
    except ValueError:
        return jsonify({"error": "Invalid hours"}), 400
        
    tracker.set_goal(category, hours)
    return jsonify({"message": "Goal updated"})

@app.route('/api/predict_category', methods=['GET'])
def predict_category_api():
    activity = request.args.get('activity')
    if not activity:
        return jsonify({"category": None})
        
    category = classifier.predict_category(activity)
    return jsonify({"category": category})

@app.route('/api/train_model', methods=['POST'])
def train_model_api():
    classifier.train()
    return jsonify({"message": "Model trained"})

if __name__ == '__main__':
    app.run(debug=True)
