import random
import math
from functools import reduce

import numpy
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt

lambd = 16 / 5
i = 1
j = 6
k = 7
l = 7
print(i+j+k+l)

def exp_transformation(x):\
    return - 1 / lambd * math.log(x)


def discretization(x):
    denom = i + j + k +l
    if 0 <= x < i/denom:
        return 1
    elif i/denom <= x < (i+j)/denom:
        return 2
    elif (i+j)/denom <= x < (i+j+k)/denom:
        return 3
    else:
        return 4


def m(dist: list())-> float:
    return reduce(lambda x,y: x + y, dist)/len(dist)


def d(dist: list())-> float:
    x2 = lambda x: x ** 2
    return m(list(map(x2, dist))) - x2(m(dist))


random_numbers = [random.random() for _ in range(50)]
points = {"x": random_numbers, "exp": [exp_transformation(x) for x in random_numbers], "discrete": [discretization(x) for x in random_numbers]}
df = pd.DataFrame(points)
file = open("table.csv", mode="x")
file.write("x,exp,discrete\n")

for i in range(len(points["x"])):
    file.write("{},{},{}\n".format(points["x"][i], points["exp"][i], points["discrete"][i]))
print("m exp", m(points["exp"]))
print("d exp", d(points["exp"]))
print("lambda-1", 1/lambd)
print("lambda-2", 1/(lambd**2))

print("m discr", m(points["discrete"]))
print("d discr", d(points["discrete"]))
sns.regplot(x="x", y="exp", data=df, fit_reg=False)
plt.show()
sns.regplot(x="x", y="discrete", data=df, fit_reg=False)
plt.show()

#
#
# # data
# df = pd.DataFrame({'x': range(1, 10), 'y': np.random.randn(9) * 80 + range(1, 10)})
#
# # plot
# plt.plot('x', 'y', data=df, linestyle='-', marker='o')
# plt.show()