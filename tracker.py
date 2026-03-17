
import sqlite3
import datetime
from database import get_db_connection

def log_activity(activity_name, category, duration_minutes):
    """
    Logs an activity into the database.
    """
    activity_name = activity_name.strip().title()
    category = category.strip().title()
    
    conn = get_db_connection()
    c = conn.cursor()
    
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(minutes=duration_minutes)
    
    c.execute('''
        INSERT INTO activities (activity_name, category, start_time, end_time, duration_minutes)
        VALUES (?, ?, ?, ?, ?)
    ''', (activity_name, category, start_time, end_time, duration_minutes))
    
    conn.commit()
    conn.close()
    print(f"Logged '{activity_name}' ({category}) for {duration_minutes} minutes.")

def set_goal(category, target_hours):
    """
    Sets or updates a weekly goal for a category.
    """
    category = category.strip().title()
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # We'll set the goal starting from the current week's Monday
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    
    # Check if goal exists, if so update, else insert
    # Using INSERT OR REPLACE would require a primary key, but category is unique
    c.execute('''
        INSERT INTO goals (category, target_hours_per_week, week_start_date)
        VALUES (?, ?, ?)
        ON CONFLICT(category) DO UPDATE SET
            target_hours_per_week=excluded.target_hours_per_week,
            week_start_date=excluded.week_start_date
    ''', (category, target_hours, week_start))
    
    conn.commit()
    conn.close()
    print(f"Goal set for '{category}': {target_hours} hours/week.")

def get_goals():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM goals')
    goals = c.fetchall()
    conn.close()
    return goals

def get_activities_since(start_date):
    conn = get_db_connection()
    # Ensure start_date matches the TIMESTAMP format or date function in sqlite
    # Here we perform simple string comparison or use datetime objects
    # sqlite stores datetime as strings usually
    c = conn.cursor()
    c.execute('SELECT * FROM activities WHERE start_time >= ?', (start_date,))
    activities = c.fetchall()
    conn.close()
    return activities
