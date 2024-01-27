import csv
import datetime
import math
import re
import statistics

import numpy as np
import seaborn as sns
from more_itertools import windowed
from scipy.stats.distributions import chi2

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

print(f"Sampled {len(fluctuations)} fluctuations")
print(f"Max = {max(fluctuations) * 100.0:+02}%, Min = {min(fluctuations) * 100.0:+02}%")
mean = statistics.mean(fluctuations)
r_year = (1.0 + mean) ** 365.25 - 1.0
print(f"Sample mean = {mean} = {r_year*100.0:.3}% per year")
stdev = statistics.stdev(fluctuations)
print(f"Sample standard deviation = {statistics.stdev(fluctuations)}")

n = float(len(fluctuations))
normal_dist = statistics.NormalDist()
var = statistics.variance(fluctuations)
k95 = -normal_dist.inv_cdf((1.0 - 0.95) / 2.0)
width = k95 * math.sqrt(var / n)
print(f"95% confidence interval of population mean: {mean - width} - {mean + width}")

chi2_min = chi2.ppf(0.025, df=n-1)
chi2_max = chi2.ppf(0.975, df=n-1)
var_min = (n-1) * var / chi2_max
stdev_min = math.sqrt(var_min)
var_max = (n-1) * var / chi2_min
stdev_max = math.sqrt(var_max)
print(f"95% confidence interval of population mean: {math.sqrt(var_min)} - {math.sqrt(var_max)}")

palette = sns.color_palette()
sns.set_theme()

# Draw the histogram
# Ignore outlines for easy understanding of the chart
xticks = [-0.1, -0.05, 0.0, 0.05, 0.1]
fluctuations_for_histogram = [f for f in fluctuations if xticks[0] <= f <= xticks[-1]]
chart = sns.histplot(data=fluctuations_for_histogram, stat='density', color=palette[0])
chart.get_xaxis().set_label_text("NASDAQ-100 Daily Change")
chart.set_xticks(xticks)
chart.set_xticklabels('±0%' if x == 0.0 else f'{int(round(x*100.0)):+}%' for x in xticks)

# Draw the curve with the sample mean and the sample variance
dist = statistics.NormalDist(mean, stdev)
xs = np.linspace(xticks[0], xticks[-1], num=200)
label = f"r = {r_year*100.0:.3}% per year\nσ = {stdev*100.0:.3}%"
sns.lineplot(x=xs, y=np.vectorize(dist.pdf)(xs), label=label, color=palette[1])

chart.get_figure().savefig("nasdaq_100.png")
print("Chart is saved as nasdaq_100.png")
