from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date, timedelta

from dateutil.relativedelta import relativedelta

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
    until = (datetime.now() + relativedelta(years=PRINT_YEARS)).date()
    while current < until and len(rows) < PRINT_ROWS:
        for transaction in dates_dict[current.day]:
            if not transaction.does_appear_here(current):
                continue
            balance, transaction_row = create_row(balance, current, transaction, rows)
            rows.append(transaction_row)
        current = current + timedelta(days=1)
    return rows


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