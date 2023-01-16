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


bl_id_type_to_collection_name = {
    bpy.types.Object: 'objects',
    bpy.types.Mesh: 'meshes',
    bpy.types.Armature: 'armatures',
}


m3_collections_suggested_names = {
    'm3_animations': ['Stand_full', 'Walk_full', 'Attack_full', 'Birth_full', 'Spell_full'],
    'm3_animation_groups': ['Stand', 'Walk', 'Attack', 'Birth', 'Spell'],
    'm3_attachmentpoints': ['Origin', 'Center', 'Overhead', 'Target'],
    'm3_billboards': ['Billboard'],
    'm3_cameras': ['CameraPortrait', 'CameraAvatar', 'Camera'],
    'm3_forces': ['Force'],
    'm3_hittests': ['Hit Test Fuzzy'],
    'm3_ikjoints': ['IK Joint'],
    'm3_lights': ['Light'],
    'm3_materiallayers': ['Layer'],
    'm3_materialrefs': ['Material'],
    'm3_particle_systems': ['Particle System'],
    'm3_particle_copies': ['Particle Copy'],
    'm3_cloths': ['Cloth'],
    'm3_clothconstraintsets': ['Cloth Constraint Set'],
    'm3_physicsshapes': ['Physics Shape'],
    'm3_physicsjoints': ['Joint'],
    'm3_projections': ['Projection'],
    'm3_ribbons': ['Ribbon'],
    'm3_ribbonsplines': ['Ribbon Spline'],
    'm3_rigidbodies': ['Rigid Body'],
    'm3_shadowbox': ['Shadow Box'],
    'm3_turrets': ['Turret'],
    'm3_warps': ['Warp'],
    'volumes': ['Volume'],
    'points': ['Spline Point'],
    'parts': ['Turret Part'],
    'constraints': ['Cloth Constraint'],
}


def m3_handle_gen():
    return '%064x' % random.getrandbits(256)


def m3_item_get_name(collection, prefix='', suggest=True):
    used_names = {item.name for item in collection}

    if prefix not in used_names:
        return prefix

    suggested_names = None if not suggest else m3_collections_suggested_names.get(collection.path_from_id().rsplit('.', 1)[-1])
    if not prefix and suggested_names:
        for name in suggested_names:
            prefix = name
            if name not in used_names:
                break
    else:
        if prefix.rsplit(' ', 1)[-1].isdigit():
            prefix = prefix.rsplit(' ', 1)[0]

    name = prefix
    num = 1
    while True:
        if name not in used_names:
            return name
        name = prefix + (' ' if prefix else '') + ('0' if num < 10 else '') + str(num)
        num += 1


def m3_item_add(collection, item_name=''):
    item = collection.add()
    item['bl_handle'] = m3_handle_gen()
    item['name'] = m3_item_get_name(collection, item_name)
    return item


