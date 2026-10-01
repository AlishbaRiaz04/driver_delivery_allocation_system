from models import Task, Driver


def create_drivers(drivers):
    driver_objects = {}
    errors = []
    for driver_id, driver_info in drivers.items():
        try:
            driver_objects[driver_id] = Driver(driver_id, **driver_info)
        except TypeError as e:
            errors.append(f"Skipped bad driver record {driver_id}: {e}")
    return driver_objects, errors


def create_tasks(deliveries):
    task_objects = []
    errors = []
    for raw in deliveries:
        try:
            task_objects.append(Task(**raw))
        except TypeError as e:
            errors.append(f"Skipped bad task record {raw}: {e}")
    return task_objects, errors