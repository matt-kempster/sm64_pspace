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
    position_traverse: Tuple[int, int, int]
    position_open: Tuple[int, int, int] = field(init=False)
    position_close: Tuple[int, int, int] = field(init=False)

    # Each platform is a square with side length equal to this times 2.
    platform_half_side_length: int = 213
    # The three platforms are collinear. This is the gap between adjacent platforms.
    gap_size_between_platforms: int = 682

    height_difference_between_platforms: int = 450
    initial_water_level_distance_below_platform: int = -100

    def __post_init__(self):
        self.position_close = (
            self.position_traverse[0] + self.gap_size_between_platforms,
            self.position_traverse[1] + self.height_difference_between_platforms,
            self.position_traverse[2],
        )

        self.position_open = (
            self.position_traverse[0] - self.gap_size_between_platforms,
            self.position_traverse[1] - self.height_difference_between_platforms,
            self.position_traverse[2],
        )

    def get_named_centers(self) -> List[Tuple[str, int, int, int]]:
        names = {
            "Traverse": self.position_traverse,
            "Open": self.position_open,
            "Close": self.position_close,
        }
        return [
            (platform_name, center_x, center_y, center_z)
            for platform_name, (center_x, center_y, center_z) in names.items()
        ]

    def get_collision_verts(self) -> List[Tuple[int, int, int]]:
        verts: List[Tuple[int, int, int]] = []

        radius = self.platform_half_side_length
        centers = [self.position_traverse, self.position_open, self.position_close]
        for (center_x, center_y, center_z) in centers:
            verts += [
                (center_x - radius, center_y, center_z + radius),
                (center_x + radius, center_y, center_z + radius),
                (center_x + radius, center_y, center_z - radius),
                (center_x - radius, center_y, center_z - radius),
            ]
        return verts

    def get_water_box_definition(self) -> Tuple[int, int, int, int, int]:
        radius = self.platform_half_side_length
        return (
            self.position_open[0] - radius,  # x1
            self.position_open[2] - radius,  # z1
            self.position_close[0] + radius,  # x2
            self.position_close[2] + radius,  # z2
            self.position_open[1] - self.initial_water_level_distance_below_platform,
        )


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

    door = DoorInLevel((0, 0, 0))

    collision_template = env.get_template("collision.inc.c.j2")
    verts = door.get_collision_verts()
    water = door.get_water_box_definition()
    print(
        collision_template.render(
            area_num=1,
            verts=verts,
            water_x1=water[0],
            water_z1=water[1],
            water_x2=water[2],
            water_z2=water[3],
            water_y=water[4],
        )
    )

    geo_template = env.get_template("geo.inc.c.j2")
    centers = door.get_named_centers()
    print(geo_template.render(area_num=1, centers=centers))

    for door2 in DoorGadget.get_instances():
        print(door2.name)

    return SM64Level()
