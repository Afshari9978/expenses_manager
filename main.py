from exports import export_csv, export_inputs
from utils import generate_transaction_rows, fit_goals_in, create_reports, generate_yearly_average_difference_reports, LowBalanceException

if __name__ == '__main__':
    try:
        transaction_rows = generate_transaction_rows()
    except LowBalanceException:
        exit()

    month_reports = create_reports(transaction_rows)
    generate_yearly_average_difference_reports(month_reports)
    print("Month report objects: ", end="")
    print(month_reports)

    transaction_rows = fit_goals_in(transaction_rows)

    print("Goals' situation:", end="\n    ")
    for transaction_row in reversed(transaction_rows):
        if "Goal" in transaction_row.name or transaction_row.name.startswith("+)"):
            print(transaction_row, end="\n    ")

    export_csv(transaction_rows)
    export_inputs(transaction_rows)
