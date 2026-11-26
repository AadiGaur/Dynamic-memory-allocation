# Dynamic Memory Allocation Simulator

A Python-based Operating System project that simulates and compares three classic memory allocation algorithms: **First Fit, Best Fit, and Worst Fit**.

The simulator demonstrates how processes are allocated to available memory blocks and analyses memory utilization, internal fragmentation, external fragmentation, and remaining free memory.

## Project Overview

Dynamic Memory Allocation is an important memory management technique in Operating Systems. It allows processes to receive memory according to their requirements.

This project implements three memory allocation strategies and provides a step-by-step allocation trace, final memory map, comparison table, and graphical representation.

## Features

- **First Fit:** Allocates the first available memory block that is large enough.
- **Best Fit:** Allocates the smallest available block that can accommodate the process.
- **Worst Fit:** Allocates the largest available block.
- **Dynamic Memory Allocation:** Splits memory blocks and keeps the remaining space available.
- **Fixed Partition Allocation:** Allocates an entire block to one process.
- Step-by-step allocation trace.
- Final memory allocation table.
- Internal and external fragmentation calculation.
- Memory utilization analysis.
- Graphical comparison using Matplotlib.
- ASCII chart fallback if Matplotlib is unavailable.
- Custom memory blocks and process sizes.

## Technologies Used

- Python 3
- Matplotlib
- Dataclasses
- Argparse
- Standard Python Libraries

## Project Structure

```text
Dynamic-Memory-Allocation-Simulator/
│
├── memory_simulator.py
├── allocation_comparison.png
└── README.md
```

## Installation

**1. Clone the repository**

```bash
git clone <repository-url>
```

**2. Navigate to the project directory**

```bash
cd Dynamic-Memory-Allocation-Simulator
```

**3. Install required library**

```bash
pip install matplotlib
```

## How to Run

**1. Interactive Mode**

```bash
python memory_simulator.py
```

**2. Run Default Demonstration**

```bash
python memory_simulator.py --demo
```

**3. Provide Custom Memory Blocks and Processes**

```bash
python memory_simulator.py -b 100 500 200 300 600 -p 212 417 112 426
```

**4. Run Fixed Partition Mode**

```bash
python memory_simulator.py --demo --mode fixed
```

**5. Save Graph Without Displaying It**

```bash
python memory_simulator.py --demo --save results.png --no-show
```

**6. Skip Graph Generation**

```bash
python memory_simulator.py --demo --no-plot
```

## Example Input

**Memory Blocks:**

```text
100 500 200 300 600
```

**Processes:**

```text
212 417 112 426
```

**Allocation Algorithms:**

1. First Fit
2. Best Fit
3. Worst Fit

## Memory Allocation Algorithms

| Algorithm | Working Principle |
|---|---|
| First Fit | Selects the first suitable memory block. |
| Best Fit | Selects the smallest suitable memory block. |
| Worst Fit | Selects the largest suitable memory block. |

## Performance Analysis

The simulator compares algorithms using the following parameters:

- Number of allocated processes
- Number of unallocated processes
- Allocated memory
- Memory utilization percentage
- Remaining free memory
- Internal fragmentation
- External fragmentation

It also identifies the best allocation outcome for the given input based on the number of allocated processes and allocated memory.

## Output

The program generates:

1. Step-by-step allocation trace.
2. Final process allocation table.
3. Memory map for each algorithm.
4. Unallocated process details.
5. Memory utilization statistics.
6. Fragmentation analysis.
7. Algorithm comparison table.
8. Graphical comparison chart.

## Learning Outcomes

- Understanding memory management in Operating Systems.
- Learning different memory allocation strategies.
- Understanding internal and external fragmentation.
- Analysing memory utilization.
- Comparing the performance of allocation algorithms.
- Implementing Operating System concepts using Python.

## Conclusion

The Dynamic Memory Allocation Simulator provides a practical understanding of memory management techniques used in Operating Systems. It demonstrates how First Fit, Best Fit, and Worst Fit algorithms allocate memory and compares their performance through statistical and graphical analysis.

This project helps students understand memory allocation, fragmentation, and efficient memory utilization.

---

**Project:** Dynamic Memory Allocation Simulator  
**Domain:** Operating Systems  
**Language:** Python  
**Course:** ENCS303
