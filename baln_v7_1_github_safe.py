
from datetime import datetime, timedelta
import calendar

def shift_if_weekend(date_obj):
    if date_obj.weekday() == 5:  # Saturday
        return date_obj + timedelta(days=2)
    elif date_obj.weekday() == 6:  # Sunday
        return date_obj + timedelta(days=1)
    return date_obj

def validate_baln(today_date, next_paycheck_date):
    # Validate weekday
    weekday_calendar = calendar.day_name[today_date.weekday()]
    weekday_strftime = today_date.strftime('%A')
    if weekday_calendar != weekday_strftime:
        raise ValueError("Weekday mismatch between calendar lookup and strftime.")
    return {
        "today": today_date,
        "weekday": weekday_calendar,
        "window_start": today_date,
        "window_end": next_paycheck_date - timedelta(days=1)
    }

def generate_baln_output():
    # Example hardcoded dates for demonstration; replace as needed
    today = datetime.today()
    next_paycheck = today + timedelta(days=(14 - today.weekday() + 1) % 14)

    # Validate
    validation = validate_baln(today, next_paycheck)
    today = validation["today"]
    baln_window_end = validation["window_end"]

    # Canonical example expenses
    expenses = [
        {"name": "Mortgage", "amount": 2328.00, "due_day": 1},
        {"name": "Auto Payment", "amount": 521.34, "due_day": 23},
        {"name": "Spotify", "amount": 19.99, "due_day": 3},
        {"name": "Google Workspace", "amount": 13.01, "due_day": 3},
        {"name": "Life Insurance", "amount": 123.00, "due_day": 6},
    ]

    included_expenses = []
    for exp in expenses:
        due_date = datetime(today.year, today.month, exp["due_day"])
        shifted_due = shift_if_weekend(due_date)
        if today <= shifted_due <= baln_window_end:
            included_expenses.append({
                "Name": exp["name"],
                "Amount": exp["amount"],
                "Due Date": shifted_due.strftime('%Y-%m-%d'),
                "Shifted": "*" if shifted_due.day != exp["due_day"] else ""
            })

    # Haircut logic (one Friday per BALN window)
    for i in range(0, 8):
        test_date = today + timedelta(days=i)
        if test_date.weekday() == 4 and today <= test_date <= baln_window_end:
            included_expenses.append({
                "Name": "Haircut",
                "Amount": 50.00,
                "Due Date": test_date.strftime('%Y-%m-%d'),
                "Shifted": ""
            })
            break

    # Biweekly housekeeping (example logic)
    housekeeping_start = datetime(2025, 4, 7)
    cursor = housekeeping_start
    while cursor <= baln_window_end:
        if cursor >= today:
            shifted = shift_if_weekend(cursor)
            if today <= shifted <= baln_window_end:
                included_expenses.append({
                    "Name": "Housekeeping",
                    "Amount": 150.00,
                    "Due Date": shifted.strftime('%Y-%m-%d'),
                    "Shifted": "*" if shifted != cursor else ""
                })
        cursor += timedelta(days=14)

    # Final output
    included_expenses.sort(key=lambda x: x["Due Date"])
    total = sum(e["Amount"] for e in included_expenses)

    return included_expenses, total, validation["weekday"]

# If running as script
if __name__ == "__main__":
    from pprint import pprint
    expenses, total, weekday = generate_baln_output()
    print(f"Weekday confirmed: {weekday}")
    pprint(expenses)
    print(f"TOTAL NEEDED: ${total:.2f}")
