import unittest

from utils import create_tasks
from pricing import calculate_delivery_charge
from validation import validate_task


class TestPricing(unittest.TestCase):

    def test_normal_task_charge(self):
        # TASK001: 4 km, normal -> base 5 + distance 4 x 1.00 = 9.00
        raw = [{"id": "T1", "customer": "Test", "zone": "A", "distance": 4,
                "order_amount": 120, "priority": "normal", "status": "pending"}]
        tasks, errors = create_tasks(raw)

        charge = calculate_delivery_charge(tasks[0])

        self.assertAlmostEqual(charge["final_charge"], 9.0)

    def test_urgent_task_charge(self):
        # TASK002: 12 km, urgent -> distance 12 x 2.00 = 24, plus base 5 = 29,
        # then 25% urgent surcharge on 29 = 7.25, final = 36.25
        raw = [{"id": "T2", "customer": "Test", "zone": "B", "distance": 12,
                "order_amount": 80, "priority": "urgent", "status": "pending"}]
        tasks, errors = create_tasks(raw)

        charge = calculate_delivery_charge(tasks[0])

        self.assertAlmostEqual(charge["final_charge"], 36.25)


class TestValidation(unittest.TestCase):

    def test_zero_distance_is_rejected(self):
        raw = [{"id": "T3", "customer": "Test", "zone": "A", "distance": 0,
                "order_amount": 100, "priority": "normal", "status": "pending"}]
        tasks, errors = create_tasks(raw)

        ok, message = validate_task(tasks[0])

        self.assertFalse(ok)
        self.assertEqual(message, "Distance cannot be zero")


if __name__ == "__main__":
    unittest.main()