def m3_item_duplicate(collection, src, dup_action_keyframes, dst_collection=None):
    # need to get path before adding item to collection
    src_path_base = src.path_from_id()
    dst_path_base = collection.path_from_id() + '[{}]'.format(len(collection))

    if dst_collection is None:
        dst_collection = collection

    dst = m3_item_add(dst_collection)

    if (type(dst) != type(src)):
        collection.remove(len(collection) - 1)
        return None

    dup_actions = []
    if dup_action_keyframes:
        for anim in collection.id_data.m3_animations:
            if anim.action not in dup_actions:
                dup_actions.append(anim.action)

    for key in type(dst).__annotations__.keys():
        prop = getattr(src, key)
        if str(type(prop)) != '<class \'bpy_prop_collection_idprop\'>':
            setattr(dst, key, prop)

            rna_props = src.bl_rna.properties[key]

            if not rna_props.is_animatable or type(prop) == str:
                continue

            src_path = '{}.{}'.format(src_path_base, key)
            dst_path = '{}.{}'.format(dst_path_base, key)

            for action in dup_actions:
                for ii in range(max(1, rna_props.array_length)):
                    src_fcurve = action.fcurves.find(src_path, index=ii)
                    if src_fcurve is None or src_fcurve.is_empty:
                        continue

                    points = len(src_fcurve.keyframe_points)
                    src_fcurve.keyframe_points.foreach_get('co', src_coords := [0] * (points * 2))
                    src_fcurve.keyframe_points.foreach_get('interpolation', src_interps := [0] * points)
                    src_fcurve.keyframe_points.foreach_get('type', src_types := [0] * points)

                    dst_fcurve = action.fcurves.new(dst_path, index=ii)
                    dst_fcurve.select = False
                    dst_fcurve.keyframe_points.add(points)
                    dst_fcurve.keyframe_points.foreach_set('co', src_coords)
                    dst_fcurve.keyframe_points.foreach_set('interpolation', src_interps)
                    dst_fcurve.keyframe_points.foreach_set('type', src_types)

        else:
            for item in prop:
                m3_item_duplicate(prop, item, dup_action_keyframes, dst_collection=getattr(dst, key))

    dst.name = ''
    dst.name = m3_item_get_name(dst_collection, src.name if not src.name.isdigit() else '', suggest=False)

    if dup_action_keyframes:
        # for some reason fcurve values are only properly displayed once animation view is updated manually
        collection.id_data.animation_data.action = collection.id_data.animation_data.action

    return dst


def m3_collection_index_set(bl, value):
    ob = bl.id_data
    rsp = bl.path_from_id().rsplit('.', 1)
    if len(rsp) == 1:
        setattr(ob, rsp[0] + '_index', value)
    else:
        setattr(ob.path_resolve(rsp[0]), rsp[1] + '_index', value)


def m3_pointer_get(search_data, handle):
    if not handle:
        return None
    for item in search_data:
        if item.bl_handle == handle:
            return item
    return None


def select_bones_handles(ob, bl_handles):
    if ob.m3_options.auto_update_bone_selection and bl_handles:
        for bone in ob.data.bones:
            bone.select = bone.bl_handle in bl_handles
            bone.select_tail = bone.select
            if bone.bl_handle == bl_handles[0]:
                ob.data.bones.active = bone


class ArmatureObjectPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'


class M3PropertyGroup(bpy.types.PropertyGroup):
    bl_handle: bpy.props.StringProperty(options=set())
    m3_export: bpy.props.BoolProperty(options=set(), default=True)
    name: bpy.props.StringProperty(options=set())


class M3BoneUserPropertyGroup(M3PropertyGroup):
    bone: bpy.props.StringProperty(options=set())


class M3VolumePropertyGroup(M3BoneUserPropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1))
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object)


class M3ObjectPropertyGroup(M3PropertyGroup):
    bl_object: bpy.props.PointerProperty(type=bpy.types.Object)


class M3CollectionOpBase(bpy.types.Operator):
    bl_idname = 'm3.collection_base'
    bl_label = 'Base Collection Operator'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    index: bpy.props.IntProperty()
    shift: bpy.props.IntProperty()


class M3CollectionOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.collection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        collection = context.object.path_resolve(self.collection)
        m3_item_add(collection)
        m3_collection_index_set(collection, len(collection) - 1)
        return {'FINISHED'}


class M3CollectionOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.collection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        collection = context.object.path_resolve(self.collection)

        if self.index not in range(len(collection)):
            return {'FINISHED'}

        collection.remove(self.index)

        remove_m3_action_keyframes(context.object, self.collection, self.index)
        for ii in range(self.index, len(collection)):
            shift_m3_action_keyframes(context.object, self.collection, ii + 1)

        m3_collection_index_set(collection, self.index - (1 if self.index == len(collection) else 0))

        return {'FINISHED'}


