#! /usr/bin/env python3.8

from dataclasses import dataclass, field
from typing import List

from gadgets import StartGadget


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


def gadgets_to_level(start_gadget: StartGadget) -> SM64Level:
    # Rough strategy:
    #  - Every door has its own area so it can have its own water level.
    #  - Every door has three platform and two water diamonds.
    #    The platforms have one-way warps leading to other doors.
    #  - The "OPEN" path of a door has an optional water diamond.
    #    The "CLOSE" path has a water diamond that overlaps the warp node,
    #    meaning it is mandatory to hit it.
    #    The "TRAVERSE" path has a door (or a warp? haven't decided).
    #    The idea is that you can't use the door while it's underwater.
    #  - A choice gadget is implemented as a platform with the required
    #    number of warps. (All choice gadgets here have fan-out 2 or 3.)
    #  - The StartGadget is where Mario starts when he begins the level.
    #  - The EndGadget contains a star.
    pass
