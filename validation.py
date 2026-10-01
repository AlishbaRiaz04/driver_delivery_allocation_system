import math
#validate driver is missing here

def validate_data(data):

    if not isinstance(data, dict):
        return False, "Data should be a dict"
    if not isinstance(data.get("drivers"), dict):
        return False, "Drivers should be a dict"
    if not isinstance(data.get("deliveries"), list):
        return False, "Deliveries should be a List"
    return True, None

def validate_driver(driver):
    if not isinstance(driver.name, str) or not driver.name.strip():
        return False, "Driver name cannot be empty"

    if not isinstance(driver.zone, str) or not driver.zone.strip():
        return False, "Driver zone cannot be empty"

    if not isinstance(driver.available, bool):
        return False, "Driver availability must be True or False"

    # bool is a kind of int in Python, so exclude it explicitly
    if isinstance(driver.rating, bool) or not isinstance(driver.rating, (int, float)):
        return False, "Driver rating must be a number"

    if not math.isfinite(driver.rating) or not 0 <= driver.rating <= 5:
        return False, "Driver rating must be between 0 and 5"

    return True, None

def validate_task(task):

    if isinstance(task.distance, bool) or not isinstance(task.distance, (int, float)):
        return False, "Distance must be a number"
    distance = task.distance

    if not math.isfinite(distance):
        return False, "Distance must be a real number"
    if distance < 0:
        return False, "Distance cannot be negative"
    if distance == 0:
        return False, "Distance cannot be zero"

    if isinstance(task.order_amount, bool) or not isinstance(task.order_amount, (int, float)):
        return False, "Order amount must be a number"
    order_amount = task.order_amount

    if  not math.isfinite(order_amount) or order_amount<=0:
        return False, "Order amount must be greater than zero"

    if not isinstance(task.zone, str) or not task.zone.strip():
        return False, "Zone cannot be empty"

    valid_priority=["normal", "urgent"]
    if task.priority not in valid_priority:
        return False, "Invalid Priority"

    valid_status=["pending", "assigned", "picked_up", "delivered","failed"]
    if task.status not in valid_status:
        return False, "Invalid status"

    return True, None

def get_valid_tasks(tasks):
    return [task for task in tasks if validate_task(task)[0]]