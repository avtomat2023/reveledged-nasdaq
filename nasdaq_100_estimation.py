import csv
from dataclasses import dataclass
import re
import datetime

from more_itertools import windowed
import seaborn as sns
import matplotlib.pyplot as plt

def row_to_price_date(row: str) -> (float, datetime.date):
    date, price, *_ = row
    price = float(price.replace(',', ''))
    month, day, year = re.fullmatch('([0-9]+)/([0-9]+)/([0-9]+)', date).groups()
    date = datetime.date(int(year), int(month), int(day))
    return (price, date)

fluctuations = []
with open('nasdaq_100_investing_com.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # Ignore header
    for row, row_prev in windowed(reader, 2):
        price, date = row_to_price_date(row)
        price_prev, date_prev = row_to_price_date(row_prev)
        days = (date - date_prev).days
        if days > 1:
            continue
        fluctuations.append(price / price_prev - 1.0)

sns.set_theme()
# Discard outliers for making the chart easy to understand
fluctuations = [x for x in fluctuations if -0.1 <= x <= 0.1]
chart = sns.histplot(data=fluctuations)
chart.get_xaxis().set_label_text("NASDAQ-100 Daily Change")
xticks = [-0.1, -0.05, 0.0, 0.05, 0.1]
chart.set_xticks(xticks)
chart.set_xticklabels('±0%' if x == 0.0 else f'{x:+.02}%' for x in xticks);

chart.get_figure().savefig("nasdaq_100.png")
print("Chart is saved as nasdaq_100.png")