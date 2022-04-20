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
from . import bl_enum


def bone_update_callback(m3, bone):
    m3.bl_update = False
    m3.bone = bone.name
    m3.bl_update = True


def bone_update_event(self, context):
    if not self.bl_update:
        return

    bone = context.object.data.bones[self.bone]
    if bone:
        bpy.msgbus.clear_by_owner(self.bone)
        bpy.msgbus.subscribe_rna(
            key=bone.path_resolve('name', False),
            owner=self.bone,
            args=(self, bone),
            notify=bone_update_callback,
            options={'PERSISTENT'}
        )
    else:
        bpy.msgbus.clear_by_owner(self.bone)


class ArmatureObjectPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'


class M3VolumePropertyGroup(bpy.types.PropertyGroup):
    bl_display: bpy.props.BoolProperty(default=False)
    bl_update: bpy.props.BoolProperty(options=set(), default=True)
    bone: bpy.props.StringProperty(options=set(), update=bone_update_event)
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))


class M3BoneUserPropertyGroup(bpy.types.PropertyGroup):
    bl_display: bpy.props.BoolProperty(default=False)
    bl_update: bpy.props.BoolProperty(options=set(), default=True)
    name: bpy.props.StringProperty(options=set())
    bone: bpy.props.StringProperty(options=set(), update=bone_update_event)


class M3CollectionOpBase(bpy.types.Operator):
    bl_idname = 'm3.collection_base'
    bl_label = 'Base Collection Operator'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    subcollection: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    shift: bpy.props.IntProperty()


class M3CollectionOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.collection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        ob = context.object
        col = getattr(ob, self.collection)

        col.add()
        setattr(ob, self.collection + '_index', len(col) - 1)

        return {'FINISHED'}


class M3CollectionOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.collection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        ob = context.object
        col = getattr(ob, self.collection)
        col_ii = getattr(ob, self.collection + '_index')

        col.remove(col_ii)

        remove_m3_action_keyframes(ob, self.collection, col_ii)
        for ii in range(col_ii, len(col)):
            shift_m3_action_keyframes(ob, self.collection, ii + 1)

        setattr(ob, self.collection + '_index', len(col) - 1)

        return {'FINISHED'}


class M3CollectionOpMove(M3CollectionOpBase):
    bl_idname = 'm3.collection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the active item up/down in the list'

    def invoke(self, context, event):
        ob = context.object
        col = getattr(ob, self.collection)
        ii = getattr(ob, self.collection + '_index')

        if (ii < len(col) - self.shift and ii >= -self.shift):
            col.move(ii, ii + self.shift)
            swap_m3_action_keyframes(ob, self.collection, ii, self.shift)
            setattr(ob, self.collection + '_index', ii + self.shift)

        return {'FINISHED'}


class M3SubCollectionOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.subcollection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        ob = context.object
        prop = getattr(ob, self.collection)[getattr(ob, self.collection + '_index')]
        subcol = getattr(prop, self.subcollection)
        subprop = subcol.add()
        subprop.bl_display = True
        subprop.name = prop.name + ' ' + self.subcollection + ' ' + str(len(subcol))

        return {'FINISHED'}


class M3SubCollectionOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.subcollection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the item from the collection'

    def invoke(self, context, event):
        ob = context.object
        prop = getattr(ob, self.collection)[getattr(ob, self.collection + '_index')]
        subcol = getattr(prop, self.subcollection)
        subcol.remove(self.index)

        remove_m3_action_keyframes(ob, self.subcollection, self.index)
        for ii in range(self.index, len(subcol)):
            shift_m3_action_keyframes(ob, self.subcollection, ii + 1)

        return {'FINISHED'}


class M3SubCollectionOpMove(M3CollectionOpBase):
    bl_idname = 'm3.subcollection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the item up/down in the list'

    def invoke(self, context, event):
        ob = context.object
        prop = getattr(ob, self.collection)[getattr(ob, self.collection + '_index')]
        subcol = getattr(prop, self.subcollection)
        if (self.index < len(subcol) - self.shift and self.index >= -self.shift):
            subcol.move(self.index, self.index + self.shift)
            subcol[self.index].name = '{} {} {}'.format(prop.name, self.subcollection, self.index + 1)
            subcol[self.index + self.shift].name = '{} {} {}'.format(prop.name, self.subcollection, self.index + self.shift + 1)
            swap_m3_action_keyframes(ob, self.subcollection, self.index, self.shift)

        return {'FINISHED'}


class M3SubCollectionOpDisplayToggle(M3CollectionOpBase):
    bl_idname = 'm3.subcollection_displaytoggle'
    bl_label = 'Toggle Collection Item Visibility'
    bl_description = 'Shows/hides the properties of the item in the list'

    def invoke(self, context, event):
        ob = context.object
        prop = getattr(ob, self.collection)[getattr(ob, self.collection + '_index')]
        subprop = getattr(prop, self.subcollection)[self.index]
        subprop.bl_display = not subprop.bl_display

        return {'FINISHED'}


