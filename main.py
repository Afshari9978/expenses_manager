from exports import export_excel, generate_balance_chart
from utils import generate_transaction_rows, fit_goals_in, create_reports, generate_yearly_average_difference_reports, LowBalanceException

if __name__ == '__main__':
    try:
        transaction_rows = generate_transaction_rows()
    except LowBalanceException:
        exit()
    transaction_rows = fit_goals_in(transaction_rows)

    month_reports = create_reports(transaction_rows)
    generate_yearly_average_difference_reports(month_reports)
    print("Month report objects: ", end="")
    print(month_reports)
    generate_balance_chart(month_reports)

    print("Goals' situation:", end="\n    ")
    for transaction_row in reversed(transaction_rows):
        if "Goal" in transaction_row.name or transaction_row.name.startswith("Credit payback"):
            print(transaction_row, end="\n    ")

    export_excel(transaction_rows)
