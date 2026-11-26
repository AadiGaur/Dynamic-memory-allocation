#!/usr/bin/env python3
"""
Dynamic Memory Allocation Simulator
===================================
Simulates three classic placement strategies:

    * First Fit  - first block that is big enough
    * Best Fit   - smallest block that is big enough
    * Worst Fit  - largest block (if it is big enough)

For each strategy it shows
    - a step-by-step allocation trace
    - final allocation table
    - unallocated processes
    - remaining (free) memory
    - internal / external fragmentation
    - a comparison table and comparison graph (matplotlib, ASCII fallback)

Two memory models are supported (--mode):

    dynamic : the chosen block is SPLIT; the leftover stays in the block as a
              free hole (default; "remaining memory" shrinks block by block).
    fixed   : fixed partitions; one process occupies a whole block and the
              unused part of that block is INTERNAL fragmentation.

Usage examples
--------------
    python memory_simulator.py                       # interactive (Enter = example)
    python memory_simulator.py --demo                # textbook example
    python memory_simulator.py -b 100 500 200 300 600 -p 212 417 112 426
    python memory_simulator.py --demo --mode fixed --save results.png --no-show
"""

import argparse
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional

# --------------------------------------------------------------------------- #
#  Data structures
# --------------------------------------------------------------------------- #

DEFAULT_BLOCKS = [100, 500, 200, 300, 600]
DEFAULT_PROCESSES = [212, 417, 112, 426]


@dataclass
class TraceStep:
    step: int
    process: int            # process number (1-based)
    size: int
    candidates: List[int]   # block numbers (1-based) that could hold it
    chosen: Optional[int]   # block number (1-based) or None
    note: str
    holes_after: List[int]  # free space in every block after this step


@dataclass
class Result:
    name: str
    mode: str
    block_sizes: List[int]
    proc_sizes: List[int]
    allocation: List[Optional[int]]      # per process -> block index (0-based) / None
    holes: List[int]                     # final free space per block
    placed: List[List[int]]              # per block -> list of process indices
    internal: int = 0
    external: int = 0
    trace: List[TraceStep] = field(default_factory=list)

    # ---- derived metrics -------------------------------------------------- #
    @property
    def total_memory(self):
        return sum(self.block_sizes)

    @property
    def allocated_ids(self):
        return [i for i, b in enumerate(self.allocation) if b is not None]

    @property
    def unallocated_ids(self):
        return [i for i, b in enumerate(self.allocation) if b is None]

    @property
    def allocated_memory(self):
        return sum(self.proc_sizes[i] for i in self.allocated_ids)

    @property
    def free_memory(self):
        return sum(self.holes)

    @property
    def utilization(self):
        return 100.0 * self.allocated_memory / self.total_memory if self.total_memory else 0.0


# --------------------------------------------------------------------------- #
#  Placement strategies: return index of chosen block or None
# --------------------------------------------------------------------------- #

def first_fit(holes: List[int], size: int, free: List[bool]) -> Optional[int]:
    for i, h in enumerate(holes):
        if free[i] and h >= size:
            return i
    return None


def best_fit(holes: List[int], size: int, free: List[bool]) -> Optional[int]:
    best = None
    for i, h in enumerate(holes):
        if free[i] and h >= size and (best is None or h < holes[best]):
            best = i
    return best


def worst_fit(holes: List[int], size: int, free: List[bool]) -> Optional[int]:
    worst = None
    for i, h in enumerate(holes):
        if free[i] and h >= size and (worst is None or h > holes[worst]):
            worst = i
    return worst


STRATEGIES = {
    "First Fit": first_fit,
    "Best Fit": best_fit,
    "Worst Fit": worst_fit,
}

# --------------------------------------------------------------------------- #
#  Simulation core
# --------------------------------------------------------------------------- #

