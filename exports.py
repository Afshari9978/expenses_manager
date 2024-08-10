from __future__ import annotations

import datetime
from datetime import date

from openpyxl import Workbook

from utils_models import TransactionRow


def export_excel(transaction_rows: list[TransactionRow]) -> None:
    filename = f"data/export_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"

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


def generate_balance_chart(month_reports: dict[str, dict[str, int | date]]) -> None:
    import matplotlib.pyplot as plt

    from data.pre_defined import REPORT_PLOT_LENGTH

    # gather data points
    REPORT_PLOT_LENGTH = min(REPORT_PLOT_LENGTH, len(month_reports.keys()))
    month_points = [report['name_date'].strftime("%m-%y") for report in
                    list(month_reports.values())[:REPORT_PLOT_LENGTH]]
    balance_points = [report['min_balance'] for report in list(month_reports.values())[:REPORT_PLOT_LENGTH]]

    # make the plot longer
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    # set points
    ax.plot(month_points, balance_points)
    # rotate x labels
    plt.xticks(rotation=55, ha="right")
    # reduce x labels
    plot_start = list(month_reports.values())[0]['name_date'].month % 2
    ax.set_xticks([i for i in range(plot_start, REPORT_PLOT_LENGTH, 2)])
    # increase bottom padding
    plt.subplots_adjust(bottom=0.2)

    plt.grid(axis="y", linewidth=0.3)

    plt.savefig(f"data/plot_{datetime.datetime.now().strftime('%Y-%m-%d')}.png")
