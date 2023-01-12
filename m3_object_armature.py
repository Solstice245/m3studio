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
    bpy.types.Object.m3_options = bpy.props.PointerProperty(type=OptionProperties)
    bpy.types.Object.m3_model_version = bpy.props.EnumProperty(options=set(), items=model_versions, default='29')
    bpy.types.Object.m3_mesh_version = bpy.props.EnumProperty(options=set(), items=mesh_versions, default='5')
    bpy.types.Object.m3_bounds = bpy.props.PointerProperty(type=BoundingProperties)


model_versions = (
    ('20', '20', 'Version 20'),
    ('21', '21', 'Version 21'),
    ('23', '23', 'Version 23'),
    ('25', '25', 'Version 25'),
    ('26', '26', 'Version 26'),
    ('28', '28', 'Version 28'),
    ('29', '29', 'Version 29'),
    ('30', '30', 'Version 30'),
)

mesh_versions = (
    ('2', '2', 'Version 2'),
    ('3', '3', 'Version 3'),
    ('4', '4', 'Version 4'),
    ('5', '5', 'Version 5'),
)


def update_bone_display_mode(self, context):
    pass


desc_auto_bone_display_mode = 'Clicking on m3 list items changes the bone display mode, when applicable'
desc_auto_update_bone_selection = 'Clicking on m3 list items selects associated bones, when applicable'
desc_auto_update_timeline = 'Clicking on an m3 animation group sets the end points of the timeline to its beginning and ending frames'
desc_auto_update_action = 'Clicking on an m3 animation sets the action of the object'


class OptionProperties(bpy.types.PropertyGroup):
    bone_display_mode: bpy.props.EnumProperty(options=set(), items=bl_enum.options_bone_display, update=update_bone_display_mode)
    auto_update_bone_display_mode: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_bone_display_mode)
    auto_update_bone_selection: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_bone_selection)
    auto_update_timeline: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_timeline)
    auto_update_action: bpy.props.BoolProperty(options=set(), default=True, description=desc_auto_update_action)


# TODO bounding preview
class BoundingProperties(bpy.types.PropertyGroup):
    bottom: bpy.props.FloatProperty(name='M3 Bounding Bottom', default=-0.25)
    top: bpy.props.FloatProperty(name='M3 Bounding Top', default=2)
    left: bpy.props.FloatProperty(name='M3 Bounding Left', default=-2)
    right: bpy.props.FloatProperty(name='M3 Bounding Right', default=2)
    front: bpy.props.FloatProperty(name='M3 Bounding Front', default=2)
    back: bpy.props.FloatProperty(name='M3 Bounding Back', default=-2)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_OBJECT_OPTIONS'
    bl_label = 'M3 Object Options'

    def draw(self, context):
        ob = context.object
        layout = self.layout
        layout.use_property_split = True
        options = ob.m3_options
        bounds = ob.m3_bounds

        op = layout.operator('m3.export')
        op.filepath = 'C:\\Users\\John Wharton\\Documents\\M3Test_studio.m3'

        col = layout.column(align=True)
        col.prop(bounds, 'bottom', text='Bounding Bottom')
        col.prop(bounds, 'top', text='Top')
        col.prop(bounds, 'left', text='Left')
        col.prop(bounds, 'right', text='Right')
        col.prop(bounds, 'front', text='Front')
        col.prop(bounds, 'back', text='Back')
        col.separator()
        col.prop(options, 'bone_display_mode', text='Bone Display')
        col.prop(options, 'auto_update_bone_display_mode', text='Auto Update Bone Display')
        col.prop(options, 'auto_update_bone_selection', text='Auto Update Bone Selection')
        col.separator()
        col.prop(options, 'auto_update_timeline', text='Auto Update Animation Timeline')
        col.prop(options, 'auto_update_action', text='Auto Update Animation Action')
        col.separator()
        col = layout.column()
        col.prop(ob, 'm3_model_version', text='M3 Model Version')
        col.prop(ob, 'm3_mesh_version', text='M3 Mesh Version')
        col.prop(ob, 'm3_materiallayers_version', text='M3 Material Layer Version')
        col.prop(ob, 'm3_materials_standard_version', text='M3 Standard Material Version')
        col.prop(ob, 'm3_materials_reflection_version', text='M3 Reflection Material Version')
        col.prop(ob, 'm3_cameras_version', text='M3 Camera Version')
        col.prop(ob, 'm3_particle_systems_version', text='M3 Particle System Version')
        col.prop(ob, 'm3_ribbons_version', text='M3 Ribbon Version')
        col.prop(ob, 'm3_rigidbodies_version', text='M3 Rigid Body Version')
        col.prop(ob, 'm3_turrets_part_version', text='M3 Turret Part Version')
        col.prop(ob, 'm3_cloths_version', text='M3 Cloth Version')


classes = (
    OptionProperties,
    BoundingProperties,
    Panel,
)
