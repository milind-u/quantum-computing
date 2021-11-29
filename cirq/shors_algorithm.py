#!/usr/bin/env python3
import math
import fractions

import cirq

import quantum_fourier_transform


class ModularExp(cirq.ArithmeticOperation):
    """ Given a, n, and |x⟩|w⟩, returns |x⟩|w ⊕ (a**x % n)⟩ """

    def __init__(self, target, exponent, base, modulus):
        self.target = target
        self.exponent = exponent
        self.base = base
        self.modulus = modulus

    def registers(self):
        return self.target, self.exponent, self.base, self.modulus

    def with_registers(self, *new_registers):
        assert len(new_registers) == 4
        return ModularExp(*new_registers)

    def apply(self, *register_values):
        assert len(register_values) == 4

        target, exponent, base, modulus = register_values
        return target if (
            target >= modulus) else target ^ (base**exponent % modulus)


def order_finding(a, n):
    bit_len = n.bit_length()
    target = cirq.LineQubit.range(bit_len)
    exponent = cirq.LineQubit.range(bit_len, 3 * bit_len)

    return cirq.Circuit(cirq.H.on_each(*exponent),
                        ModularExp(target, exponent, a, n),
                        cirq.measure(*target),
                        cirq.inverse(quantum_fourier_transform.qft(*exponent)),
                        cirq.measure(*exponent, key="result"))


def find_period_quantum(a, n):
    circ = order_finding(a, n)
    result = 0

    # If we measure 0 we have to redo the circuit, 0 doesn't tell us anything about r
    while result == 0:
        result = list(
            cirq.sample(circ, repetitions=1).histogram(key="result").keys())[0]
        print("measured", result)

    # If m is the measurement result and N is bit length of n,
    # jN/r = m -> N = mr/j -> r/j = N/m
    r = fractions.Fraction(2**n.bit_length(), result).numerator

    return r


def find_period_classical(a, n):
    r = 1
    result = a % n
    while result != 1:
        result = (result * a) % n
        r += 1
    print("r = %d" % r)
    return r


def is_prime(i):
    prime = i >= 2
    for j in range(2, int(math.sqrt(i))):
        if i % j == 0:
            prime = False
            break
    return prime


def correct_prime_factor(p, n):
    return n % p == 0 and is_prime(p)


def prime_factors_of(n, quantum):
    p, q = None, None
    for a in range(3, n):
        print("a = %d" % a)
        if math.gcd(a, n) == 1:
            r = find_period_quantum(
                a, n) if quantum else find_period_classical(a, n)
            x = a**(r // 2)

            if (r % 2 == 0) and ((x + 1) % n != 0):
                p = math.gcd(x + 1, n)
                q = math.gcd(x - 1, n)
                if not correct_prime_factor(p, n):
                    p = n / q
                elif not correct_prime_factor(q, n):
                    q = n / p

                if correct_prime_factor(p, n) and correct_prime_factor(q, n):
                    break
    return p, q


N = 35


def main():
    for method, quantum in [("Quantum", True), ("Classical", False)]:
        p, q = prime_factors_of(N, quantum)
        print("%s result: %d = %d * %d" % (method, N, p, q))


if __name__ == '__main__':
    main()
