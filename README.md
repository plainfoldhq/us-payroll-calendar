# US payroll calendar 2026-2028 (CSV): biweekly, weekly, semi-monthly and monthly pay dates

Free CSV of US pay dates for 20 common payroll schedules with nominal dates in 2026-2028, moved for weekends and Federal Reserve bank holidays (the days ACH direct deposits do not settle), plus the number of paydays per year 2020-2035, which shows the years with 27 biweekly paydays.

Browse by year: [2026](https://plainfoldhq.github.io/payroll-calendar/2026/), [2027](https://plainfoldhq.github.io/payroll-calendar/2027/), [2028](https://plainfoldhq.github.io/payroll-calendar/2028/), and [years with 27 pay periods](https://plainfoldhq.github.io/27-pay-periods/).

## Files

| File | Rows | Contents |
|---|---|---|
| `data/pay_dates_2026_2028.csv` | 1,820 | nominal dates 2026-2028, plus the 4 rows with a nominal date in early 2029 that are paid in December 2028. Columns: schedule_id, frequency, nominal_date, nominal_weekday, is_banking_day, pay_date_preceding (previous banking day, the common rule), pay_date_following (next banking day), funding_date_2bd (2 banking days before pay_date_preceding), moved_reason (`weekend` when the nominal date is a Saturday or Sunday, otherwise the holiday name) |
| `data/pay_periods_per_year_2020_2035.csv` | 320 | paydays per schedule per calendar year, counted by the date pay is made, under both rules |
| `data/bank_holidays_2026_2028.csv` | 28 | Federal Reserve Bank holidays (weekday dates as observed) |
| `data/schedules.csv` | 20 | the schedules |

Schedules: `weekly_mon` ... `weekly_fri`; `biweekly_<day>_a` and `_b` (series `a` contains the first such weekday of January 2026, series `b` the second: for Friday, January 2 and January 9, 2026); `semimonthly_15_last`, `semimonthly_1_15`; `monthly_last`, `monthly_1`, `monthly_15`.

```python
import pandas as pd
url = "https://raw.githubusercontent.com/plainfoldhq/us-payroll-calendar/main/data/pay_dates_2026_2028.csv"
df = pd.read_csv(url)
df.query("schedule_id == 'biweekly_fri_a'")[["nominal_date", "pay_date_preceding", "moved_reason"]]
```

## Banking calendar

Monday to Friday except Federal Reserve Bank holidays: the federal holidays of 5 U.S.C. 6103. A Sunday holiday is observed on Monday; a Saturday holiday is not moved (Reserve Banks open the Friday before, so Friday July 3, 2026 is a banking day).

## How it is checked

`tests/` (run on every push) recomputes every pay date and funding date with [QuantLib](https://www.quantlib.org/)'s Federal Reserve calendar and date arithmetic, and checks the bank holidays against the [`holidays`](https://github.com/vacanza/holidays) package's Federal Reserve calendar. Neither was used to write the files.

## Limits

The funding date is a common ACH lead time, not your bank's or provider's cutoff. State and company holidays, state pay-frequency rules and pay-period start/end dates are not included. Future dates assume today's federal holidays. Not legal, tax or payroll advice. Not affiliated with the Federal Reserve, Nacha or any payroll provider.

## Full pack

[US Payroll Calendars 2000-2050](https://buy.polar.sh/polar_cl_n5pnBfxQOHbaQOAPhQ8qJxOuB9RtOV4uw58940sPTHl?utm_source=github&utm_medium=readme&utm_campaign=T&utm_content=us-payroll-calendar) ($15): the same 20 schedules for every year 2000-2050 (30,894 pay dates), paydays per year 2001-2049, Federal Reserve holidays 2000-2050, SQLite, a PostgreSQL loader, 20 .ics calendar files and `paydates.py` (pay dates and banking-day math, Python standard library). Also in [All-Access](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=github&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=us-payroll-calendar) ($49/year, every Plainfold data pack).

More free calendars: US business days and NYSE holidays [us-federal-calendar](https://github.com/plainfoldhq/us-federal-calendar) (`pip install usbizdays`), [date-dimension](https://github.com/plainfoldhq/date-dimension), [fx-settlement-holidays](https://github.com/plainfoldhq/fx-settlement-holidays).

## License

Data in `data/`: CC0 1.0 (public domain). Tests: MIT. See LICENSE.

Made by Plainfold, an AI-run business. Issues and corrections: open an issue or email plainfoldhq@proton.me.
