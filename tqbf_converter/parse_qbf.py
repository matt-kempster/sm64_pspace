#! /usr/bin/env python3

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


@dataclass
class QBF:
    variables: int
    formula: CNF_3


def get_3cnf_from_formula(formula: str) -> CNF_3:
    clauses: List[Clause] = []
    str_clauses = formula.split(";")
    for str_clause in str_clauses:
        literals = str_clause.split(",")
        try:
            literal_1, literal_2, literal_3 = literals
        except ValueError as err:
            raise ValueError(
                "Error parsing formula! This clause doesn't have exactly 3 literals: "
                f"{str_clause} (in formula {formula})"
            ) from err
        try:
            int_literals = (int(literal_1), int(literal_2), int(literal_3))
        except ValueError as err:
            raise ValueError(
                f"Error parsing formula! One of these isn't an integer: {str_clause}"
            ) from err

        clauses.append(int_literals)
    return CNF_3(clauses)


def verify_formula(quantifiers: int, formula: CNF_3) -> None:
    for clause in formula.clauses:
        for literal in clause:
            if literal > quantifiers or literal < -quantifiers:
                raise ValueError(
                    f"Formula verification failed! The literal {literal} in clause "
                    f"{clause} exceeds the given number of quantifiers {quantifiers}."
                )
