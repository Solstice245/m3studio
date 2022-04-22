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
import random
from . import bl_enum


def m3_ob_getter(name, obj=None):
    if obj is None:
        obj = bpy.context.object
    for attr in name.split('.'):
        index = None
        lbs = attr.split('[', 1)
        if len(lbs) > 1:
            rbs = lbs[1].split(']', 1)
            index = int(rbs[0])
        if index is not None:
            obj = getattr(obj, lbs[0])[index]
        else:
            obj = getattr(obj, attr, None)
        if obj is None:
            return None
    return obj


def m3_ob_setter(name, value, obj='default'):
    rsp = name.rsplit('.', 1)
    if obj == 'default':
        obj = bpy.context.object
    if len(rsp) > 1:
        obj = m3_ob_getter(rsp[1], obj=obj)
    if obj is not None:
        setattr(obj, rsp[0], value)


def m3_item_new(collection):
    item = collection.add()
    item.bl_display = True
    item.bl_handle = '%030x' % random.getrandbits(60)
    item.bl_index = len(collection) - 1
    return item


def m3_item_duplicate(collection, src):
    dst = m3_item_new(collection)

    if (type(dst) != type(src)):
        collection.remove(len(collection) - 1)
        return None

    for key in type(dst).__annotations__.keys():
        prop = getattr(src, key)
        if str(type(prop)) != '<class \'bpy_prop_collection_idprop\'>':
            setattr(dst, key, prop)
        else:
            for item in prop:
                m3_item_duplicate(getattr(dst, key), item)

    return dst


def m3_msgbus_callback(self, context, owner, sub, key):
    self.bl_update = False
    setattr(self, owner, getattr(sub, key))
    self.bl_update = True


def m3_msgbus_sub(self, context, owner, sub, key):
    if sub:
        bpy.msgbus.subscribe_rna(
            key=sub.path_resolve(key, False),
            owner=self.bl_handle + owner,
            args=(self, context, owner, sub, key),
            notify=m3_msgbus_callback,
            options={'PERSISTENT'}
        )


def bone_update_event(self, context):
    if not self.bl_update:
        return

    bpy.msgbus.clear_by_owner(self.bl_handle + 'bone')
    bone = context.object.data.bones.get(self.bone)
    m3_msgbus_sub(self, context, 'bone', bone, 'name')


def bone1_update_event(self, context):
    if not self.bl_update:
        return

    bpy.msgbus.clear_by_owner(self.bl_handle + 'bone1')
    bone = context.object.data.bones.get(self.bone1)
    m3_msgbus_sub(self, context, 'bone1', bone, 'name')


def bone2_update_event(self, context):
    if not self.bl_update:
        return

    bpy.msgbus.clear_by_owner(self.bl_handle + 'bone2')
    bone = context.object.data.bones.get(self.bone2)
    m3_msgbus_sub(self, context, 'bone2', bone, 'name')


class ArmatureObjectPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'


class M3PropertyGroup(bpy.types.PropertyGroup):
    bl_display: bpy.props.BoolProperty(default=False)
    bl_update: bpy.props.BoolProperty(options=set(), default=True)
    bl_index: bpy.props.IntProperty(options=set())
    bl_handle: bpy.props.StringProperty(options=set())
    name: bpy.props.StringProperty(options=set())


class M3BoneUserPropertyGroup(M3PropertyGroup):
    bone: bpy.props.StringProperty(options=set(), update=bone_update_event)


class M3VolumePropertyGroup(M3BoneUserPropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))


class M3CollectionOpBase(bpy.types.Operator):
    bl_idname = 'm3.collection_base'
    bl_label = 'Base Collection Operator'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    index: bpy.props.IntProperty()
    shift: bpy.props.IntProperty()
    set_display: bpy.props.BoolProperty(default=True)
    set_name: bpy.props.BoolProperty(default=False)


class M3CollectionOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.collection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)
        item = m3_item_new(collection)

        m3_ob_setter('bl_display', self.set_display, obj=item)
        m3_ob_setter(self.collection + '_index', item.bl_index)

        return {'FINISHED'}


class M3CollectionOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.collection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)
        collection.remove(self.index)

        remove_m3_action_keyframes(context.object, self.collection, self.index)
        for ii in range(self.index, len(collection)):
            collection[ii].bl_index -= 1
            shift_m3_action_keyframes(context.object, self.collection, ii + 1)

        new_index = self.index
        new_index -= 1 if (self.index == 0 and len(collection) > 0) or self.index == len(collection) else 0

        m3_ob_setter(self.collection + '_index', new_index)

        return {'FINISHED'}


class M3CollectionOpMove(M3CollectionOpBase):
    bl_idname = 'm3.collection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the active item up/down in the list'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)

        if (self.index < len(collection) - self.shift and self.index >= -self.shift):
            collection[self.index].bl_index += self.shift
            collection[self.index + self.shift].bl_index -= self.shift
            collection.move(self.index, self.index + self.shift)
            swap_m3_action_keyframes(context.object, self.collection, self.index, self.shift)
            m3_ob_setter(self.collection + '_index', self.index + self.shift)

        return {'FINISHED'}


