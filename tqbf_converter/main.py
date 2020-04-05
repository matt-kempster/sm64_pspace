#! /usr/bin/env python3
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import DefaultDict, Dict, Iterable, List, Mapping, Optional, Tuple, Union

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


class DoorEntrance(Enum):
    OPEN = auto()
    TRAVERSE = auto()
    CLOSE = auto()


@dataclass
class DoorGadget:
    name: str
    path_exits: Dict[DoorEntrance, Union["DoorGadget", "ChoiceGadget"]] = field(
        default_factory=dict
    )


@dataclass
class ChoiceGadget:
    name: str
    choices: List[Tuple[DoorGadget, DoorEntrance]] = field(default_factory=list)


def create_and_hook_up_doors_existential(
    variable: int, door_gadgets_literals: Mapping[int, Iterable[DoorGadget]]
) -> None:

    # Create doors.
    door_a = DoorGadget(name=f"existential_{variable}_a")
    door_b = DoorGadget(name=f"existential_{variable}_b")

    # Create choice gadget.
    choice_gadget = ChoiceGadget(
        name=f"existential_{variable}_choices",
        choices=[(door_b, DoorEntrance.CLOSE), (door_a, DoorEntrance.CLOSE)],
    )

    ## Hook doors to literal instance doors.

    # Door B:
    last_door_path = (door_b, DoorEntrance.CLOSE)
    full_path = (
        [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[variable]]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[-variable]]
        + [(door_a, DoorEntrance.OPEN), (door_a, DoorEntrance.TRAVERSE)]
    )
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target[0]
        last_door_path = warp_target

    # Door A:
    last_door_path = (door_a, DoorEntrance.CLOSE)
    full_path = (
        [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[-variable]]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[variable]]
        + [(door_b, DoorEntrance.OPEN), (door_b, DoorEntrance.TRAVERSE)]
    )
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target[0]
        last_door_path = warp_target


def create_and_hook_up_doors_universal(
    variable: int, door_gadgets_literals: Mapping[int, Iterable[DoorGadget]]
) -> None:
    # Create doors.
    door_a = DoorGadget(name=f"universal_{variable}_a")
    door_b = DoorGadget(name=f"universal_{variable}_b")
    door_c = DoorGadget(name=f"universal_{variable}_c")
    door_d = DoorGadget(name=f"universal_{variable}_d")

    # Create choice gadget.
    # TODO

    # Hook doors to literal instance doors.
    last_door_path = (door_d, DoorEntrance.CLOSE)
    full_path = (
        [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[variable]]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[-variable]]
        + [(door_a, DoorEntrance.OPEN), (door_a, DoorEntrance.TRAVERSE)]
    )
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target[0]
        last_door_path = warp_target

    # Then, hook to next quantifier...
    # Then, come BACK from that quantifier via a choice gadget...
    last_door_path = (door_b, DoorEntrance.OPEN)
    full_path = (
        [(door_b, DoorEntrance.TRAVERSE), (door_b, DoorEntrance.CLOSE)]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[variable]]
        + [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[-variable]]
        + [
            (door_d, DoorEntrance.OPEN),
            (door_c, DoorEntrance.OPEN),
            (door_c, DoorEntrance.TRAVERSE),
            (door_c, DoorEntrance.CLOSE),
            (door_a, DoorEntrance.CLOSE),
        ]
    )
    # Then, hook to next quantifier again.


def create_and_hook_up_doors_clauses(
    clauses: Iterable[Clause],
) -> DefaultDict[int, List[DoorGadget]]:

    door_gadgets_literals: DefaultDict[int, List[DoorGadget]] = defaultdict(list)
    prev_door_1: Optional[DoorGadget] = None
    prev_door_2: Optional[DoorGadget] = None
    prev_door_3: Optional[DoorGadget] = None
    for (literal_1, literal_2, literal_3) in clauses:
        # Create a door for each literal appearance
        door_1 = DoorGadget(name=str(literal_1))
        door_2 = DoorGadget(name=str(literal_2))
        door_3 = DoorGadget(name=str(literal_3))
        door_gadgets_literals[literal_1].append(door_1)
        door_gadgets_literals[literal_2].append(door_2)
        door_gadgets_literals[literal_3].append(door_3)
        clause_choice = ChoiceGadget(
            name="clause",
            choices=[
                (door_1, DoorEntrance.TRAVERSE),
                (door_2, DoorEntrance.TRAVERSE),
                (door_3, DoorEntrance.TRAVERSE),
            ],
        )
        if prev_door_1 and prev_door_2 and prev_door_3:
            prev_door_1.path_exits[DoorEntrance.TRAVERSE] = clause_choice
            prev_door_2.path_exits[DoorEntrance.TRAVERSE] = clause_choice
            prev_door_3.path_exits[DoorEntrance.TRAVERSE] = clause_choice
        prev_door_1 = door_1
        prev_door_2 = door_2
        prev_door_3 = door_3
        # Hook them up (?) (TODO)
    return door_gadgets_literals


def translate_to_level(qbf: QBF) -> SM64Level:
    # There's 3 doors per clause; 1 per occurrence of a literal.
    # There's 2 extra doors per existential quantifier gadget,
    # and 4 extra doors per universal quantifier gadget.
    # There's also "choice gadgets", one per quantifier gadget.
    # Each door gadget requires its own "area".

    ## Initialize doors
    door_gadgets_literals = create_and_hook_up_doors_clauses(qbf.formula.clauses)

    for alternation in range(1, qbf.variables + 1):
        if alternation % 2 == 1:
            ## Existential.
            create_and_hook_up_doors_existential(alternation, door_gadgets_literals)
        else:
            ## Universal.
            create_and_hook_up_doors_universal(alternation, door_gadgets_literals)

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
