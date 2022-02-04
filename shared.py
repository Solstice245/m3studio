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


class ArmatureDataPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
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


class M3CollectionOpAdd(bpy.types.Operator):
    bl_idname = 'm3.collection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')

    def invoke(self, context, event):
        data = context.object.data
        getattr(data, self.collection).add()
        setattr(data, self.collection + '_index', len(getattr(data, self.collection)) - 1)

        return {'FINISHED'}


class M3CollectionOpRemove(bpy.types.Operator):
    bl_idname = 'm3.collection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty()

    def invoke(self, context, event):
        data = context.object.data
        getattr(data, self.collection).remove(getattr(data, self.collection + '_index'))

        for ii in range(getattr(data, self.collection + '_index'), len(getattr(data, self.collection))):
            shift_m3_action_keyframes(context.object, self.collection, ii + 1)

        setattr(data, self.collection + '_index', len(getattr(data, self.collection)) - 1)

        return {'FINISHED'}


class M3CollectionOpMove(bpy.types.Operator):
    bl_idname = 'm3.collection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the active item up/down in the list'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    shift: bpy.props.IntProperty(default=0)

    def invoke(self, context, event):
        ob = context.object
        data = ob.data
        ii = getattr(data, self.collection + '_index')

        if (ii < len(getattr(data, self.collection)) - self.shift and ii >= -self.shift):
            getattr(data, self.collection).move(ii, ii + self.shift)
            swap_m3_action_keyframes(ob, self.collection, ii, self.shift)
            setattr(data, self.collection + '_index', ii + self.shift)

        return {'FINISHED'}


class M3SubCollectionOpAdd(bpy.types.Operator):
    bl_idname = 'm3.subcollection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    subcollection: bpy.props.StringProperty()

    def invoke(self, context, event):
        data = context.object.data
        collection = getattr(data, self.collection)
        collection_index = getattr(data, self.collection + '_index')
        collection_item = collection[collection_index]
        subcollection = getattr(collection_item, self.subcollection)
        subcollection_item = subcollection.add()
        subcollection_item.bl_display = True
        subcollection_item.name = collection_item.name + ' ' + self.subcollection + ' ' + str(len(subcollection))

        return {'FINISHED'}


class M3SubCollectionOpRemove(bpy.types.Operator):
    bl_idname = 'm3.subcollection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the item from the collection'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    subcollection: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        data = context.object.data
        collection = getattr(data, self.collection)
        collection_index = getattr(data, self.collection + '_index')
        collection_item = collection[collection_index]
        subcollection = getattr(collection_item, self.subcollection)
        subcollection.remove(self.index)

        return {'FINISHED'}


class M3SubCollectionOpMove(bpy.types.Operator):
    bl_idname = 'm3.subcollection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the item up/down in the list'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    subcollection: bpy.props.StringProperty()
    index: bpy.props.IntProperty()
    shift: bpy.props.IntProperty()

    def invoke(self, context, event):
        ob = context.object
        data = ob.data
        collection = getattr(data, self.collection)
        collection_index = getattr(data, self.collection + '_index')
        collection_item = collection[collection_index]
        subcollection = getattr(collection_item, self.subcollection)
        if (self.index < len(subcollection) - self.shift and self.index >= -self.shift):
            subcollection_item = subcollection[self.index]
            subcollection_itemshift = subcollection[self.index + self.shift]
            subcollection.move(self.index, self.index + self.shift)
            subcollection_item.name = '{} {} {}'.format(collection_item.name, self.subcollection, self.index + 1)
            subcollection_itemshift.name = '{} {} {}'.format(collection_item.name, self.subcollection, self.index + self.shift + 1)
            swap_m3_action_keyframes(ob, '{}[{}].{}'.format(self.collection, collection_index, self.subcollection), self.index, self.shift)

        return {'FINISHED'}


class M3SubCollectionOpDisplayToggle(bpy.types.Operator):
    bl_idname = 'm3.subcollection_displaytoggle'
    bl_label = 'Toggle Collection Item Visibility'
    bl_description = 'Shows/hides the properties of the item in the list'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    subcollection: bpy.props.StringProperty()
    index: bpy.props.IntProperty()

    def invoke(self, context, event):
        data = context.object.data
        collection = getattr(data, self.collection)
        collection_index = getattr(data, self.collection + '_index')
        collection_item = collection[collection_index]
        subcollection = getattr(collection_item, self.subcollection)
        subcollection_item = subcollection[self.index]
        subcollection_item.bl_display = not subcollection_item.bl_display

        return {'FINISHED'}


def draw_bone_prop(item, data, layout, bone_prop='bone', prop_text='Bone'):
    if getattr(item, bone_prop, None) is not None:
        layout.prop_search(item, bone_prop, data, 'bones', text=prop_text)

        if not data.bones.get(getattr(item, bone_prop)):
            row = layout.row()
            row.label(text='')
            row.label(text='No bone match.', icon='ERROR')
            row.label(text='')


def draw_collection_list_active(data, layout, collection, draw_func):

    count = len(getattr(data, collection))
    rows = 5 if count > 1 else 3

    row = layout.row()
    col = row.column()
    col.template_list('UI_UL_list', collection, data, collection, data, collection + '_index', rows=rows)
    col = row.column()
    sub = col.column(align=True)
    op = sub.operator('m3.collection_add', icon='ADD', text='')
    op.collection = collection
    sub2 = sub.column(align=True)
    sub2.active = bool(len(getattr(data, collection)))
    op = sub2.operator('m3.collection_remove', icon='REMOVE', text='')
    op.collection = collection

    if rows == 5:
        sub = col.column(align=True)
        op = sub.operator('m3.collection_move', icon='TRIA_UP', text='')
        op.collection, op.shift = (collection, -1)
        op = sub.operator('m3.collection_move', icon='TRIA_DOWN', text='')
        op.collection, op.shift = (collection, -1)

    index = getattr(data, collection + '_index')

    if index < 0:
        return (None, None)

    item = getattr(data, collection)[index]

    box = layout.box()
    box.use_property_split = True
    col = box.column()
    col.prop(item, 'name', text='Identifier')
    draw_bone_prop(item, data, col)
    draw_func(item, box)


def draw_subcollection_list(data, layout, collection_id, subcollection_id, subcollection_name, draw_func):
    subcollection = getattr(data, subcollection_id)

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
                draw_bone_prop(item, bpy.context.object.pose, col)
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

        counter = '0' + str(num) if num < 10 else str(num)
        name = prefix + counter

        if name not in used_names:
            return name

        num += 1


def shift_m3_action_keyframes(arm, prefix, index):
    for action in [action for action in bpy.data.actions if arm.name in action.name]:
        path = '%s[%d]' % (prefix, index)
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            fcurve.data_path = fcurve.data_path.replace(path, '%s[%d]' % (prefix, index - 1))


def swap_m3_action_keyframes(arm, prefix, old, shift):
    for action in bpy.data.actions:
        if arm.name not in action.name:
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
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3SubCollectionOpAdd,
    M3SubCollectionOpRemove,
    M3SubCollectionOpMove,
    M3SubCollectionOpDisplayToggle,
}
