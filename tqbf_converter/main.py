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


@dataclass
class EndGadget:
    pass


class DoorEntrance(Enum):
    OPEN = auto()
    TRAVERSE = auto()
    CLOSE = auto()

    def __str__(self):
        if self == self.OPEN:
            return "+"
        elif self == self.TRAVERSE:
            return "~"
        else:
            return "-"


@dataclass
class DoorGadget:
    name: str
    path_exits: Dict[
        DoorEntrance, Union["DoorPath", "ChoiceGadget", EndGadget]
    ] = field(default_factory=dict)

    def __str__(self):
        return self.name


DoorPath = Tuple[DoorGadget, DoorEntrance]


def path_to_str(door_path: DoorPath) -> str:
    next_gadget = door_path[0].path_exits[door_path[1]]

    path_str = f"{door_path[1]}{door_path[0]}"

    if isinstance(next_gadget, ChoiceGadget):
        temp = str(next_gadget)
        temp = temp.replace("\n", "\n  ")
        path_str += f" → {temp}"
    elif isinstance(next_gadget, EndGadget):
        path_str += "!"
    else:
        path_str += f" (→) {path_to_str(next_gadget)}"

    return path_str


@dataclass
class ChoiceGadget:
    name: str
    choices: List[DoorPath] = field(default_factory=list)

    def __str__(self):
        # TODO: This chooses the second choice always. If we were to 
        # print both, our recursion would print repetitively due to 
        # converging paths. I don't know if this is a priority to fix.
        return f"ChoiceGadget\n  [→] {path_to_str(self.choices[1])}"


@dataclass
class ExistentialGadget:
    door_a: DoorGadget
    door_b: DoorGadget
    choice_gadget: ChoiceGadget


def create_and_hook_up_doors_existential(
    variable: int, door_gadgets_literals: Mapping[int, Iterable[DoorGadget]]
) -> ExistentialGadget:

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
        last_door_path[0].path_exits[last_door_path[1]] = warp_target
        last_door_path = warp_target

    # Door A:
    last_door_path = (door_a, DoorEntrance.CLOSE)
    full_path = (
        [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[-variable]]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[variable]]
        + [(door_b, DoorEntrance.OPEN), (door_b, DoorEntrance.TRAVERSE)]
    )
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target
        last_door_path = warp_target

    return ExistentialGadget(door_a, door_b, choice_gadget)


@dataclass
class UniversalGadget:
    door_a: DoorGadget
    door_b: DoorGadget
    door_c: DoorGadget
    door_d: DoorGadget
    choice_gadget: ChoiceGadget


def create_and_hook_up_doors_universal(
    variable: int, door_gadgets_literals: Mapping[int, Iterable[DoorGadget]]
) -> UniversalGadget:
    # Create doors.
    door_a = DoorGadget(name=f"universal_{variable}_a")
    door_b = DoorGadget(name=f"universal_{variable}_b")
    door_c = DoorGadget(name=f"universal_{variable}_c")
    door_d = DoorGadget(name=f"universal_{variable}_d")

    # Create choice gadget.
    choice_gadget = ChoiceGadget(
        name="universal",
        choices=[(door_b, DoorEntrance.OPEN), (door_d, DoorEntrance.TRAVERSE)],
    )

    # Hook doors to literal instance doors.
    last_door_path = (door_d, DoorEntrance.CLOSE)
    full_path = (
        [(door, DoorEntrance.OPEN) for door in door_gadgets_literals[variable]]
        + [(door, DoorEntrance.CLOSE) for door in door_gadgets_literals[-variable]]
        + [(door_a, DoorEntrance.OPEN), (door_a, DoorEntrance.TRAVERSE)]
    )
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target
        last_door_path = warp_target

    # Then, hook to next quantifier... (done in create_and_hook_up_quantifiers())

    # Then, come BACK from that quantifier via the choice gadget...
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
    for warp_target in full_path:
        last_door_path[0].path_exits[last_door_path[1]] = warp_target
        last_door_path = warp_target

    # Then, hook to next quantifier again. (done in create_and_hook_up_quantifiers())

    return UniversalGadget(door_a, door_b, door_c, door_d, choice_gadget)


