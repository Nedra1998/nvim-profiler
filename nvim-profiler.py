#!/usr/bin/env python3

__version__ = "0.1.0"
__description__ = "(N)vim startup time profiler and visualizer"

import logging
import re

from argparse import Namespace, ArgumentParser
from subprocess import CompletedProcess, run, PIPE
from pathlib import Path
from typing import Dict, List, Match, NamedTuple, Optional, Tuple, Union
from statistics import mean, stdev
from os.path import commonprefix
from math import nan

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from rich.progress import track
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich import box

console = Console()
install(console=console)
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
log = logging.getLogger()

__STEP_REGEX__ = re.compile(r"^(\d+\.\d+)\s+(\d+\.\d+): (.+)$")
__SOURCING_REGEX__ = re.compile(
    r"^(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+): sourcing (.+)$"
)
__BAR_WIDTH__ = 40
__BLOCK_ELEMENTS__ = ["█", "▉", "▊", "▋", "▌", "▍", "▍", "▎", "▏"]


class SourcedStats(NamedTuple):
    file: str
    total: float
    min: float
    max: float
    avg: float
    std: float
    perc: float


class StartupTimeSample(NamedTuple):
    total: float
    files: Dict[str, List[float]]


class StartupTimes(object):
    def __init__(self):
        self.raw: List[StartupTimeSample] = []

    def parse(self, data: Union[str, List[str]]):
        if isinstance(data, str):
            data = [x.strip() for x in data.split("\n")]
        else:
            data = [x.strip() for x in data]

        total: float = 0.0
        files: Dict[str, List[float]] = {}

        for line in data:
            match: Optional[Match[str]] = __STEP_REGEX__.match(line)
            if match is not None:
                total = max(float(match[1]), total)
                continue

            match = __SOURCING_REGEX__.match(line)
            if match is not None:
                total = max(float(match[1]), total)
                if match[4] in files.keys():
                    files[match[4]].append(float(match[3]))
                else:
                    files[match[4]] = [float(match[3])]
        self.raw.append(StartupTimeSample(total, files))

    def append(self, sample: Optional[StartupTimeSample] = None):
        self.raw.append(sample or StartupTimeSample(0.0, {}))

    def total(self) -> List[float]:
        return [x.total for x in self.raw]

    def files(self) -> Dict[str, List[float]]:
        data: Dict[str, List[float]] = {}
        for sample in self.raw:
            for k, v in sample.files.items():
                if k in data.keys():
                    data[k].append(sum(v))
                else:
                    data[k] = [sum(v)]
        return data

    def __repr__(self) -> str:
        return self.raw.__repr__()


class Gradient(object):
    def __init__(
        self,
        min: float,
        max: float,
        log: bool = False,
        colors: List[str] = ["blue", "green", "yellow", "red"],
    ):
        self.min = min
        self.max = max
        self.log = log
        self.colors = colors

    def _get_color(self, perc: float) -> str:
        if perc >= 1.0:
            return self.colors[-1]
        elif perc <= 0.0:
            return self.colors[0]
        elif not self.log:
            return self.colors[int(len(self.colors) * perc)]
        else:
            return self.colors[int(len(self.colors) * perc ** (1 / 4))]

    def __call__(self, val: float, perc: bool = False) -> str:
        if perc:
            return self._get_color(val)
        else:
            return self._get_color((val - self.min) / (self.max - self.min))


