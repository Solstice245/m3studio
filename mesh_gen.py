#!/usr/bin/python3
# -*- coding: utf-8 -*-

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


def get_circular_mesh_data(index, radius, height, sides, circles):
    vertices = []
    faces = []
    next_index = (index + 1) % circles
    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        vertices += [(x, y, height)]

        next_side = ((ii + 1) % sides)
        if next_index != 0:
            i0 = index * sides + ii
            i1 = index * sides + next_side
            i2 = next_index * sides + next_side
            i3 = next_index * sides + ii
            faces += [(i0, i1, i2, i3)]

    return (vertices, [], faces)


def attachment_point(x=0.05):
    y = x * 2
    z = x * 4
    vertices = [(0, -y, 0), (0, y, 0), (x, 0, 0), (0, 0, z)]
    faces = [(0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3)]
    return (vertices, [], faces)


def camera(field_of_view, focal_depth):
    x = field_of_view
    y = field_of_view / 1.5
    z = focal_depth / 2
    vertices = [(0, 0, 0), (-x, -y, z), (-x, y, z), (x, -y, z), (x, y, z)]
    faces = [(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)]
    return (vertices, [], faces)


def point():
    s1 = 0.5
    s2 = s1 / 2
    vertices = [(-s1, 0, 0), (s1, 0, 0), (0, -s1, 0), (0, s1, 0), (0, 0, -s1), (0, 0, s1)]
    vertices += [(-s2, 0, 0), (s2, 0, 0), (0, -s2, 0), (0, s2, 0), (0, 0, -s2), (0, 0, s2)]
    edges = [(0, 1), (2, 3), (4, 5)]
    faces = [(6, 8, 10), (6, 8, 11), (7, 8, 10), (7, 8, 11)]
    faces += [(6, 9, 10), (6, 9, 11), (7, 9, 10), (7, 9, 11)]
    return (vertices, edges, faces)


def plane(size):
    x = size[1]
    y = size[0]

    vertices = [(-x, -y, 0), (-x, y, 0), (x, y, 0), (x, -y, 0)]
    faces = [(0, 1, 2, 3)]

    return (vertices, [], faces)


def cube(size):
    x = size[1]
    y = size[0]
    z = size[2]

    vertices = [(-x, -y, -z), (-x, -y, z), (-x, y, z), (-x, y, -z), (x, -y, -z), (x, -y, z), (x, y, -z), (x, y, z)]
    faces = [(0, 1, 2, 3), (6, 7, 5, 4), (4, 5, 1, 0), (3, 2, 7, 6), (0, 3, 6, 4), (5, 7, 2, 1)]

    return (vertices, [], faces)


def disc(radius, sides=10):
    vertices = []

    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        vertices += [(x, y, 0)]

    faces = [tuple([ii for ii in range(len(vertices))])]

    return (vertices, [], faces)


def cylinder(size, radius, sides=10):
    vertices = []
    faces = []
    z = size[2] / 2

    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        vertices += [(x, y, -z)]
        vertices += [(x, y, z)]
        i0 = ii * 2 + 1
        i1 = ii * 2
        i2 = ((ii + 1) * 2) % (sides * 2)
        i3 = ((ii + 1) * 2 + 1) % (sides * 2)
        faces += [(i0, i1, i2, i3)]

    return (vertices, [], faces)


def capsule(size, radius, sides=10, circles=10):
    vertices = []
    faces = []
    z = size[1] / 2

    for index in range(circles):
        if index < circles / 2:
            angle = pi * index / (circles - 1)
            height = -z - radius * cos(angle)
        else:
            angle = pi * index / (circles - 1)
            height = z - radius * cos(angle)
        index_radius = radius * sin(angle)

        mesh_data = get_circular_mesh_data(index, index_radius, height, sides, circles)
        vertices += mesh_data[0]
        faces += mesh_data[2]

    return (vertices, [], faces)


def sphere(radius, sides=10, circles=10):
    vertices = []
    faces = []
    for index in range(circles):
        angle = pi * (index) / (circles - 1)
        index_radius = radius * sin(angle)
        height = -radius * cos(angle)

        mesh_data = get_circular_mesh_data(index, index_radius, height, sides, circles)
        vertices += mesh_data[0]
        faces += mesh_data[2]

    return (vertices, [], faces)


def hemisphere(radius, sides=10, circles=5):
    vertices = []
    faces = []
    for index in range(circles):
        angle = pi * (index) / (circles - 1 * 2)
        index_radius = radius * sin(angle)
        height = -radius * cos(angle)

        mesh_data = get_circular_mesh_data(index, index_radius, height, sides, circles)
        vertices += mesh_data[0]
        faces += mesh_data[2]

    return (vertices, [], faces)


def cone(size, radius, sides=10):
    vertices = []
    faces = []

    for ii in range(sides):
        angle = 2 * pi * ii / sides
        x = cos(angle) * radius
        y = sin(angle) * radius
        vertices += [(x, y, size)]

    faces = [tuple([ii for ii in range(len(vertices))])]

    tip_vertex_index = len(vertices)
    vertices += [(0, 0, 0)]
    for ii in range(sides):
        nextI = ((ii + 1) % sides)
        i0 = nextI
        i1 = tip_vertex_index
        i2 = ii
        faces += [(i0, i1, i2)]

    return (vertices, [], faces)


def cone_dome(cone_ratio, radius, sides=10, circles=5):
    vertices = []
    faces = []
    cone_ratio = sorted((0, cone_ratio, 1))[1]
    cone = abs(cone_ratio - 1)
    for circle_index in range(circles):
        circle_angle = pi * (circle_index) / ((circles - 1) * 2)
        circle_radius = radius * sin(circle_angle) * cone * (cone + (cone_ratio * 1.75))
        circle_height = radius * cos(circle_angle) * cone + (radius * cone_ratio)

        mesh_data = get_circular_mesh_data(circle_index, circle_radius, circle_height, sides, circles)
        vertices += mesh_data[0]
        faces += mesh_data[2]

    bot_vertex_index = len(vertices)
    vertices += [(0, 0, 0)]
    for ii in range(sides):
        nextI = ((ii + 1) % sides)
        i0 = ((circles - 1) * sides) + nextI
        i1 = bot_vertex_index
        i2 = ((circles - 1) * sides) + ii
        faces += [(i0, i1, i2)]

    return (vertices, [], faces)
