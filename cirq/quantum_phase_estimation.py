#!/usr/bin/env python3
import math

import cirq
import numpy as np

import quantum_fourier_transform


def _eigenvalue(theta):
    return math.e**(((2 * math.pi) * theta) * 1j)


_THETA = 1 / 3
_U = np.matrix([[1, 0], [0, _eigenvalue(_THETA)]])


class _UnknownGate(cirq.Gate):
    def __init__(self, u=_U):
        self.u = u
        super(_UnknownGate, self)

    def _num_qubits_(self) -> int:
        return 1

    def _unitary_(self):
        return self.u

    def _circuit_diagram_info_(self, _):
        return "U"

    def __pow__(self, power):
        return _UnknownGate(self.u**power)


def qpe(psi, num_counting_qubits, unknown_gate):
    counting_qubits = cirq.LineQubit.range(num_counting_qubits)

    yield cirq.H.on_each(*counting_qubits)

    power = 1
    for qubit in counting_qubits:
        yield (unknown_gate**power).on(psi).controlled_by(qubit)
        power *= 2

    yield quantum_fourier_transform.qft_dagger(*counting_qubits, swap=False)
    yield cirq.measure(*counting_qubits, key="result")


_NUM_COUNTING_QUBITS = 20
_REPETITIONS = 1000


def main():
    psi = cirq.NamedQubit("ψ")
    circ = cirq.Circuit(cirq.X(psi),
                        qpe(psi, _NUM_COUNTING_QUBITS, _UnknownGate()))
    print(circ)

    result = cirq.sample(circ,
                         repetitions=_REPETITIONS).histogram(key="result")

    numerator_theta = max(result, key=result.get)
    denominator_theta = 2**_NUM_COUNTING_QUBITS
    theta = numerator_theta / denominator_theta
    print("Actual θ =", _THETA)
    print("Estimated θ = %d/%d = %f" %
          (numerator_theta, denominator_theta, theta))
    print("Eigenvalue of U: e^2πiθ = e^2πi%f = %s" %
          (theta, _eigenvalue(theta)))


if __name__ == "__main__":
    main()
