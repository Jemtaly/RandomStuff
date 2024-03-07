# Quthon

A simple quantum simulator implemented in python.

## Usage

### Acquire Qubits

```py
import quthon
qbts = quthon.Qubits(3) # Acquire 3 qubits
```

### Appy quantum logic gates

```py
qbts.H(0)          # Apply a hadamard gate on q1
qbts.H(1)          # Apply a hadamard gate on q2
qbts.TOFF(0, 1, 2) # Apply a toffoli gate, use q1 and q2 to control q3
```

You could also write the above code in the following way:

```py
qbts.H(0).H(1).TOFF(0, 1, 2)
```

### Measure the Qubits (Get the probability distribution table)

```py
prob = qbts.getprob(2, 1, 0) # Obtain the probability distribution table for the states of these three qubits
print(prob[0, 0, 1])         # Print out the probability of {q2, q1, q0} = |001>, it's supposed to be 0.25
```

### An example

Calculate the probability distribution of the sum of 16 random bits:

```py
import quthon
import matplotlib.pyplot as plt
qsta = quthon.Qubits(26)
for i in range(0, 22, 11):
    for j in range(0, 8, 4):
        for k in range(0, 2, 1):
            t = sum([i, j, k])
            qsta.H(t + 0).ADDER(range(t + 0 + 0, t + 0 + 0), range(t + 0 + 0, t + 0 + 0), range(t + 0, t + 1))
        t = sum([i, j])
        qsta.H(t + 2).ADDER(range(t + 0 + 0, t + 0 + 1), range(t + 1 + 0, t + 1 + 1), range(t + 2, t + 4))
    t = sum([i])
    qsta.H(t + 8).ADDER(range(t + 0 + 2, t + 0 + 4), range(t + 4 + 2, t + 4 + 4), range(t + 8, t + 11))
t = sum([])
qsta.H(t + 22).ADDER(range(t + 0 + 8, t + 0 + 11), range(t + 11 + 8, t + 11 + 11), range(t + 22, t + 26))
prob = qsta.getprob(22, 23, 24, 25)
list = meas.T.reshape((-1,)) # list[a << 0 | b << 1 | c << 2 | d << 3] = prob[a, b, c, d]
plt.bar(range(16), list)
plt.show()
```

Screenshot of the running result:

![image](https://user-images.githubusercontent.com/83796250/223098305-1472e264-7c51-42c5-9337-cc8af2123c7d.png)
