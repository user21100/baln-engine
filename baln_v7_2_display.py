from datetime import datetime, timedelta
import calendar

EXPENSES = [
    {"name": "Mortgage", "amount": 2328.00, "due_day": 1, "critical": True},
    {"name": "Auto Payment", "amount": 521.34, "due_day": 23, "critical": True},
    {"name": "Spotify", "amount": 19.99, "due_day": 3, "critical": False},
    {"name": "Google Workspace", "amount": 13.01, "due_day": 3, "critical": False},
    {"name": "Life Insurance", "amount": 123.00, "due_day": 6, "critical": False},
]

HOUSEKEEPING_START = datetime(2025, 4, 7)
HOUSEKEEPING_AMOUNT = 150.00
HAIRCUT_AMOUNT = 50.00

def shift_if_weekend(date_obj):
    if date_obj.weekday() == 5:
        return date_obj + timedelta(days=2)
    elif date_obj.weekday() == 6:
        return date_obj + timedelta(days=1)
    return date_obj

def next_paycheck_after(date):
    offset = (1 - date.weekday() + 7) % 7  # Tuesday = 1
    candidate = date + timedelta(days=offset)
    while candidate <= date:
        candidate += timedelta(days=14)
    return candidate

def format_markdown_table(expenses):
    lines = ["| Name | Amount | Due Date | Shifted |", "|------|--------|----------|---------|"]
    for e in expenses:
        lines.append(f"| {e['Name']} | ${e['Amount']:.2f} | {e['Due Date']} | {e['Shifted']} |")
    return "\n".join(lines)

def run_baln(today=None):
    if today is None:
        today = datetime.today()

    derived_weekday = calendar.day_name[today.weekday()]
    if derived_weekday != today.strftime('%A'):
        return {"status": "FAIL", "error": "Weekday mismatch between calendar and strftime."}

    next_check = next_paycheck_after(today)
    window_end = next_check - timedelta(days=1)
    included = []
    validation_errors = []

    for exp in EXPENSES:
        due_raw = datetime(today.year, today.month, exp["due_day"])
        due_shifted = shift_if_weekend(due_raw)
        if today <= due_shifted <= window_end:
            included.append({
                "Name": exp["name"],
                "Amount": exp["amount"],
                "Due Date": due_shifted.strftime('%Y-%m-%d'),
                "Shifted": "*" if due_raw != due_shifted else ""
            })
        elif exp["critical"] and today <= due_shifted <= window_end:
            validation_errors.append(f"{exp['name']} due {due_shifted.date()} was not included.")

    haircut_added = False
    for i in range(8):
        check = today + timedelta(days=i)
        if check.weekday() == 4 and today <= check <= window_end:
            included.append({
                "Name": "Haircut",
                "Amount": HAIRCUT_AMOUNT,
                "Due Date": check.strftime('%Y-%m-%d'),
                "Shifted": ""
            })
            haircut_added = True
            break
    if not haircut_added:
        validation_errors.append("Haircut for next Friday not scheduled (if within window).")

    cursor = HOUSEKEEPING_START
    while cursor <= window_end:
        if cursor >= today:
            shifted = shift_if_weekend(cursor)
            if today <= shifted <= window_end:
                included.append({
                    "Name": "Housekeeping",
                    "Amount": HOUSEKEEPING_AMOUNT,
                    "Due Date": shifted.strftime('%Y-%m-%d'),
                    "Shifted": "*" if shifted != cursor else ""
                })
        cursor += timedelta(days=14)

    included.sort(key=lambda x: x["Due Date"])
    total = sum(e["Amount"] for e in included)

    if validation_errors:
        return {
            "status": "FAIL",
            "errors": validation_errors,
            "date": today.strftime('%Y-%m-%d'),
            "window": [today.strftime('%Y-%m-%d'), window_end.strftime('%Y-%m-%d')],
            "weekday": derived_weekday,
            "render_markdown": False
        }

    return {
        "status": "PASS",
        "date": today.strftime('%Y-%m-%d'),
        "window": [today.strftime('%Y-%m-%d'), window_end.strftime('%Y-%m-%d')],
        "weekday": derived_weekday,
        "total": total,
        "expenses": included,
        "markdown": format_markdown_table(included),
        "render_markdown": True
    }
