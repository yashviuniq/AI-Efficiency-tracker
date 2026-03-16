
import schedule
import time
import datetime
import analysis
from colorama import init, Fore, Style

init(autoreset=True)

def check_progress():
    print(Fore.CYAN + f"\n[Reminder System] Checking progress at {datetime.datetime.now().strftime('%H:%M')}...")
    
    report = analysis.calculate_efficiency()
    
    if report.empty:
        print(Fore.YELLOW + "No goals set or activity data found.")
        return

    print("Current Efficiency Report:")
    print(report)

    # Simple logic: If any category is below 20% efficiency by Wednesday, or 50% by Friday, warn user.
    # For now, let's just warn if efficiency is 0 for any goal with > 0 target
    
    for index, row in report.iterrows():
        category = row['category']
        efficiency = row['Efficiency %']
        
        if efficiency < 50.0:
            print(Fore.RED + f"ALERT: Low efficiency in '{category}' ({efficiency}%). Time to focus!")
        else:
            print(Fore.GREEN + f"Great job on '{category}' ({efficiency}%)!")

def start_daemon():
    print("Starting Reminder Daemon...")
    # Schedule check every minute for demonstration purposes
    # In real usage, maybe every few hours
    schedule.every(1).minutes.do(check_progress)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_daemon()
