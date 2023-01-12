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
    bpy.types.Object.m3_physicsshapes = bpy.props.CollectionProperty(type=ShapeProperties)
    bpy.types.Object.m3_physicsshapes_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_physicsshapes_version = bpy.props.EnumProperty(options=set(), items=physics_shape_versions, default='3')
    bpy.types.Object.m3_rigidbodies = bpy.props.CollectionProperty(type=BodyProperties)
    bpy.types.Object.m3_rigidbodies_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_rigidbodies_version = bpy.props.EnumProperty(options=set(), items=rigid_body_versions, default='4')


physics_shape_versions = (
    ('1', '1', 'Version 1'),
    ('2', '2', 'Version 2'),
    ('3', '3', 'Version 3'),
)

# need better documentation of non version 3 version
rigid_body_versions = (
    ('2', '2', 'Version 2'),
    ('3', '3', 'Version 3'),
    ('4', '4', 'Version 4'),
)


def update_collection_index(self, context):
    ob = context.object
    if len(ob.m3_rigidbodies):
        bl = ob.m3_rigidbodies[ob.m3_rigidbodies_index]
        shared.select_bones_handles(ob, [bl.bone])
        shared.auto_update_bone_display_mode(ob, 'PHRB')


def draw_volume_props(shape, layout):
    sub = layout.column(align=True)
    sub.prop(shape, 'shape', text='Shape Type')
    if shape.shape in ['CONVEXHULL', 'MESH']:
        sub.prop_search(shape, 'mesh_object', bpy.data, 'meshes', text='Mesh Object')
    elif shape.shape == 'CUBE':
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


def draw_shape_props(shape, layout):
    shared.draw_collection_list(layout.box(), shape.volumes, draw_volume_props)


def draw_body_props(rigidbody, layout):
    shared.draw_pointer_prop(layout, rigidbody.id_data.data.bones, rigidbody, 'bone', bone_search=True, label='Bone', icon='BONE_DATA')
    shared.draw_pointer_prop(layout, rigidbody.id_data.m3_physicsshapes, rigidbody, 'physics_shape', label='Physics Body Shape', icon='LINKED')
    col = layout.column()
    col.prop(rigidbody, 'physical_material', text='Physical Material')
    # col.prop(rigidbody, 'simulation_type', text='Simulation Type')  # unknown if effective
    col.prop(rigidbody, 'mass', text='Mass')
    col.prop(rigidbody, 'friction', text='Friction')
    col.prop(rigidbody, 'restitution', text='Restitution')
    col.prop(rigidbody, 'damping_linear', text='Linear Damping')
    col.prop(rigidbody, 'damping_angular', text='Angular Damping')
    col.prop(rigidbody, 'gravity_factor', text='Gravity Factor')
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
    col.prop(rigidbody, 'no_simulation', text='Do Not Simulate')
    col.prop(rigidbody, 'collidable', text='Collidable')
    col.prop(rigidbody, 'stackable', text='Stackable')
    col.prop(rigidbody, 'walkable', text='Walkable')


class VolumeProperties(shared.M3PropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, default=(0, 0, 0))
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)


class ShapeProperties(shared.M3PropertyGroup):
    volumes: bpy.props.CollectionProperty(type=VolumeProperties)
    volumes_index: bpy.props.IntProperty(options=set(), default=-1)


class BodyProperties(shared.M3BoneUserPropertyGroup):
    physics_shape: bpy.props.StringProperty(options=set())
    simulation_type: bpy.props.IntProperty(options=set())
    physical_material: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_materials)
    mass: bpy.props.FloatProperty(options=set(), default=2400)
    friction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    restitution: bpy.props.FloatProperty(options=set(), default=0.1)
    damping_linear: bpy.props.FloatProperty(options=set(), default=0.001)
    damping_angular: bpy.props.FloatProperty(options=set(), default=0.001)
    gravity_factor: bpy.props.FloatProperty(options=set(), default=1)
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)
    world_forces: bpy.props.BoolVectorProperty(options=set(), size=16)
    priority: bpy.props.IntProperty(options=set(), min=0)
    collidable: bpy.props.BoolProperty(options=set())
    stackable: bpy.props.BoolProperty(options=set())
    walkable: bpy.props.BoolProperty(options=set())
    simulate_collision: bpy.props.BoolProperty(options=set())
    ignore_local_bodies: bpy.props.BoolProperty(options=set())
    always_exists: bpy.props.BoolProperty(options=set())
    no_simulation: bpy.props.BoolProperty(options=set())


class ShapePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PHYSICSSHAPES'
    bl_label = 'M3 Physics Shapes'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_physicsshapes, draw_shape_props)


class BodyPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PHYSICSRIGIDBODIES'
    bl_label = 'M3 Physics Rigid Bodies'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_rigidbodies, draw_body_props)


classes = (
    VolumeProperties,
    ShapeProperties,
    BodyProperties,
    ShapePanel,
    BodyPanel,
)
