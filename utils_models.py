from __future__ import annotations

import datetime
from dataclasses import dataclass
from functools import cached_property

from models import Transaction


@dataclass
class TransactionRow:
    date: datetime.date
    transaction: Transaction
    balance: int

    @property
    def amount(self):
        return self.transaction.calculated_amount(self.date)

    @cached_property
    def name(self):
        label = self.transaction.label()
        if label.startswith("="):
            new_label = self.date.strftime('= %B ') + label.strip()[2:]
            white_space = int((80 - len(new_label)) / 2)
            return "=" * white_space + new_label + "=" * white_space
        return self.transaction.label()

    def __str__(self):
        return f'{self.date.strftime("%Y-%m-%d")} | ' \
               f'{str(self.name).ljust(80)} | ' \
               f'{str(self.amount).rjust(8)} | ' \
               f'{str(self.balance).rjust(8)}'
