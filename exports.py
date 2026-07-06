from __future__ import annotations

import csv
import datetime
import shutil

from pathlib import Path
from utils_models import TransactionRow


def export_csv(transaction_rows: list[TransactionRow]) -> None:
    filename = f"data/export_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv"

    headers = ["date", "transaction name", "amount", "balance"]
    data = [
        [
            transaction_row.date.strftime("%Y-%m-%d"),
            transaction_row.transaction.name,
            transaction_row.amount,
            transaction_row.balance,
        ] for transaction_row in transaction_rows
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(headers)
        writer.writerows(data)


def export_inputs(transaction_rows: list[TransactionRow]) -> None:
    filename = f"data/inputs_{datetime.datetime.now().strftime('%Y-%m-%d')}.py"

    inputs_file = Path("data/pre_defined.py")
    export_file = Path(filename)

    shutil.copy2(inputs_file, export_file)
