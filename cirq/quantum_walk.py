#!/usr/bin/env python3
"""
    Demonstrates the difference between a classical and quantum walk.
    This involves traversing a number line in which the ends are connected, meaning
    that going past the right end of the line loops around to the left, and vice
    versa. A classical walker will randomly walk one step left or right, and will
    stay close to the starting position with a much higher probability.
    On the other hand, a quantum walker will be travelling left and right at the
    same time, and it interferes with itself causing higher peaks of probabilities
    of being found in certain positions, and lower troughs in others.

"""
import random

import cirq
import matplotlib.pyplot as plt

NUM_QUBITS = 7
POSITIONS = 2**NUM_QUBITS
INITIAL_POSITION_POW = NUM_QUBITS - 1
STEPS = 30
SAMPLES = 5000

_coin = cirq.LineQubit(0)
_qubits = cirq.LineQubit.range(1, NUM_QUBITS + 1)


def classical_walk():
    results = {}
    for _ in range(SAMPLES):
        pos = 2**INITIAL_POSITION_POW
        for _ in range(STEPS):
            coin_flip = bool(random.randint(0, 1))
            pos += 1 if coin_flip else -1

            if pos < 0:
                pos = POSITIONS - 1
            elif pos >= POSITIONS:
                pos = 0

        if pos in results:
            results[pos] += 1
        else:
            results[pos] = 1
    return results


def initial_state():
    yield cirq.X(_qubits[INITIAL_POSITION_POW])

    yield cirq.H(_coin)
    yield cirq.S(_coin)


def walk_step():
    yield cirq.H(_coin)
    yield cirq.X(_coin)

    mcx = lambda i: cirq.X(_qubits[i]).controlled_by(_coin, *_qubits[:i])

    # Addition
    for i in range(NUM_QUBITS):
        yield mcx(i)
        if i != NUM_QUBITS - 1:
            yield cirq.X(_qubits[i])

    yield cirq.X(_coin)

    # Subtraction
    for i in range(NUM_QUBITS - 1, 0, -1):
        if i != NUM_QUBITS - 1:
            yield cirq.X(_qubits[i])
        yield mcx(i)


def quantum_walk():
    circuit = cirq.Circuit(initial_state())
    for _ in range(STEPS):
        circuit.append(walk_step())
    circuit.append(cirq.measure(*_qubits, key='x'))

    sim = cirq.Simulator()
    results = sim.run(circuit, repetitions=SAMPLES).histogram(key='x')
    return results


def plot(results, title):
    x = list(results.keys())
    x.sort()
    y = [dict(results)[i] for i in x]

    plt.plot(x, y)
    plt.scatter(x, y)
    plt.title(title)
    plt.xlabel("Final position")
    plt.ylabel("Occurences")
    plt.show()


def main():
    for walk, title in ((classical_walk, "Classical Walk"), (quantum_walk,
                                                             "Quantum Walk")):
        results = walk()
        print("%s Results:\n%s" % (title, results))
        plot(results, title)


if __name__ == '__main__':
    main()
