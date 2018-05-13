import math
import os
from typing import Iterable, Tuple, List

import pandas as pd
from matplotlib import pyplot as plt

i = 7
j = 7
n = 4

original_series = [1, 2, 6, 8, 10, 6, 7, 13, 3, 8, 5, 15, 7, 12, 14, 15, 20, 18]
work_series = [(i + j) * x + (i - j) ** 2 + i * j for x in original_series]
print(work_series, sum(original_series[:8]) / 8, sum([x ** 2 for x in original_series[:8]]) / 8)


def smooth_with_weights(income: Iterable[int], weights: Tuple[float, ...]):
    series = iter(income)
    i = 0
    last: Tuple[int] = tuple()
    for value in series:
        if i < len(weights) - 1:
            i += 1
            last += (value,)
            yield float(value)
            continue

        last = last + (value,)
        av: float = 0
        for i, w in enumerate(weights):
            av += last[i] * w
        last = last[1:]
        yield av


def exp_smooth(lam: float, seq: List[float]) -> List[float]:
    prev = seq[0]
    new: List[float] = [seq[0]]
    for v in seq[1:]:
        t = v * lam + (1 - lam) * prev
        new.append(t)
        prev = t
    return new


def av(a: Iterable[float]) -> float:
    count = 0
    sum = 0
    for v in a:
        count += 1
        sum += v
    return sum / count


def coeff(x: List[float], y: List[float]) -> float:
    x_av = av(x)
    y_av = av(y)
    xy_av = av(list(map(lambda a, b: a * b, x, y)))
    st_dev_x = math.sqrt(av(list(map(lambda v: (v - x_av) ** 2, x))))
    st_dev_y = math.sqrt(av(list(map(lambda v: (v - y_av) ** 2, y))))
    return (xy_av - x_av * y_av) / (st_dev_x * st_dev_y)


def gen_autoregr(x: List[float], y: List[float]) -> Tuple[List[float], float, float, float]:
    x_av = av(x)
    y_av = av(y)
    x2_av = av(map(lambda x: x ** 2, x))
    xy_av = av(map(lambda z: z[0] * z[1], zip(x, y)))
    r = coeff(x, y)
    a = (xy_av - x_av * y_av) / (x2_av - x_av ** 2)
    b = y_av - a * x_av
    out: List[float] = [x[0]]
    for v in x:
        out.append(a * v + b)
    return out, r, a, b


CA = list(smooth_with_weights(work_series, (1 / 4, 1 / 4, 1 / 4, 1 / 4)))
WMA = list(smooth_with_weights(work_series, (0.1, 0.15, 0.25, 0.5)))
Exp = exp_smooth(1 / 2, work_series)
index = [x for x in range(len(work_series))]
part = 10
AUTOPREV, prev_r, a1, b1 = gen_autoregr(work_series[:-1], work_series[1:])
AUTOPREV_HALF, prev_half_r, a2, b2 = gen_autoregr(work_series[:part], work_series[1:part + 1])
AUTOTIME, time_r, a3, b3 = gen_autoregr(index[:-1], work_series[1:])
AUTOTIME_HALF, time_half_r, a4, b4 = gen_autoregr(index[:part], work_series[1:part + 1])

points = {"index": index, "original": work_series, "CA": CA, "WMA": WMA, "EXP": Exp,
          "Yn=a*Yn-1+b": AUTOPREV, "Yn=a*t+b": AUTOTIME}
df = pd.DataFrame(points)
plt.plot("index", "original", data=df, color="skyblue", linestyle="dashed")
plt.plot("index", "CA", data=df, color="orange")
plt.plot("index", "WMA", data=df, color="purple")
plt.plot("index", "EXP", data=df, color="lightgreen")
plt.legend()
plt.savefig("./4.png", dpi=200)
plt.clf()
df = pd.DataFrame(points)
plt.plot("index", "original", data=df, color="skyblue", linestyle="dashed")
plt.plot("index", "Yn=a*Yn-1+b", data=df, color="orange")
plt.plot("index", "Yn=a*t+b", data=df, color="purple")
plt.legend()
plt.savefig("./5.png", dpi=200)
plt.clf()
half = {"index": index[:part + 1], "original": work_series[:part + 1], "Yn=a*Yn-1+b": AUTOPREV_HALF,
        "Yn=a*t+b": AUTOTIME_HALF}
[line1] = plt.plot("index", "original", data=half, color="skyblue", linestyle="dashed", label='original')
[line2] = plt.plot("index", "Yn=a*Yn-1+b", data=half, color="orange", label='Yn=a*Yn-1+b')
[line3] = plt.plot("index", "Yn=a*t+b", data=half, color="purple", label="Yn=a*t+b")
plt.legend(handles=[line1, line2, line3])
plt.savefig("./5_part.png", dpi=200)
plt.clf()

fig, ax = plt.subplots()

# Hide axes
ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

# Table from Ed Smith answer
clust_data = list(
    zip(index, original_series, work_series, AUTOPREV, list(map(lambda a, b: a - b, work_series, AUTOPREV))))
collabel = ("i", "original", "generated", "autoregression", "remnants")
ax.table(cellText=clust_data, colLabels=collabel, loc='center')
fig.savefig("./table.png", dpi=200)

try:
    os.remove("./report_print.md")
finally:
    with open("./report.md", "r") as income, open("./report_print.md", "w") as outcome:
        text = income.read().split("{}")
        args: tuple = (a1, b1, time_r, a3, b3, prev_half_r, a2, b2, prev_half_r, a4, b4, time_half_r)
        for i in range(len(text)):
            outcome.write(text[i])
            try:
                outcome.write("{:.5}".format(args[i]))
            except Exception as e:
                print(e)
