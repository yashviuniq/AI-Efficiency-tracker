
import pandas as pd
import datetime
from database import get_db_connection
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pickle
import os

MODEL_FILE = "activity_classifier.pkl"

def calculate_efficiency():
    """
    Calculates efficiency based on logged activities vs weekly goals.
    Returns a DataFrame with columns: [Category, Target Hours, Actual Hours, Efficiency %]
    """
    conn = get_db_connection()
    
    # Get Goals
    goals_df = pd.read_sql_query("SELECT * FROM goals", conn)
    if goals_df.empty:
        conn.close()
        return pd.DataFrame()

    # Get Activities for the current week
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    
    # Filter activities since week_start
    # Note: sqlite timestamp strings need to be handled.
    # We will fetch all and filter in pandas for simplicity in this MVP, 
    # or rely on string comparison if format matches.
    activities_df = pd.read_sql_query(
        "SELECT * FROM activities WHERE start_time >= ?", 
        conn, 
        params=(week_start,)
    )
    conn.close()
    
    if activities_df.empty:
        report = goals_df.copy()
        report['Actual Hours'] = 0.0
        report['Efficiency %'] = 0.0
        return report[['category', 'target_hours_per_week', 'Actual Hours', 'Efficiency %']]

    # Group by category
    summary = activities_df.groupby('category')['duration_minutes'].sum().reset_index()
    summary['Actual Hours'] = summary['duration_minutes'] / 60.0
    
    # Merge with goals
    report = pd.merge(goals_df, summary, on='category', how='left')
    report['Actual Hours'] = report['Actual Hours'].fillna(0.0)
    
    report['Efficiency %'] = (report['Actual Hours'] / report['target_hours_per_week']) * 100
    report['Efficiency %'] = report['Efficiency %'].round(2)
    
    return report[['category', 'target_hours_per_week', 'Actual Hours', 'Efficiency %']]

class ActivityClassifier:
    def __init__(self):
        self.model = None
        self.load_model()

    def train(self):
        """
        Trains the model on existing data in the database.
        """
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT activity_name, category FROM activities", conn)
        conn.close()
        
        if len(df) < 5:
            print("Not enough data to train model (need at least 5 entries).")
            return

        X = df['activity_name']
        y = df['category']
        
        self.model = make_pipeline(CountVectorizer(), MultinomialNB())
        self.model.fit(X, y)
        
        # Save model
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(self.model, f)
        print("Model trained and saved.")

    def load_model(self):
        if os.path.exists(MODEL_FILE):
            with open(MODEL_FILE, 'rb') as f:
                self.model = pickle.load(f)

    def predict_category(self, activity_name):
        if self.model:
            try:
                prediction = self.model.predict([activity_name])[0]
                return prediction
            except Exception:
                return None
        return None
