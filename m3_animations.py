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
        val = shared.m3_ob_getter(prop[0], obj=ob)
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
            attr = shared.m3_ob_getter(prop[0], obj=ob)
            if attr is not None:
                if type(default_val) in [float, int, bool]:
                    shared.m3_ob_setter(prop[0], default_val, obj=ob)
                else:
                    shared.m3_ob_setter(prop[0] + '[{}]'.format(prop[1]), default_val, obj=ob)
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


def draw_animation_handle(ob, anim, layout, index):
    search_prop = 'm3_animations'
    prop_name = 'm3_animation_groups[{}].animations[{}].handle'.format(ob.m3_animation_groups_index, index)
    pointer_ob = shared.m3_pointer_get(ob, search_prop, prop_name)
    row = layout.row(align=True)
    row.use_property_split = False
    op = row.operator('m3.proppointer_search', text=pointer_ob.name if pointer_ob else 'Select Animation', icon='VIEWZOOM')
    op.prop = prop_name
    op.search_prop = search_prop
    op = row.operator('m3.animation_handle_remove', text='', icon='X')
    op.index = index


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
    box = layout.box()
    box.operator('m3.animation_handle_add')
    for ii, anim in enumerate(anim_group.animations):
        draw_animation_handle(bpy.context.object, anim, box, ii)


class AnimationProperties(shared.M3PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action, update=anim_update)
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())


class AnimationHandleProperties(bpy.types.PropertyGroup):
    handle: bpy.props.StringProperty(options=set())


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
    animations: bpy.props.CollectionProperty(type=AnimationHandleProperties)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        self.layout.label(text='Animation Sequences:')
        shared.draw_collection_list(self.layout, 'm3_animations', draw_animation_props, can_duplicate=False)
        self.layout.separator()
        self.layout.label(text='Animation Groups:')
        shared.draw_collection_list(self.layout, 'm3_animation_groups', draw_group_props)


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


class M3AnimationHandleAddOp(bpy.types.Operator):
    bl_idname = 'm3.animation_handle_add'
    bl_label = 'Add Animation To Group'
    bl_description = 'Adds a new item to the collection'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
        anim_group.animations.add()
        return {'FINISHED'}


class M3AnimationHandleRemoveOp(bpy.types.Operator):
    bl_idname = 'm3.animation_handle_remove'
    bl_label = 'Remove Animation From Group'
    bl_description = 'Removes the item from the collection'
    bl_options = {'UNDO'}

    index: bpy.props.IntProperty(options=set())

    def invoke(self, context, event):
        anim_group = context.object.m3_animation_groups[context.object.m3_animation_groups_index]
        anim_group.animations.remove(self.index)
        return {'FINISHED'}


classes = (
    AnimationProperties,
    AnimationHandleProperties,
    GroupProperties,
    Panel,
    M3AnimationActionNewOp,
    M3AnimationActionUnlinkOp,
    M3AnimationHandleAddOp,
    M3AnimationHandleRemoveOp,
)
