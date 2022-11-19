from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date, timedelta

from models import Transaction, Goal, TransactionRow

try:
    from pre_defined import TRANSACTIONS
except ImportError:
    raise ImportError("Add `pre_defined.py` file on the root, according to the `pre_defined.example.py` file.")

MINIMUM_BALANCE = 500
IGNORE_MINIMUM_BALANCE_UNTIL = date(2023, 2, 25)
GOAL_SAVING_WINDOW = 2 * 30
PRINT_ROWS = 1000
PRINT_YEARS = 8
REPORT_START_OF_MONTH_DAY = 25
REPORT_NEXT_MONTH_NAME = True
REPORT_PLOT_LENGTH = 12 * 5
MONTH_DAYS = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def create_dates_dict() -> dict[int, list[Transaction]]:
    dates = defaultdict(list)
    for transaction in [item for item in TRANSACTIONS if not isinstance(item, Goal)]:
        if transaction.date_affect is None:
            dates[0].append(transaction)
        else:
            dates[transaction.date_affect.day].append(transaction)
    return dates


def create_row(
        initial_amount: int,
        current_date: date,
        transaction: Transaction,
        rows: list[TransactionRow]) -> tuple[int, TransactionRow]:
    transaction_amount = transaction.calculated_amount(current_date)
    initial_amount += transaction_amount
    try:
        _is_balance_acceptable(initial_amount, current_date, transaction.name, transaction_amount)
    except AssertionError as e:
        for row in reversed(rows):
            print(row)
        raise e
    return initial_amount, TransactionRow(
        current_date, transaction, initial_amount
    )


def create_transactions(dates_dict: dict[int, list[Transaction]]) -> list[TransactionRow]:
    rows = []
    balance = 0

    for transaction in dates_dict[0]:
        balance, transaction_row = create_row(balance, date(2000, 1, 1), transaction, rows)
        rows.append(transaction_row)

    current = datetime.now().date()
    until = move_month(datetime.now().date(), PRINT_YEARS * 12)
    while current < until and len(rows) < PRINT_ROWS:
        for transaction in dates_dict[current.day]:
            if not transaction.does_appear_here(current):
                continue
            balance, transaction_row = create_row(balance, current, transaction, rows)
            rows.append(transaction_row)
        current = current + timedelta(days=1)
    return rows


def calculate_rolling_difference(
        rolling_difference_1: int | None,
        rolling_difference_2: int | None,
        rolling_difference_3: int | None,
        difference: int) -> \
        tuple[int | None, int | None, int | None, int]:
    rolling_difference = None
    if rolling_difference_1 is None:
        rolling_difference_1 = difference
        rolling_difference = difference
    elif rolling_difference_2 is None:
        rolling_difference_2 = difference
        rolling_difference = int((rolling_difference_1 + rolling_difference_2) / 2)
    elif rolling_difference_3 is None:
        rolling_difference_3 = difference
    else:
        rolling_difference_1, rolling_difference_2, rolling_difference_3 = \
            rolling_difference_2, rolling_difference_3, difference
    if not rolling_difference:
        rolling_difference = int((rolling_difference_1 + rolling_difference_2 + rolling_difference_3) / 3)

    return rolling_difference_1, rolling_difference_2, rolling_difference_3, rolling_difference


def create_reports(transaction_rows: list[TransactionRow]) -> dict[str, dict[str, int | date]]:
    month_reports = {}
    month_start = month_name = name_date = None
    min_balance = incomes = expenses = 0
    rolling_difference_1 = rolling_difference_2 = rolling_difference_3 = None
    for i, transaction_row in enumerate(transaction_rows):
        if transaction_row.transaction.date_affect is None:
            continue
        if month_start != transaction_row.date and transaction_row.date.day == REPORT_START_OF_MONTH_DAY:
            if month_name:
                difference = incomes - expenses
                month_reports[month_name] = {
                    'min_balance': min_balance, 'incomes': incomes, 'expenses': expenses,
                    'difference': difference, 'name_date': name_date
                }

                rolling_difference_1, rolling_difference_2, rolling_difference_3, month_reports[month_name][
                    'rolling_difference'] = calculate_rolling_difference(rolling_difference_1, rolling_difference_2,
                                                                         rolling_difference_3, difference)

            name_date = transaction_row.date
            if REPORT_NEXT_MONTH_NAME:
                name_date += timedelta(days=28)

            month_name = f'{name_date.strftime("%B")} {name_date.year}'
            month_start = transaction_row.date
            incomes = expenses = 0
            min_balance = transaction_row.balance

        min_balance = min(min_balance, transaction_row.balance)
        if transaction_row.amount > 0:
            incomes += transaction_row.amount
        else:
            expenses -= transaction_row.amount

    return month_reports