def gen_bar(
    val: float,
    max: float = 1.0,
    width: int = __BAR_WIDTH__,
    grad: Optional[Gradient] = None,
) -> str:
    current_color: Optional[str] = None
    bar: str = ""
    for i in range(0, width):
        if grad is not None:
            color = grad(i / width * max)
            if color != current_color:
                if len(bar) == 0 or bar[-1] == __BLOCK_ELEMENTS__[0]:
                    bar += f"[{color}]"
                current_color = color
        if ((i + 1) / width) * max < val:
            bar += __BLOCK_ELEMENTS__[0]
        elif ((i / width) + 0.875) * max < val:
            bar += __BLOCK_ELEMENTS__[1]
        elif ((i / width) + 0.750) * max < val:
            bar += __BLOCK_ELEMENTS__[2]
        elif ((i / width) + 0.625) * max < val:
            bar += __BLOCK_ELEMENTS__[3]
        elif ((i / width) + 0.500) * max < val:
            bar += __BLOCK_ELEMENTS__[4]
        elif ((i / width) + 0.375) * max < val:
            bar += __BLOCK_ELEMENTS__[5]
        elif ((i / width) + 0.250) * max < val:
            bar += __BLOCK_ELEMENTS__[6]
        elif ((i / width) + 0.125) * max < val:
            bar += __BLOCK_ELEMENTS__[7]
        elif (i / width) * max < val:
            bar += __BLOCK_ELEMENTS__[8]
        else:
            bar += " "
    return bar


def fmt_table(total: SourcedStats, stats: List[SourcedStats]):
    table = Table(title=f"Neovim startup times (total: {total.avg:.3f}ms)")
    table.add_column("File", style="bold magenta")
    table.add_column("Perc")
    table.add_column("Min")
    table.add_column("Average")
    table.add_column("Max")
    table.add_column("Stdev")

    grad_perc = Gradient(
        min([x.perc for x in stats]), max([x.perc for x in stats]), log=True
    )
    grad_min = Gradient(
        min([x.min for x in stats]), max([x.min for x in stats]), log=True
    )
    grad_avg = Gradient(
        min([x.avg for x in stats]), max([x.avg for x in stats]), log=True
    )
    grad_max = Gradient(
        min([x.max for x in stats]), max([x.max for x in stats]), log=True
    )
    grad_std = Gradient(
        min([x.std for x in stats]), max([x.std for x in stats]), log=True
    )

    for r in stats:
        table.add_row(
            r.file.split("/")[-1],
            f"[{grad_perc(r.perc)}]{r.perc:6.2%}[/]",
            f"[{grad_min(r.min)}]{r.min:7.3f}[/]",
            f"[{grad_avg(r.avg)}]{r.avg:7.3f}[/]",
            f"[{grad_max(r.max)}]{r.max:7.3f}[/]",
            f"[{grad_std(r.std)}]{r.std:4.2e}[/]",
        )

    console.print(table)


def fmt_graph(total: SourcedStats, stats: List[SourcedStats]):
    table = Table(
        title=f"Neovim startup times (total: {total.avg:.3f}ms)", box=box.SIMPLE_HEAVY
    )
    table.add_column("File", style="magenta", justify="right")
    table.add_column("Startup Time (Avg)")

    max_avg = max([x.avg for x in stats])
    grad_avg = Gradient(
        min([x.avg for x in stats]), max([x.avg for x in stats]), log=True
    )

    for r in stats:
        bar = gen_bar(r.avg, max_avg, grad=grad_avg).strip()
        bar += f" [bold cyan]{r.avg:5.2f}ms[/]"

        table.add_row(r.file.split("/")[-1], Text.from_markup(bar))

    console.print(table)


