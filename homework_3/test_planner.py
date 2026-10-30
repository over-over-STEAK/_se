import unittest
import tempfile
from pathlib import Path
from datetime import date
from copy import deepcopy
from main import schedule, demo_data, save, load, minutes

class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.day = date(2026, 10, 30)
        self.data = demo_data(self.day)

    def test_capacity_and_deadlines(self):
        rows, warnings = schedule(self.data, self.day, 7)
        for day in {r[0] for r in rows}:
            self.assertLessEqual(sum(r[2] for r in rows if r[0] == day), 120)
        self.assertTrue(all(day <= due for day, _, _, due in rows))
        self.assertEqual(sum(r[2] for r in rows), 480)
        self.assertEqual(len(warnings), 1)
        self.assertIn('60 分鐘', warnings[0])

    def test_does_not_change_progress(self):
        before = deepcopy(self.data)
        schedule(self.data, self.day, 7)
        self.assertEqual(before, self.data)

    def test_overdue(self):
        self.data['tasks'] = [self.data['tasks'][0]]
        rows, warnings = schedule(self.data, date(2026, 10, 31), 7)
        self.assertEqual(rows, [])
        self.assertIn('已逾期', warnings[0])

    def test_outside_horizon(self):
        self.data['tasks'] = [self.data['tasks'][1]]
        _, warnings = schedule(self.data, self.day, 1)
        self.assertIn('尚未判定', warnings[0])

    def test_complete(self):
        for task in self.data['tasks']:
            task['remaining'] = 0
        self.assertEqual(schedule(self.data, self.day, 7), ([], []))

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'tasks.json'
            save(path, self.data)
            self.assertEqual(load(path), self.data)

    def test_invalid_hours(self):
        for value in ['-1', '0', 'NaN', 'Infinity', 'abc', '0.001']:
            with self.assertRaises(ValueError):
                minutes(value)
        self.assertEqual(minutes('1.5'), 90)

    def test_empty(self):
        self.data['tasks'] = []
        self.assertEqual(schedule(self.data, self.day, 1), ([], []))

    def test_invalid_capacity(self):
        self.data['daily_minutes'] = 0
        with self.assertRaises(ValueError):
            schedule(self.data, self.day, 7)

if __name__ == '__main__':
    unittest.main(verbosity=2)
