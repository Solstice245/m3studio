# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from math import pi, cos, sin
from mathutils import Vector as V
from mathutils import Color as C


att_point_color_normal = C((0.1, 0.5, 0.1))
att_point_color_select = C((0.3, 1.0, 0.3))

hittest_color_normal = C((0.4, 0.3, 0.4))
hittest_color_select = C((0.75, 0.6, 0.75))

light_color_normal = C((0.5, 0.5, 0.1))
light_color_select = C((1.0, 1.0, 0.25))

particle_color_normal = C((0.5, 0.1, 0.1))
particle_color_select = C((1.0, 0.3, 0.3))

force_color_normal = C((0.6, 0.3, 0.1))
force_color_select = C((1.0, 0.6, 0.2))

projector_color_normal = C((0.4, 0.0, 0.4))
projector_color_select = C((0.8, 0.2, 0.8))

physics_color_normal = C((0.3, 0.1, 0.7))
physics_color_select = C((0.6, 0.3, 1.0))

cloth_color_normal = C((0.5, 0.0, 0.25))
cloth_color_select = C((1.0, 0.1, 0.6))

camera_color_normal = C((0.1, 0.2, 0.5))
camera_color_select = C((0.3, 0.6, 1.0))

ik_color_normal = C((0.5, 0.25, 0.0))
ik_color_select = C((1.0, 0.5, 0.15))

shbx_color_normal = C((0.1, 0.25, 0.5))
shbx_color_select = C((0.25, 0.75, 1.0))

warp_color_normal = C((0.1, 0.1, 0.5))
warp_color_select = C((0.3, 0.3, 1.0))

turret_yaw_color_normal = C((0.3, 0.1, 0.7))
turret_yaw_color_select = C((0.6, 0.3, 1.0))

turret_pitch_color_normal = C((0.5, 0.0, 0.25))
turret_pitch_color_select = C((1.0, 0.1, 0.6))


def get_circular_wire_data(index, radius, height, sides, circles):
    coords = []
    indices = []
    next_index = (index + 1) % circles
    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        coords.append(V((x, y, height)))

        next_side = ((ii + 1) % sides)
        if next_index != 0:
            i0 = index * sides + ii
            i1 = index * sides + next_side
            i2 = next_index * sides + ii
            indices.append((i0, i1))
            indices.append((i0, i2))

    return (coords, indices)


def get_arc_wire_data(arc):
    coords = []
    indices = []

    if arc == 0:
        coords.append(V((0.0, 0.0, 0.0)))
        coords.append(V((cos(0), sin(0), 0.0)))
        indices.append((0, 1))
        return (coords, indices)

    sides = sorted((1, round(arc * 4)))[1]
    for ii in range(sides, -1, -1):
        angle = arc * ii / sides / 2
        if angle >= 0:
            coords.append(V((cos(angle), sin(angle), 0.0)))
            coords.append(V((cos(-angle), sin(-angle), 0.0)))
            i2 = ii * 2
            indices.append((i2, i2 + 2))
            indices.append((i2 + 1, i2 + 3))
        else:
            coords.append(V((cos(0), sin(0), 0.0)))
            coords.append(V((cos(0), sin(0), 0.0)))

    center_index = len(coords)
    coords.append(V((0.0, 0.0, 0.0)))
    indices[0] = (i2, center_index)
    indices[1] = (i2 + 1, center_index)

    return (coords, indices)


