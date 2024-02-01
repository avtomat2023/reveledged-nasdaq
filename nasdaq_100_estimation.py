import csv
import datetime
import math
import re
import statistics

import numpy as np
import seaborn as sns
from more_itertools import windowed

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
        f = price / price_prev - 1.0
        if days > 1:
            print(f"Ignored multi-day fluctuation: {date_prev} - {date} {f * 100.0:+02}%")
            continue
        fluctuations.append(f)

n = len(fluctuations)
print(f"Sampled {n} fluctuations")
print(f"Max = {max(fluctuations) * 100.0:+02}%, Min = {min(fluctuations) * 100.0:+02}%")
mean = statistics.mean(fluctuations)
r_year = (1.0 + mean) ** 365.0 - 1.0
print(f"Sample mean = {mean} = {r_year*100.0:.3}% per year")
stdev = statistics.stdev(fluctuations)
print(f"Sample standard deviation = {stdev}")

normal_dist = statistics.NormalDist()
var = statistics.variance(fluctuations)
k95 = -normal_dist.inv_cdf((1.0 - 0.95) / 2.0)
width = k95 * math.sqrt(var / n)
print(f"95% confidence interval of population mean: [{mean - width}, {mean + width}]")

m = math.sqrt(2 * (n-1))
stdev_min = m*stdev / (m+k95)
stdev_max = m*stdev / (m-k95)
print(f"95% confidence interval of population standard deviation: [{stdev_min}, {stdev_max}]")

palette = sns.color_palette()
sns.set_theme()

# Draw the histogram
xticks = np.linspace(-0.1, 0.1, 11)
# Ignore outlines for easy understanding of the chart
fluctuations_for_histogram = []
for f in fluctuations:
    if f < xticks[0] or xticks[-1] < f:
        print(f"This outliner won't be drawn on the histogram: {f*100.0:+}%")
        continue
    fluctuations_for_histogram.append(f)
chart = sns.histplot(data=fluctuations_for_histogram, stat='density', color=palette[0])
chart.get_xaxis().set_label_text("NASDAQ-100 Daily Change")
chart.set_xticks(xticks)
chart.set_xticklabels('±0%' if x == 0.0 else f'{int(round(x*100.0)):+}%' for x in xticks)

chart.get_figure().savefig("nasdaq_100.png")
print("Histogram is saved as nasdaq_100.png")

# Draw the curve with the sample mean and the sample variance
dist = statistics.NormalDist(mean, stdev)
xs = np.linspace(xticks[0], xticks[-1], num=200)
label = f"r = {r_year*100.0:.3}% per year\nσ = {stdev*100.0:.3}%"
chart = sns.lineplot(x=xs, y=np.vectorize(dist.pdf)(xs), label=label, color=palette[1])

chart.get_figure().savefig("nasdaq_100_with_curve.png")
print("Histogram is saved as nasdaq_100_with_curve.png")
