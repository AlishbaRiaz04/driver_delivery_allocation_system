from dataclasses import dataclass
import json


@dataclass
class Driver:
    driver_id:str
    name:str
    zone:str
    available:bool
    rating: float

@dataclass
class Task:
    id:str
    customer:str
    zone:str
    distance:int
    order_amount:int
    priority:str
    status:str

def validate_data(data):

    if not isinstance(data, dict):
        return False, "Data should be a dict"
    if not isinstance(data.get("drivers"), dict):
        return False, "Drivers should be a dict"
    if not isinstance(data.get("deliveries"), list):
        return False, "Deliveies should be a List"
    return True, None

def create_drivers(drivers):
    driver_objects={}
    for driver_id, driver_info in drivers.items():
        driver=Driver(driver_id, **driver_info)
        driver_objects[driver_id]=driver

    return driver_objects

def create_tasks(deliveries):
    task_objects=[]
    for task in deliveries:
        t=Task(**task)
        task_objects.append(t)
    return task_objects
def validate_task(task):

    if not task.distance>0:
        return False, "Distance must be greater than zero"

    if not task.order_amount>0:
        return False, "Order amount must be greater than zero"

    valid_priority=["normal", "urgent"]
    if not task.priority in valid_priority:
        return False, "Invalid Priority"

    valid_status=["pending", "assigned", "picked_up", "delivered","failed"]
    if not task.status in valid_status:
        return False, "Invalid status"

    return True, None

def get_eligible_drivers(drivers, task):
    eligible_drivers=[]
    zone=task.zone
    for driver_object in drivers.values():
        if driver_object.available:
            if driver_object.zone==zone:
                eligible_drivers.append(driver_object)
    return eligible_drivers


def assign_driver(eligible_drivers,task):

    if task.status != "pending":
        return None

    if not eligible_drivers:
        return None

    highest_rating = 0
    top_drivers = []

    for driver in eligible_drivers:
        rating = driver.rating

        if rating > highest_rating:
            highest_rating = rating
            top_drivers.clear()
            top_drivers.append(driver)

        elif rating == highest_rating:
            top_drivers.append(driver)

    if len(top_drivers) > 1:
        top_drivers = sorted(top_drivers, key=lambda driver: driver.name)

    selected_driver = top_drivers[0]

    task.status = "assigned"
    task.driver_id = selected_driver.driver_id
    selected_driver.available = False

    return selected_driver.driver_id

def process_all_assignments(drivers, tasks):
    assignments={}
    for task in tasks:
        eligible_drivers=get_eligible_drivers(drivers, task)
        assigned_driver=assign_driver(eligible_drivers, task)
        assignments[task.id]=assigned_driver

    return assignments

def calculate_delivery_charge(task):
    base_charge=5
    distance_rate=0
    distance=task.distance
    if distance<=5:
        distance_rate=distance*1
    elif distance<=10:
        distance_rate=distance*1.5
    else:
        distance_rate=distance*2

    pre_surcharge_amount=distance_rate+base_charge
    priority_surcharge=0
    if task.priority=="urgent":
        priority_surcharge=pre_surcharge_amount*0.25
        final_charge=pre_surcharge_amount+priority_surcharge
    else:
        final_charge=pre_surcharge_amount

    return {
        "base_charge": base_charge,
        "distance_charge": distance_rate,
        "priority_surcharge": priority_surcharge,
        "final_charge": final_charge
    }


def calculate_driver_earning(task):
    base_earning=3
    distance_rate=0
    distance=task.distance
    if distance<=5:
        distance_rate=distance*0.8

    elif distance<=10:
        distance_rate=distance*1.2

    else:
        distance_rate=distance*1.5

    subtotal=base_earning+distance_rate
    order_amount=task.order_amount
    bonus=0
    if order_amount>=150:
        bonus=subtotal*0.1

    final_earning=subtotal+bonus
    return final_earning

def update_task_status(task, new_status, driver):
    status=task.status
    if status=="assigned" and new_status=="picked_up":
        task.status=new_status
        return True, None
    if status=="picked_up":
        if new_status=="failed" or new_status=="delivered":
            task.status=new_status
            driver.available = True
            return True, None

    return False,"Invalid Transition"

def generate_driver_report(drivers, tasks, assignments):
    driver_stats = {}

    for driver_id in drivers:
        total_assigned_tasks = 0
        delivered_task = 0
        failed_task = 0
        total_earnings = 0
        total_delivery_distance = 0

        for task in tasks:
            assigned_driver = assignments[task.id]

            if driver_id == assigned_driver:
                total_assigned_tasks += 1
                total_delivery_distance += task.distance

                if task.status == "delivered":
                    delivered_task += 1

                if task.status == "failed":
                    failed_task += 1

                total_earnings += calculate_driver_earning(task)

        completion_rate = 0

        if total_assigned_tasks > 0:
            completion_rate = delivered_task / total_assigned_tasks * 100

        driver_stats[driver_id] = {
            "name": drivers[driver_id].name,
            "zone": drivers[driver_id].zone,
            "total_assigned_tasks": total_assigned_tasks,
            "delivered_tasks": delivered_task,
            "failed_tasks": failed_task,
            "total_delivery_distance": total_delivery_distance,
            "total_earnings": total_earnings,
            "completion_rate": completion_rate
        }

    return driver_stats


