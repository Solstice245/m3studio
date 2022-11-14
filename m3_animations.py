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
    bpy.types.Object.m3_animations_default = bpy.props.PointerProperty(type=bpy.types.Action)
    bpy.types.Object.m3_animations = bpy.props.CollectionProperty(type=AnimationProperties)
    bpy.types.Object.m3_animations_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_update)
    bpy.types.Object.m3_animation_groups = bpy.props.CollectionProperty(type=GroupProperties)
    bpy.types.Object.m3_animation_groups_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_group_update)


def anim_update(self, context):
    ob = context.object

    if not ob.m3_options.auto_update_action:
        return

    if ob.animation_data is None:
        ob.animation_data_create()

    if ob.m3_animations_default is None:
        ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

    if ob.m3_animations_index < 0:
        ob.animation_data.action = ob.m3_animations_default
        bpy.context.scene.frame_current = 0
    else:
        old_action = ob.animation_data.action
        old_props = set()
        new_action = ob.m3_animations[ob.m3_animations_index].action
        new_props = set()

        if old_action is not None:
            old_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in old_action.fcurves])

        if new_action is not None:
            new_props = set([(fcurve.data_path, fcurve.array_index) for fcurve in new_action.fcurves])

        props = new_props.difference(old_props)

        for prop in props:
            val = ob.path_resolve(prop[0])
            if type(val) not in [float, int, bool, None]:
                val = val[prop[1]]
            if val is not None:
                set_default_value(ob.m3_animations_default, prop[0], prop[1], val)

        unanim_props = old_props.difference(new_props)
        removed_default_props = set()

        for fcurve in ob.m3_animations_default.fcurves:
            prop = (fcurve.data_path, fcurve.array_index)
            if prop in unanim_props:
                if ob.path_resolve(prop[0]) is None:
                    removed_default_props.add(prop)

        for fcurve in [fcurve for fcurve in ob.m3_animations_default.fcurves if (fcurve.data_path, fcurve.array_index) in removed_default_props]:
            ob.m3_animations_default.fcurves.remove(fcurve)

        ob.animation_data.action = ob.m3_animations_default
        bpy.context.view_layer.update()
        ob.animation_data.action = new_action


# this function is imported into io_m3_import.py
def set_default_value(action, path, index, value):
    fcurve = action.fcurves.find(path, index=index) or action.fcurves.new(path, index=index)
    fcurve.keyframe_points.insert(0, value)


def anim_group_update(self, context):
    ob = context.object
    anim_group = ob.m3_animation_groups[ob.m3_animation_groups_index]

    if not ob.m3_options.auto_update_timeline:
        return

    bpy.context.scene.frame_start = anim_group.frame_start
    bpy.context.scene.frame_current = anim_group.frame_start
    bpy.context.scene.frame_end = anim_group.frame_end


def anim_group_frame_update(self, context):
    ob = context.object
    anim_group = ob.m3_animation_groups[ob.m3_animtions_groups_index]

    if not ob.m3_options.auto_update_timeline:
        return

    bpy.context.scene.frame_start = anim_group.frame_start
    bpy.context.scene.frame_end = anim_group.frame_end


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
    col = layout.column(align=True)
    col.prop(anim_group, 'frame_start', text='Frame Start')
    col.prop(anim_group, 'frame_end', text='End')
    col = layout.column()
    col.prop(anim_group, 'frequency', text='Frequency')
    col.prop(anim_group, 'movement_speed', text='Movement Speed')
    col.prop(anim_group, 'not_looping', text='Does Not Loop')
    col.prop(anim_group, 'always_global', text='Always Global')
    col.prop(anim_group, 'global_in_previewer', text='Global In Previewer')
    shared.draw_handle_list(layout.box(), anim_group.id_data.m3_animations, anim_group.animations, label='Animation')


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
    global_in_previewer: bpy.props.BoolProperty(options=set())
    animations: bpy.props.CollectionProperty(type=shared.M3PropertyGroup)


class SequencePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_animations, draw_animation_props, can_duplicate=False)


class GroupPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONGROUPS'
    bl_label = 'M3 Animation Groups'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_animation_groups, draw_group_props)


class M3AnimationActionNewOp(bpy.types.Operator):
    bl_idname = 'm3.animation_action_new'
    bl_label = 'New Action'
    bl_description = 'Create new action'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        anim = context.object.m3_animations[context.object.m3_animations_index]
        action = bpy.data.actions.new(name=anim.name)
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
    AnimationProperties,
    GroupProperties,
    SequencePanel,
    GroupPanel,
    M3AnimationActionNewOp,
    M3AnimationActionUnlinkOp,
)
