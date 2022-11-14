from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    name: str
    amount: int
    date_affect: datetime.date | None = None

    def does_appear_here(self, here: datetime.date) -> bool:
        if self.date_affect == here:
            return True
        return False

    def label(self):
        return self.name

    def calculated_amount(self, date: datetime.date | None = None) -> int:
        return self.amount


@dataclass
class Goal(Transaction):
    date_affect = None
    importance: int = 0

    def label(self):
        return f'Goal ({self.importance}): {self.name}'


@dataclass
class RecurringTransaction(Transaction):
    date_end: datetime.date | None = None
    each_month: int = 1

    def go_back(self, here: datetime.date):
        from utils import move_month

        return move_month(here, -self.each_month)

    def does_appear_here(self, here: datetime.date) -> bool:
        if self.date_affect == here:
            return True
        if self.date_affect > here:
            return False
        if self.date_end and self.date_end < here:
            return False

        here = self.go_back(here)
        while here >= self.date_affect:
            if self.date_affect == here:
                return True
            here = self.go_back(here)

        return False


@dataclass
class IncrementalTransaction(RecurringTransaction):
    increase_each_month: int = 12
    increase_amount: int = 0

    def calculated_amount(self, date: datetime.date | None = None) -> int:
        from utils import move_month

        if not date:
            return self.amount

        date_cap = self.date_affect
        month_counter = 0
        amount = self.amount
        while True:
            date_cap = move_month(date_cap, 1)
            month_counter += 1
            if month_counter % self.increase_each_month == 0:
                amount += self.increase_amount
            if date <= date_cap:
                return amount


@dataclass
class TransactionRow:
    date: datetime.date
    transaction: Transaction
    balance: int

    @property
    def amount(self):
        return self.transaction.calculated_amount(self.date)

    @property
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