def simulate(name: str, strategy: Callable, blocks: List[int],
             procs: List[int], mode: str = "dynamic") -> Result:
    holes = list(blocks)
    # In fixed mode a block that has been used is no longer available.
    # In dynamic mode a block stays available as long as it has space left.
    available = [True] * len(blocks)
    placed: List[List[int]] = [[] for _ in blocks]
    allocation: List[Optional[int]] = [None] * len(procs)
    res = Result(name, mode, list(blocks), list(procs), allocation, holes, placed)

    for pi, size in enumerate(procs):
        candidates = [i + 1 for i, h in enumerate(holes) if available[i] and h >= size]
        idx = strategy(holes, size, available)

        if idx is None:
            note = "No block is large enough -> NOT ALLOCATED"
            chosen = None
        else:
            chosen = idx + 1
            before = holes[idx]
            allocation[pi] = idx
            placed[idx].append(pi)
            if mode == "fixed":
                waste = before - size
                res.internal += waste
                holes[idx] = 0
                available[idx] = False
                note = (f"Block {chosen} ({before}) -> whole block used, "
                        f"internal waste {waste}")
            else:
                holes[idx] = before - size
                note = f"Block {chosen} ({before}) split -> {holes[idx]} left free"

        res.trace.append(TraceStep(pi + 1, pi + 1, size, candidates, chosen, note, list(holes)))

    # External fragmentation: free memory exists but could not satisfy a
    # waiting process (every remaining hole is smaller than the failed request).
    if res.unallocated_ids:
        res.external = sum(h for i, h in enumerate(holes) if available[i])
    return res


def run_all(blocks, procs, mode) -> List[Result]:
    return [simulate(n, f, blocks, procs, mode) for n, f in STRATEGIES.items()]


# --------------------------------------------------------------------------- #
#  Console output
# --------------------------------------------------------------------------- #

LINE = "=" * 78


def fmt_list(items):
    return ", ".join(map(str, items)) if items else "-"


def print_trace(r: Result):
    print(f"\n{LINE}\n  {r.name.upper()}   (mode: {r.mode})\n{LINE}")
    print(f"Initial blocks : {fmt_list(r.block_sizes)}")
    print("\nAllocation trace:")
    print(f"{'Step':<5}{'Process':<10}{'Size':<7}{'Fits in blocks':<18}{'Decision'}")
    print("-" * 78)
    for t in r.trace:
        fits = fmt_list(t.candidates)
        print(f"{t.step:<5}P{t.process:<9}{t.size:<7}{fits:<18}{t.note}")
        print(f"{'':<5}{'free space per block ->':<35}[{fmt_list(t.holes_after)}]")


def print_result(r: Result):
    print_trace(r)

    print("\nFinal allocation:")
    print(f"{'Process':<10}{'Size':<8}{'Block':<8}{'Block size':<12}")
    print("-" * 40)
    for i, size in enumerate(r.proc_sizes):
        b = r.allocation[i]
        if b is None:
            print(f"P{i+1:<9}{size:<8}{'--':<8}{'Not Allocated':<12}")
        else:
            print(f"P{i+1:<9}{size:<8}{b+1:<8}{r.block_sizes[b]:<12}")

    print("\nMemory map (per block):")
    print(f"{'Block':<8}{'Size':<8}{'Processes':<18}{'Free left':<10}")
    print("-" * 44)
    for b, size in enumerate(r.block_sizes):
        procs = ", ".join(f"P{p+1}" for p in r.placed[b]) or "-"
        if r.mode == "fixed" and r.placed[b]:
            free_txt = f"0 (waste {size - r.proc_sizes[r.placed[b][0]]})"
        else:
            free_txt = str(r.holes[b])
        print(f"{b+1:<8}{size:<8}{procs:<18}{free_txt:<10}")

    un = [f"P{i+1}({r.proc_sizes[i]})" for i in r.unallocated_ids]
    print("\nSummary:")
    print(f"  Unallocated processes     : {fmt_list(un)}")
    print(f"  Allocated memory          : {r.allocated_memory} / {r.total_memory}"
          f"  ({r.utilization:.1f}% utilised)")
    print(f"  Remaining (free) memory   : {r.free_memory}")
    print(f"  Internal fragmentation    : {r.internal}")
    print(f"  External fragmentation    : {r.external}"
          + ("   (free space exists but is too small for the waiting process)"
             if r.external else ""))


