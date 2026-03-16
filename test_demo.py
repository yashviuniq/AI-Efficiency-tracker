
import tracker
import analysis
import database
import time
import os

def test_system():
    print("Initializing DB...")
    database.init_db()
    
    print("Testing Goal Setting...")
    tracker.set_goal("Work", 40.0)
    tracker.set_goal("Exercise", 5.0)
    
    print("Testing Activity Logging...")
    tracker.log_activity("Writing Code", "Work", 120)  # 2 hours
    tracker.log_activity("Running", "Exercise", 30)    # 0.5 hours
    tracker.log_activity("Debugging", "Work", 60)      # 1 hour
    
    print("Testing Efficiency Calculation...")
    report = analysis.calculate_efficiency()
    print("Report Output:")
    print(report)
    
    # Assertions / Validations
    work_row = report[report['category'] == 'Work'].iloc[0]
    exercise_row = report[report['category'] == 'Exercise'].iloc[0]
    
    assert work_row['Actual Hours'] == 3.0, f"Expected 3.0 hours Work, got {work_row['Actual Hours']}"
    assert exercise_row['Actual Hours'] == 0.5, f"Expected 0.5 hours Exercise, got {exercise_row['Actual Hours']}"
    
    # Efficiency for Work: 3/40 = 7.5%
    # Efficiency for Exercise: 0.5/5 = 10%
    
    print("\nVerifying ML Training (Smoke Test)...")
    clf = analysis.ActivityClassifier()
    # Need more data for actual training to work nicely, but we run the function to ensure no crash
    clf.train()
    pred = clf.predict_category("Writing Code")
    print(f"Prediction for 'Writing Code': {pred}")

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    test_system()
