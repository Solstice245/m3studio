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
    bpy.types.Object.m3_animations = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_animations_index = bpy.props.IntProperty(options=set(), default=-1, update=anim_update)


def init_msgbus(ob, context):
    for animation in ob.m3_animations:
        action = animation.action
        for subgroup in animation.subgroups:
            for fcurve in action.fcurves:
                for item in subgroup.data_paths:
                    if fcurve.data_path == item.val:
                        shared.m3_msgbus_sub(item, fcurve, 'data_path', 'val')
                        break


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
        context.scene.frame_current = context.scene.frame_start = anim.frame_start
        context.scene.frame_end = anim.frame_end - 1


def draw_subgroup_props(subgroup, layout):
    layout.prop(subgroup, 'concurrent', text='Concurrent')
    layout.prop(subgroup, 'priority', text='Priority')
    layout.separator()
    row = layout.row()
    op = row.operator('m3.animation_subgroup_select')
    op.index = subgroup.bl_index
    op = row.operator('m3.animation_subgroup_assign')
    op.index = subgroup.bl_index


def draw_props(anim, layout):
    col = layout.column(align=True)
    col.prop(anim, 'frame_start', text='Frame Start')
    col.prop(anim, 'frame_end', text='End')
    row = layout.row(heading='Simulate Physics')
    row.prop(anim, 'simulate', text='')
    col = row.column()
    col.active = anim.simulate
    col.prop(anim, 'simulate_frame', text='On Frame')
    col = layout.column()
    col.prop(anim, 'frequency', text='Frequency')
    col.prop(anim, 'movement_speed', text='Movement Speed')
    col.prop(anim, 'not_looping', text='Does Not Loop')
    col.prop(anim, 'always_global', text='Always Global')
    col.prop(anim, 'global_in_previewer', text='Global In Previewer')

    shared.draw_collection_stack(
        layout=layout, collection_path='m3_animations[{}].subgroups'.format(anim.bl_index), label='Animation Subgroup',
        draw_func=draw_subgroup_props, use_name=True, can_duplicate=False
    )


class DataPathProperties(bpy.types.PropertyGroup):
    bl_handle: bpy.props.StringProperty(options=set())
    val: bpy.props.StringProperty(options=set())


class SubgroupProperties(shared.M3PropertyGroup):
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())
    data_paths: bpy.props.CollectionProperty(type=DataPathProperties)


class Properties(shared.M3PropertyGroup):
    action: bpy.props.PointerProperty(type=bpy.types.Action, update=anim_update)
    frame_start: bpy.props.IntProperty(options=set(), min=0)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60)
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set(), min=0)
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0, default=100)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    subgroups: bpy.props.CollectionProperty(type=SubgroupProperties)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        layout = self.layout
        ob = context.object
        index = ob.m3_animations_index
        rows = 5 if len(ob.m3_animations) else 3

        layout.operator('m3.animation_deselect')

        row = layout.row()
        col = row.column()
        col.template_list('UI_UL_list', 'm3_animations', ob, 'm3_animations', ob, 'm3_animations' + '_index', rows=rows)
        col = row.column()
        sub = col.column(align=True)
        op = sub.operator('m3.animation_add', icon='ADD', text='')
        op = sub.operator('m3.animation_remove', icon='REMOVE', text='')
        sub.separator()
        op = sub.operator('m3.animation_duplicate', icon='DUPLICATE', text='')

        if len(ob.m3_animations):
            sub.separator()
            op = sub.operator('m3.animation_move', icon='TRIA_UP', text='')
            op.shift = -1
            op = sub.operator('m3.animation_move', icon='TRIA_DOWN', text='')
            op.shift = 1

        if index < 0:
            return

        anim = ob.m3_animations[index]

        col = layout.column()
        col.use_property_split = True
        col.prop(anim, 'action', text='Action')
        col.separator()
        col.prop(anim, 'name', text='Name')
        col.separator()
        draw_props(anim, col)


class M3AnimationOpAdd(bpy.types.Operator):
    bl_idname = 'm3.animation_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        ob = context.object
        shared.m3_item_new('m3_animations')
        ob.m3_animations_index = len(ob.m3_animations) - 1

        return {'FINISHED'}


class M3AnimationOpRemove(bpy.types.Operator):
    bl_idname = 'm3.animation_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        ob = context.object
        ii = ob.m3_animations_index

        if ii < 0:
            return {'FINISHED'}

        ob.m3_animations.remove(ii)

        for ii in range(ii, len(ob.m3_animations)):
            ob.m3_animations[ii].bl_index -= 1

        ob.m3_animations_index -= 1 if (ii == 0 and len(ob.m3_animations) > 0) or ii == len(ob.m3_animations) else 0

        if ob.m3_animations_index == ii:
            anim_update(context.object, context)

        return {'FINISHED'}