class M3CollectionOpMove(M3CollectionOpBase):
    bl_idname = 'm3.collection_move'
    bl_label = 'Move Collection Item'
    bl_description = 'Moves the active item up/down in the list'

    def invoke(self, context, event):
        collection = context.object.path_resolve(self.collection)

        if (self.index < len(collection) - self.shift and self.index >= -self.shift):
            collection.move(self.index, self.index + self.shift)
            swap_m3_action_keyframes(context.object, self.collection, self.index, self.index + self.shift)
            m3_collection_index_set(collection, self.index + self.shift)

        return {'FINISHED'}


class M3CollectionOpDuplicate(M3CollectionOpBase):
    bl_idname = 'm3.collection_duplicate'
    bl_label = 'Duplicate Collection Item'
    bl_description = 'Duplicates the active item in the collection'

    dup_action_keyframes: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        collection = context.object.path_resolve(self.collection)

        if self.index == -1:
            return {'FINISHED'}

        m3_item_duplicate(collection, collection[self.index], self.dup_action_keyframes)
        m3_collection_index_set(collection, len(collection) - 1)

        return {'FINISHED'}


class M3HandleListOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.handle_add'
    bl_label = 'Add Item To List'
    bl_description = 'Adds a new item to the list'

    def invoke(self, context, event):
        m3_item_add(context.object.path_resolve(self.collection))
        return {'FINISHED'}


class M3HandleListOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.handle_remove'
    bl_label = 'Remove Item From List'
    bl_description = 'Removes the item from the list'

    index: bpy.props.IntProperty(options=set())

    def invoke(self, context, event):
        context.object.path_resolve(self.collection).remove(self.index)
        return {'FINISHED'}


def m3_data_handles_verify(self, context):
    if self.search_data_verify:
        handles = set()
        for item in self.search_data:
            if not item.bl_handle or item.bl_handle in handles:
                item.bl_handle = m3_hangle_get()
            handles.add(item.bl_handle)


def m3_data_handles_enum(self, context):
    search_data_id = getattr(bpy.data, self.search_data_id_collection_name).get(self.search_data_id_name)
    search_data = search_data_id.path_resolve(self.search_data_path)
    for item in search_data:
        yield item.bl_handle, item.name, ''


class M3PropHandleSearch(bpy.types.Operator):
    bl_idname = 'm3.prophandle_search'
    bl_label = 'Search'
    bl_description = 'Search for an object to point to for the m3 property'
    bl_property = 'enum'

    prop_id_name: bpy.props.StringProperty()
    prop_id_collection_name: bpy.props.StringProperty()
    prop_path: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    search_data_id_name: bpy.props.StringProperty()
    search_data_id_collection_name: bpy.props.StringProperty()
    search_data_path: bpy.props.StringProperty()
    search_data_verify: bpy.props.BoolProperty()
    enum: bpy.props.EnumProperty(items=m3_data_handles_enum)

    def invoke(self, context, event):
        self.search_data_id = getattr(bpy.data, self.search_data_id_collection_name).get(self.search_data_id_name)
        self.search_data = self.search_data_id.path_resolve(self.search_data_path)
        m3_data_handles_verify(self, context)
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.prop_id = getattr(bpy.data, self.prop_id_collection_name).get(self.prop_id_name)
        self.prop_owner = self.prop_id.path_resolve(self.prop_path)
        setattr(self.prop_owner, self.prop_name, self.enum)
        return {'FINISHED'}


class M3PropHandleUnlink(bpy.types.Operator):
    bl_idname = 'm3.prophandle_unlink'
    bl_label = 'Unlink'
    bl_description = 'Removes the pointer to this object from the m3 property'
    bl_options = {'UNDO'}

    prop_id_name: bpy.props.StringProperty()
    prop_id_collection_name: bpy.props.StringProperty()
    prop_path: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        self.prop_id = getattr(bpy.data, self.prop_id_collection_name).get(self.prop_id_name)
        self.prop_owner = prop_id.path_resolve(self.prop_path)
        setattr(self.prop_owner, self.prop_name, '')
        return {'FINISHED'}


