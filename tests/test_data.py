"""Recompute every row with QuantLib (Federal Reserve calendar + date arithmetic) and check the banking days
against the `holidays` package (XFED). Both are independent of the generator that wrote the files.

    pip install QuantLib holidays
    python -m unittest discover -s tests -v
"""
import csv
import os
import unittest
from datetime import date, timedelta

import holidays
import QuantLib as ql

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
CAL = ql.UnitedStates(ql.UnitedStates.FederalReserve)


def rows(name):
    with open(os.path.join(DATA, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def qd(s):
    d = date.fromisoformat(s)
    return ql.Date(d.day, d.month, d.year)


def iso(q):
    return f"{q.year():04d}-{q.month():02d}-{q.dayOfMonth():02d}"


class Data(unittest.TestCase):
    def test_pay_dates(self):
        rs = rows("pay_dates_2026_2028.csv")
        self.assertEqual(len(rs), 1816)
        for r in rs:
            q = qd(r["nominal_date"])
            pre = CAL.adjust(q, ql.Preceding)
            self.assertEqual(r["pay_date_preceding"], iso(pre), r)
            self.assertEqual(r["pay_date_following"], iso(CAL.adjust(q, ql.Following)), r)
            self.assertEqual(r["funding_date_2bd"], iso(CAL.advance(pre, -2, ql.Days)), r)

    def test_bank_holidays(self):
        ours = {r["date"] for r in rows("bank_holidays_2026_2028.csv")}
        x = holidays.financial_holidays("XFED", years=range(2026, 2029))
        want = {d.isoformat() for d in x if d.weekday() < 5}
        self.assertEqual(ours, want)
        d = date(2026, 1, 1)
        while d.year < 2029:
            if d.weekday() < 5:
                self.assertEqual(d.isoformat() not in ours, CAL.isBusinessDay(qd(d.isoformat())), d)
            d += timedelta(days=1)

    def test_counts(self):
        by = {(r["schedule_id"], r["year"]): r["pay_dates_preceding"] for r in rows("pay_periods_per_year_2020_2035.csv")}
        self.assertEqual(by[("biweekly_fri_a", "2026")], "27")
        self.assertEqual(by[("biweekly_fri_b", "2026")], "26")
        self.assertEqual(len(by), 320)


if __name__ == "__main__":
    unittest.main()
