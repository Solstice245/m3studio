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


# TODO make a function for auto NLA track generation when selecting animation groups


def register_props():
    bpy.types.Object.m3_animations_default = bpy.props.PointerProperty(type=bpy.types.Action)
    bpy.types.Object.m3_animation_groups = bpy.props.CollectionProperty(type=GroupProperties)
    bpy.types.Object.m3_animation_groups_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_group_update)


# this function is exported to io_m3_import.py and io_m3_export.py
def ob_anim_data_set(scene, ob, new_action=None):
    if ob.animation_data is None:
        ob.animation_data_create()

    if ob.m3_animations_default is None:
        ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

    dft_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in ob.m3_animations_default.fcurves])
    old_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in ob.animation_data.action.fcurves]) if ob.animation_data.action else set()
    new_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in new_action.fcurves]) if new_action else set()

    for prop in new_props.difference(old_props):
        try:
            val = ob.path_resolve(prop[0])
            if type(val) not in [float, int, bool]:
                val = val[prop[1]]
            set_default_value(ob.m3_animations_default, prop[0], prop[1], val)
        except ValueError:
            pass  # fcurve data path is invalid

    for prop in dft_props.difference(old_props, new_props):
        try:
            val = ob.path_resolve(prop[0])
            if type(val) not in [float, int, bool]:
                val = val[prop[1]]
            set_default_value(ob.m3_animations_default, prop[0], prop[1], val)
        except ValueError:
            pass  # fcurve data path is invalid

    ob.animation_data.action = ob.m3_animations_default

    if new_action:
        scene.frame_set(scene.frame_current)
        ob.animation_data.action = new_action
    else:
        scene.frame_set(0)


# this function is exported to io_m3_import.py
def set_default_value(action, path, index, value):
    fcurve = action.fcurves.find(path, index=index) or action.fcurves.new(path, index=index)
    fcurve.keyframe_points.insert(0, value)


def anim_update(self, context):
    if context.object and context.object.m3_options.update_anim_data:
        anim = None
        if context.object.m3_animation_groups_index in range(len(context.object.m3_animation_groups)):
            anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
            if anim_group.animations_index in range(len(anim_group.animations)):
                anim = anim_group.animations[anim_group.animations_index]
        ob_anim_data_set(context.scene, context.object, anim.action if anim else None)


def anim_group_update(self, context):
    anim_update(self, context)
    anim_group_frame_update(self, context)


def anim_group_frame_update(self, context):
    ob = context.object
    anim_group = ob.m3_animation_groups[ob.m3_animation_groups_index]

    if not ob.m3_options.update_timeline:
        return

    bpy.context.scene.frame_start = anim_group.frame_start
    bpy.context.scene.frame_end = anim_group.frame_end - 1


def draw_animation_props(animation, layout):
    layout.template_ID(animation, 'action', new='m3.animation_action_new', unlink='m3.animation_action_unlink')
    row = layout.row()
    row.use_property_split = False
    row.prop(animation, 'priority', text='Priority')
    row.prop(animation, 'concurrent', text='Concurrent')


def draw_group_props(anim_group, layout):
    # layout.prop(anim_group, 'm3_export', text='Export')
    row = layout.row(align=True)
    row.prop(anim_group, 'frame_start', text='Frame Range')
    row.prop(anim_group, 'frame_end', text='')
    col = layout.column()
    col.prop(anim_group, 'frequency', text='Frequency')
    col.prop(anim_group, 'movement_speed', text='Movement Speed')
    row = layout.row(heading='Simulate Physics')
    row.prop(anim_group, 'simulate', text='')
    col = row.column()
    col.active = anim_group.simulate
    col.prop(anim_group, 'simulate_frame', text='On Frame')
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(anim_group, 'not_looping', text='Does Not Loop')
    col.prop(anim_group, 'unknown0x4', text='Unknown (0x4)')
    col.prop(anim_group, 'always_global', text='Always Global')
    col.prop(anim_group, 'global_in_previewer', text='Global In Previewer')
    shared.draw_collection_list(layout.box(), anim_group.animations, draw_animation_props)


class AnimationProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Anim Sequence'

    action: bpy.props.PointerProperty(type=bpy.types.Action, update=anim_update)
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())


class GroupProperties(shared.M3PropertyGroup):

    def _get_identifier(self):
        return 'M3 Anim Group'

    animations: bpy.props.CollectionProperty(type=AnimationProperties)
    animations_index: bpy.props.IntProperty(options=set(), default=-1, update=anim_update)
    frame_start: bpy.props.IntProperty(options=set(), min=0, update=anim_group_frame_update)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60, update=anim_group_frame_update)
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0, default=100)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    unknown0x4: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set(), min=0)


class SequenceMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_animations'
    bl_label = 'Menu'

    def draw(self, context):
        anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
        shared.draw_menu_duplicate(self.layout, anim_group.animations, dup_keyframes_opt=False)


class GroupMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_animation_groups'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_animation_groups, dup_keyframes_opt=False)


class GroupPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONGROUPS'
    bl_label = 'M3 Animation Groups'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_animation_groups, draw_group_props, menu_id=GroupMenu.bl_idname)


class M3AnimationActionNewOp(bpy.types.Operator):
    bl_idname = 'm3.animation_action_new'
    bl_label = 'New Action'
    bl_description = 'Create new action'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
        anim = anim_group.animations[anim_group.animations_index]
        action = bpy.data.actions.new(name=f'{anim.id_data.name}_{anim_group.name}_{anim.name}')
        anim.action = action
        return {'FINISHED'}


class M3AnimationActionUnlinkOp(bpy.types.Operator):
    bl_idname = 'm3.animation_action_unlink'
    bl_label = 'Unlink Action'
    bl_description = 'Unlink this action from the active action slot'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
        anim = anim_group.animations[anim_group.animations_index]
        anim.action = None
        return {'FINISHED'}


classes = (
    AnimationProperties,
    GroupProperties,
    SequenceMenu,
    GroupMenu,
    GroupPanel,
    M3AnimationActionNewOp,
    M3AnimationActionUnlinkOp,
)