def generate_business_report(drivers, tasks, assignments):
    unique_zones = set()
    revenue_per_zone = {}
    tasks_per_zone = {}

    total_order_amount = 0
    longest_delivery = None
    longest_distance = 0

    highest_value_order = None
    urgent_deliveries = 0
    tasks_not_assigned = []

    for task in tasks:
        unique_zones.add(task.zone)

        # Tasks per zone
        if task.zone in tasks_per_zone:
            tasks_per_zone[task.zone] += 1
        else:
            tasks_per_zone[task.zone] = 1

        # Revenue per zone
        charge = calculate_delivery_charge(task)
        final_charge = charge["final_charge"]

        if task.zone in revenue_per_zone:
            revenue_per_zone[task.zone] += final_charge
        else:
            revenue_per_zone[task.zone] = final_charge

        # Total order amount
        total_order_amount += task.order_amount

        # Longest delivery
        if task.distance > longest_distance:
            longest_distance = task.distance
            longest_delivery = task.id

        # Highest-value order
        if highest_value_order is None:
            highest_value_order = task.id
        elif task.order_amount > next(
            t.order_amount for t in tasks if t.id == highest_value_order
        ):
            highest_value_order = task.id

        # Urgent deliveries
        if task.priority == "urgent":
            urgent_deliveries += 1

        # Unassigned tasks
        if assignments[task.id] is None:
            tasks_not_assigned.append(task.id)

    available_drivers = []
    busy_drivers = []

    for driver_id, driver in drivers.items():
        if driver.available:
            available_drivers.append(driver_id)
        else:
            busy_drivers.append(driver_id)

    average_order_amount = 0

    if tasks:
        average_order_amount = total_order_amount / len(tasks)

    return {
        "unique_delivery_zones": unique_zones,
        "tasks_per_zone": tasks_per_zone,
        "revenue_per_zone": revenue_per_zone,
        "average_order_amount": average_order_amount,
        "longest_delivery": longest_delivery,
        "highest_value_order": highest_value_order,
        "urgent_deliveries": urgent_deliveries,
        "tasks_not_assigned": tasks_not_assigned,
        "available_drivers": available_drivers,
        "busy_drivers": busy_drivers
    }


def generate_delivery_dashboard(drivers, tasks, assignments):
    total_tasks = len(tasks)
    pending = 0
    assigned = 0
    picked_up = 0
    delivered = 0
    failed = 0

    total_order_amount = 0
    total_delivery_charges = 0
    total_driver_earning = 0
    total_delivery_distance = 0

    unassigned_tasks = []

    for task in tasks:
        status = task.status

        if status == "pending":
            pending += 1
        elif status == "assigned":
            assigned += 1
        elif status == "picked_up":
            picked_up += 1
        elif status == "delivered":
            delivered += 1
        elif status == "failed":
            failed += 1

        if assignments.get(task.id) is None:
            unassigned_tasks.append(task.id)

        total_order_amount += task.order_amount
        total_delivery_charges += calculate_delivery_charge(task)["final_charge"]
        total_driver_earning += calculate_driver_earning(task)
        total_delivery_distance += task.distance

    if len(tasks) == 0:
        average_distance = 0
    else:
        average_distance = total_delivery_distance / len(tasks)

    print("Delivery Dashboard".center(50, "="))
    print(f"Total Tasks: {total_tasks}")
    print(f"Pending: {pending}")
    print(f"Assigned: {assigned}")
    print(f"Picked Up: {picked_up}")
    print(f"Delivered: {delivered}")
    print(f"Failed: {failed}")
    print(f"Total Order Value: ${total_order_amount}")
    print(f"Total Delivery Charges: ${total_delivery_charges}")
    print(f"Total Driver Earnings: ${total_driver_earning}")
    print(f"Average Delivery Distance: {average_distance:.2f}")

    print("Unassigned Tasks:")
    if len(unassigned_tasks) == 0:
        print("\tNo unassigned tasks")
    else:
        for task_id in unassigned_tasks:
            print(f"\t{task_id}")


if __name__=="__main__":
    with open("input_data.json", "r") as file:
        data=json.load(file)
    driver_objects=create_drivers(data["drivers"])
    task_objects=create_tasks(data["deliveries"])
    assignments=process_all_assignments(driver_objects, task_objects)

    generate_delivery_dashboard(driver_objects, task_objects, assignments)















