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


def register_props():
    bpy.types.Object.m3_cloths = bpy.props.CollectionProperty(type=ClothProperties)
    bpy.types.Object.m3_cloths_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_clothconstraintsets = bpy.props.CollectionProperty(type=ConstraintSetProperties)
    bpy.types.Object.m3_clothconstraintsets_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)


def update_collection_index(self, context):
    shared.auto_update_bone_shapes(context.object, 'PHCL')


def draw_constraint_props(constraint, layout):
    col = layout.column()
    col.prop(constraint, 'radius', text='Radius')
    col.prop(constraint, 'height', text='Height')
    col = layout.column()
    col.prop(constraint, 'location', text='Location')
    col.prop(constraint, 'rotation', text='Rotation')
    col.prop(constraint, 'scale', text='Scale')


def draw_constraint_set_props(constraint_set, layout):
    shared.draw_collection_list(layout, 'm3_clothconstraintsets[{}].constraints'.format(constraint_set.bl_index), draw_constraint_props)


def draw_object_pair_props(pair, layout):
    layout.prop(pair, 'mesh_object', text='Mesh Object')
    layout.prop(pair, 'simulator_object', text='Simulator Object')


def draw_cloth_props(cloth, layout):
    box = layout.box()
    box.use_property_split = False
    op = box.operator('m3.collection_add', text='Add Mesh/Simulator Object Pair')
    op.collection = 'm3_cloths[%d].object_pairs' % cloth.bl_index
    for index, item in enumerate(cloth.object_pairs):
        row = box.row()
        row.prop(item, 'mesh_object', text='')
        row.prop(item, 'simulator_object', text='')
        op = row.operator('m3.collection_remove', icon='X', text='')
        op.collection, op.index = ('m3_cloths[%d].object_pairs' % cloth.bl_index, index)
    layout.separator()
    shared.draw_pointer_prop(bpy.context.object, layout, 'm3_clothconstraintsets', 'm3_cloths[%d].constraint_set' % cloth.bl_index, 'Constraint Set', 'LINKED')
    layout.separator()
    layout.prop(cloth, 'density', text='Cloth Density')
    layout.separator()
    col = layout.column(align=True)
    col.prop(cloth, 'stiffness_stretching', text='Stiffness Stretching')
    col.prop(cloth, 'stiffness_horizontal', text='Horizontal')
    col.prop(cloth, 'stiffness_blending', text='Blending')
    col.prop(cloth, 'stiffness_shear', text='Shear')
    col.prop(cloth, 'stiffness_spheres', text='Spheres')
    layout.separator()
    layout.prop(cloth, 'tracking', text='Tracking')
    layout.prop(cloth, 'damping', text='Damping')
    layout.prop(cloth, 'friction', text='Friction')
    layout.prop(cloth, 'gravity', text='Gravity')
    layout.separator()
    col = layout.column(align=True)
    col.prop(cloth, 'explosion_scale', text='Explosion Force')
    col.prop(cloth, 'wind_scale', text='Wind')
    layout.separator()
    col = layout.column()
    col.prop(cloth, 'drag_factor', text='Drag')
    col.prop(cloth, 'lift_factor', text='Lift')
    layout.separator()
    col = layout.column(align=True)
    col.prop(cloth, 'skin_collision', text='Skin Collision')
    sub = col.column(align=True)
    sub.active = cloth.skin_collision
    sub.prop(cloth, 'skin_offset', text='Offset')
    sub.prop(cloth, 'skin_exponent', text='Exponent')
    sub.prop(cloth, 'skin_stiffness', text='Stiffness')
    layout.separator()
    layout.prop(cloth, 'local_wind', text='Local Wind')


class ConstraintProperties(shared.M3BoneUserPropertyGroup):
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, update=shared.bone_shape_update_event)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, update=shared.bone_shape_update_event)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=shared.bone_shape_update_event)
    radius: bpy.props.FloatProperty(options=set(), min=0, default=1, update=shared.bone_shape_update_event)
    height: bpy.props.FloatProperty(options=set(), min=0, default=1, update=shared.bone_shape_update_event)


class ConstraintSetProperties(shared.M3PropertyGroup):
    constraints: bpy.props.CollectionProperty(type=ConstraintProperties)
    constraints_index: bpy.props.IntProperty(options=set(), default=-1)


class ObjectPairProperties(shared.M3PropertyGroup):
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)
    simulator_object: bpy.props.PointerProperty(type=bpy.types.Object)


class ClothProperties(shared.M3PropertyGroup):
    object_pairs: bpy.props.CollectionProperty(type=ObjectPairProperties)
    constraint_set: bpy.props.StringProperty(options=set())
    density: bpy.props.FloatProperty(options=set(), min=0, default=10)
    tracking: bpy.props.FloatProperty(options=set(), min=0, default=0.25)
    stiffness_stretching: bpy.props.FloatProperty(options=set(), min=0, default=0.5)
    stiffness_horizontal: bpy.props.FloatProperty(options=set(), min=0, default=0.5)
    stiffness_blending: bpy.props.FloatProperty(options=set(), min=0, default=0.5)
    stiffness_shear: bpy.props.FloatProperty(options=set(), min=0, default=1)
    stiffness_spheres: bpy.props.FloatProperty(options=set(), min=0, default=1)
    damping: bpy.props.FloatProperty(options=set(), min=0, default=2)
    friction: bpy.props.FloatProperty(options=set(), min=0, max=1, subtype='FACTOR')
    gravity: bpy.props.FloatProperty(options=set(), default=1)
    explosion_scale: bpy.props.FloatProperty(options=set(), default=1)
    wind_scale: bpy.props.FloatProperty(options=set(), default=1)
    drag_factor: bpy.props.FloatProperty(options=set(), min=0, default=1)
    lift_factor: bpy.props.FloatProperty(options=set(), min=0, default=1)
    skin_collision: bpy.props.BoolProperty(options=set())
    skin_offset: bpy.props.FloatProperty(options=set(), default=1)
    skin_exponent: bpy.props.FloatProperty(options=set(), default=1)
    skin_stiffness: bpy.props.FloatProperty(options=set(), default=1)
    local_wind: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ')


class ClothPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_cloths'
    bl_label = 'M3 Cloths'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_cloths', draw_cloth_props)


class ClothConstraintsPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_cloth_constraints'
    bl_label = 'M3 Cloth Constraint Sets'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_clothconstraintsets', draw_constraint_set_props)


classes = (
    ConstraintProperties,
    ConstraintSetProperties,
    ObjectPairProperties,
    ClothProperties,
    ClothPanel,
    ClothConstraintsPanel,
)