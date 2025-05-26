
from datetime import datetime, timedelta
import calendar

# --- Configuration: Canonical Recurring Expenses ---
EXPENSES = [
    {"name": "Mortgage", "amount": 2328.00, "due_day": 1},
    {"name": "Auto Payment", "amount": 521.34, "due_day": 23},
    {"name": "Spotify", "amount": 19.99, "due_day": 3},
    {"name": "Google Workspace", "amount": 13.01, "due_day": 3},
    {"name": "Life Insurance", "amount": 123.00, "due_day": 6},
]

HOUSEKEEPING_START = datetime(2025, 4, 7)
HOUSEKEEPING_AMOUNT = 150.00
HAIRCUT_AMOUNT = 50.00

# --- Helper Functions ---
def shift_if_weekend(date_obj):
    if date_obj.weekday() == 5:
        return date_obj + timedelta(days=2)
    elif date_obj.weekday() == 6:
        return date_obj + timedelta(days=1)
    return date_obj

def next_paycheck_after(date):
    offset = (1 - date.weekday() + 7) % 7  # 1 = Tuesday
    candidate = date + timedelta(days=offset)
    while candidate <= date:
        candidate += timedelta(14)
    return candidate

def format_markdown_table(expenses):
    lines = ["| Name | Amount | Due Date | Shifted |", "|------|--------|----------|---------|"]
    for e in expenses:
        lines.append(f"| {e['Name']} | ${e['Amount']:.2f} | {e['Due Date']} | {e['Shifted']} |")
    return "\n".join(lines)

# --- Main Function ---
def run_baln(today=None):
    if today is None:
        today = datetime.today()

    # Validate weekday
    derived_weekday = calendar.day_name[today.weekday()]
    if derived_weekday != today.strftime('%A'):
        raise ValueError("❌ Weekday mismatch between calendar and strftime.")

    next_check = next_paycheck_after(today)
    window_end = next_check - timedelta(days=1)
    included = []
    validation_errors = []

    # Step 1: Fixed Expenses
    expected_inclusions = []
    for exp in EXPENSES:
        due = datetime(today.year, today.month, exp["due_day"])
        shifted_due = shift_if_weekend(due)
        if today <= shifted_due <= window_end:
            included.append({
                "Name": exp["name"],
                "Amount": exp["amount"],
                "Due Date": shifted_due.strftime('%Y-%m-%d'),
                "Shifted": "*" if shifted_due != due else ""
            })
            expected_inclusions.append(exp["name"])
        elif exp["name"] in ["Mortgage", "Auto Payment"] and today <= shifted_due <= window_end:
            validation_errors.append(f"❌ {exp['name']} due {shifted_due.date()} should be included but is missing.")

    # Step 2: Haircut
    haircut_added = False
    for i in range(8):
        d = today + timedelta(days=i)
        if d.weekday() == 4 and today <= d <= window_end:
            included.append({
                "Name": "Haircut",
                "Amount": HAIRCUT_AMOUNT,
                "Due Date": d.strftime('%Y-%m-%d'),
                "Shifted": ""
            })
            haircut_added = True
            break
    if not haircut_added:
        validation_errors.append("❌ Haircut for next Friday not scheduled (if within window).")

    # Step 3: Housekeeping (biweekly)
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

    # Final Sort
    included.sort(key=lambda x: x["Due Date"])
    total = sum(e["Amount"] for e in included)

    # Final Validation
    if validation_errors:
        print("❌ BALN VALIDATION FAILED:")
        for err in validation_errors:
            print("-", err)
        return

    # Markdown Output
    print("✅ BALN VALIDATION PASSED")
    print(f"**Date:** {today.strftime('%Y-%m-%d')} ({derived_weekday})")
    print(f"**BALN Window:** {today.strftime('%Y-%m-%d')} → {window_end.strftime('%Y-%m-%d')}")
    print(f"**Total Needed:** ${total:.2f}\n")
    print(format_markdown_table(included))

# Uncomment below to run directly
# run_baln()
