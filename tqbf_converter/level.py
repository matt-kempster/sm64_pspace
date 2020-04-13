#! /usr/bin/env python3.8
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Text, Tuple

import jinja2
from gadgets import DoorGadget, StartGadget


@dataclass
class Point3D:
    x: int
    y: int
    z: int


@dataclass
class Collision:
    vertices: List[str] = field(default_factory=list)
    tris: List[str] = field(default_factory=list)
    water_boxes: List[str] = field(default_factory=list)


@dataclass
class SM64Level:
    areas: List[Area] = field(default_factory=list)
    geo_inc_c: str = ""
    leveldata_inc_c: str = ""
    model_inc_c: str = ""
    script_inc_c: str = ""


@dataclass
class WaterBox:
    x1: int
    z1: int
    x2: int
    z2: int
    y: int


@dataclass
class DoorInLevel:
    # The center position of the center platform of the door.
    position_traverse: Point3D
    position_open: Point3D = field(init=False)
    position_close: Point3D = field(init=False)

    diamond_positions: List[Point3D] = field(init=False)
    diamond_height_above_platform: int = 15

    # Each platform is a square with side length equal to this times 2.
    platform_half_side_length: int = 213
    # The three platforms are collinear. This is the gap between adjacent platforms.
    gap_size_between_platforms: int = 682

    height_difference_between_platforms: int = 450
    initial_water_level_distance_below_platform: int = -100

    def __post_init__(self):
        self.position_close = Point3D(
            self.position_traverse.x + self.gap_size_between_platforms,
            self.position_traverse.y + self.height_difference_between_platforms,
            self.position_traverse.z,
        )

        self.position_open = Point3D(
            self.position_traverse.x - self.gap_size_between_platforms,
            self.position_traverse.y - self.height_difference_between_platforms,
            self.position_traverse.z,
        )

        self.diamond_positions: List[Point3D] = []
        for point in [self.position_close, self.position_open]:
            self.diamond_positions.append(
                Point3D(point.x, point.y + self.diamond_height_above_platform, point.z)
            )

    def get_named_centers(self) -> List[Tuple[str, Point3D]]:
        names = {
            "Traverse": self.position_traverse,
            "Open": self.position_open,
            "Close": self.position_close,
        }
        return [(platform_name, point) for platform_name, point in names.items()]

    def get_collision_verts(self) -> List[Point3D]:
        verts: List[Point3D] = []

        radius = self.platform_half_side_length
        centers = [self.position_traverse, self.position_open, self.position_close]
        for center in centers:
            verts += [
                Point3D(center.x - radius, center.y, center.z + radius),
                Point3D(center.x + radius, center.y, center.z + radius),
                Point3D(center.x + radius, center.y, center.z - radius),
                Point3D(center.x - radius, center.y, center.z - radius),
            ]
        return verts

    def get_water_box_definition(self) -> WaterBox:
        radius = self.platform_half_side_length
        return WaterBox(
            self.position_open.x - radius,
            self.position_open.z - radius,
            self.position_close.x + radius,
            self.position_close.z + radius,
            self.position_open.y - self.initial_water_level_distance_below_platform,
        )


@dataclass
class Area:
    num: int
    door: DoorInLevel


class LevelTemplateEnvironment(jinja2.Environment):
    def render_collision(
        self, area_num: int, verts: List[Point3D], water: WaterBox
    ) -> Text:
        collision_template = self.get_template("collision.inc.c.j2")
        return collision_template.render(area_num=area_num, verts=verts, water=water)

    def render_movtext(self, water: WaterBox):
        movtext_template = self.get_template("movtext.inc.c.j2")
        return movtext_template.render(water=water)

    def render_geo(self, area_num: int, centers: List[Tuple[str, Point3D]]):
        geo_template = self.get_template("geo.inc.c.j2")
        return geo_template.render(area_num=area_num, centers=centers)

    def render_script(self, areas: List[Area]):
        script_template = self.get_template("script.inc.c.j2")
        return script_template.render(areas=areas)

    def render_model(self, platform_names: List[str], radius: int):
        model_template = self.get_template("model.inc.c.j2")
        return model_template.render(platform_names=platform_names, radius=radius)


def get_template_environment(template_dir: Path) -> LevelTemplateEnvironment:
    return LevelTemplateEnvironment(loader=jinja2.FileSystemLoader(str(template_dir)))


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
    for door2 in DoorGadget.get_instances():
        print(door2.name)

    template_dir = Path(__file__).parent / "templates"
    env = get_template_environment(template_dir)

    areas = [Area(num=1, door=DoorInLevel(Point3D(0, 0, 0)))]
    print(env.render_script(areas=areas))

    for area in areas:
        door = area.door
        verts = door.get_collision_verts()
        water = door.get_water_box_definition()
        centers = door.get_named_centers()
        radius = door.platform_half_side_length
        platform_names = ["Open", "Traverse", "Close"]

        print(env.render_collision(area.num, verts, water))
        print(env.render_movtext(water))
        print(env.render_geo(area.num, centers))
        print(env.render_model(platform_names, radius))

    return SM64Level()
