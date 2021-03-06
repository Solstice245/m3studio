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
from . import bl_enum


def register_props():
    bpy.types.Object.m3_rigidbodies = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_rigidbodies_index = bpy.props.IntProperty(options=set(), default=-1, update=update_bone_shapes_option)


def update_bone_shapes_option(self, context):
    if context.object.m3_options.auto_update_bone_shapes:
        if context.object.m3_options.bone_shapes != 'PHRB':
            context.object.m3_options.bone_shapes = 'PHRB'


def bone_shape_update_event(self, context):
    ob = context.object
    bone = shared.m3_pointer_get(ob, 'data.bones', 'm3_rigidbodies[{}].bone'.format(ob.m3_rigidbodies_index))
    shared.set_bone_shape(ob, bone)


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

    shared.draw_collection_stack(
        layout, 'm3_rigidbodies[{}].shapes'.format(rigidbody.bl_index), 'Shape', draw_shape_props, use_name=False, can_duplicate=True,
        ops=['m3.rigidbody_shape_add', 'm3.rigidbody_shape_remove', 'm3.collection_move', 'm3.rigidbody_shape_duplicate'],
    )

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
    for ii, val in bl_enum.world_forces:
        col.prop(rigidbody, 'world_forces', index=ii, text=val)
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.label(text='Flags:')
    col.prop(rigidbody, 'simulate_collision', text='Simulate On Collision')
    col.prop(rigidbody, 'ignore_local_bodies', text='Ignore Local Bodies')
    col.prop(rigidbody, 'always_exists', text='Always Exists')
    col.prop(rigidbody, 'do_not_simulate', text='Do Not Simulate')
    col.prop(rigidbody, 'collidable', text='Collidable')
    col.prop(rigidbody, 'stackable', text='Stackable')
    col.prop(rigidbody, 'walkable', text='Walkable')


class ShapeProperties(shared.M3PropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_shape, update=bone_shape_update_event)
    mesh: bpy.props.StringProperty(options=set(), update=bone_shape_update_event)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, update=bone_shape_update_event)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, default=(0, 0, 0), update=bone_shape_update_event)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)


class Properties(shared.M3BoneUserPropertyGroup):
    shapes: bpy.props.CollectionProperty(type=ShapeProperties)
    simulation_type: bpy.props.IntProperty(options=set())
    material: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_materials)
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


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIGIDBODIES'
    bl_label = 'M3 Rigid Bodies'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_rigidbodies', draw_props)


class M3ShapeOpAdd(shared.M3CollectionOpBase):
    bl_idname = 'm3.rigidbody_shape_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        rigid_body = context.object.m3_rigidbodies[context.object.m3_rigidbodies_index]
        shared.m3_item_new('shapes', obj=rigid_body)
        bone = shared.m3_pointer_get(context.object, 'data.bones', 'm3_rigidbodies[{}].bone'.format(context.object.m3_rigidbodies_index))
        shared.set_bone_shape(context.object, bone)
        return {'FINISHED'}


class M3ShapeOpRemove(shared.M3CollectionOpBase):
    bl_idname = 'm3.rigidbody_shape_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        shapes = context.object.m3_rigidbodies[context.object.m3_rigidbodies_index].shapes
        shapes.remove(self.index)

        for ii in range(self.index, len(shapes)):
            shapes[ii].bl_index -= 1

        bone = shared.m3_pointer_get(context.object, 'data.bones', 'm3_rigidbodies[{}].bone'.format(context.object.m3_rigidbodies_index))
        shared.set_bone_shape(context.object, bone)

        return {'FINISHED'}


class M3ShapeOpDuplicate(shared.M3CollectionOpBase):
    bl_idname = 'm3.rigidbody_shape_duplicate'
    bl_label = 'Duplicate Collection Item'
    bl_description = 'Duplicates the active item in the collection'

    def invoke(self, context, event):
        if self.index == -1:
            return {'FINISHED'}

        rigid_body = context.object.m3_rigidbodies[context.object.m3_rigidbodies_index]
        shared.m3_item_duplicate('shapes', rigid_body.shapes[self.index], obj=rigid_body)
        bone = shared.m3_pointer_get(context.object, 'data.bones', 'm3_rigidbodies[{}].bone'.format(context.object.m3_rigidbodies_index))
        shared.set_bone_shape(context.object, bone)

        return {'FINISHED'}


classes = (
    ShapeProperties,
    Properties,
    Panel,
    M3ShapeOpAdd,
    M3ShapeOpRemove,
    M3ShapeOpDuplicate,
)
