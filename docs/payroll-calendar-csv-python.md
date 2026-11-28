# Payroll pay dates and pay periods from CSV in Python

A payroll calendar is mostly date arithmetic, and the awkward part is the days that are not banking days. This guide loads the pay dates in the free [US payroll calendar CSV](https://github.com/plainfoldhq/us-payroll-calendar), shows how a pay date moves for a weekend or a Federal Reserve holiday, and finds the years with 27 biweekly pay dates and the months with three biweekly paychecks. It uses pandas 3.1 and QuantLib 1.44 on Python 3.11, run from the root of the repo:

```
pip install pandas QuantLib
```

All output below was produced by running the code in this order, in one session. The CSV files cover pay dates for 2026-2028 and paydays per year for 2020-2035.

## Load the pay dates

```python
import pandas as pd

pay = pd.read_csv("data/pay_dates_2026_2028.csv", dtype=str, keep_default_na=False)
print(pay.schedule_id.nunique(), "schedules,", len(pay), "rows")
bi = pay[pay.schedule_id == "biweekly_fri_a"]
print(bi[["nominal_date", "pay_date_preceding"]].head(4).to_string(index=False))
```

```
20 schedules, 1820 rows
nominal_date pay_date_preceding
  2026-01-02         2026-01-02
  2026-01-16         2026-01-16
  2026-01-30         2026-01-30
  2026-02-13         2026-02-13
```

`dtype=str` keeps the dates as ISO strings, which sort correctly, and `keep_default_na=False` keeps the empty `moved_reason` as an empty string. Each row is one nominal date of one schedule. `biweekly_fri_a` is the series that contains the first Friday of January 2026 (January 2); `biweekly_fri_b` starts a week later.

## How a pay date moves

The file has two rules side by side. `pay_date_preceding` is the previous banking day (the common rule: pay early), `pay_date_following` is the next banking day. A banking day is Monday to Friday except a Federal Reserve holiday. Semimonthly on the 15th and last day, first quarter of 2026:

```python
semi = pay[pay.schedule_id == "semimonthly_15_last"]
q1 = semi[semi.nominal_date.between("2026-01-01", "2026-03-31")]
print(q1[["nominal_date", "nominal_weekday", "pay_date_preceding", "pay_date_following", "moved_reason"]].to_string(index=False))
```

```
nominal_date nominal_weekday pay_date_preceding pay_date_following moved_reason
  2026-01-15             Thu         2026-01-15         2026-01-15             
  2026-01-31             Sat         2026-01-30         2026-02-02      weekend
  2026-02-15             Sun         2026-02-13         2026-02-17      weekend
  2026-02-28             Sat         2026-02-27         2026-03-02      weekend
  2026-03-15             Sun         2026-03-13         2026-03-16      weekend
  2026-03-31             Tue         2026-03-31         2026-03-31             
```

February 15, 2026 is a Sunday. Moving back gives Friday the 13th; moving forward gives Tuesday the 17th, not Monday the 16th, because Monday the 16th is Washington's Birthday. Biweekly Friday rows that moved for a holiday in 2026-2028:

```python
moved = bi[bi.moved_reason != ""]
print(moved[["nominal_date", "nominal_weekday", "pay_date_preceding", "pay_date_following", "funding_date_2bd", "moved_reason"]].to_string(index=False))
```

```
nominal_date nominal_weekday pay_date_preceding pay_date_following funding_date_2bd                         moved_reason
  2026-06-19             Fri         2026-06-18         2026-06-22       2026-06-16 Juneteenth National Independence Day
  2027-01-01             Fri         2026-12-31         2027-01-04       2026-12-29                       New Year's Day
```

`funding_date_2bd` is two banking days before `pay_date_preceding`, a common ACH lead time. It is not your bank's or provider's cutoff, so check yours. Note the second row: a 2027 nominal date is paid in 2026, which matters for the next section.

## Years with 27 biweekly pay dates

A biweekly schedule has 26 pay dates in most years and 27 in some, because 52 weeks plus one or two days does not divide evenly into pairs of weeks. `pay_periods_per_year_2020_2035.csv` counts paydays per calendar year by the date pay is actually made, under both rules:

```python
pp = pd.read_csv("data/pay_periods_per_year_2020_2035.csv")
b = pp[pp.frequency == "biweekly"]
print(b[b.pay_dates_preceding == 27].sort_values(["year", "schedule_id"])[["schedule_id", "year", "pay_dates_preceding", "pay_dates_following"]].to_string(index=False))
```

```
   schedule_id  year  pay_dates_preceding  pay_dates_following
biweekly_fri_b  2020                   27                   26
biweekly_thu_b  2020                   27                   27
biweekly_mon_b  2022                   27                   26
biweekly_tue_b  2024                   27                   27
biweekly_wed_b  2024                   27                   26
biweekly_thu_a  2025                   27                   26
biweekly_fri_a  2026                   27                   26
biweekly_mon_a  2028                   27                   26
biweekly_tue_a  2029                   27                   26
biweekly_wed_a  2030                   27                   26
biweekly_thu_b  2031                   27                   26
biweekly_fri_b  2032                   27                   27
biweekly_mon_b  2033                   27                   26
biweekly_tue_b  2035                   27                   26
```

Within 2020-2035 each of the ten biweekly schedules has at least one 27-pay-date year under the "previous banking day" rule. The two rules do not always agree, which is why the table has both columns. Look at Friday series `a` around the turn of 2027:

```python
print(pp[(pp.schedule_id == "biweekly_fri_a") & (pp.year.between(2025, 2028))].to_string(index=False))
```

```
   schedule_id frequency  year  pay_dates_preceding  pay_dates_following
biweekly_fri_a  biweekly  2025                   26                   26
biweekly_fri_a  biweekly  2026                   27                   26
biweekly_fri_a  biweekly  2027                   26                   27
biweekly_fri_a  biweekly  2028                   26                   26
```

Series `a` has only 26 nominal Fridays in 2026 (the last is December 18). The 27th pay date in 2026 is January 1, 2027, paid early on December 31, 2026. Under the "following" rule that date is paid on January 4, 2027, so 2027 gets the extra one instead. Which year gets the extra paycheck depends on the rule, so check the one your payroll provider uses.

## Months with three biweekly paychecks

Group the pay dates by the month in which they are paid:

```python
for sid in ["biweekly_fri_a", "biweekly_fri_b"]:
    x = pay[pay.schedule_id == sid]
    counts = x.groupby(x.pay_date_preceding.str[:7]).size()
    print(sid, list(counts[counts == 3].index))
```

```
biweekly_fri_a ['2026-01', '2026-07', '2026-12', '2027-07', '2027-12', '2028-06', '2028-12']
biweekly_fri_b ['2026-05', '2026-10', '2027-04', '2027-10', '2028-03', '2028-09']
```

December 2026 for series `a` has three pay dates only because of the holiday move above: December 4, December 18 and December 31.

## Cross-check with QuantLib

The CSV was not written with QuantLib, so it is an independent check. QuantLib's `UnitedStates(FederalReserve)` calendar adjusts each nominal date with `Preceding` and `Following`. First, all 1,820 rows:

```python
import QuantLib as ql
from datetime import date, timedelta

cal = ql.UnitedStates(ql.UnitedStates.FederalReserve)
def q(d): return ql.Date(d.day, d.month, d.year)
def py(x): return date(x.year(), x.month(), x.dayOfMonth())

ok = bad = 0
for r in pay.itertuples():
    n = q(date.fromisoformat(r.nominal_date))
    pre, fol = py(cal.adjust(n, ql.Preceding)), py(cal.adjust(n, ql.Following))
    if (pre.isoformat(), fol.isoformat()) == (r.pay_date_preceding, r.pay_date_following):
        ok += 1
    else:
        bad += 1
print("pay dates:", ok, "agree,", bad, "differ")
```

```
pay dates: 1820 agree, 0 differ
```

Second, the paydays-per-year table, rebuilt without using the nominal dates in the CSV. Each biweekly series is generated by adding 14 days from January 2 or January 9, 2026, then adjusted and counted by year paid:

```python
days = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4}
agree = diff = 0
for r in pp[pp.frequency == "biweekly"].itertuples():
    wd = days[r.schedule_id.split("_")[1]]
    first = date(2026, 1, 1) + timedelta((wd - date(2026, 1, 1).weekday()) % 7)
    if r.schedule_id.endswith("_b"):
        first += timedelta(7)
    n = {"pre": 0, "fol": 0}
    d = first - timedelta(14 * 400)
    while d <= date(2036, 12, 31):
        if py(cal.adjust(q(d), ql.Preceding)).year == r.year: n["pre"] += 1
        if py(cal.adjust(q(d), ql.Following)).year == r.year: n["fol"] += 1
        d += timedelta(14)
    if (n["pre"], n["fol"]) == (r.pay_dates_preceding, r.pay_dates_following):
        agree += 1
    else:
        diff += 1
print("biweekly year counts:", agree, "agree,", diff, "differ")
```

```
biweekly year counts: 160 agree, 0 differ
```

That is 10 biweekly schedules times 16 years, all equal. The three-paycheck months for Friday series `a` and `b` were also recomputed this way (a similar loop, counting by month paid) and gave the same lists as above.

## Limits

- Pay dates are nominal dates for 2026-2028 only. Paydays per year cover 2020-2035.
- The calendar is the Federal Reserve holiday schedule. Saturday holidays are not moved to Friday (July 3, 2026 is a banking day). Future dates assume today's federal holidays.
- Both rules follow the Fed calendar. Your bank, payroll provider, state law or company holidays may differ, and so may the pay period start and end dates, which are not in the files.

## Full pack: 2000-2050

[US Payroll Calendars 2000-2050](https://buy.polar.sh/polar_cl_n5pnBfxQOHbaQOAPhQ8qJxOuB9RtOV4uw58940sPTHl?utm_source=github&utm_medium=readme&utm_campaign=T&utm_content=us-payroll-calendar) ($15, one-time; Polar is the merchant of record and handles sales tax) has:

- the same 20 schedules for every year 2000-2050 (30,894 pay dates) and paydays per year 2001-2049
- Federal Reserve holidays 2000-2050
- SQLite, a PostgreSQL loader and 20 .ics calendar files
- `paydates.py` (pay dates and banking-day math, Python standard library)

It is also in the [All-Access yearly plan](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=github&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=us-payroll-calendar) ($49/year, every Plainfold data pack). Details: [README](../README.md#full-pack).

---

Made by Plainfold. Written with AI assistance.

Not payroll, tax or legal advice.
