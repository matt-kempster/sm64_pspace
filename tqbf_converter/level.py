#! /usr/bin/env python3.8

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import jinja2
from gadgets import DoorGadget, StartGadget


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
class DoorInLevel:
    # The center position of the center platform of the door.
    position: Tuple[int, int, int]
    # Each platform is a square with side length equal to this times 2.
    platform_half_side_length: int = 213
    # The three platforms are collinear. This is the gap between adjacent platforms.
    gap_size_between_platforms: int = 682
    # Self explanatory.
    height_difference_between_platforms: int = 450

    def get_collision_verts(self) -> List[Tuple[int, int, int]]:
        verts: List[Tuple[int, int, int]] = []

        centers: List[Tuple[int, int, int]] = [
            self.position,
            (
                self.position[0] + self.gap_size_between_platforms,
                self.position[1] + self.height_difference_between_platforms,
                self.position[2],
            ),
            (
                self.position[0] - self.gap_size_between_platforms,
                self.position[1] - self.height_difference_between_platforms,
                self.position[2],
            ),
        ]
        radius = self.platform_half_side_length
        for (center_x, center_y, center_z) in centers:
            verts += [
                (center_x - radius, center_y, center_z + radius),
                (center_x + radius, center_y, center_z + radius),
                (center_x + radius, center_y, center_z - radius),
                (center_x - radius, center_y, center_z - radius),
            ]
        return verts


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
    print("List of doors")

    template_dir = Path(__file__).parent / "templates"
    loader = jinja2.FileSystemLoader(str(template_dir))
    env = jinja2.Environment(loader=loader)
    template = env.get_template("collision.inc.c.j2")
    verts = DoorInLevel((0, 0, 0)).get_collision_verts()
    print(template.render(area_num=1, verts=verts))

    for door in DoorGadget.get_instances():
        print(door.name)

    return SM64Level()