class M3CollectionOpDuplicate(M3CollectionOpBase):
    bl_idname = 'm3.collection_duplicate'
    bl_label = 'Duplicate Collection Item'
    bl_description = 'Duplicates the active item in the collection'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)

        if self.index == -1:
            return {'FINISHED'}

        item = collection[self.index]
        m3_item_duplicate(collection, item)

        m3_ob_setter(self.collection + '_index', len(collection) - 1)

        return {'FINISHED'}


class M3CollectionOpDisplayToggle(M3CollectionOpBase):
    bl_idname = 'm3.collection_displaytoggle'
    bl_label = 'Toggle Collection Item Visibility'
    bl_description = 'Shows/hides the properties of the item in the list'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)
        collection[self.index].bl_display = not collection[self.index].bl_display

        return {'FINISHED'}


def draw_bone_prop(item, ob, layout, bone_prop='bone', prop_text='Bone'):
    if hasattr(item, bone_prop):
        layout.prop_search(item, bone_prop, ob.data, 'bones', text=prop_text)

        if not ob.data.bones.get(getattr(item, bone_prop)):
            row = layout.row()
            row.label(text='')
            row.label(text='No bone match.', icon='ERROR')
            row.label(text='')


def draw_collection_list(layout, collection_path, draw_func):
    collection = m3_ob_getter(collection_path)
    index = m3_ob_getter(collection_path + '_index')
    rows = 5 if len(collection) else 3

    rsp = collection_path.rsplit('.', 1)
    if len(rsp) == 1:
        list_str = collection_path
        list_obj = bpy.context.object
    else:
        list_str = rsp[1]
        list_obj = m3_ob_getter(rsp[0])

    row = layout.row()
    col = row.column()
    col.template_list('UI_UL_list', list_str, list_obj, list_str, list_obj, list_str + '_index', rows=rows)  # TODO
    col = row.column()
    sub = col.column(align=True)
    op = sub.operator('m3.collection_add', icon='ADD', text='')
    op.collection, op.index = (collection_path, index)
    op = sub.operator('m3.collection_remove', icon='REMOVE', text='')
    op.collection, op.index = (collection_path, index)
    sub.separator()
    op = sub.operator('m3.collection_duplicate', icon='DUPLICATE', text='')
    op.collection, op.index = (collection_path, index)

    if len(collection):
        sub.separator()
        op = sub.operator('m3.collection_move', icon='TRIA_UP', text='')
        op.collection, op.index, op.shift = (collection_path, index, -1)
        op = sub.operator('m3.collection_move', icon='TRIA_DOWN', text='')
        op.collection, op.index, op.shift = (collection_path, index, 1)

    if index < 0:
        return

    item = collection[index]

    box = layout.box()
    box.use_property_split = True
    col = box.column()
    col.prop(item, 'name', text='Identifier')

    draw_bone_prop(item, bpy.context.object, col)
    draw_func(item, box)


def draw_collection_stack(layout, collection_path, label, draw_func):
    collection = m3_ob_getter(collection_path)

    box = layout.box()
    op = box.operator('m3.collection_add', text='Add ' + label)
    op.collection = collection_path

    if len(collection):
        for index, item in enumerate(collection):

            row = box.row(align=True)
            col = row.column(align=True)

            if not item.bl_display:
                op = col.operator('m3.collection_displaytoggle', icon='TRIA_RIGHT', text='Toggle ' + label + ' Display')
                op.collection, op.index = (collection_path, index)
            else:
                op = col.operator('m3.collection_displaytoggle', icon='TRIA_DOWN', text='')
                op.collection, op.index = (collection_path, index)
                col = row.column()
                draw_bone_prop(item, bpy.context.object, col)
                draw_func(item, col)

            col = row.column(align=True)
            op = col.operator('m3.collection_remove', icon='X', text='')
            op.collection, op.index = (collection_path, index)

            if item.bl_display:
                sub = col.column(align=True)
                op = sub.operator('m3.collection_move', icon='TRIA_UP', text='')
                op.collection, op.index, op.shift = (collection_path, index, -1)
                op = sub.operator('m3.collection_move', icon='TRIA_DOWN', text='')
                op.collection, op.index, op.shift = (collection_path, index, 1)


def collection_find_unused_name(collections=[], suggested_names=[], prefix=''):
    used_names = [item.name for item in collection for collection in collections]
    num = 1
    while True:
        for name in [name for name in suggested_names if name not in used_names]:
            return name

        name = prefix + ' 0' + str(num) if num < 10 else str(num)

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
    M3PropertyGroup,
    M3VolumePropertyGroup,
    M3BoneUserPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3CollectionOpDuplicate,
    M3CollectionOpDisplayToggle,
}
