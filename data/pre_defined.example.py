from datetime import date

from models import Transaction, RecurringTransaction, Goal, IncrementalTransaction

HOLIDAY_TAX = 12 * 0.08 * 0.48
MINIMUM_BALANCE = 500
IGNORE_MINIMUM_BALANCE_UNTIL = date(2023, 5, 25)
GOAL_SAVING_WINDOW = 4 * 30
PRINT_ROWS = 1000
PRINT_YEARS = 8
REPORT_START_OF_MONTH_DAY = 25
REPORT_NEXT_MONTH_NAME = True
REPORT_PLOT_LENGTH = 12 * 5
MONTH_DAYS = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

TRANSACTIONS = [
    # Incomes
    IncrementalTransaction('= Salary =', 4060, date(2022, 2, 25), date(2027, 1, 31), increase_amount=500),
    IncrementalTransaction('Holiday Allowance', int(4060 * HOLIDAY_TAX), date(2022, 5, 25),
                           increase_amount=int(500 * HOLIDAY_TAX), each_month=12),

    # Subscriptions
    RecurringTransaction('Xbox GamePass', -13, date(2022, 11, 1)),
    RecurringTransaction('Swapfiets', -24, date(2022, 10, 1)),
    RecurringTransaction('ING subscription', -5, date(2022, 10, 1)),
    RecurringTransaction('HBO Max', -4, date(2022, 9, 20)),
    RecurringTransaction('NS', -35, date(2022, 11, 27), date(2023, 10, 26)),
    RecurringTransaction('Vodafone', -75, date(2022, 11, 27), date(2024, 4, 1)),
    RecurringTransaction('Zilveren Kruis Insurance', -137, date(2022, 9, 27)),

    # Yearly subscriptions
    RecurringTransaction('Jetbrains', -302, date(2023, 7, 7), None, each_month=12),
    RecurringTransaction('Bol Select', -12, date(2023, 6, 24), None, each_month=12),

    # Monthly expenses
    RecurringTransaction('Living costs', -1000, date(2022, 11, 26)),

    # Home expenses
    RecurringTransaction('Kruisstraat Budget Energy', -48, date(2022, 10, 1)),
    RecurringTransaction('Kruisstraat BrabantWater', -26, date(2022, 11, 1), each_month=2),
    RecurringTransaction('Kruisstraat Rent', -1051, date(2022, 7, 26)),

    # Bank accounts
    Transaction('Revolut', 500),
    Transaction('ING', 500),

    # This month
    Transaction('Living Costs', -50),

    # Payments
    Transaction('Zilveren Kruis', -250, date(2022, 12, 28)),
    Transaction('Klarna', -440, date(2022, 12, 12)),

    # Vacations
    # Winter 2022
    Transaction('Malaga Budget (7 days)', -400, date(2022, 11, 28)),
    # Spring 2023
    Transaction('France in winter (10 days)', -1300, date(2023, 1, 28)),
    Transaction('France return NL living costs', 300, date(2023, 1, 28)),

    # Goals
    # I want it now (10)
    # I can wait for it (8)
    Goal('Airpod pro 2', -300, None, 8),
    Goal('Ace & Tate sunglasses', -250, None, 8),
    # I need it (6)
    Goal('Gazelle City Bike', -1500, None, 6),
    # I need it but it's fancy (4)
    Goal('Roborock', -1750, None, 4),
    # I don't need it, nice to have (2)
    Goal('Driving License', -3000, None, 2),
    # I don't care if I have it (0)
    Goal('Gazelle e-bike', -6500, None, 0),

]
