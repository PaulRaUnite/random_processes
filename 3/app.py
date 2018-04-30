import math
import os
from fractions import Fraction as R
from math import factorial
from random import random
from typing import NamedTuple, List

i = R(7)
j = R(7)
n = 3 + (i + j) // 8
tau = 5 / (5 + j)
nu = 1 / tau
lam = i / 4

simulation_steps = 1_000_000


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


def with_refusal_simultation(lam: R, nu: R, n: int) -> WithRefusalResult:
    Elam = lam / math.exp(float(lam))
    Enu = nu / math.exp(float(nu))
    Enu_prob = lambda k: (nu ** k) / (factorial(k)) * Enu
    is_message = lambda: True if random() <= Elam else False
    is_handled = lambda k: True if random() <= Enu_prob(k) else False
    state = 0
    flow: List[int] = list()
    refuses: int = 0
    requests: int = 0
    for _ in range(simulation_steps):
        flow.append(state)
        if is_message():
            requests += 1
            if state == n:
                refuses += 1
            else:
                state += 1
        if is_handled(state):
            if state != 0:
                state -= 1
    P_ref = refuses / simulation_steps
    K = sum(flow) / R(simulation_steps)
    Q = 1 - P_ref
    A = lam * Q
    return WithRefusalResult(P_ref, A, Q, K)


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


print(lam / nu)
print(to_float_map(with_refusal(lam / nu, 3)))
#print(to_float_map(with_refusal_simultation(lam, nu, n)))
#print(to_float_map(with_queue(lam / nu, n)))

try:
    os.remove("./report_print.md")
finally:
    with open("./report.md", "r") as income, open("./report_print.md", "w") as outcome:
        text = income.read().split("{}")
        args: tuple = to_float_map(with_refusal(lam / nu, n)) +(3.0,)+ to_float_map(with_refusal_simultation(lam, nu, n)) + to_float_map(with_queue(lam / nu, n))
        for i in range(len(text)):
            outcome.write(text[i])
            try:
                outcome.write("{:.5}".format(args[i]))
            except Exception as e:
                print(e)