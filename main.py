from export import export
from utils import create_dates_dict, create_transactions, fit_goals_in, create_reports, generate_balance_chart

if __name__ == '__main__':
    dates_dict = create_dates_dict()
    transaction_rows = create_transactions(dates_dict)
    transaction_rows = fit_goals_in(transaction_rows)

    month_reports = create_reports(transaction_rows)
    print("Average monthly difference: ", end="")
    print(int(sum([month['difference'] for month in month_reports.values()]) / len(month_reports.keys())))
    print("Month report objects: ", end="")
    print(month_reports)
    generate_balance_chart(month_reports)

    print("Goals' situation:", end="\n    ")
    for transaction_row in reversed(transaction_rows):
        if "Goal" in transaction_row.name:
            print(transaction_row, end="\n    ")

    export(transaction_rows)