def print_comparison(results: List[Result]):
    print(f"\n{LINE}\n  COMPARISON\n{LINE}")
    head = (f"{'Algorithm':<12}{'Allocated':<11}{'Unalloc.':<10}{'Used mem':<10}"
            f"{'Util %':<9}{'Free':<7}{'Int.Frag':<10}{'Ext.Frag':<9}")
    print(head)
    print("-" * len(head))
    for r in results:
        print(f"{r.name:<12}{len(r.allocated_ids):<11}{len(r.unallocated_ids):<10}"
              f"{r.allocated_memory:<10}{r.utilization:<9.1f}{r.free_memory:<7}"
              f"{r.internal:<10}{r.external:<9}")

    best = max(results, key=lambda r: (len(r.allocated_ids), r.allocated_memory))
    ties = [r.name for r in results
            if (len(r.allocated_ids), r.allocated_memory)
            == (len(best.allocated_ids), best.allocated_memory)]
    print(f"\nBest outcome for this input: {', '.join(ties)} "
          f"({len(best.allocated_ids)}/{len(best.proc_sizes)} processes placed, "
          f"{best.utilization:.1f}% utilisation)")


# --------------------------------------------------------------------------- #
#  Graphs
# --------------------------------------------------------------------------- #

def ascii_chart(results: List[Result]):
    """Fallback when matplotlib is not installed."""
    print("\nComparison chart (ASCII):")
    metrics = [
        ("Allocated processes", lambda r: len(r.allocated_ids)),
        ("Memory utilisation %", lambda r: r.utilization),
        ("Internal fragmentation", lambda r: r.internal),
        ("External fragmentation", lambda r: r.external),
        ("Remaining memory", lambda r: r.free_memory),
    ]
    for title, fn in metrics:
        vals = [fn(r) for r in results]
        top = max(vals) or 1
        print(f"\n  {title}")
        for r, v in zip(results, vals):
            print(f"    {r.name:<10}|{'#' * int(40 * v / top):<40}| {v:g}")


def plot_results(results: List[Result], save: Optional[str], show: bool):
    try:
        import matplotlib
        if not show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[matplotlib not installed - run `pip install matplotlib` for graphs]")
        ascii_chart(results)
        return

    names = [r.name for r in results]
    colors = ["#4C78A8", "#59A14F", "#E15759"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(f"Memory Allocation Comparison  (mode: {results[0].mode})",
                 fontsize=15, fontweight="bold")

    def bar(ax, values, title, ylabel, fmt="{:g}"):
        bars = ax.bar(names, values, color=colors)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, (max(values) or 1) * 1.18)
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), fmt.format(v),
                    ha="center", va="bottom", fontsize=9)

    bar(axes[0][0], [len(r.allocated_ids) for r in results],
        "Processes allocated", "count")
    bar(axes[0][1], [r.utilization for r in results],
        "Memory utilisation", "%", "{:.1f}%")
    bar(axes[0][2], [r.free_memory for r in results],
        "Remaining free memory", "units")

    # grouped bars: internal vs external fragmentation
    ax = axes[1][0]
    x = range(len(results))
    w = 0.38
    ax.bar([i - w / 2 for i in x], [r.internal for r in results], w,
           label="Internal", color="#F28E2B")
    ax.bar([i + w / 2 for i in x], [r.external for r in results], w,
           label="External", color="#B07AA1")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_title("Fragmentation")
    ax.set_ylabel("units")
    ax.legend()

    # memory layout of the final state for each algorithm (stacked per block)
    ax = axes[1][1]
    ax.axis("off")
    ax.set_title("Unallocated processes", pad=12)
    lines = []
    for r in results:
        un = [f"P{i+1}({r.proc_sizes[i]})" for i in r.unallocated_ids]
        lines.append(f"{r.name}:  {', '.join(un) if un else 'none'}")
    ax.text(0.02, 0.6, "\n\n".join(lines), fontsize=11, va="center")

    # Stacked final memory map, per block, for each algorithm
    ax = axes[1][2]
    n = len(results[0].block_sizes)
    width = 0.25
    for k, r in enumerate(results):
        xs = [b + (k - 1) * width for b in range(n)]
        bottoms = [0] * n
        for pos, b in enumerate(range(n)):
            for p in r.placed[b]:
                ax.bar(xs[pos], r.proc_sizes[p], width * 0.95, bottom=bottoms[pos],
                       color=colors[k], edgecolor="white")
                ax.text(xs[pos], bottoms[pos] + r.proc_sizes[p] / 2, f"P{p+1}",
                        ha="center", va="center", fontsize=7, color="white")
                bottoms[pos] += r.proc_sizes[p]
            waste = r.block_sizes[b] - bottoms[pos]
            if waste:
                ax.bar(xs[pos], waste, width * 0.95, bottom=bottoms[pos],
                       color="#DDDDDD", edgecolor="white")
    ax.set_xticks(range(n))
    ax.set_xticklabels([f"B{b+1}\n({s})" for b, s in enumerate(results[0].block_sizes)])
    ax.set_title("Final block usage (grey = free / wasted)")
    ax.set_ylabel("units")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=n_) for c, n_ in zip(colors, names)],
              fontsize=8, loc="upper left")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    if save:
        fig.savefig(save, dpi=140)
        print(f"\nGraph saved to {save}")
    if show:
        plt.show()
    plt.close(fig)


