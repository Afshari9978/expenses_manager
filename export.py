import datetime

from openpyxl import Workbook

from models import TransactionRow


def export(transaction_rows: list[TransactionRow]):
    filename = f"export_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"

    workbook = Workbook()
    sheet = workbook.active

    sheet[f'A1'] = sheet[f'B1'] = sheet[f'C1'] = sheet[f'E1'] = 0
    sheet[f'D1'] = "Zero for a reason"

    for i, row in enumerate(transaction_rows):
        sheet[f'A{i + 2}'] = row.date.strftime("%Y")
        sheet[f'B{i + 2}'] = row.date.strftime("%m")
        sheet[f'C{i + 2}'] = row.date.strftime("%d")
        sheet[f'D{i + 2}'] = row.transaction.label().replace("=", "--")
        sheet[f'E{i + 2}'] = row.amount

    workbook.save(filename=filename)