def init_camera(field_of_view=1, focal_depth=1):
    x = field_of_view
    y = field_of_view / 1.5
    z = focal_depth / 2
    coords = (V((0, 0, 0)), V((-x, -y, -z)), V((-x, y, -z)), V((x, -y, -z)), V((x, y, -z)))
    indices = ((0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (2, 4), (3, 4))
    return coords, indices


def init_point(x=0.05):
    y = x * 2
    z = x * 4
    coords = (V((0, -y, 0)), V((0, y, 0)), V((x, 0, 0)), V((0, 0, z)))
    indices = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    return coords, indices


def init_plane(x=1, y=1):
    coords = (V((-x, -y, 0)), V((-x, y, 0)), V((x, y, 0)), V((x, -y, 0)))
    indices = ((0, 1), (0, 3), (1, 2), (2, 3))
    return coords, indices


def init_cube(x=1, y=1, z=1):
    coords = (
        V((-x, -y, -z)), V((+x, -y, -z)), V((-x, +y, -z)), V((+x, +y, -z)),
        V((-x, -y, +z)), V((+x, -y, +z)), V((-x, +y, +z)), V((+x, +y, +z)),
    )

    indices = (
        (0, 1), (0, 2), (1, 3), (2, 3), (4, 5), (4, 6),
        (5, 7), (6, 7), (0, 4), (1, 5), (2, 6), (3, 7),
    )
    return coords, indices


def init_disc(radius=1, sides=10):
    coords = []
    indices = []
    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        coords.append(V((x, y, 0)))

    for ii in range(0, len(coords)):
        indices.append((ii, ii + 1))
    indices[-1] = (len(coords) - 1, 0)

    return coords, indices


def init_sphere(radius=1, sides=10, circles=10):
    coords = []
    indices = []
    for index in range(circles):
        angle = pi * index / (circles - 1)
        index_radius = radius * sin(angle)
        height = radius * cos(angle)

        data = get_circular_wire_data(index, index_radius, height, sides, circles)
        coords.extend(data[0])
        indices.extend(data[1])
    return coords, indices


def init_hemisphere(radius=1, sides=10, circles=5):
    coords = []
    indices = []
    semicircle = (circles - 1) * 2
    for index in range(circles):
        angle = pi * index / semicircle
        index_radius = radius * sin(angle)
        height = radius * cos(angle)

        data = get_circular_wire_data(index, index_radius, height, sides, circles)
        coords.extend(data[0])
        indices.extend(data[1])

    ring_range = range(sides * circles - sides, sides * circles)
    ring_list = list(ring_range)

    for jj, ii in enumerate(ring_range):
        indices.append((ii, ring_list[jj - 1]))

    return coords, indices


def init_cylinder(radius=1, height=1, sides=10):
    coords = []
    indices = []
    z = height / 2

    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        coords.append(V((x, y, -z)))
        coords.append(V((x, y, z)))
        i0 = ii * 2 + 1
        i1 = ii * 2
        i2 = ((ii + 1) * 2) % (sides * 2)
        i3 = ((ii + 1) * 2 + 1) % (sides * 2)
        indices.append((i0, i1))
        indices.append((i0, i3))
        indices.append((i1, i2))
        indices.append((i2, i3))

    return coords, indices


def init_capsule(radius=1, height=1, sides=10, circles=10):
    coords = []
    indices = []
    z = height / 2

    circles_half = circles / 2
    for index in range(circles):
        if index < circles_half:
            angle = pi * index / (circles - 1)
            height = -z - radius * cos(angle)
        else:
            angle = pi * index / (circles - 1)
            height = z - radius * cos(angle)
        index_radius = radius * sin(angle)

        data = get_circular_wire_data(index, index_radius, height, sides, circles)
        coords += data[0]
        indices += data[1]

    return (coords, indices)


def init_cone(radius=1, height=1, sides=10):
    coords = []
    indices = []

    side_range = range(sides)
    side_list = list(side_range)

    for ii in side_range:
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        coords.append(V((x, y, -height)))
        indices.append((ii, side_list[ii - 1]))
        indices.append((ii, sides))

    coords.append(V((0, 0, 0)))

    return coords, indices


def init_cone_dome(radius=1, cone_ratio=0.5, sides=10, circles=5):
    coords = []
    indices = []
    cone_ratio = sorted((0, cone_ratio, 1))[1]
    cone = abs(cone_ratio - 1)
    semicircle = (circles - 1) * 2
    for circle_index in range(circles):
        circle_angle = pi * circle_index / semicircle
        circle_radius = radius * sin(circle_angle) * cone * (cone + (cone_ratio * 1.75))
        circle_height = radius * cos(circle_angle) * cone + (radius * cone_ratio)

        data = get_circular_wire_data(circle_index, circle_radius, circle_height, sides, circles)
        coords.extend(data[0])
        indices.extend(data[1])

    ring_range = range(sides * circles - sides, sides * circles)
    ring_list = list(ring_range)

    tip_coord_index = len(coords)
    coords.append(V((0, 0, 0)))
    for jj, ii in enumerate(ring_range):
        indices.append((ii, ring_list[jj - 1]))
        indices.append((ii, tip_coord_index))

    return coords, indices


# caching various shapes
camera = init_camera()
point = init_point()
plane = init_plane()
disc = init_disc()
cube = init_cube()
sphere = init_sphere()
hemisphere = init_hemisphere()
cylinder = init_cylinder()
cone = init_cone()
arc180 = get_arc_wire_data(pi)
arc360 = get_arc_wire_data(pi * 2)
# no generic cache for capsule or cone_dome because a scale vector would distort their shape
