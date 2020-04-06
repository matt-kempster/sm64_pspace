#! /usr/bin/env python3.8
import argparse
from typing import List

from gadgets import (
    DoorGadget,
    create_and_hook_up_doors_clauses,
    create_and_hook_up_quantifiers,
    print_gadgets,
)
from parse_qbf import QBF, get_3cnf_from_formula, verify_formula
from sm64_levels import Area, SM64Level


def translate_to_level(qbf: QBF) -> SM64Level:
    # There's 3 doors per clause; 1 per occurrence of a literal.
    # There's 2 extra doors per existential quantifier gadget,
    # and 4 extra doors per universal quantifier gadget.
    # There's also "choice gadgets", one per quantifier gadget.
    # Each door gadget requires its own "area".

    door_gadgets_literals, first_clause, last_clause = create_and_hook_up_doors_clauses(
        qbf.formula.clauses
    )
    start_gadget = create_and_hook_up_quantifiers(
        qbf.variables, door_gadgets_literals, first_clause, last_clause
    )
    print_gadgets(start_gadget)

    # Create areas
    door_gadgets: List[DoorGadget] = []
    areas = [Area() for door in door_gadgets]  # probably more; lower bound

    # Create the level
    return SM64Level(areas=areas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Convert instances of QBF in prenex normal form to levels in "
            "Super Mario 64."
        )
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
    parser.add_argument(
        "formula",
        help=(
            "A 3-CNF formula formatted such that each clause is a comma-separated "
            "list of integers, and clauses are separated by semicolons. For example: "
            "'1,2,3;-1,-2,4' would correspond to the 3-CNF formula "
            "'(x1 OR x2 OR x3) AND (NOT(x1) OR NOT(x2) OR NOT(x4)'."
        ),
    )
    args = parser.parse_args()

    if args.quantifiers < 1:
        raise ValueError("You need at least one literal for a proper formula.")

    formula_3cnf = get_3cnf_from_formula(args.formula)
    verify_formula(args.quantifiers, formula_3cnf)

    input_qbf = QBF(args.quantifiers, formula_3cnf)
    level = translate_to_level(input_qbf)
    print(level)
