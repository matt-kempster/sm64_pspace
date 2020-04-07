#! /usr/bin/env python3.8
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    ClassVar,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from parse_qbf import Clause


@dataclass
class StartGadget:
    path_to: ChoiceGadget

    def __str__(self):
        path_str = str(self.path_to)
        indented_path = path_str.replace("\n", "\n  ")
        return f"StartGadget \n  → {indented_path}"


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
    path_exits: Dict[DoorEntrance, Union[DoorPath, ChoiceGadget, EndGadget]] = field(
        default_factory=dict
    )

    instances: ClassVar[List[DoorGadget]] = []

    def __post_init__(self):
        DoorGadget.instances.append(self)

    @classmethod
    def get_instances(cls) -> List[DoorGadget]:
        return DoorGadget.instances

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
        path_str += f" → {path_to_str(next_gadget)}"

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
        name=f"universal_{variable}",
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
        appearances_1 = len(door_gadgets_literals[literal_1])
        door_1 = DoorGadget(name=f"literal_{str(literal_1)}_{appearances_1}")
        door_gadgets_literals[literal_1].append(door_1)

        appearances_2 = len(door_gadgets_literals[literal_2])
        door_2 = DoorGadget(name=f"literal_{str(literal_2)}_{appearances_2}")
        door_gadgets_literals[literal_2].append(door_2)

        appearances_3 = len(door_gadgets_literals[literal_3])
        door_3 = DoorGadget(name=f"literal_{str(literal_3)}_{appearances_3}")
        door_gadgets_literals[literal_3].append(door_3)

        clause_choice = ChoiceGadget(
            name=f"clause{(literal_1, literal_2, literal_3)}",
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
    #      the FIRST clause's ChoiceGadget.
    #  - The LAST clause's three doors connect to the LAST Universal's ChoiceGadget.
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

    curr_universal.door_a.path_exits[DoorEntrance.TRAVERSE] = first_clause
    curr_universal.door_a.path_exits[DoorEntrance.CLOSE] = first_clause
    for door_path in last_clause.choices:
        door_path[0].path_exits[door_path[1]] = curr_universal.choice_gadget

    if not start_gadget:
        raise RuntimeError("Start gadget never initialized - cannot proceed.")
    return start_gadget
