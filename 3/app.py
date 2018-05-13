import math
import os
from fractions import Fraction as R
from math import factorial
from random import random, seed
from typing import NamedTuple

i = R(7)
j = R(7)
n = 3 + (i + j) // 8
tau = 5 / (5 + j)
nu = 1 / tau
lam = i / 4


class WithRefusalResult(NamedTuple):
    refuse_probability: R
    average_throughput: R
    relative_throughput: R
    average_channel_filling: R


class WithQueueResult(NamedTuple):
    queue_probability: R
    average_queue_length: R
    average_waiting_time: R
    average_handling_time: R


def with_refusal(ro: R, n: int) -> WithRefusalResult:
    P0: R = 1 / sum([((ro ** x) / R(factorial(x))) for x in range(0, n + 1)])
    Ps = [P0 * (ro ** x) / factorial(x) for x in range(0, n + 1)]
    P_ref = Ps[n]
    Q = 1 - P_ref
    A = lam * Q
    K = sum([i * x for i, x in enumerate(Ps)])
    return WithRefusalResult(P_ref, A, Q, K)


def with_refusal_simulation(lam: R, nu: R, n: int, duration: int) -> WithRefusalResult:
    resolution = 60
    busy = 0
    rejects = 0
    filled_sum = 0
    steps = int(duration * resolution)
    M_prob = math.exp(-lam / resolution)
    for t in range(steps):
        pick = random()
        if pick > M_prob:
            if busy < n:
                busy += 1
            else:
                rejects += 1
        if busy > 0:
            H_prob = math.exp(-nu * busy / resolution)
            pick = random()
            if pick > H_prob:
                busy -= 1
        filled_sum += busy
    P_ref = rejects / duration
    Q = 1 - P_ref
    A = lam * Q
    K = filled_sum / (duration * resolution)
    return WithRefusalResult(P_ref, A, Q, K)


def imitate(count):
    delta_t = 1 / 60
    i = 0
    n_busy = 0
    declined = 0
    accepted = 0
    busy_count = 0
    while i < count / delta_t:
        P_no_inc = math.exp(-lam * delta_t)
        to_go = random()
        if to_go > P_no_inc:
            if n_busy < n:
                n_busy += 1
                accepted += 1
            else:
                declined += 1
        P_free = math.exp(-nu * n_busy * delta_t)
        to_go = random()
        if to_go > P_free:
            if n_busy > 0:
                n_busy -= 1
        busy_count += n_busy
        i += 1
    busy_count *= delta_t
    return accepted / count, declined / count, busy_count / count


def with_queue(ro: R, n: int) -> (R, R, R, R):
    P0 = 1 / sum(
        [((ro ** x) / R(factorial(x))) for x in range(0, n + 1)] + [(ro ** (n + 1)) / (factorial(n) * (n - ro))])
    P_queue = (ro ** (n + 1)) * P0 / (factorial(n) * (n - ro))
    L_queue = (ro ** (n + 1) * P0) / (n * factorial(n) * ((1 - ro / n) ** 2))
    L_system = L_queue + ro
    T_queue = L_queue / lam
    T_system = L_system / lam
    return WithQueueResult(P_queue, L_queue, T_queue, T_system)


def to_float_map(t: tuple) -> tuple:
    e = tuple()
    for v in t:
        e = e + (float(v),)
    return e


# print(lam / nu)
# print(to_float_map(with_refusal(lam / nu, 3)))
# print(imitate(24 * 90))
# print(to_float_map(with_refusal_simultation(lam, nu, n)))
# print(to_float_map(with_queue(lam / nu, n)))
seed()
try:
    os.remove("./report_print.md")
finally:
    with open("./report.md", "r") as income, open("./report_print.md", "w") as outcome:
        text = income.read().split("{}")
        args: tuple = to_float_map(with_refusal(lam / nu, n)) + (3.0,) + to_float_map(
            with_refusal_simulation(lam, nu, n, 24 * 365)) + to_float_map(with_queue(lam / nu, n))
        for i in range(len(text)):
            outcome.write(text[i])
            try:
                outcome.write("{:.5}".format(args[i]))
            except Exception as e:
                print(e)