class M3AnimationOpMove(bpy.types.Operator):
    bl_idname = 'm3.animation_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the active item up/down in the list'
    bl_options = {'UNDO'}

    shift: bpy.props.IntProperty()

    def invoke(self, context, event):
        ob = context.object
        ii = ob.m3_animations_index

        if (ii < len(ob.m3_animations) - self.shift and ii >= -self.shift):
            ob.m3_animations[ii].bl_index += self.shift
            ob.m3_animations[ii + self.shift].bl_index -= self.shift
            ob.m3_animations.move(ii, ii + self.shift)
            ob.m3_animations_index = ii + self.shift

        return {'FINISHED'}


class M3AnimationOpDuplicate(bpy.types.Operator):
    bl_idname = 'm3.animation_duplicate'
    bl_label = 'Duplicate Collection Item'
    bl_description = 'Duplicates the active item in the collection'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        ob = context.object
        ii = ob.m3_animations_index

        if ii < 0:
            return {'FINISHED'}

        shared.m3_item_duplicate('m3_animations', ob.m3_animations[ii])

        ob.m3_animations_index = len(ob.m3_animations) - 1

        return {'FINISHED'}


class M3AnimationOpDeselect(bpy.types.Operator):
    bl_idname = 'm3.animation_deselect'
    bl_label = 'Edit Default Values'
    bl_description = 'Deselects the active M3 animation sequence so that the default values can be edited'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        ob = context.object
        ob.m3_animations_index = -1
        return {'FINISHED'}


class M3AnimationSubgroupOpSelect(bpy.types.Operator):
    bl_idname = 'm3.animation_subgroup_select'
    bl_label = 'Select FCurves'
    bl_description = 'Selects all f-curves whose data paths are stored in the subgroup data'

    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        ob = context.object
        if ob.m3_animations_index < 0:
            return {'FINISHED'}

        animation = ob.m3_animations[ob.m3_animations_index]
        subgroup = animation.subgroups[self.index]
        data_paths = [data_path.val for data_path in subgroup.data_paths]

        if ob.animation_data is not None:
            action = ob.animation_data.action
            if action is not None:
                for fcurve in action.fcurves:
                    fcurve.select = True if fcurve.data_path in data_paths else False

        return {'FINISHED'}


class M3AnimationSubgroupOpAssign(bpy.types.Operator):
    bl_idname = 'm3.animation_subgroup_assign'
    bl_label = 'Assign FCurves'
    bl_description = 'Sets all selected f-curves data paths as members of the active subgroup'

    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        ob = context.object
        if ob.m3_animations_index < 0:
            return {'FINISHED'}

        fcurve_set = set()

        if ob.animation_data is not None:
            action = ob.animation_data.action
            if action is not None:
                fcurve_set = set([fcurve for fcurve in action.fcurves if fcurve.select])

        animation = ob.m3_animations[ob.m3_animations_index]

        for subgroup in animation.subgroups:

            for item in subgroup.data_paths:
                bpy.msgbus.clear_by_owner(item.bl_handle + 'val')

            if subgroup.bl_index == self.index:
                subgroup.data_paths.clear()
                for fcurve in fcurve_set:
                    item = subgroup.data_paths.add()
                    item.bl_handle = shared.m3_handle_gen()
                    item.val = fcurve.data_path
                    shared.m3_msgbus_sub(item, fcurve, 'data_path', 'val')
            else:
                sg_data_paths = set([data_path.val for data_path in subgroup.data_paths])
                sg_fcurve_set = set([fcurve for fcurve in action.fcurves if fcurve.data_path in sg_data_paths])
                sg_fcurve_set = sg_fcurve_set - fcurve_set
                subgroup.data_paths.clear()
                for fcurve in sg_fcurve_set:
                    item = subgroup.data_paths.add()
                    item.bl_handle = shared.m3_handle_gen()
                    item.val = fcurve.data_path
                    shared.m3_msgbus_sub(item, fcurve, 'data_path', 'val')

        return {'FINISHED'}


classes = (
    DataPathProperties,
    SubgroupProperties,
    Properties,
    Panel,
    M3AnimationOpAdd,
    M3AnimationOpRemove,
    M3AnimationOpMove,
    M3AnimationOpDuplicate,
    M3AnimationOpDeselect,
    M3AnimationSubgroupOpSelect,
    M3AnimationSubgroupOpAssign,
)
