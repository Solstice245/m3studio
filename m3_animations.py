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
    bpy.types.Object.m3_animation_groups_index = bpy.props.IntProperty(options=set(), default=-1)


def set_default_value(action, path, index, value):
    fcurve = None
    for c in action.fcurves:
        if c.data_path == path and c.array_index == index:
            fcurve = c
            break
    if fcurve is None:
        fcurve = action.fcurves.new(path, index=index)
    keyframe = fcurve.keyframe_points.insert(0, value)
    keyframe.interpolation = 'CONSTANT'


def get_default_values(ob, new_action, old_action):
    old_props = set()
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
            default_val = fcurve.evaluate(0)
            attr = ob.path_resolve(prop[0])
            if attr is not None:
                if type(default_val) in [float, int, bool]:
                    shared.bl_resolved_set(ob, prop[0], default_val)
                else:
                    shared.bl_resolved_set(ob, prop[0] + '[{}]'.format(prop[1]), default_val)
            else:
                removed_default_props.add(prop)

    for fcurve in [fcurve for fcurve in ob.m3_animations_default.fcurves if (fcurve.data_path, fcurve.array_index) in removed_default_props]:
        ob.m3_animations_default.fcurves.remove(fcurve)

    return new_action


def anim_update(self, context):
    ob = context.object
    if ob.animation_data is None:
        ob.animation_data_create()

    if ob.m3_animations_default is None:
        ob.m3_animations_default = bpy.data.actions.new(ob.name + '_DEFAULTS')

    if ob.m3_animations_index < 0:
        ob.animation_data.action = ob.m3_animations_default
    else:
        anim = ob.m3_animations[ob.m3_animations_index]

        old_action = ob.animation_data.action
        ob.animation_data.action = anim.action
        get_default_values(ob, anim.action, old_action)


def draw_animation_props(animation, layout):
    layout.template_ID(animation, 'action', new='m3.animation_action_new', unlink='m3.animation_action_unlink')
    row = layout.row()
    row.use_property_split = False
    row.alignment = 'CENTER'
    row.split(factor=0.5)
    row.label(text='Priority')
    row.prop(animation, 'priority', text='')
    row.prop(animation, 'concurrent', text='Concurrent')


def draw_group_props(anim_group, layout):
    col = layout.column(align=True)
    col.prop(anim_group, 'frame_start', text='Frame Start')
    col.prop(anim_group, 'frame_end', text='End')
    row = layout.row(heading='Simulate Physics')
    row.prop(anim_group, 'simulate', text='')
    col = row.column()
    col.active = anim_group.simulate
    col.prop(anim_group, 'simulate_frame', text='On Frame')
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


class GroupProperties(shared.M3PropertyGroup):
    frame_start: bpy.props.IntProperty(options=set(), min=0)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60)
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set(), min=0)
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0, default=100)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    animations: bpy.props.CollectionProperty(type=shared.M3PropertyGroup)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_animations, draw_animation_props, can_duplicate=False, label='Animation Sequences:')
        self.layout.separator()
        shared.draw_collection_list(self.layout, context.object.m3_animation_groups, draw_group_props, label='Animation Groups:')


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
    Panel,
    M3AnimationActionNewOp,
    M3AnimationActionUnlinkOp,
)