def generate_balance_chart(month_reports: dict[str, dict[str, int | date]]) -> None:
    import matplotlib.pyplot as plt

    global REPORT_PLOT_LENGTH

    # gather data points
    REPORT_PLOT_LENGTH = min(REPORT_PLOT_LENGTH, len(month_reports.keys()))
    month_points = [report['name_date'].strftime("%m-%y") for report in
                    list(month_reports.values())[:REPORT_PLOT_LENGTH]]
    balance_points = [report['min_balance'] for report in list(month_reports.values())[:REPORT_PLOT_LENGTH]]

    # make the plot longer
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    # set points
    ax.plot(month_points, balance_points)
    # rotate x labels
    plt.xticks(rotation=55, ha="right")
    # reduce x labels
    plot_start = list(month_reports.values())[0]['name_date'].month % 2
    ax.set_xticks([i for i in range(plot_start, REPORT_PLOT_LENGTH, 2)])
    # increase bottom padding
    plt.subplots_adjust(bottom=0.2)

    plt.grid(axis="y", linewidth=0.3)

    plt.savefig(f"plot_{datetime.now().strftime('%Y-%m-%d')}.png")


def can_insert_transaction_on_index(
        target: Transaction,
        on_index: int,
        transaction_rows: list[TransactionRow],
        raise_assert: bool = False
) -> tuple[bool, int, date]:
    balance = transaction_rows[on_index].balance - transaction_rows[on_index].amount + target.calculated_amount(
        transaction_rows[on_index].date)
    if not _is_balance_acceptable(balance, transaction_rows[on_index - 1].date, target.name,
                                  target.calculated_amount(transaction_rows[on_index].date), raise_assert):
        return False, balance, transaction_rows[on_index - 1].date

    for transaction_row in transaction_rows[on_index:]:
        balance += transaction_row.amount
        if not _is_balance_acceptable(balance, transaction_row.date, transaction_row.name, transaction_row.amount,
                                      raise_assert):
            return False, balance, transaction_row.date

    return True, balance, transaction_rows[on_index - 1].date


def insert_transaction(target: Transaction, on_index: int, transaction_rows: list[TransactionRow]):
    balance = transaction_rows[on_index].balance - transaction_rows[on_index].amount + target.calculated_amount(
        transaction_rows[on_index].date)
    transaction_row = TransactionRow(transaction_rows[on_index - 1].date, target, balance)
    transaction_rows.insert(on_index, transaction_row)

    for transaction_row in transaction_rows[on_index + 1:]:
        balance += transaction_row.amount
        transaction_row.balance = balance


def insert_goal(goal: Goal, transaction_rows: list[TransactionRow]) -> None:
    index = 0
    if goal.date_affect is not None:
        for transaction in transaction_rows:
            if transaction.date <= max(
                    goal.date_affect - timedelta(days=GOAL_SAVING_WINDOW),
                    transaction_rows[0].date
            ):
                index += 1
                continue
            break

    for transaction in transaction_rows[index:]:
        if goal.date_affect and transaction.date > goal.date_affect:
            print(f"Goal {goal.name} expired")

        can_insert, balance, balance_date = can_insert_transaction_on_index(goal, index, transaction_rows, False)
        if can_insert:
            insert_transaction(goal, index, transaction_rows)
            return None
        index += 1
    print(f"Goal {goal.name} didn't took place")


def fit_goals_in(transaction_rows: list[TransactionRow]) -> list[TransactionRow]:
    goals = [item for item in TRANSACTIONS if isinstance(item, Goal)]
    for goal in sorted(goals, key=lambda x: x.importance, reverse=True):
        insert_goal(goal, transaction_rows)

    return transaction_rows


def _is_balance_acceptable(balance: int, current_date: date, name: str, amount: int,
                           raise_assert: bool = True) -> bool:
    if amount >= 0:
        return True

    if current_date > IGNORE_MINIMUM_BALANCE_UNTIL:
        _MINIMUM_BALANCE = MINIMUM_BALANCE
    else:
        _MINIMUM_BALANCE = 0

    if not raise_assert and balance < _MINIMUM_BALANCE:
        return False

    assert balance >= _MINIMUM_BALANCE, \
        f'Balance goes under minimum on {current_date.strftime("%Y-%m-%d")} \n' \
        f'    Because of {name} ({amount}) became {balance}'
    return True


def move_month(start_date: date, amount: int = 1) -> date:
    year, month, day = start_date.year, start_date.month, start_date.day
    if amount > 0:
        for _ in range(amount):
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
    else:
        for _ in range(abs(amount)):
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
    day = min(MONTH_DAYS[month], day)
    return date(year, month, day)
