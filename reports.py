from config import CONFIG
from validation import get_valid_tasks, validate_task
from pricing import calculate_delivery_charge, calculate_driver_earning, calculate_total

# Rule: delivery charges, driver earnings and zone revenue count DELIVERED tasks only.
# Pending, assigned, picked_up and failed tasks have not earned anything yet.


def generate_driver_report(drivers, tasks):
    valid_tasks = get_valid_tasks(tasks)
    driver_stats = {}

    for driver_id in drivers:
        total_assigned_tasks = 0
        delivered_tasks = 0
        failed_tasks = 0
        total_earnings = 0
        total_delivery_distance = 0

        for task in valid_tasks:

            if driver_id == task.driver_id:
                total_assigned_tasks += 1
                # Distance counts every task assigned to this driver
                total_delivery_distance += task.distance

                if task.status == "delivered":
                    delivered_tasks += 1
                    total_earnings += calculate_driver_earning(task)

                if task.status == "failed":
                    failed_tasks += 1

        completion_rate = 0

        if total_assigned_tasks > 0:
            completion_rate = delivered_tasks / total_assigned_tasks * 100

        driver_stats[driver_id] = {
            "name": drivers[driver_id].name,
            "zone": drivers[driver_id].zone,
            "total_assigned_tasks": total_assigned_tasks,
            "delivered_tasks": delivered_tasks,
            "failed_tasks": failed_tasks,
            "total_delivery_distance": total_delivery_distance,
            "total_earnings": total_earnings,
            "completion_rate": completion_rate
        }

    return driver_stats


def generate_business_report(drivers, tasks):
    valid_tasks = get_valid_tasks(tasks)

    # Invalid tasks: keep the ID and the reason so the report explains them
    invalid_tasks = []
    for task in tasks:
        valid, reason = validate_task(task)
        if not valid:
            invalid_tasks.append((task.id, reason))

    unique_zones = set()
    revenue_per_zone = {}
    tasks_per_zone = {}

    total_order_amount = 0
    total_distance = 0
    longest_delivery = None
    longest_distance = 0

    highest_value_order = None
    urgent_deliveries = 0
    tasks_not_assigned = []

    for task in valid_tasks:
        unique_zones.add(task.zone)

        # Tasks per zone (all valid tasks)
        if task.zone in tasks_per_zone:
            tasks_per_zone[task.zone] += 1
        else:
            tasks_per_zone[task.zone] = 1

        # Revenue per zone (delivered tasks only)
        if task.status == "delivered":
            charge = calculate_delivery_charge(task)
            final_charge = charge["final_charge"]

            if task.zone in revenue_per_zone:
                revenue_per_zone[task.zone] += final_charge
            else:
                revenue_per_zone[task.zone] = final_charge

        # Totals
        total_order_amount += task.order_amount
        total_distance += task.distance

        # Longest delivery
        if task.distance > longest_distance:
            longest_distance = task.distance
            longest_delivery = task.id

        # Highest-value order
        if highest_value_order is None:
            highest_value_order = task.id
        elif task.order_amount > next(
                t.order_amount for t in valid_tasks if t.id == highest_value_order
            ):
            highest_value_order = task.id

        # Urgent deliveries
        if task.priority == "urgent":
            urgent_deliveries += 1

        # Unassigned tasks
        if task.status == "pending" and task.driver_id is None:
            tasks_not_assigned.append(task.id)

    available_drivers = []
    busy_drivers = []

    for driver_id, driver in drivers.items():
        if driver.available:
            available_drivers.append(driver_id)
        else:
            busy_drivers.append(driver_id)

    average_order_amount = 0
    average_distance = 0

    if valid_tasks:
        average_order_amount = total_order_amount / len(valid_tasks)
        average_distance = total_distance / len(valid_tasks)

    return {
        "unique_delivery_zones": unique_zones,
        "tasks_per_zone": tasks_per_zone,
        "revenue_per_zone": revenue_per_zone,
        "average_order_amount": average_order_amount,
        "average_distance": average_distance,
        "longest_delivery": longest_delivery,
        "highest_value_order": highest_value_order,
        "urgent_deliveries": urgent_deliveries,
        "tasks_not_assigned": tasks_not_assigned,
        "invalid_tasks": invalid_tasks,
        "available_drivers": available_drivers,
        "busy_drivers": busy_drivers
    }


