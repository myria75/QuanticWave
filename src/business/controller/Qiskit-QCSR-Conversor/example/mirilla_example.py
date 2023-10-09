from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from numpy import pi

qreg_q = QuantumRegister(4, 'q')
creg_c = ClassicalRegister(4, 'c')
circuit = QuantumCircuit(qreg_q, creg_c)

circuit.h(qreg_q[0])
circuit.s(qreg_q[1])
circuit.h(qreg_q[3])
circuit.measure(qreg_q[0], creg_c[0])
circuit.cx(qreg_q[1], qreg_q[2])
circuit.z(qreg_q[1])