#! /usr/bin/env python3
import argparse
from dataclasses import dataclass

from typing import List, Tuple

# A clause, in 3CNF, is composed of 3 literals.
# Each literal can be positive or negative (but not 0).
# A negative integer corresponds to the negation of the
# literal represented by a positive integer, and vice versa.
Clause = Tuple[int, int, int]


@dataclass
class CNF_3:
    clauses: List[Clause]


def get_3cnf_from_formula(formula: str) -> CNF_3:
    pass


@dataclass
class QBF:
    variables: int
    formula: CNF_3


@dataclass
class SM64Level:
    pass


def translate_to_level(qbf: QBF) -> SM64Level:
    return SM64Level()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert instances of QBF in prenex normal form to levels in Super Mario 64."
    )
    parser.add_argument(
        "quantifiers",
        type=int,
        help=(
            "The number of alternating quantifiers in the formula, 1-indexed, where "
            "the first quantifier is EXISTS(). If this number is odd, the last "
            "quantifier is EXISTS(). If it is even, the last quantifier is FORALL()."
        ),
    )
    parser.add_argument("formula", help=("A 3-CNF formula. Hm..."))
    args = parser.parse_args()
    input_qbf = QBF(args.quantifiers, get_3cnf_from_formula(args.formula))
    level = translate_to_level(input_qbf)
    print(level)