def fmt_tree(total: SourcedStats, stats: List[SourcedStats]):
    console.print(
        Text(
            f"Neovim startup times (total: {total.avg:.3f}ms)",
            style="italic",
            justify="center",
        ),
        width=80,
    )

    grad_avg = Gradient(0.0, total.avg, log=True)
    grad_perc = Gradient(0.0, 1.0, log=True)

    paths = [x.file for x in stats]
    root = commonprefix(paths)

    def gen_node(key: str, path: str, parent: Optional[str] = None) -> str:
        if parent is None:
            pms = total.avg
        else:
            pms = sum([x.avg for x in stats if x.file.startswith(parent)])
        ms = sum([x.avg for x in stats if x.file.startswith(path)])
        lperc = ms / pms
        tperc = ms / total.avg
        return f"[magenta]{key}[/] [{grad_avg(ms)}]{ms:5.2f}ms[/] [{grad_perc(lperc)}]{lperc:.2%}[/] ([{grad_perc(tperc)}]{tperc:.2%}[/])"

    tree = Tree(gen_node(root, root))

    def walk_tree(tree: Tree, key: str):
        console.print(key)
        valid = [x[len(key) :].split("/") for x in paths if x.startswith(key)]
        visited = set()
        for p in valid:
            if len(p) == 1:
                tree.add(gen_node(p[0], key + p[0], key))
            else:
                pref = commonprefix([x for x in paths if x.startswith(key + p[0])])
                if pref in paths and pref not in visited:
                    visited.add(pref)
                    tree.add(gen_node(pref[len(key) :], pref, key))
                else:
                    if pref[-1] != "/":
                        pref = "/".join(pref.split("/")[:-1]) + "/"
                        if not p[0] in pref:
                            pref += p[0] + '/'
                    if pref not in visited:
                        visited.add(pref)
                        walk_tree(tree.add(gen_node(pref[len(key) :], pref, key)), pref)

    walk_tree(tree, "/")

    console.print(tree)


def exec(cmd: list[str], samples: int) -> Optional[StartupTimes]:
    cmd += ["--startuptime", "vim.log", "-c", "qa!"]

    file = Path("vim.log")

    data: StartupTimes = StartupTimes()

    for _ in track(
        range(samples),
        description="Profiling neovim...",
        console=console,
        transient=True,
    ):
        result: CompletedProcess = run(cmd, stdout=PIPE, stderr=PIPE)
        if result.returncode != 0:
            log.error(
                f"[magenta]{cmd[0]}[/] exited with non-zero return code ({result.returncode})\n:{result.stderr.decode('utf-8')}",
                extra={"markup": True},
            )
            return None

        if not file.exists() or not file.is_file():
            log.warning(f'Startup log file "{file}" was not created')
            continue

        with file.open() as f:
            data.parse(f.read())

        file.unlink()
    return data


def analyze(data: StartupTimes) -> Tuple[SourcedStats, List[SourcedStats]]:
    stats: List[SourcedStats] = []

    totals: List[float] = data.total()
    total = SourcedStats(
        "Total",
        sum(totals),
        min(totals),
        max(totals),
        mean(totals),
        stdev(totals) if len(totals) != 1 else nan,
        1.0,
    )

    files: Dict[str, List[float]] = data.files()
    for k, v in files.items():
        stats.append(
            SourcedStats(
                k,
                sum(v),
                min(v),
                max(v),
                mean(v),
                stdev(v) if len(v) != 1 else nan,
                sum(v) / total.total,
            )
        )

    stats.sort(key=lambda x: x.avg, reverse=True)
    return total, stats


def main():
    parser = ArgumentParser(description=__description__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "CMD",
        default=["nvim"],
        type=str,
        nargs="*",
        help="(n)vim command to run when profiling startup times",
    )
    parser.add_argument(
        "-s",
        "--samples",
        default=10,
        type=int,
        help="number of samples to take for averaging results",
    )
    parser.add_argument(
        "-c", "--count", type=int, help="number of sourced files to list in the report"
    )
    parser.add_argument(
        "-f",
        "--format",
        default="table",
        choices=(
            "table",
            "graph",
            "tree",
        ),
        help="formatter for displaying the results",
    )

    args: Namespace = parser.parse_args()
    data: Optional[StartupTimes] = exec(args.CMD, args.samples)

    if data is None:
        return False

    total, stats = analyze(data)

    if args.count is not None and len(stats) > args.count:
        stats = stats[: args.count]

    if args.format == "table":
        fmt_table(total, stats)
    elif args.format == "graph":
        fmt_graph(total, stats)
    elif args.format == "tree":
        fmt_tree(total, stats)


if __name__ == "__main__":
    main()
