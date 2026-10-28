# Task 6: Attendance and Leave Trends

**Page file:** `pages/3_Attendance_Leave_Trends.py`
**Data used:** `fact_attendance_monthly`, `fact_leave`, `dim_date`
**Period:** 2025-04 to 2026-09

## What I built

- Attendance rate by month (present days / scheduled days), with the axis zoomed in so small dips are visible.
- Red diamond markers on months that have a holiday or a long weekend.
- Heatmap of attendance rate by month and department.
- Late arrivals shown as a rate (per 100 present days), and overtime hours by month.
- Approved leave days by type and by department, plus a leave status table.
- An "Unusual Months" table that finds 3 months far from normal.
- A department filter and a month range filter in the sidebar.

## Screenshots

![Trend and heatmap](screenshots/task6_trend_heatmap.png)

![Leave trends and unusual months](screenshots/task6_leave_unusual.png)

## 3 unusual months

1. **2025-12, overtime.** Overtime was 787.0 hours, about 48% above the typical month (532.8 hours). This month has 1 holiday and no long weekend. Possible cause: year-end deadlines. Next step: check which department drove it.

2. **2026-05, attendance dip.** Attendance fell to 92.64%, the lowest month and 2.71 points below the best month (2025-07, 95.35%). This month has a red marker, so I checked the calendar first. Legal & Compliance changed most: 83.33% against its own average of 94.13% (-10.80 points). Engineering, the largest department, dropped only 1.54 points. Possible cause: holiday or long-weekend leave.

3. **2026-03, late arrivals.** The late-arrival rate was highest at 7.53 per 100 present days (583 late arrivals). This month has 2 holidays and 3 long-weekend days. Possible cause: people returning late after the long weekend.

The data gives context only. It does not prove the cause.

## 3 insights with numbers

1. Attendance stayed in a narrow range of 92.64% to 95.35%, with an overall rate of 94.00%. A gap of 2.71 points is small, so a flat 0 to 100 axis hid every dip.
2. Counts and rates tell different stories. The highest late-arrival count was 2026-09 (618), but the highest late-arrival rate was 2026-03 (7.53 per 100 present days). Rates are the fair comparison.
3. Overtime in 2025-12 was 787.0 hours, 48% above the typical month. This is the strongest outlier on the page.

## Think for yourself: which department do I check first after a dip?

I check the department that changed most from its own normal, not the biggest one. Engineering has about 38% of all scheduled days, so it moves the company average the most. But a small department, like Legal & Compliance (3,487 scheduled days), can show a big drop that the total hides. So I compare each department with its own average, then check how much of the total dip that department caused.

## Checklist

- [x] Rates use present days / scheduled days
- [x] Holidays and long weekends are marked on the chart
- [x] 3 numeric insights written
- [x] Department filter tested (removing a department changes the charts)
- [ ] Denominator checked in the "Check: is the denominator based on working days?" box

## Reference links

- Streamlit: https://github.com/streamlit/streamlit
- Plotly: https://github.com/plotly/plotly.py
- Altair: https://github.com/vega/altair

## How real companies do it

Analysts always check the calendar before reporting a dip. A holiday is not a crisis.

## Link to the next task

I now know when people are present. Task 7 asks who leaves and why.

*I turned raw attendance records into clear trends with explanations.*
