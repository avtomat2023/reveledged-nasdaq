import re
import math
import sys
from statistics import mean

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

HEADER_REGEX = re.compile(r'\s*#\s*(.*)$')

class ResultReaders:
    def __init__(self, file):
        self._reader = file
        self._header = re.match(HEADER_REGEX, self._reader.readline())[1]
        self._is_exhausted = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._is_exhausted:
            raise StopIteration
        else:
            return ResultReader(self)

    def current_chunk_header(self):
        return self._header

class ResultReader:
    def __init__(self, readers):
        self._readers = readers
        self._header = readers.current_chunk_header()

    def __iter__(self):
        return self

    def __next__(self):
        line = self._readers._reader.readline()
        if not line:
            self._readers._is_exhausted = True
            raise StopIteration

        match = re.match(HEADER_REGEX, line)
        if match:
            self._readers._header = match[1]
            raise StopIteration

        return math.log10(float(line.rstrip()))

    def header(self):
        return self._header

results = [(r.header(), list(r)) for r in ResultReaders(sys.stdin)]
ordinary = results[0][1]
reveledged = results[1][1]

print(f"Average of ordinary: {math.pow(10, mean(ordinary))} Million Yen")
print(f"Average of reveledged: {math.pow(10, mean(reveledged))} Million Yen")

df = pd.DataFrame({header: data for (header, data) in results})
sns.set_theme()
hist = sns.histplot(df, binwidth=0.1, stat='density')

if len(sys.argv) >= 3:
    xlim = (int(sys.argv[1]), int(sys.argv[2]))
else:
    left = math.floor(min([min(ordinary), min(reveledged)]))
    right = math.ceil(max([max(ordinary), max(reveledged)]))
xtick_labels = ["¥1M", "¥10M", "¥100M", "¥1B", "¥10B", "¥100B", "¥1T", "¥10T", "¥100T", "¥1K", "¥10K", "¥100K"]
xticks = list(range(xlim[0], xlim[1] + 1))
if xlim[0] < 0:
    labels = xtick_labels[xlim[0]:] + xtick_labels[:xlim[1]+1]
else:
    labels = xtick_labels[xlim[0]:xlim[1]+1]
hist.set_xlim(xlim)
hist.set_xticks(xticks)
hist.set_xticklabels(labels)
hist.get_xaxis().set_label_text("Asset in 5,000 Days starting from 1M Yen")

sns.move_legend(hist, 'lower center', bbox_to_anchor=(0.5, 1))
plt.tight_layout()

if len(sys.argv) >= 3:
    filename = sys.argv[3]
else:
    filename = 'montecarlo.png'
hist.get_figure().savefig(filename)
print("Histogram is saved as", filename)
