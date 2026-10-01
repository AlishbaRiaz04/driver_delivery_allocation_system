# Delivery & Driver Allocation Management System

A command-line program that takes drivers and delivery tasks, assigns drivers automatically, calculates delivery charges and driver earnings, tracks task status, and prints operational reports.

Built with plain Python (dataclasses and JSON only, no external packages or frameworks).

## How to run

Requires Python 3.10 or newer.

```
python main.py
```

`input_data.json` must be in the same folder as `main.py`. It contains the `drivers` dictionary and the `deliveries` list.



## Project structure

```
config.py       settings: base charge, urgent surcharge, base earning, bonus rate, currency
models.py       Driver and Task dataclasses, and building objects from the input data
validation.py   checks for the input data, tasks and drivers
pricing.py      delivery charge, driver earning, and total calculations
allocation.py   picking the best driver for each task
status.py       allowed status changes and updating a task's status
reports.py      driver performance report, business report, delivery dashboard
main.py         loads the data and runs the whole flow
input_data.json starter data
```

## How it works

1. `main.py` loads `input_data.json` and checks its structure.
2. Drivers and tasks are created. A bad record is skipped and a message is printed.
3. Each valid pending task is assigned to the best eligible driver (available and in the same zone). The driver then becomes busy.
4. Status updates are applied (`picked_up`, `delivered`, `failed`). The driver becomes available again when a task is delivered or failed.
5. The driver report, business report and dashboard are printed.

Status updates are simulated with a list of events in `main.py`, since there is no real driver app. `delivered` means the customer received the order and `failed` means they did not.

## Design decisions

- **Tie rule:** if two eligible drivers have the same rating, the one with the lower driver ID is chosen. IDs are unique, so the result is always the same.
- **Pricing rule:** the rate of the distance band applies to the whole distance, not in tiers. For example, a 12 km delivery costs 12 x $2.00 for the distance part. A distance such as 5.5 km falls in the 6 to 10 km band.
- **What counts as earned:** delivery charges, driver earnings and zone revenue count delivered tasks only. Pending, assigned, picked up and failed tasks have not earned anything yet.
- **Status flow:** `pending -> assigned -> picked_up -> delivered or failed`. A task cannot be delivered before it is picked up. `assigned -> failed` is rejected on purpose, because a task must be picked up before it can fail. `delivered` and `failed` are final.
- **Driver availability:** a driver becomes busy when assigned and is freed only when the task is delivered or failed, not when it is picked up.
- **Top driver:** the driver with the most delivered tasks. Ties are broken by higher earnings, then by lower driver ID. If nothing has been delivered, the dashboard shows N/A.
- **Unassigned task:** a task that is still pending and has no driver. The reason is shown in the assignment output, for example `No available driver in zone C`.
- **Invalid tasks:** a task with invalid data never takes a driver. It is left out of the reports and listed under `invalid_tasks` in the business report with the reason.

## Configuration

Settings live in the `CONFIG` dictionary in `config.py`. Functions only read it and never modify it, so no `global` keyword is needed. A single call can override a value through `**options`, for example:

```python
calculate_delivery_charge(task, urgent_surcharge=0.5)
calculate_driver_earning(task, bonus_rate=0.2)
```

Totals use `calculate_total(*amounts)`, which accepts any number of values.

## Error handling

The program does not crash on bad input. It handles:

- a missing or invalid `input_data.json`
- input data with the wrong shape (for example `drivers` not being a dictionary)
- a task or driver record with missing or extra fields (skipped and reported)
- a driver with a bad rating, a bad availability value, or an empty name or zone (skipped and reported)
- invalid task data: zero or negative distance, an invalid order amount, an invalid priority or an invalid status
- an invalid task ID, an invalid driver ID, or an invalid status change
- an already assigned task, a busy driver, or no available driver in the zone
- empty drivers or empty deliveries

Any unexpected error prints a message instead of a traceback.

## Assumptions

- Dataclasses and JSON are used, as approved by the team lead.
- A driver's rating is expected to be between 0 and 5.
- The input must contain real numbers for distance and order amount. Text such as `"4"` is rejected as invalid.
