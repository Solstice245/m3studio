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
    bpy.types.Object.m3_animations = bpy.props.CollectionProperty(type=Properties)
    bpy.types.Object.m3_animations_index = bpy.props.IntProperty(options=set(), default=-1)


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
        draw_func=draw_subgroup_props, use_name=True, can_duplicate=False,
    )


class DataPathProperties(bpy.types.PropertyGroup):
    val: bpy.props.StringProperty(options=set())


class SubgroupProperties(shared.M3PropertyGroup):
    priority: bpy.props.IntProperty(options=set(), min=0)
    concurrent: bpy.props.BoolProperty(options=set())
    data_paths: bpy.props.CollectionProperty(type=DataPathProperties)


class Properties(shared.M3PropertyGroup):
    frame_start: bpy.props.IntProperty(options=set(), min=0)
    frame_end: bpy.props.IntProperty(options=set(), min=0, default=60)
    simulate: bpy.props.BoolProperty(options=set())
    simulate_frame: bpy.props.IntProperty(options=set())
    movement_speed: bpy.props.FloatProperty(options=set())
    frequency: bpy.props.IntProperty(options=set(), min=0)
    not_looping: bpy.props.BoolProperty(options=set())
    always_global: bpy.props.BoolProperty(options=set())
    global_in_previewer: bpy.props.BoolProperty(options=set())
    subgroups: bpy.props.CollectionProperty(type=SubgroupProperties)


class Panel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ANIMATIONS'
    bl_label = 'M3 Animations'

    def draw(self, context):
        shared.draw_collection_list(self.layout, 'm3_animations', draw_props)


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

        print('select', data_paths)

        if ob.animation_data is not None:
            action = ob.animation_data.action
            if action is not None:
                for fcurve in action.fcurves:
                    print(fcurve.data_path)
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

        data_paths = set()

        if ob.animation_data is not None:
            action = ob.animation_data.action
            if action is not None:
                data_paths = set([fcurve.data_path for fcurve in action.fcurves if fcurve.select])

        animation = ob.m3_animations[ob.m3_animations_index]

        for subgroup in animation.subgroups:
            print(subgroup.bl_index, self.index)
            if subgroup.bl_index == self.index:
                subgroup.data_paths.clear()
                for data_path in data_paths:
                    item = subgroup.data_paths.add()
                    item.val = data_path
                    print(item, item.val)
            else:
                sg_data_paths = set([data_path.val for data_path in subgroup.data_paths])
                sg_data_paths = sg_data_paths - data_paths
                subgroup.data_paths.clear()
                for data_path in sg_data_paths:
                    item = subgroup.data_paths.add()
                    item.val = data_path

        print(data_paths)

        return {'FINISHED'}


classes = (
    DataPathProperties,
    SubgroupProperties,
    Properties,
    Panel,
    M3AnimationSubgroupOpSelect,
    M3AnimationSubgroupOpAssign,
)
