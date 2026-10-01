import json
from validation import validate_data
from utils import create_drivers, create_tasks
from allocation import process_all_assignments
from status import update_task_status
from reports import generate_driver_report, generate_business_report, generate_delivery_dashboard


def main():
    try:
        with open("input_data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: input_data.json not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: input_data.json is not valid JSON ({e}).")
        return

    valid, error = validate_data(data)
    if not valid:
        print(f"Error: {error}")
        return

    driver_objects, driver_errors = create_drivers(data["drivers"])
    task_objects, task_errors = create_tasks(data["deliveries"])
    for message in driver_errors + task_errors:
        print(message)

    #Automatic assignment
    results = process_all_assignments(driver_objects, task_objects)
    for task_id, (driver_id, reason) in results.items():
        print(f"{task_id}: {driver_id if driver_id else reason}")

    # Simulated status updates (a driver app would send these in a real system)
    #added them by myself to test real transitions if happens
    events = [
        ("TASK001", "picked_up"),
        ("TASK001", "delivered"),
        ("TASK002", "picked_up"),
        ("TASK002", "failed"),
    ]
    for task_id, new_status in events:
        ok, message = update_task_status(task_objects, driver_objects, task_id, new_status)
        print(f"{task_id} -> {new_status}: {'OK' if ok else message}")

    #Reports
    driver_report = generate_driver_report(driver_objects, task_objects)
    print("Driver Performance Report".center(50, "="))
    for driver_id, stats in driver_report.items():
        print(driver_id, stats)
    print("-" * 50)

    business_report = generate_business_report(driver_objects, task_objects)
    print("Business Report".center(50,"="))
    for name, value in business_report.items():
        print(f"{name}: {value}")
    print("-"*50)
    generate_delivery_dashboard(driver_objects, task_objects)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")