#! /usr/bin/env python3
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import DefaultDict, Dict, List, Optional, Tuple

# A clause, in 3CNF, is composed of 3 literals.
# Each literal can be positive or negative (but not 0).
# A negative integer corresponds to the negation of the
# literal represented by a positive integer, and vice versa.
Clause = Tuple[int, int, int]


@dataclass
class CNF_3:
    clauses: List[Clause]


def get_3cnf_from_formula(formula: str) -> CNF_3:
    clauses: List[Clause] = []
    str_clauses = formula.split(";")
    for str_clause in str_clauses:
        literals = str_clause.split(",")
        int_literals = tuple(int(lit) for lit in literals)
        if len(int_literals) != 3:
            raise ValueError(
                "Error parsing formula! This clause doesn't have exactly 3 literals: "
                f"{str_clause} (in formula {formula})"
            )
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


@dataclass
class QBF:
    variables: int
    formula: CNF_3


@dataclass
class Collision:
    vertices: List[str] = field(default_factory=list)
    tris: List[str] = field(default_factory=list)
    water_boxes: List[str] = field(default_factory=list)


@dataclass
class Area:
    collision_inc_c: Collision = Collision()
    geo_inc_c: str = ""
    macro_inc_c: str = ""  # mostly empty
    movtext_inc_c: str = ""


@dataclass
class SM64Level:
    areas: List[Area] = field(default_factory=list)
    geo_inc_c: str = ""
    leveldata_inc_c: str = ""
    model_inc_c: str = ""
    script_inc_c: str = ""


class DoorGadgetEntranceType(Enum):
    OPEN = auto()
    TRAVERSE = auto()
    CLOSE = auto()


@dataclass
class DoorGadget:
    name: str
    open_path_warp_to: Optional[Tuple["DoorGadget", DoorGadgetEntranceType]] = None
    traverse_path_warp_to: Optional[Tuple["DoorGadget", DoorGadgetEntranceType]] = None
    close_path_warp_to: Optional[Tuple["DoorGadget", DoorGadgetEntranceType]] = None


# Instead of name, maybe have subclasses; one for
# literal instances, one for quantifier subtypes, etc.


@dataclass
class ChoiceGadget:
    name: str
    choices: List[Tuple[DoorGadget, DoorGadgetEntranceType]] = field(
        default_factory=list
    )


def translate_to_level(qbf: QBF) -> SM64Level:
    # There's 3 doors per clause; 1 per occurrence of a literal.
    # There's 2 extra doors per existential quantifier gadget,
    # and 4 extra doors per universal quantifier gadget.
    # There's also "choice gadgets", one per quantifier gadget.
    # Each door gadget requires its own "area".

    ## Initialize doors
    door_gadgets = []
    door_gadgets_literals: DefaultDict[int, List[DoorGadget]] = defaultdict(list)
    choice_gadgets = []
    for (literal_1, literal_2, literal_3) in qbf.clauses:
        # Create a door for each literal appearance
        door_gadgets_literals[literal_1].append(DoorGadget(name=str(literal_1)))
        door_gadgets_literals[literal_2].append(DoorGadget(name=str(literal_2)))
        door_gadgets_literals[literal_3].append(DoorGadget(name=str(literal_3)))

        # Create a choice gadget for each clause
        # (TODO)

        # Hook them up (?) (TODO)

    for alternation in range(1, qbf.variables + 1):
        if alternation % 2 == 1:
            ## Existential.

            # Create doors.
            door_a = DoorGadget(name=f"existential_{alternation}_a")
            door_b = DoorGadget(name=f"existential_{alternation}_b")

            # Create choice gadget.
            choice_gadgets.append(
                ChoiceGadget(
                    name=f"existential_{alternation}_choices",
                    choices=[
                        (door_b, DoorGadgetEntranceType.CLOSE),
                        (door_a, DoorGadgetEntranceType.CLOSE),
                    ],
                )
            )
            # Hook doors to literal instance doors.
            # (TODO)
            for i, door in enumerate(door_gadgets_literals[alternation]):
                if i == 0:
                    door_b.close_path_warp_to = (
                        door,
                        DoorGadgetEntranceType.OPEN,
                    )
                else:
                    door_gadgets_literals[alternation][i - 1].open_path_warp_to = (
                        door,
                        DoorGadgetEntranceType.OPEN,
                    )
            else:
                pass  # don't forget this edge case

            for door in door_gadgets_literals[-alternation]:
                pass
            else:
                pass

            DoorGadget(f"existential_{alternation}_b").close_path_warp_to = (
                DoorGadget(name=f"{alternation}_occurrence_{1}"),  # if exists
                DoorGadgetEntranceType.OPEN,
            )

        else:
            ## Universal.

            # Create doors.
            door_gadgets.append(DoorGadget(name=f"universal_{alternation}_a"))
            door_gadgets.append(DoorGadget(name=f"universal_{alternation}_b"))
            door_gadgets.append(DoorGadget(name=f"universal_{alternation}_c"))
            door_gadgets.append(DoorGadget(name=f"universal_{alternation}_d"))

            # Hook doors to literal instance doors.
            # (TODO)

    # Create areas
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
