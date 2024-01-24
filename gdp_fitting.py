import csv
import math

from scipy.optimize import curve_fit
import seaborn as sns

def linear(x, log_y0, log_r):
    # logarithm of: y0 * r**x
    return log_y0 + log_r*x

def exp(x, y0, r):
    return y0 * r**x

gdp_list = []
with open('us_gdp.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for (_, gdp) in reader:
        gdp_list.append(float(gdp) / 1_000_000_000_000.0)
log_gdp_list = list(map(math.log, gdp_list))

xs = list(map(float, range(0, len(log_gdp_list))))

(y0, r), _pcov = curve_fit(exp, xs, gdp_list, (gdp_list[0], 1.1))
estimated_by_exp = list(map(lambda x: y0 * r**x, xs))
label_exp = f"Exp Least-Squares: Growth = {(r-1.0) * 100.0:.2}%"

(log_y0, log_r), _pcov = curve_fit(linear, xs, log_gdp_list, (log_gdp_list[0], 0.05))
y0 = math.exp(log_y0)
r = math.exp(log_r)
estimated_by_linear = list(map(lambda x: y0 * r**x, xs))
label_linear = f"Linear Least-Squares for Logged Data: Growth = {(r-1.0) * 100.0:.2}%"

sns.pointplot(x=xs, y=gdp_list, markersize=3, linestyle='none', legend='brief', label="Actual GDP")
sns.lineplot(x=xs, y=estimated_by_exp, legend='brief', label=label_exp)
chart = sns.lineplot(x=xs, y=estimated_by_linear, linestyle='--', legend='brief', label=label_linear)

chart.set_xticks([0, 9, 19, 29, 39, 49])
chart.set_xticklabels([1971, 1980, 1990, 2000, 2010, 2020])
chart.get_xaxis().set_label_text("Year")
chart.get_yaxis().set_label_text("United States GDP (Trillion US$)")

chart.get_figure().savefig("gdp_fitting.png")
print("Chart is saved as gdp_fitting.png")
