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
    bpy.types.Object.m3_physicsshapes_index = bpy.props.IntProperty(options=set(), default=-1)
    bpy.types.Object.m3_physicsshapes_version = bpy.props.EnumProperty(options=set(), items=physicsshapes_versions, default='3')
    bpy.types.Object.m3_rigidbodies = bpy.props.CollectionProperty(type=BodyProperties)
    bpy.types.Object.m3_rigidbodies_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_rigidbodies_version = bpy.props.EnumProperty(options=set(), items=rigid_body_versions, default='4')


physicsshapes_versions = (
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
    if self.m3_rigidbodies_index in range(len(self.m3_rigidbodies)):
        bl = self.m3_rigidbodies[self.m3_rigidbodies_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_volume_props(shape, layout):
    sub = layout.column(align=True)
    sub.prop(shape, 'shape', text='Shape Type')
    if shape.shape in ['CONVEXHULL', 'MESH']:
        sub.prop_search(shape, 'mesh_object', bpy.data, 'objects', text='Mesh Object')
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
    shared.draw_prop_pointer_search(layout, rigidbody.physics_shape, rigidbody.id_data, 'm3_physicsshapes', text='Physics Body Shape', icon='LINKED')
    layout.separator()
    layout.prop(rigidbody, 'physical_material', text='Physical Material')
    # layout.prop(rigidbody, 'simulation_type', text='Simulation Type')  # unknown if effective
    layout.prop(rigidbody, 'mass', text='Mass')
    layout.prop(rigidbody, 'friction', text='Friction')
    layout.prop(rigidbody, 'bounce', text='Bounciness')
    layout.prop(rigidbody, 'damping_linear', text='Linear Damping')
    layout.prop(rigidbody, 'damping_angular', text='Angular Damping')
    layout.prop(rigidbody, 'gravity_factor', text='Gravity Factor')
    layout.prop(rigidbody, 'priority', text='Priority')
    layout.separator()
    row = shared.draw_prop_split(layout, text='Local Force Channels')
    row.prop(rigidbody, 'local_forces', text='')
    row = shared.draw_prop_split(layout, text='World Force Channels')
    col = row.column_flow(align=True, columns=2)
    for ii, val in bl_enum.world_forces:
        col.prop(rigidbody, 'world_forces', index=ii, text=val)
    layout.separator()
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


class ShapePointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=shared.pointer_get_args('m3_physicsshapes'), set=shared.pointer_set_args('m3_physicsshapes', False))
    handle: bpy.props.StringProperty(options=set())


class VolumeProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Physics Shape Volume'

    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, default=(0, 0, 0))
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)


class ShapeProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Physics Shape'

    volumes: bpy.props.CollectionProperty(type=VolumeProperties)
    volumes_index: bpy.props.IntProperty(options=set(), default=-1)


class BodyProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Physics Body'

    name: bpy.props.StringProperty(options=set(), get=shared.get_bone_value)
    bone: bpy.props.PointerProperty(type=shared.M3BonePointerPropExclusive)
    physics_shape: bpy.props.PointerProperty(type=ShapePointerProp)
    simulation_type: bpy.props.IntProperty(options=set())
    physical_material: bpy.props.EnumProperty(options=set(), items=bl_enum.physics_materials)
    mass: bpy.props.FloatProperty(options=set(), default=2400)
    friction: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0.0, max=1.0, default=0.5)
    bounce: bpy.props.FloatProperty(options=set(), subtype='FACTOR', default=0.1, soft_min=0.0, soft_max=1.0)
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


class BodyMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_rigidbodies'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_rigidbodies, dup_keyframes_opt=False)


class ShapePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PHYSICSSHAPES'
    bl_label = 'M3 Physics Shapes'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_physicsshapes, draw_shape_props)


class BodyPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_PHYSICSRIGIDBODIES'
    bl_label = 'M3 Physics Rigid Bodies'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_rigidbodies, draw_body_props, ui_list_id='UI_UL_M3_bone_user', menu_id=BodyMenu.bl_idname)


classes = (
    ShapePointerProp,
    VolumeProperties,
    ShapeProperties,
    BodyProperties,
    BodyMenu,
    ShapePanel,
    BodyPanel,
)