def draw_menu_duplicate(layout, collection, dup_keyframes_opt=False):
    path = collection.path_from_id()
    index = collection.id_data.path_resolve(path + '_index')
    op = layout.operator('m3.collection_duplicate', icon='DUPLICATE', text='Duplicate')
    op.collection = collection.path_from_id()
    op.index = index
    op.dup_action_keyframes = False
    if dup_keyframes_opt:
        op = layout.operator('m3.collection_duplicate', text='Duplicate With Animations')
        op.collection = collection.path_from_id()
        op.index = index
        op.dup_action_keyframes = True


# TODO Make it so that handle list items must be unique
def draw_handle_list(layout, search_data, data, prop_name, label=''):
    op = layout.operator('m3.handle_add', text=('Add ' + label) if label else None)
    op.collection = data.path_from_id(prop_name)
    for ii, item in enumerate(getattr(data, prop_name)):
        draw_handle_list_item(layout, search_data, data, prop_name, label, item, ii)


def draw_handle_list_item(layout, search_data, data, prop_name, label, item, index):
    pointer_ob = m3_pointer_get(search_data, item.bl_handle)

    row = layout.row(align=True)
    row.use_property_split = False
    op = row.operator('m3.prophandle_search', text=pointer_ob.name if pointer_ob else 'Select ' + label, icon='VIEWZOOM')
    op.prop_id_name = data.id_data.name
    op.prop_id_collection_name = bl_id_type_to_collection_name[type(data.id_data)]
    op.prop_path = item.path_from_id()
    op.prop_name = 'bl_handle'
    op.search_data_id_name = search_data.id_data.name
    op.search_data_id_collection_name = bl_id_type_to_collection_name[type(search_data.id_data)]
    op.search_data_path = search_data.path_from_id()
    op = row.operator('m3.handle_remove', text='', icon='X')
    op.collection = data.path_from_id(prop_name)
    op.index = index


def draw_pointer_prop(layout, search_data, data, prop_name, label='', icon=''):
    search_data_verify = False

    search_id_bl = search_data.id_data
    if type(search_id_bl) == bpy.types.Armature:
        if search_data == search_id_bl.bones:
            search_data_verify = True
            if search_id_bl.is_editmode:
                search_data = search_id_bl.edit_bones

    main = layout.row(align=True)
    main.use_property_split = False

    if label:
        split = main.split(factor=0.4)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text=label)
        row = split.row(align=True)
    else:
        row = main

    pointer_ob = m3_pointer_get(search_data, getattr(data, prop_name))

    op = row.operator('m3.prophandle_search', text='' if pointer_ob else 'Select', icon='VIEWZOOM')
    op.prop_id_name = data.id_data.name
    op.prop_id_collection_name = bl_id_type_to_collection_name[type(data.id_data)]
    op.prop_path = data.path_from_id()
    op.prop_name = prop_name
    op.search_data_id_name = search_id_bl.name
    op.search_data_id_collection_name = bl_id_type_to_collection_name[type(search_data.id_data)]
    op.search_data_path = search_data.path_from_id()
    op.search_data_verify = search_data_verify

    if pointer_ob:
        if icon:
            row.prop(pointer_ob, 'name', text='', icon=icon)
        else:
            row.prop(pointer_ob, 'name', text='')
        op = row.operator('m3.prophandle_unlink', text='', icon='CANCEL')
        op.prop_id_name = data.id_data.name
        op.prop_id_collection_name = bl_id_type_to_collection_name[type(data.id_data)]
        op.prop_path = data.path_from_id()
        op.prop_name = prop_name

    if layout.use_property_split and layout.use_property_decorate:
        row = main.row()
        row.alignment = 'RIGHT'
        row.separator(factor=3.6)


