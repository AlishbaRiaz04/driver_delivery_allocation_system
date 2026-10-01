from validation import validate_task

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
        return None, f"Task {task.id} is already {task.status}"

    if not eligible_drivers:
        return None, f"No available driver in zone {task.zone}"

    selected=sorted(eligible_drivers, key=lambda d: (-d.rating, d.driver_id))[0]

    task.status="assigned"
    task.driver_id=selected.driver_id
    selected.available=False

    return selected.driver_id, None

def process_all_assignments(drivers, tasks):
    results={}
    for task in tasks:
        valid, reason=validate_task(task)
        if not valid:
            results[task.id]= (None, reason)
            continue
        eligible_drivers=get_eligible_drivers(drivers, task)
        results[task.id]=assign_driver(eligible_drivers, task)
    return results
