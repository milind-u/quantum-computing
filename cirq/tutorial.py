import cirq

qc = cirq.Circuit()
q0, q1 = cirq.LineQubit.range(2)
qc.append(cirq.H(q0))
qc.append(cirq.CX(q0, q1))

sim = cirq.Simulator()
results = sim.simulate(qc)
print("Bell circuit results:\n%s\n" % results)

qc.append(cirq.measure(q0, q1, key="result"))

samples = sim.run(qc, repetitions=1000)
print("Samples:\n%s" % samples.histogram(key="result"))
