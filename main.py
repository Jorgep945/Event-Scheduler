# main.py
# Author: Jorge
# Date: April 2026
# Description:
#   Menu-driven driver program for event_scheduler.py.
#   Simulates a do-while loop to allow repeated user interaction.

from Event_scheduler import EventScheduler

import time

def print_menu():
    print("\n===== EVENT SCHEDULER MENU =====")
    print("1. Add Event")
    print("2. Cancel Event")
    print("3. Update Priority")
    print("4. Get Event by ID")
    print("5. Peek Next Event")
    print("6. Pop Next Event")
    print("7. Events in Timestamp Range")
    print("8. Load Sample Data")
    print("9. Exit")
    print("================================")

def main():
    scheduler = EventScheduler()

    while True:   # do-while simulation
        print_menu()
        choice = input("Enter your choice: ").strip()

        # ---------------------------------------------------------
        # 1. Add Event
        # ---------------------------------------------------------
        if choice == "1":
            event_id = input("Event ID: ").strip()
            title = input("Title: ").strip()
            timestamp = float(input("Timestamp (float): "))
            priority = int(input("Priority (int): "))
            duration = float(input("Duration (float): "))

            scheduler.add_event(event_id, title, timestamp, priority, duration)
            print("Event added successfully.")

        # ---------------------------------------------------------
        # 2. Cancel Event
        # ---------------------------------------------------------
        elif choice == "2":
            event_id = input("Event ID to cancel: ").strip()
            if scheduler.cancel_event(event_id):
                print("Event cancelled.")
            else:
                print("Event not found.")

        # ---------------------------------------------------------
        # 3. Update Priority
        # ---------------------------------------------------------
        elif choice == "3":
            event_id = input("Event ID: ").strip()
            new_priority = int(input("New Priority: "))
            if scheduler.update_priority(event_id, new_priority):
                print("Priority updated.")
            else:
                print("Event not found.")

        # ---------------------------------------------------------
        # 4. Get Event
        # ---------------------------------------------------------
        elif choice == "4":
            event_id = input("Event ID: ").strip()
            ev = scheduler.get_event(event_id)
            if ev:
                print(ev)
            else:
                print("Event not found.")

        # ---------------------------------------------------------
        # 5. Peek Next Event
        # ---------------------------------------------------------
        elif choice == "5":
            ev = scheduler.peek_next()
            if ev:
                print("Next Event:", ev)
            else:
                print("No events available.")

        # ---------------------------------------------------------
        # 6. Pop Next Event
        # ---------------------------------------------------------
        elif choice == "6":
            ev = scheduler.pop_next()
            if ev:
                print("Popped Event:", ev)
            else:
                print("No events available.")

        # ---------------------------------------------------------
        # 7. Events in Range
        # ---------------------------------------------------------
        elif choice == "7":
            start_ts = float(input("Start timestamp: "))
            end_ts = float(input("End timestamp: "))
            events = scheduler.events_in_range(start_ts, end_ts)
            if events:
                print("\nEvents in range:")
                for ev in events:
                    print(ev)
            else:
                print("No events found in range.")

        # ---------------------------------------------------------
        # 8. Load Sample Data
        # ---------------------------------------------------------
        elif choice == "8":
            scheduler.load_sample_data()
            print("Sample data loaded.")

        # ---------------------------------------------------------
        # 9. Exit
        # ---------------------------------------------------------
        elif choice == "9":
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
