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

import bpy
from . import shared
from . import enum


def register_props():
    bpy.types.Armature.m3_rigidbodies = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Armature.m3_rigidbodies_index = bpy.props.IntProperty(options=set(), default=-1)


def init_msgbus(arm, context):
    for rigidbody in arm.data.m3_rigidbodies:
        shared.bone_update_event(rigidbody, context)
        trail_update_event(rigidbody, context)
        for shape in rigidbody.shapes:
            shared.bone_update_event(shape, context)


def draw_shape_props(shape, layout):
    sub = layout.column(align=True)
    sub.prop(shape, 'shape', text='Shape Type')
    if shape.shape in ['CONVEXHULL', 'MESH']:
        sub.prop_search(shape, 'mesh', bpy.data, 'meshes', text='Mesh Data')
    else:
        if shape.shape == 'CUBE':
            sub.prop(shape, 'size', text='Size')
        elif shape.shape == 'SPHERE':
            sub.prop(shape, 'size', index=0, text='Size R')
        elif shape.shape in ['CAPSULE', 'CYLINDER']:
            sub.prop(shape, 'size', index=0, text='Size R')
            sub.prop(shape, 'size', index=1, text='H')

    col = layout.column()
    col.prop(shape, 'location', text='Location')
    col.prop(shape, 'rotation', text='Rotation')
    col.prop(shape, 'scale', text='Scale')


def draw_props(rigidbody, layout):

    shared.draw_subcollection_list(bpy.context.object.data, layout, 'm3_rigidbodies', 'shapes', 'Shape', draw_shape_props)

    col = layout.column()
    col.prop(rigidbody, 'material', text='Physics Material')
    col.prop(rigidbody, 'simulation_type', text='Simulation Type')
    col.prop(rigidbody, 'gravity_scale', text='Gravity Scale')
    col.prop(rigidbody, 'priority', text='Priority')
    col = layout.column()
    col.use_property_split = False
    col.prop(rigidbody, 'local_forces', text='Local Forces')
    col.label(text='World Forces:')
    col = col.column_flow(align=True, columns=2)
    col.use_property_split = False
    for ii, val in enum.world_forces:
        col.prop(rigidbody, 'world_forces', index=ii, text=val)
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(rigidbody, 'simulate_collision', text='Simulate On Collision')
    col.prop(rigidbody, 'ignore_local_bodies', text='Ignore Local Bodies')
    col.prop(rigidbody, 'always_exists', text='Always Exists')
    col.prop(rigidbody, 'do_not_simulate', text='Do Not Simulate')
    col.prop(rigidbody, 'collidable', text='Collidable')
    col.prop(rigidbody, 'stackable', text='Stackable')
    col.prop(rigidbody, 'walkable', text='Walkable')


class ShapeProperties(bpy.types.PropertyGroup):
    bl_display: bpy.props.BoolProperty(default=False)
    shape: bpy.props.EnumProperty(options=set(), items=enum.physics_shape)
    mesh: bpy.props.StringProperty(options=set())
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0)
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, default=(0, 0, 0))
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))


class Properties(shared.M3BoneUserPropertyGroup):
    shapes: bpy.props.CollectionProperty(type=ShapeProperties)
    simulation_type: bpy.props.IntProperty(options=set())
    material: bpy.props.EnumProperty(options=set(), items=enum.physics_materials)
    density: bpy.props.FloatProperty(options=set())
    friction: bpy.props.FloatProperty(options=set())
    restitution: bpy.props.FloatProperty(options=set())
    linear_damp: bpy.props.FloatProperty(options=set())
    angular_damp: bpy.props.FloatProperty(options=set())
    gravity_scale: bpy.props.FloatProperty(options=set(), default=1)
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    world_forces: bpy.props.BoolVectorProperty(options=set(), size=8)
    priority: bpy.props.IntProperty(options=set(), min=0)
    collidable: bpy.props.BoolProperty(options=set())
    stackable: bpy.props.BoolProperty(options=set())
    walkable: bpy.props.BoolProperty(options=set())
    simulate_collision: bpy.props.BoolProperty(options=set())
    ignore_local_bodies: bpy.props.BoolProperty(options=set())
    always_exists: bpy.props.BoolProperty(options=set())
    do_not_simulate: bpy.props.BoolProperty(options=set())


class Panel(bpy.types.Panel):
    bl_idname = 'DATA_PT_M3_RIGIDBODIES'
    bl_label = 'M3 Rigid Bodies'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        shared.draw_collection_list_active(context.object.data, self.layout, 'm3_rigidbodies', draw_props)


classes = (
    ShapeProperties,
    Properties,
    Panel,
)