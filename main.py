from pprint import pprint

from export import export
from utils import create_dates_dict, create_transactions, fit_goals_in, create_reports, print_charts

if __name__ == '__main__':
    dates_dict = create_dates_dict()
    transaction_rows = create_transactions(dates_dict)
    month_reports = create_reports(transaction_rows)
    print(sum([month['difference'] for month in month_reports.values()]) / len(month_reports.keys()))
    print(month_reports)
    print_charts(month_reports)
    transaction_rows = fit_goals_in(transaction_rows)

    for transaction_row in reversed(transaction_rows):
        if "Goal" in transaction_row.name:
            print(transaction_row)

    export(transaction_rows)
