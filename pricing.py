from config import CONFIG
def calculate_delivery_charge(task, **options):

    base_charge=options.get("base_charge", CONFIG["base_charge"])
    urgent_surcharge=options.get("urgent_surcharge", CONFIG["urgent_surcharge"])

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
        priority_surcharge=pre_surcharge_amount*urgent_surcharge
        final_charge=pre_surcharge_amount+priority_surcharge
    else:
        final_charge=pre_surcharge_amount

    return {
        "base_charge": base_charge,
        "distance_charge": distance_rate,
        "priority_surcharge": priority_surcharge,
        "final_charge": final_charge
    }


def calculate_driver_earning(task, **options):

    base_earning=options.get("base_earning", CONFIG["base_earning"])
    bonus_rate=options.get("bonus_rate", CONFIG["bonus_rate"])
    bonus_threshold=options.get("bonus_threshold", CONFIG["bonus_threshold"])

    distance=task.distance
    if distance<=5:
        distance_rate=distance*0.8

    elif distance<=10:
        distance_rate=distance*1.2

    else:
        distance_rate=distance*1.5

    subtotal=base_earning+distance_rate

    bonus=0
    if task.order_amount>=bonus_threshold:
        bonus=subtotal*bonus_rate

    final_earning=subtotal+bonus
    return final_earning

def calculate_total(*amounts):
    return sum(amounts)

