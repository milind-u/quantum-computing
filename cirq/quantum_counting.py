import cirq
import math

import quantum_phase_estimation
""" Implementation of Grover's Algorithm with quantum counting """


class GroverIteration(cirq.Gate):
    """
    Given n qubits, finds solutions where the first and last are |1⟩
    """

    def __init__(self, num_qubits, power=1):
        assert num_qubits >= 2

        self.n = num_qubits
        self.power = power
        super(GroverIteration, self)

    def _num_qubits_(self) -> int:
        return self.n

    def _decompose_(self, qubits):
        assert len(qubits) == self.n

        for _ in range(self.power):
            # Oracle
            yield cirq.Z(qubits[-1]).controlled_by(qubits[0])

            # Diffuser
            yield cirq.H.on_each(*qubits)
            yield cirq.X.on_each(*qubits)
            yield cirq.Z(qubits[-1]).controlled_by(*qubits[:-1])
            yield cirq.X.on_each(*qubits)
            yield cirq.H.on_each(*qubits)

    def _circuit_diagram_info_(self, _):
        return ["G**%d" % self.power] * self.n

    def __pow__(self, power):
        return GroverIteration(self.n, self.power * power)


def main():
    n = 4
    # Find the number of solutions with quantum counting
    qubits = cirq.LineQubit.range(100, 100 + n)
    theta = quantum_phase_estimation.main(qubits, GroverIteration(n), cirq.H,
                                          4) * (2 * math.pi)
    # N = 2^n, sin(θ / 2) = sqrt(M / N) -> M = N * sin^2(θ / 2)
    # M_actual = N - M because diffuser adds global phase of -1
    m_float = 2**n - (2**n * math.sin(theta / 2)**2)
    m = int(m_float)
    print("M = %f -> %d" % (m_float, m))

    # Calculate the optimal number of iterations
    r = int((math.pi / 4) * (math.sqrt(2**n / m)))
    print("r =", r)

    # Apply Grover's algorithm
    circ = cirq.Circuit(cirq.H.on_each(*qubits),
                        GroverIteration(n, r)(*qubits),
                        cirq.measure(*qubits, key="result"))
    print(circ)
    print("Grover result:",
          cirq.sample(circ, repetitions=1000).histogram(key="result"))


if __name__ == "__main__":
    main()
