import cirq
import numpy as np
"""
CHSH Game demonstrating Bell's Theorem:

Alice and Bob given bits x and y, output bits a and b

Need to make it so that x * y = a ⊕ b.
I.E. If x and y are 1, return different outputs, otherwise same.

Classically the best way to do this is always returning 0, giving a winning probability of 0.75.
By entangling the output qubits and performing clever rotations based on inputs, a quantum solution
gets a winning probability of cos^2(π/8), or around 0.854!
"""


class Rotation(cirq.Gate):
    def __init__(self, theta):
        self.theta = theta
        self.u = np.matrix([[np.cos(theta), -np.sin(theta)],
                            [np.sin(theta), np.cos(theta)]])

    def _num_qubits_(self) -> int:
        return 1

    def _unitary_(self):
        return self.u

    def _circuit_diagram_info_(self, _):
        return "R(%d)" % self.theta


def play(alice_input, bob_input):
    alice_output, bob_output = cirq.LineQubit.range(2)
    # Create bell pair
    circ = cirq.Circuit(cirq.H(alice_output), cirq.CX(alice_output,
                                                      bob_output))

    # Rotate measurement basis based on inputs - keep the relative angle π/8 if the inputs aren't both one,
    # otherwise separate them by 3π/8.
    # This makes the probability of success cos^2(π/8)
    if alice_input:
        circ.append(Rotation(np.pi / 4.0)(alice_output))

    circ.append(Rotation((-1 if bob_input else 1) * (np.pi / 8.0))(bob_output))

    circ.append(cirq.measure(alice_output, bob_output, key="result"))

    samples = 1024
    result = cirq.sample(circ, repetitions=samples).histogram(key="result")

    win_percent = 0
    for outputs in result:
        # If they won, increment the winnings
        alice_output_result, bob_output_result = (outputs &
                                                  (1 << 1)) >> 1, outputs & 1
        if alice_input * bob_input == alice_output_result ^ bob_output_result:
            win_percent += result[outputs]
    win_percent /= samples
    print("Alice input: %d, Bob input: %d, Accuracy: %.4f%%" %
          (alice_input, bob_input, win_percent * 100))


def main():
    print("Expected accuracy: %.4f%%" % (np.cos(np.pi / 8)**2 * 100))
    for alice_input in [0, 1]:
        for bob_input in [0, 1]:
            play(alice_input, bob_input)


if __name__ == "__main__":
    main()