def draw_bone_prop(item, ob, layout, bone_prop='bone', prop_text='Bone'):
    if getattr(item, bone_prop, None) is not None:
        layout.prop_search(item, bone_prop, ob.data, 'bones', text=prop_text)

        if not ob.data.bones.get(getattr(item, bone_prop)):
            row = layout.row()
            row.label(text='')
            row.label(text='No bone match.', icon='ERROR')
            row.label(text='')


def draw_collection_list_active(ob, layout, collection, draw_func):

    count = len(getattr(ob, collection))
    rows = 5 if count > 1 else 3

    row = layout.row()
    col = row.column()
    col.template_list('UI_UL_list', collection, ob, collection, ob, collection + '_index', rows=rows)
    col = row.column()
    sub = col.column(align=True)
    op = sub.operator('m3.collection_add', icon='ADD', text='')
    op.collection = collection
    sub2 = sub.column(align=True)
    sub2.active = bool(len(getattr(ob, collection)))
    op = sub2.operator('m3.collection_remove', icon='REMOVE', text='')
    op.collection = collection

    if rows == 5:
        sub = col.column(align=True)
        op = sub.operator('m3.collection_move', icon='TRIA_UP', text='')
        op.collection, op.shift = (collection, -1)
        op = sub.operator('m3.collection_move', icon='TRIA_DOWN', text='')
        op.collection, op.shift = (collection, 1)

    index = getattr(ob, collection + '_index')

    if index < 0:
        return (None, None)

    item = getattr(ob, collection)[index]

    box = layout.box()
    box.use_property_split = True
    col = box.column()
    col.prop(item, 'name', text='Identifier')
    draw_bone_prop(item, ob, col)
    draw_func(item, box)


def draw_subcollection_list(ob, layout, collection_id, subcollection_id, subcollection_name, draw_func):
    subcollection = getattr(ob, subcollection_id)

    box = layout.box()
    op = box.operator('m3.subcollection_add', text='Add ' + subcollection_name)
    op.collection, op.subcollection = (collection_id, subcollection_id)

    items = []

    if len(subcollection):
        for index, item in enumerate(subcollection):
            items.append(item)

            row = box.row(align=True)
            col = row.column(align=True)

            if not item.bl_display:
                op = col.operator('m3.subcollection_displaytoggle', icon='TRIA_RIGHT', text='Toggle ' + subcollection_name + ' Display')
                op.collection, op.subcollection, op.index = (collection_id, subcollection_id, index)
            else:
                op = col.operator('m3.subcollection_displaytoggle', icon='TRIA_DOWN', text='')
                op.collection, op.subcollection, op.index = (collection_id, subcollection_id, index)
                col = row.column()
                draw_bone_prop(item, bpy.context.object, col)
                draw_func(item, col)

            col = row.column(align=True)
            op = col.operator('m3.subcollection_remove', icon='X', text='')
            op.collection, op.subcollection, op.index = (collection_id, subcollection_id, index)

            if item.bl_display and len(subcollection) > 1:
                sub = col.column(align=True)
                op = sub.operator('m3.subcollection_move', icon='TRIA_UP', text='')
                op.collection, op.subcollection, op.index, op.shift = (collection_id, subcollection_id, index, -1)
                op = sub.operator('m3.subcollection_move', icon='TRIA_DOWN', text='')
                op.collection, op.subcollection, op.index, op.shift = (collection_id, subcollection_id, index, 1)


def collection_find_unused_name(collections=[], suggested_names=[], prefix=''):
    used_names = [item.name for item in collection for collection in collections]
    num = 1
    while True:
        for name in [name for name in suggested_names if name not in used_names]:
            return name

        name = prefix + '0' + str(num) if num < 10 else str(num)

        if name not in used_names:
            return name

        num += 1


def remove_m3_action_keyframes(ob, prefix, index):
    for action in [action for action in bpy.data.actions if ob.name in action.name]:
        path = '%s[%d]' % (prefix, index)
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            action.fcurves.remove(fcurve)


def shift_m3_action_keyframes(ob, prefix, index, offset=-1):
    for action in [action for action in bpy.data.actions if ob.name in action.name]:
        path = '%s[%d]' % (prefix, index)
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            fcurve.data_path = fcurve.data_path.replace(path, '%s[%d]' % (prefix, index + offset))


def swap_m3_action_keyframes(ob, prefix, old, shift):
    for action in bpy.data.actions:
        if ob.name not in action.name:
            continue

        path = '%s[%d]' % (prefix, old)
        path_shift = '%s[%d]' % (prefix, old + shift)

        fcurves = [fcurve for fcurve in action.fcurves if path in fcurve.data_path]
        fcurves_shift = [fcurve for fcurve in action.fcurves if path_shift in fcurve.data_path]

        for fcurve in fcurves:
            fcurve.data_path = fcurve.data_path.replace(path, path_shift)

        for fcurve in fcurves_shift:
            fcurve.data_path = fcurve.data_path.replace(path_shift, path)


classes = {
    M3VolumePropertyGroup,
    M3BoneUserPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3SubCollectionOpAdd,
    M3SubCollectionOpRemove,
    M3SubCollectionOpMove,
    M3SubCollectionOpDisplayToggle,
}
