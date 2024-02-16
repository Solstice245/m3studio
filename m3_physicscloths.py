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
    bpy.types.Object.m3_cloths_index = bpy.props.IntProperty(options=set(), default=-1)
    bpy.types.Object.m3_cloths_version = bpy.props.EnumProperty(options=set(), items=cloth_versions, default='4')
    bpy.types.Object.m3_clothconstraintsets = bpy.props.CollectionProperty(type=ConstraintSetProperties)
    bpy.types.Object.m3_clothconstraintsets_index = bpy.props.IntProperty(options=set(), default=-1)


cloth_versions = (
    ('2', '2', 'Version 2'),
    ('4', '4', 'Version 4'),
)


def update_constraints_collection_index(self, context):
    if self.constraints_index in range(len(self.constraints)):
        bl = self.constraints[self.constraints_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_constraint_props(constraint, layout):
    shared.draw_prop_pointer_search(layout, constraint.bone, constraint.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    col = layout.column(align=True)
    col.prop(constraint, 'radius', text='Radius')
    col.prop(constraint, 'height', text='Height')
    col = layout.column()
    col.prop(constraint, 'location', text='Location')
    col.prop(constraint, 'rotation', text='Rotation')
    col.prop(constraint, 'scale', text='Scale')


def draw_constraint_set_props(constraint_set, layout):
    shared.draw_collection_list(layout, constraint_set.constraints, draw_constraint_props, menu_id=ConstraintMenu.bl_idname)


def draw_cloth_props(cloth, layout):
    version = int(cloth.id_data.m3_cloths_version)

    layout.prop(cloth, 'mesh_object', text='Mesh Object')
    layout.prop(cloth, 'simulator_object', text='Simulator Object')
    layout.separator()
    shared.draw_prop_pointer_search(layout, cloth.constraint_set, cloth.id_data, 'm3_clothconstraintsets', text='Constraint Set', icon='LINKED')
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
    layout.prop(cloth, 'drag_factor', text='Drag')
    layout.prop(cloth, 'lift_factor', text='Lift')

    if version >= 4:
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


class ConstraintSetPointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=shared.pointer_get_args('m3_clothconstraintsets'), set=shared.pointer_set_args('m3_clothconstraintsets', False))
    handle: bpy.props.StringProperty(options=set())


class ConstraintProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Physics Constraint Volume'

    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    radius: bpy.props.FloatProperty(options=set(), min=0, default=1)
    height: bpy.props.FloatProperty(options=set(), min=0, default=1)


class ConstraintSetProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Physics Constraint Set'

    constraints: bpy.props.CollectionProperty(type=ConstraintProperties)
    constraints_index: bpy.props.IntProperty(options=set(), default=-1, update=update_constraints_collection_index)


class ClothProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Cloth Simulator'

    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)
    simulator_object: bpy.props.PointerProperty(type=bpy.types.Object)
    constraint_set: bpy.props.PointerProperty(type=ConstraintSetPointerProp)
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


class ClothMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_cloths'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_cloths, dup_keyframes_opt=False)


class ClothConstraintsMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_cloth_constraints'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_clothconstraintsets, dup_keyframes_opt=False)


class ConstraintMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_cloth_constraints_item'
    bl_label = 'Menu'

    def draw(self, context):
        constraintset = context.object.m3_clothconstraintsets[context.object.m3_clothconstraintsets_index]
        shared.draw_menu_duplicate(self.layout, constraintset.constraints, dup_keyframes_opt=False)


class ClothPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_cloths'
    bl_label = 'M3 Cloths'

    def draw(self, context):
        model_version = int(context.object.m3_model_version)
        mesh_version = int(context.object.m3_mesh_version)

        if model_version >= 28 and mesh_version >= 4:
            shared.draw_collection_list(self.layout, context.object.m3_cloths, draw_cloth_props, menu_id=ClothMenu.bl_idname)
        else:
            if model_version < 28:
                self.layout.label(icon='ERROR', text='M3 model version must be at least 28.')
            if mesh_version < 4:
                self.layout.label(icon='ERROR', text='M3 mesh version must be at least 4.')


class ClothConstraintsPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_m3_cloth_constraints'
    bl_label = 'M3 Cloth Constraint Sets'

    def draw(self, context):
        model_version = int(context.object.m3_model_version)
        mesh_version = int(context.object.m3_mesh_version)

        if model_version >= 28 and mesh_version >= 4:
            shared.draw_collection_list(self.layout, context.object.m3_clothconstraintsets, draw_constraint_set_props, menu_id=ClothConstraintsMenu.bl_idname)
        else:
            if model_version < 28:
                self.layout.label(icon='ERROR', text='M3 model version must be at least 28.')
            if mesh_version < 4:
                self.layout.label(icon='ERROR', text='M3 mesh version must be at least 4.')


classes = (
    ConstraintSetPointerProp,
    ConstraintProperties,
    ConstraintSetProperties,
    ClothMenu,
    ClothConstraintsMenu,
    ConstraintMenu,
    ClothProperties,
    ClothPanel,
    ClothConstraintsPanel,
)