def get_top_driver(driver_report):
    # Rule: most delivered tasks, then highest earnings, then lowest driver ID
    best_id = None
    for driver_id, stats in driver_report.items():
        if stats["delivered_tasks"] == 0:
            continue
        if best_id is None:
            best_id = driver_id
            continue
        best = driver_report[best_id]
        if (-stats["delivered_tasks"], -stats["total_earnings"], driver_id) < \
           (-best["delivered_tasks"], -best["total_earnings"], best_id):
            best_id = driver_id
    return best_id


def generate_delivery_dashboard(drivers, tasks):
    valid_tasks = get_valid_tasks(tasks)

    total_tasks = len(tasks)
    pending = 0
    assigned = 0
    picked_up = 0
    delivered = 0
    failed = 0

    order_amounts = []
    delivery_charges = []
    driver_earnings = []
    distances = []

    unassigned_tasks = []

    for task in valid_tasks:
        status = task.status

        if status == "pending":
            pending += 1
        elif status == "assigned":
            assigned += 1
        elif status == "picked_up":
            picked_up += 1
        elif status == "delivered":
            delivered += 1
            # Only delivered tasks count as earned
            delivery_charges.append(calculate_delivery_charge(task)["final_charge"])
            driver_earnings.append(calculate_driver_earning(task))
        elif status == "failed":
            failed += 1

        if task.status == "pending" and task.driver_id is None:
            unassigned_tasks.append(task.id)

        order_amounts.append(task.order_amount)
        distances.append(task.distance)

    total_order_amount = calculate_total(*order_amounts)
    total_delivery_charges = calculate_total(*delivery_charges)
    total_driver_earning = calculate_total(*driver_earnings)
    total_delivery_distance = calculate_total(*distances)

    # Top driver
    driver_report = generate_driver_report(drivers, tasks)
    top_driver_id = get_top_driver(driver_report)
    if top_driver_id is None:
        top_driver_text = "N/A"
    else:
        top_driver_text = f"{drivers[top_driver_id].name} ({top_driver_id})"

    # Highest revenue zone
    business_report = generate_business_report(drivers, tasks)
    revenue_per_zone = business_report["revenue_per_zone"]

    top_zone = max(revenue_per_zone, key=lambda zone: revenue_per_zone[zone], default=None)
    top_zone_text = top_zone if top_zone else "N/A"

    if len(valid_tasks) == 0:
        average_distance = 0
    else:
        average_distance = total_delivery_distance / len(valid_tasks)

    currency = CONFIG["currency"]
    print("Delivery Dashboard".center(50, "="))
    print(f"Total Tasks: {total_tasks}")
    print(f"Pending: {pending}")
    print(f"Assigned: {assigned}")
    print(f"Picked Up: {picked_up}")
    print(f"Delivered: {delivered}")
    print(f"Failed: {failed}")
    print(f"Total Order Value: {currency}{total_order_amount:.2f}")
    print(f"Total Delivery Charges: {currency}{total_delivery_charges:.2f}")
    print(f"Total Driver Earnings: {currency}{total_driver_earning:.2f}")
    print(f"Top Driver: {top_driver_text}")
    print(f"Highest Revenue Zone: {top_zone_text}")
    print(f"Average Delivery Distance: {average_distance:.2f}")

    print("Unassigned Tasks:")
    if len(unassigned_tasks) == 0:
        print("\tNo unassigned tasks")
    else:
        for task_id in unassigned_tasks:
            print(f"\t{task_id}")
    print("=" * 50)