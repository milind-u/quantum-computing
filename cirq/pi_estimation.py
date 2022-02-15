""" Estimates π with QPE """
import math

import cirq
import numpy as np

import quantum_phase_estimation

_U = np.matrix([[1, 0], [0, math.e**1j]])


class PiEstimationGate(cirq.Gate):
    def __init__(self, u=_U, power=1):
        self.u = u
        self.power = power
        super(PiEstimationGate, self)

    def _num_qubits_(self) -> int:
        return 1

    def _unitary_(self):
        return self.u

    def _circuit_diagram_info_(self, _):
        return "U^%d" % self.power

    def __pow__(self, power):
        return PiEstimationGate(self.u**power, power)


def main():
    theta = quantum_phase_estimation.main(unknown_gate=PiEstimationGate())
    # e^2πiθ = e^i -> 2πiθ = i -> 2πθ = 1 -> π = 1/(2θ)
    pi = 1 / (2 * theta)
    print("math.π = ", math.pi)
    print("π =", pi)


if __name__ == "__main__":
    main()
