from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date, timedelta

from models import Transaction, Goal
from utils_models import TransactionRow

try:
    from data.pre_defined import TRANSACTIONS, PRINT_YEARS, REPORT_START_OF_MONTH_DAY, \
        REPORT_NEXT_MONTH_NAME, GOAL_SAVING_WINDOW, MINIMUM_BALANCE
except ImportError:
    raise ImportError("Add `pre_defined.py` file in /data folder, according to the `pre_defined.example.py` file.")


def get_non_dynamic_transactions() -> list[Transaction]:
    return [transaction for transaction in TRANSACTIONS if not isinstance(transaction, Goal)]


def create_dates_dict() -> dict[int, list[Transaction]]:
    dates = defaultdict(list)
    for transaction in get_non_dynamic_transactions():
        if transaction.date_affect is None:
            dates[0].append(transaction)
        else:
            dates[transaction.date_affect.day].append(transaction)
    return dates


class LowBalanceException(Exception):
    pass


def create_transaction_row(
        initial_amount: int,
        current_date: date,
        transaction: Transaction,
        rows: list[TransactionRow]) -> tuple[int, TransactionRow]:
    transaction_amount = transaction.calculated_amount(current_date)
    initial_amount += transaction_amount
    try:
        _is_balance_acceptable(
            balance=initial_amount,
            current_date=current_date,
            name=transaction.name,
            amount=transaction_amount
        )
    except LowBalanceException as e:
        # Stop processing transactions if the balance is lower that allowed, plus, printing transactions until here
        for row in reversed(rows):
            print(row)
        print(f"\033[91m{e} \033[0m")  # color the message in red
        raise e
    return initial_amount, TransactionRow(
        current_date, transaction, initial_amount
    )


def generate_transaction_rows() -> list[TransactionRow]:
    rows = []
    balance = 0
    dates_dict = create_dates_dict()

    # Add all no-date transactions to the beginning
    for transaction in sorted(dates_dict[0], key=lambda x: x.amount, reverse=True):
        balance, transaction_row = create_transaction_row(balance, date(2000, 1, 1), transaction, rows)
        rows.append(transaction_row)

    # Now start from today until the end of the PRINT_YEARS to generate transactions
    current_day = datetime.now().date()
    last_day_to_report = move_month(datetime.now().date(), PRINT_YEARS * 12)
    while current_day < last_day_to_report:
        for transaction in sorted(dates_dict[current_day.day], key=lambda x: x.amount, reverse=True):
            if not transaction.does_appear_on_this_day(current_day):
                continue
            balance, transaction_row = create_transaction_row(balance, current_day, transaction, rows)
            rows.append(transaction_row)
        current_day = current_day + timedelta(days=1)
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


def generate_yearly_average_difference_reports(month_reports: dict[str, dict[str, int | date]]) -> None:
    sums = defaultdict(int)
    lengths = defaultdict(int)
    for month_name, month in month_reports.items():
        sums['Total average monthly difference'] += month['difference']
        lengths['Total average monthly difference'] += 1

        year = int(month_name[-4:])
        sums[year] += month['difference']
        lengths[year] += 1

    for year in sums:
        if sums[year] and lengths[year]:
            print(f"{year}: {sums[year] // lengths[year]}")


def can_insert_transaction_on_already_processed_rows(
        target: Transaction,
        after_index: int,
        transaction_rows: list[TransactionRow],
) -> bool:
    balance = transaction_rows[after_index].balance - transaction_rows[after_index].amount + target.calculated_amount(
        transaction_rows[after_index].date)
    if not _is_balance_acceptable(
            balance=balance,
            current_date=transaction_rows[after_index - 1].date,
            name=target.name,
            amount=target.calculated_amount(transaction_rows[after_index].date),
            raise_exception=False
    ):
        return False

    for transaction_row in transaction_rows[after_index:]:
        balance += transaction_row.amount
        if not _is_balance_acceptable(
                balance=balance,
                current_date=transaction_row.date,
                name=transaction_row.name,
                amount=transaction_row.amount,
                raise_exception=False
        ):
            return False

    return True


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
    if goal.date_affect:
        index = skip_transaction_rows_to_date(goal.date_affect, index, transaction_rows)

    for transaction in transaction_rows[index:]:
        if goal.date_affect and transaction.date > goal.date_affect:
            print(f"{goal.label()} expired")
            break

        can_insert = can_insert_transaction_on_already_processed_rows(goal, index, transaction_rows)
        if can_insert:
            insert_transaction(goal, index, transaction_rows)
            return None
        index += 1
    print(f"\033[93m{goal.label()} didn't took place\033[0m") # Color it yellow


def skip_transaction_rows_to_date(to_date: date, index, transaction_rows):
    start_date = max(transaction_rows[0].date, to_date - timedelta(days=GOAL_SAVING_WINDOW))
    for transaction in transaction_rows:
        if transaction.date <= start_date:
            index += 1
            continue
        break
    return index


def fit_goals_in(transaction_rows: list[TransactionRow]) -> list[TransactionRow]:
    goals = [item for item in TRANSACTIONS if isinstance(item, Goal)]
    for goal in sorted(goals, key=lambda x: x.importance, reverse=True):
        insert_goal(goal, transaction_rows)

    return transaction_rows


def _is_balance_acceptable(balance: int, current_date: date, name: str, amount: int,
                           raise_exception: bool = True) -> bool:
    if amount >= 0:
        return True

    if balance >= MINIMUM_BALANCE:
        return True

    if not raise_exception:
        return False

    raise LowBalanceException(
        f'Balance goes under minimum on {current_date.strftime("%Y-%m-%d")} \n'
        f'Because of the {name} ({amount}) it became {balance}')


def move_month(start_date: date, amount: int = 1) -> date:
    # Simple date mover to improve performance
    days_in_each_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
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
    day = min(days_in_each_month[month], day)
    return date(year, month, day)
