from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    name: str
    amount: int
    date_affect: datetime.date | None = None

    def does_appear_on_this_day(self, here: datetime.date) -> bool:
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

    def does_appear_on_this_day(self, here: datetime.date) -> bool:
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