def create_and_hook_up_doors_clauses(
    clauses: Iterable[Clause],
) -> Tuple[DefaultDict[int, List[DoorGadget]], ChoiceGadget, ChoiceGadget]:
    """
    Return three things:
      - A mapping from literals to a list of doors, one per literal instance.
      - The ChoiceGadget for the first clause in the input.
      - The ChoiceGadget for the last clause in the input.
    """
    door_gadgets_literals: DefaultDict[int, List[DoorGadget]] = defaultdict(list)
    prev_door_1: Optional[DoorGadget] = None
    prev_door_2: Optional[DoorGadget] = None
    prev_door_3: Optional[DoorGadget] = None
    for i, (literal_1, literal_2, literal_3) in enumerate(clauses):
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
        if i == 0:
            first_clause = clause_choice
        if prev_door_1 and prev_door_2 and prev_door_3:
            prev_door_1.path_exits[DoorEntrance.TRAVERSE] = clause_choice
            prev_door_2.path_exits[DoorEntrance.TRAVERSE] = clause_choice
            prev_door_3.path_exits[DoorEntrance.TRAVERSE] = clause_choice
        prev_door_1 = door_1
        prev_door_2 = door_2
        prev_door_3 = door_3
    return door_gadgets_literals, first_clause, clause_choice


@dataclass
class StartGadget:
    path_to: ChoiceGadget

    def __str__(self):
        path_str = str(self.path_to)
        indented_path = path_str.replace("\n", "\n  ")
        return f"StartGadget \n  → {indented_path}"


def create_and_hook_up_quantifiers(
    variables: int,
    door_gadgets_literals: DefaultDict[int, List[DoorGadget]],
    first_clause: ChoiceGadget,
    last_clause: ChoiceGadget,
) -> StartGadget:

    start_gadget: Optional[StartGadget] = None

    # To interleave existential and universal quantifiers:
    #  - Existential's (door_a, TRAVERSE) and (door_b, TRAVERSE) -->
    #      Universal's (door_d, CLOSE).
    #  - Universal's (door_a, TRAVERSE) and (door_a, CLOSE) -->
    #      Existential's ChoiceGadget.
    #
    # To interleave the clause gadgets with the quantifier gadgets:
    #  - The LAST Universal's (door_a, TRAVERSE) and (door_a, CLOSE) -->
    #      the LAST clause's ChoiceGadget.
    #  - The FIRST clause's three doors connect to the LAST Universal's ChoiceGadget.
    #  - The (door_d, TRAVERSE) of one universal quantifier connects to the
    #      previous universal quantifier's ChoiceGadget.
    entrance: Union[ChoiceGadget, DoorPath]
    prev_existential: Optional[ExistentialGadget] = None
    prev_universal: Optional[UniversalGadget] = None
    for alternation in range(1, variables + 1):
        if alternation % 2 == 1:
            ## Existential.
            curr_existential = create_and_hook_up_doors_existential(
                alternation, door_gadgets_literals
            )
            if not prev_universal:
                # This is the first existential gadget, which should be
                # connected from the "start" gadget.
                start_gadget = StartGadget(path_to=curr_existential.choice_gadget)
            else:
                entrance = curr_existential.choice_gadget
                prev_universal.door_a.path_exits[DoorEntrance.TRAVERSE] = entrance
                prev_universal.door_a.path_exits[DoorEntrance.CLOSE] = entrance

            prev_existential = curr_existential
        else:
            ## Universal.
            curr_universal = create_and_hook_up_doors_universal(
                alternation, door_gadgets_literals
            )
            if not prev_existential:
                raise RuntimeError("Missing existential gadget before universal gadget")

            entrance = (curr_universal.door_d, DoorEntrance.CLOSE)
            prev_existential.door_a.path_exits[DoorEntrance.TRAVERSE] = entrance
            prev_existential.door_b.path_exits[DoorEntrance.TRAVERSE] = entrance

            curr_exit: Union[ChoiceGadget, EndGadget]
            if not prev_universal:
                # This is the first universal gadget, which actually
                # connects directly to the "end" gadget.
                curr_exit = EndGadget()
            else:
                curr_exit = prev_universal.choice_gadget
            curr_universal.door_d.path_exits[DoorEntrance.TRAVERSE] = curr_exit

            prev_universal = curr_universal

    curr_universal.door_a.path_exits[DoorEntrance.TRAVERSE] = last_clause
    curr_universal.door_a.path_exits[DoorEntrance.CLOSE] = last_clause
    for door_path in first_clause.choices:
        door_path[0].path_exits[door_path[1]] = curr_universal.choice_gadget

    if not start_gadget:
        raise RuntimeError("Start gadget never initialized - cannot proceed.")
    return start_gadget


def print_gadgets(start_gadget: StartGadget):
    print(start_gadget)


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
