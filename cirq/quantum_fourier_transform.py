#!/usr/bin/env python3

import math

import cirq

_NUM_QUBITS = 4


def _initial_state():
    yield cirq.X(cirq.LineQubit(_NUM_QUBITS - 1))


def _swap(qubits):
    """ Swap qubits to reverse and correct QFT order """

    for i in range(len(qubits) // 2):
        yield cirq.SWAP(qubits[i], qubits[len(qubits) - 1 - i])


def _cphase(qubits, i, j, sign):
    return cirq.cphase(sign * (math.pi / 2**(j - i))).on(qubits[j], qubits[i])


def qft(*qubits, swap=True):
    """ Performs the Quantum Fourier Transform """

    for i in range(len(qubits)):
        yield cirq.H(qubits[i])

        for j in range(i + 1, len(qubits)):
            yield _cphase(qubits, i, j, 1)

    if swap:
        yield from _swap(qubits)


def main():
    qubits = cirq.LineQubit.range(_NUM_QUBITS)
    my_qft = cirq.Circuit(_initial_state(), qft(*qubits))

    cirq_qft = cirq.Circuit(_initial_state(), cirq.qft(*qubits))

    my_qft_result = cirq.Simulator().simulate(my_qft)
    cirq_qft_result = cirq.Simulator().simulate(cirq_qft)

    print("my qft:", my_qft_result)
    print()
    print("cirq qft:", cirq_qft_result)


if __name__ == "__main__":
    main()
