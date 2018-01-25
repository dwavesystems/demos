# Demo for Circuit Fault Diagnosis

## How to run the demo

```
>>> pip install -r requirements.txt
>>> python demo.py
```

The demo will construct a Binary Quadratic Model for a three-bit multiplier and embed it on the system.
The user will be prompted for 3 integers:
 * multiplier A (<=7)
 * multiplicand B (<=7)
 * product P (<=63)

The system will find a minimum fault diagnosis and output for each gate whether it is valid or faulty.

<!-- ## How to run the demo with the QPU

```
>>> pip install -r requirements_qpu.txt
>>> python demo.py
``` -->

## Interesting cases to try
There are four cases in which only one faulty gate can lead to five of the six bits in the product being incorrect:
 * `A = 6; B = 5; P = 32`
 * `A = 5; B = 6; P = 32`
 * `A = 7; B = 4; P = 34`
 * `A = 4; B = 7; P = 34`

There are four cases in which only two faulty gates can lead to all six bits in the product being incorrect:
 * `A = 6; B = 5; P = 33`
 * `A = 5; B = 6; P = 33`
 * `A = 7; B = 4; P = 35`
 * `A = 4; B = 7; P = 35`

The maximum number of faulty gates in a minimum fault diagnosis for this circuit is four.
Many of these cases only product in four of the six bits in the product being incorrect.
One such case is: `A = 7; B = 6; P = 1`.

In general, the number of incorrect bits in the product is greater than or equal to the number of faulty gates.

## License

See LICENSE file.
