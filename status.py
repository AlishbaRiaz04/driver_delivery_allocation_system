VALID_STATUSES = {"pending", "assigned", "picked_up", "delivered", "failed"}

TRANSITIONS = {
    "pending": {"assigned"},
    "assigned": {"picked_up"},
    "picked_up": {"delivered", "failed"},
}

def update_task_status(tasks, drivers, task_id, new_status):
    task = next((t for t in tasks if t.id == task_id), None)
    if task is None:
        return False, f"Invalid task ID: {task_id}"

    if new_status not in VALID_STATUSES:
        return False, f"Invalid status: {new_status}"

    if task.status in ("delivered", "failed"):
        return False, f"Task {task_id} is already {task.status}"

    if new_status not in TRANSITIONS.get(task.status, set()):
        return False, f"Cannot move {task_id} from {task.status} to {new_status}"

    driver = drivers.get(task.driver_id)
    if new_status in ("delivered", "failed") and driver is None:
        return False, f"Invalid driver ID: {task.driver_id}"

    task.status = new_status

    # Task is finished, so the driver becomes available again
    if new_status in ("delivered", "failed"):
        driver.available = True

    return True, None