def draw_volume_props(volume, layout):
    draw_pointer_prop(layout, volume.id_data.data.bones, volume, 'bone', label='Bone', icon='BONE_DATA')
    sub = layout.column(align=True)
    sub.prop(volume, 'shape', text='Shape Type')
    if volume.shape == 'CUBE':
        sub.prop(volume, 'size', text='Size')
    elif volume.shape == 'SPHERE':
        sub.prop(volume, 'size', index=0, text='Size R')
    elif volume.shape in ['CAPSULE', 'CYLINDER']:
        sub.prop(volume, 'size', index=0, text='Size R')
        sub.prop(volume, 'size', index=1, text='H')
    elif volume.shape == 'MESH':
        sub.prop(volume, 'mesh_object', text='Mesh Object')
    col = layout.column()
    col.prop(volume, 'location', text='Location')
    col.prop(volume, 'rotation', text='Rotation')
    col.prop(volume, 'scale', text='Scale')


def draw_collection_list(layout, collection, draw_func, menu_id='', ops=[], label=''):
    ob = collection.id_data
    collection_path = collection.path_from_id()
    index = ob.path_resolve(collection_path + '_index')
    rows = 5 if len(collection) else 3

    if not ops:
        ops = ['m3.collection_add', 'm3.collection_remove', 'm3.collection_move', 'm3.collection_duplicate']

    rsp = collection_path.rsplit('.', 1)
    if len(rsp) == 1:
        list_str = collection_path
        list_obj = ob
    else:
        list_str = rsp[1]
        list_obj = ob.path_resolve(rsp[0])

    if label:
        col = layout.column(align=True)
        col.label(text=label)
        row = col.row()
    else:
        row = layout.row()

    col = row.column()
    col.template_list('UI_UL_list', list_str, list_obj, list_str, list_obj, list_str + '_index', rows=rows)
    col = row.column()
    sub = col.column(align=True)
    op = sub.operator(ops[0], icon='ADD', text='')
    op.collection, op.index = (collection_path, index)
    op = sub.operator(ops[1], icon='REMOVE', text='')
    op.collection, op.index = (collection_path, index)
    if menu_id:
        sub.separator()
        sub.menu(menu_id, icon='DOWNARROW_HLT', text='')

    if len(collection):
        sub.separator()
        op = sub.operator(ops[2], icon='TRIA_UP', text='')
        op.collection, op.index, op.shift = (collection_path, index, -1)
        op = sub.operator(ops[2], icon='TRIA_DOWN', text='')
        op.collection, op.index, op.shift = (collection_path, index, 1)

    if not len(collection):
        return

    item_ii = sorted((-1, index, len(collection) - 1))[1]

    if item_ii >= 0:
        item = collection[item_ii]
        col = layout.column()
        col.use_property_split = True
        draw_func(item, col)


def remove_m3_action_keyframes(ob, prefix, index):
    for action in [action for action in bpy.data.actions if ob.name in action.name]:
        path = '{}[{}]'.format(prefix, index)
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            action.fcurves.remove(fcurve)


def shift_m3_action_keyframes(ob, prefix, index, offset=-1):
    for action in [action for action in bpy.data.actions if ob.name in action.name]:
        path = '{}[{}]'.format(prefix, index)
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            fcurve.data_path = fcurve.data_path.replace(path, '{}[{}]'.format(prefix, index + offset))


def swap_m3_action_keyframes(ob, prefix, old, new):
    for action in bpy.data.actions:
        if ob.name not in action.name:
            continue

        path = '{}[{}]'.format(prefix, old)
        path_new = '{}[{}]'.format(prefix, new)

        fcurves = [fcurve for fcurve in action.fcurves if path in fcurve.data_path]
        fcurves_new = [fcurve for fcurve in action.fcurves if path_new in fcurve.data_path]

        for fcurve in fcurves:
            fcurve.data_path = fcurve.data_path.replace(path, path_new)

        for fcurve in fcurves_new:
            fcurve.data_path = fcurve.data_path.replace(path_new, path)


classes = (
    M3PropertyGroup,
    M3VolumePropertyGroup,
    M3BoneUserPropertyGroup,
    M3ObjectPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3CollectionOpDuplicate,
    M3HandleListOpAdd,
    M3HandleListOpRemove,
    M3PropHandleUnlink,
    M3PropHandleSearch,
)
