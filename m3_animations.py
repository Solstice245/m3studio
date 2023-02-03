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
    bpy.types.Object.m3_animations = bpy.props.CollectionProperty(type=AnimationProperties)
    bpy.types.Object.m3_animations_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_update)
    bpy.types.Object.m3_animation_groups = bpy.props.CollectionProperty(type=GroupProperties)
    bpy.types.Object.m3_animation_groups_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_group_update)


def anim_update(self, context):
    if context.object.m3_options.update_anim_data:
        anim = None
        if context.object.m3_animations_index in range(len(context.object.m3_animations)):
            anim = context.object.m3_animations[context.object.m3_animations_index]
        anim_set(context.scene, context.object, anim)


# this function is exported to io_m3_import.py and io_m3_export.py
def anim_set(scene, ob, anim):
    if ob.animation_data is None:
        ob.animation_data_create()

    if ob.m3_animations_default is None:
        ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

    dft_action = ob.m3_animations_default
    old_action = ob.animation_data.action  # can be None
    new_action = anim.action if anim else None

    dft_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in dft_action.fcurves])
    old_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in old_action.fcurves]) if old_action else set()
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


def anim_group_update(self, context):
    anim_group_frame_update(self, context)
    anim_group_anim_update(self, context)


def anim_group_frame_update(self, context):
    ob = context.object
    anim_group = ob.m3_animation_groups[ob.m3_animation_groups_index]

    if not ob.m3_options.update_timeline:
        return

    bpy.context.scene.frame_start = anim_group.frame_start
    bpy.context.scene.frame_end = anim_group.frame_end - 1


def anim_group_anim_update(self, context):
    ob = context.object
    anim_group = ob.m3_animation_groups[ob.m3_animation_groups_index]

    if ob.m3_options.update_anim_data and anim_group.animations_index >= 0:
        ob.m3_animations_index = ob.m3_animations.find(anim_group.animations[anim_group.animations_index].value)


def draw_animation_props(animation, layout):
    layout.template_ID(animation, 'action', new='m3.animation_action_new', unlink='m3.animation_action_unlink')
    col = layout.column()
    col.prop(animation, 'concurrent', text='Concurrent')
    col.prop(animation, 'priority', text='Priority')
    row = layout.row(heading='Simulate Physics')
    row.prop(animation, 'simulate', text='')
    col = row.column()
    col.active = animation.simulate
    col.prop(animation, 'simulate_frame', text='On Frame')


def draw_group_props(anim_group, layout):
    row = layout.row(align=True)
    row.prop(anim_group, 'frame_start', text='Frame Range')
    row.prop(anim_group, 'frame_end', text='')
    col = layout.column()
    col.prop(anim_group, 'frequency', text='Frequency')
    col.prop(anim_group, 'movement_speed', text='Movement Speed')
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(anim_group, 'not_looping', text='Does Not Loop')
    col.prop(anim_group, 'unknown0x4', text='Unknown (0x4)')
    col.prop(anim_group, 'always_global', text='Always Global')
    col.prop(anim_group, 'global_in_previewer', text='Global In Previewer')
    shared.draw_collection_list(layout.box(), anim_group.animations, None, ui_list_id=AnimPointerList.bl_idname)


class AnimPointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=shared.pointer_get_args('m3_animations'), set=shared.pointer_set_args('m3_animations', False))
    handle: bpy.props.StringProperty(options=set())


class AnimPointerList(bpy.types.UIList):
    bl_idname = 'UI_UL_M3_animations'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            anim = shared.m3_pointer_get(item.id_data.m3_animations, item)
            row = layout.row()
            row.prop(item, 'value', text='', emboss=False, icon='ANIM_DATA')
            if not anim:
                split = row.split()
                split.alignment = 'RIGHT'
                split.label(icon='ERROR', text='Invalid anim name')


class AnimationProperties(shared.M3PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action, update=anim_update)
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set(), min=0)


class GroupProperties(shared.M3PropertyGroup):
    frame_start: bpy.props.IntProperty(options=set(), min=0, update=anim_group_frame_update)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60, update=anim_group_frame_update)
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0, default=100)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    unknown0x4: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    animations: bpy.props.CollectionProperty(type=AnimPointerProp)
    animations_index: bpy.props.IntProperty(options=set(), default=-1, update=anim_group_anim_update)


class SequenceMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_animations'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_animations, dup_keyframes_opt=False)


class GroupMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_animation_groups'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_animation_groups, dup_keyframes_opt=False)


class SequencePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_animations, draw_animation_props, menu_id=SequenceMenu.bl_idname)


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
        anim = context.object.m3_animations[context.object.m3_animations_index]
        action = bpy.data.actions.new(name='{}_{}'.format(anim.id_data.name, anim.name))
        anim.action = action
        return {'FINISHED'}


class M3AnimationActionUnlinkOp(bpy.types.Operator):
    bl_idname = 'm3.animation_action_unlink'
    bl_label = 'Unlink Action'
    bl_description = 'Unlink this action from the active action slot'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        anim = context.object.m3_animations[context.object.m3_animations_index]
        anim.action = None
        return {'FINISHED'}


classes = (
    AnimPointerProp,
    AnimPointerList,
    AnimationProperties,
    GroupProperties,
    SequenceMenu,
    GroupMenu,
    SequencePanel,
    GroupPanel,
    M3AnimationActionNewOp,
    M3AnimationActionUnlinkOp,
)
