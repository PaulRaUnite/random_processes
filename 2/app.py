import functools
import os
import random
from typing import List

import numpy

i = 7
j = 7
k = 5

ij = i + j
ijk = i + j + k
# A - 0, B - 1, C - 2
P = numpy.array(
    [[0, i / ij, j / ij],
     [i / ijk, k / ijk, j / ijk],
     [j / ij, i / ij, 0]]
)

print("P")
print(P)
w, v = numpy.linalg.eig(P.transpose())
print(v)
v = -1 * v[:, 0]
print("v:", w[0], v)
s = functools.reduce(lambda x, y: x + y, v)
v = v / s
print("v:", functools.reduce(lambda x, y: x + y, v), v)

T = numpy.array([v, v, v])
Z = numpy.linalg.inv(numpy.identity(3) - (P - T))
print("Z", Z)

I = numpy.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
D = numpy.diag([1 / v[0], 1 / v[1], 1 / v[2]])
ZDiag = numpy.diag(Z.diagonal())
M = (numpy.identity(3) - Z + I.dot(ZDiag)).dot(D)
print(M)


# simulation


def interval_choose(x: float, chanses) -> int:
    accum = 0
    for i, chance in enumerate(chanses):
        accum += chance
        if x < accum:
            return i
    raise Exception("chances must be stohastic")


simulations: int = 1_000
iterations: int = 1_000

V = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
N = numpy.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
randoms: List[float] = list()
for _ in range(simulations * iterations):
    randoms.append(random.random())

for sim_num in range(simulations):
    if sim_num % 1000 == 0:
        print(sim_num)
    state: int = 0
    steps: List[int] = [0, 0, 0]
    for iter_num in range(1000 * sim_num, 1000 * sim_num + iterations):
        for i in range(3):
            if state == i or steps[i] != 0:
                steps[i] += 1

        state = interval_choose(randoms[iter_num], P[state])
        for i in range(3):
            if steps[i] != 0:
                V[state, i] += steps[i]
                N[state, i] += 1
        steps[state] = 0

A = numpy.empty((3, 3))
for i in range(3):
    for j in range(3):
        A[i, j] = V[i, j] / N[i, j]
print(A)


def matrix_as_table(m: numpy.ndarray, left: List[str], top: List[str]) -> str:
    w, h = m.shape
    output = "| \\ |"
    for j in range(w):
        output += f" {top[j]} |"
    output += "\n|" + ("---|" * (w + 1)) + "\n"
    for i in range(h):
        output += f"| {left[i]} |"
        for j in range(w):
            output += f" {m[i,j]:5.4} |"
        output += "\n"
    return output


def vector_as_table(v:numpy.ndarray, top: List[str]) -> str:
    [w] = v.shape
    output = "|"
    for j in range(w):
        output += f" {top[j]} |"
    output += "\n|" + ("---|" *  w) + "\n|"
    for j in range(w):
        output += f" {v[j]:5.4} |"
    output += "\n"
    return output


c = ["A", "B", "C"]
try:
    os.remove("./report.md")
except:
    pass
finally:
    with open("./schema.md", "r") as income, open("./report.md", "w") as outcome:
        content = income.read()
        outcome.write(content.format(simulations, iterations, matrix_as_table(P, c, c), vector_as_table(v, c), matrix_as_table(M, c, c), matrix_as_table(A, c,c)))