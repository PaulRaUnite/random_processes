import random
from functools import reduce
from typing import List

import numpy
import os
from pathlib import Path


def interval_choose(x: float, chanses) -> int:
    if x > 1 or x < 0:
        raise Exception("x not from (0,1)")

    accum = 0
    for i, chance in enumerate(chanses):
        accum += chance
        if x < accum:
            return i
    raise Exception("chanses must be stohastic")


i = 7
j = 7
k = 5

ij = i + j
jk = j + k
ki = i + k
ijk = i + j + k
P = numpy.array(
    [[1,      0,       0,       0,       0],
     [0,      1,       0,       0,       0],
     [i / ij, 0,       0,       j / ij,  0],
     [0,      0,       i / ijk, k / ijk, j / ijk],
     [0,       j / jk, 0,       k / jk,  0]])

print("P:", P)
Q = P[2:, 2:]
print("Q:", Q)
R = P[2:5, 0:2]
print("R:", R)
E = numpy.identity(3)
N = numpy.linalg.inv(E - Q)
print("N:", N)
B = N.dot(R)
print("B:", B)

living_left: List[int] = list()
living_middle: List[int] = list()
living_right: List[int] = list()
river_falls: int = 0
spikes_falls: int = 0

simulations: int = 10000
limitation: int = 1000
for _ in range(simulations):
    state: int = 2
    left: int = 0
    middle: int = 0
    right: int = 0
    for step in range(limitation):
        if state == 2:
            left += 1
        elif state == 3:
            middle += 1
        elif state == 4:
            right += 1

        prev = state
        state = interval_choose(random.random(), P[prev])

        if state < 2:
            if state == 0:
                river_falls += 1
            elif state == 1:
                spikes_falls += 1
            living_left.append(left)
            living_middle.append(middle)
            living_right.append(right)
            break

print("---------------------------")
print(living_left)
print(living_middle)
print(living_right)
print(river_falls)
print(spikes_falls)
print("---------------------------")

template_file = open("./scheme.md", mode="r")
template = template_file.read()
template_file.close()

report = Path("./report.md")
if report.is_file():
    os.remove("./report.md")

outcome = open("./report.md", mode="w")
args = list()
for i in range(5):
    for j in range(5):
        args.append("{:.5f}".format(P[i, j]))

for i in range(3):
    for j in range(3):
        args.append("{:.5f}".format(N[i, j]))

for i in range(3):
    for j in range(2):
        args.append("{:.5f}".format(B[i, j]))

add = lambda x,y: x+y
avg = lambda li: 0 if len(li) == 0 else reduce(add, li, 0)/len(li)
outcome.write(template.format(*args,
                              N[0][0], N[0][1], N[0][2], (N[0][0] + N[0][1] + N[0][2])/3,
                              avg(living_left), avg(living_middle), avg(living_right), avg(living_right+living_middle+living_left),
                              B[0][0], B[0][1], B[0][0] + B[0][1],
                              river_falls/simulations, spikes_falls/simulations, (river_falls+spikes_falls)/simulations))

outcome.close()