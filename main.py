from export import export
from utils import create_dates_dict, create_transactions, fit_goals_in

if __name__ == '__main__':
    dates_dict = create_dates_dict()
    transaction_rows = create_transactions(dates_dict)
    transaction_rows = fit_goals_in(transaction_rows)

    for transaction_row in reversed(transaction_rows):
        if "Goal" in transaction_row.name:
            print(transaction_row)

    export(transaction_rows)
