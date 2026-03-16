
import sys
import subprocess
import tracker
import analysis
from colorama import init, Fore, Style

init(autoreset=True)

def print_header():
    print(Fore.BLUE + Style.BRIGHT + "="*50)
    print(Fore.BLUE + Style.BRIGHT + "   AI PERSONAL EFFICIENCY TRACKER   ")
    print(Fore.BLUE + Style.BRIGHT + "="*50)

def main_menu():
    classifier = analysis.ActivityClassifier()
    
    while True:
        print_header()
        print("1. Log Activity")
        print("2. Set Weekly Goal")
        print("3. View Efficiency Report")
        print("4. Train AI Model (Update based on history)")
        print("5. Start Reminder Daemon")
        print("6. Exit")
        
        choice = input(Fore.YELLOW + "\nEnter your choice: ")
        
        if choice == '1':
            activity = input("Enter activity name (e.g., 'Coding Python'): ")
            
            # Suggest category using AI
            suggested_category = classifier.predict_category(activity)
            if suggested_category:
                print(f"AI Suggestion: Is this '{suggested_category}'? (y/n)")
                if input().lower() == 'y':
                    category = suggested_category
                else:
                    category = input("Enter category (e.g., Work, Study, Leisure): ")
            else:
                category = input("Enter category (e.g., Work, Study, Leisure): ")
                
            try:
                duration = float(input("Enter duration in minutes: "))
                tracker.log_activity(activity, category, duration)
                print(Fore.GREEN + "Activity Request Logged Successfully!")
            except ValueError:
                print(Fore.RED + "Invalid duration. Please enter a number.")
                
        elif choice == '2':
            category = input("Enter category to set goal for: ")
            try:
                hours = float(input("Enter target hours per week: "))
                tracker.set_goal(category, hours)
                print(Fore.GREEN + "Goal updated!")
            except ValueError:
                print(Fore.RED + "Invalid number.")

        elif choice == '3':
            print(Fore.CYAN + "\n--- Efficiency Report ---")
            report = analysis.calculate_efficiency()
            if not report.empty:
                print(report.to_string(index=False))
            else:
                print("No data available.")
            input("\nPress Enter to continue...")

        elif choice == '4':
            print("Training model on your history...")
            classifier.train()
            print(Fore.GREEN + "Model updated!")
            
        elif choice == '5':
            print(Fore.MAGENTA + "Starting daemon in separate window...")
            subprocess.Popen([sys.executable, 'reminder_daemon.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("Daemon started.")
            
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print(Fore.RED + "Invalid choice.")

if __name__ == "__main__":
    main_menu()