# --------------------------------------------------------------------------- #
#  Input handling
# --------------------------------------------------------------------------- #

def read_numbers(prompt: str, default: List[int]) -> List[int]:
    while True:
        raw = input(f"{prompt} [Enter = {' '.join(map(str, default))}]: ").strip()
        if not raw:
            return list(default)
        try:
            nums = [int(x) for x in raw.replace(",", " ").split()]
            if nums and all(n > 0 for n in nums):
                return nums
        except ValueError:
            pass
        print("  Please enter positive integers separated by spaces.")


def validate(blocks, procs):
    if not blocks or not procs:
        sys.exit("Error: need at least one block and one process.")
    if any(x <= 0 for x in blocks + procs):
        sys.exit("Error: all sizes must be positive integers.")


def parse_args():
    p = argparse.ArgumentParser(description="Dynamic Memory Allocation Simulator "
                                            "(First / Best / Worst Fit)")
    p.add_argument("-b", "--blocks", type=int, nargs="+", help="memory block sizes")
    p.add_argument("-p", "--processes", type=int, nargs="+", help="process sizes")
    p.add_argument("--mode", choices=["dynamic", "fixed"], default=None,
                   help="dynamic = split blocks (default), fixed = whole-block partitions")
    p.add_argument("--demo", action="store_true", help="run the textbook example")
    p.add_argument("--save", default="allocation_comparison.png",
                   help="file name for the comparison graph")
    p.add_argument("--no-plot", action="store_true", help="skip the graph")
    p.add_argument("--no-show", action="store_true",
                   help="save the graph but do not open a window")
    return p.parse_args()


def main():
    args = parse_args()

    if args.demo:
        blocks, procs = DEFAULT_BLOCKS, DEFAULT_PROCESSES
    elif args.blocks and args.processes:
        blocks, procs = args.blocks, args.processes
    else:
        print("Dynamic Memory Allocation Simulator")
        print("-----------------------------------")
        blocks = read_numbers("Memory blocks", DEFAULT_BLOCKS)
        procs = read_numbers("Processes     ", DEFAULT_PROCESSES)

    mode = args.mode
    if mode is None:
        if args.demo or (args.blocks and args.processes):
            mode = "dynamic"
        else:
            ans = input("Mode - (d)ynamic split or (f)ixed partitions "
                        "[Enter = dynamic]: ").strip().lower()
            mode = "fixed" if ans.startswith("f") else "dynamic"

    validate(blocks, procs)
    print(f"\nMemory blocks : {fmt_list(blocks)}   (total {sum(blocks)})")
    print(f"Processes     : {fmt_list(procs)}   (total {sum(procs)})")
    print(f"Mode          : {mode}")

    results = run_all(blocks, procs, mode)
    for r in results:
        print_result(r)
    print_comparison(results)

    if not args.no_plot:
        plot_results(results, args.save, show=not args.no_show)


if __name__ == "__main__":
    main()
