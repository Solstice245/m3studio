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


m3_collections_suggested_names = {
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
    'm3_particlesystems': ['Particle System'],
    'm3_particlecopies': ['Particle Copy'],
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
    'animations': ['full', 'sub'],
    'volumes': ['Volume'],
    'points': ['Spline Point'],
    'parts': ['Turret Part'],
    'constraints': ['Cloth Constraint'],
}


material_collections = (
    'None', 'm3_materials_standard', 'm3_materials_displacement', 'm3_materials_composite', 'm3_materials_terrain', 'm3_materials_volume', 'None',
    'm3_materials_creep', 'm3_materials_volumenoise', 'm3_materials_stb', 'm3_materials_reflection', 'm3_materials_lensflare', 'm3_materials_buffer',
)


material_type_to_model_reference = {
    1: 'materials_standard',
    2: 'materials_displacement',
    3: 'materials_composite',
    4: 'materials_terrain',
    5: 'materials_volume',
    7: 'materials_creep',
    8: 'materials_volumenoise',
    9: 'materials_stb',
    10: 'materials_reflection',
    11: 'materials_lensflare',
    12: 'materials_buffer',
}


material_type_to_layers = {
    1: ['diff', 'decal', 'spec', 'gloss', 'emis1', 'emis2', 'envi', 'envi_mask', 'alpha1', 'alpha2', 'norm',
        'height', 'light', 'ao', 'norm_blend1_mask', 'norm_blend2_mask', 'norm_blend1', 'norm_blend2'],
    2: ['norm', 'strength'],
    3: [],
    4: ['terrain'],
    5: ['color', 'unknown1', 'unknown2'],
    7: ['creep'],
    8: ['color', 'noise1', 'noise2'],
    9: ['diff', 'spec', 'normal'],
    10: ['norm', 'strength', 'blur'],
    11: ['color', 'unknown'],
    12: []
}


def get_ob_bones(ob):
    if ob.mode == 'EDIT':
        return ob.data.edit_bones
    elif ob.mode == 'POSE':
        return ob.pose.bones
    else:
        return ob.data.bones


def m3_handle_gen():
    return '%064x' % random.getrandbits(256)


def m3_anim_id_gen():
    # anim ids in list reserved for events and bounds
    while (num := random.randint(1, 2 ** 32 - 1)) in (0x001f9bd2, 0x65bd3215):
        num = random.randint(1, 2 ** 32 - 1)

    return hex(num)[2:]


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

    for key in type(item).__annotations__.keys():
        prop = getattr(item, key)
        if type(prop) == M3AnimHeaderProp:
            prop.hex_id = m3_anim_id_gen()

    return item


def m3_item_duplicate(collection, src, dup_action_keyframes, dst_collection=None):
    # need to get path before adding item to collection
    src_path_base = src.path_from_id()

    try:
        dst_path_base = f'{collection.path_from_id()}[{len(collection)}]'
    except ValueError:
        print('unable to create path to collection', collection)
        dst_path_base = None

    if dst_collection is None:
        dst_collection = collection

    dst = m3_item_add(dst_collection)

    if (type(dst) != type(src)):
        collection.remove(len(collection) - 1)
        return None

    dup_actions = []
    if dup_action_keyframes:
        for anim_group in collection.id_data.m3_animation_groups:
            for anim in anim_group.animations:
                if anim.action and anim.action not in dup_actions:
                    dup_actions.append(anim.action)

    for key in type(dst).__annotations__.keys():
        prop = getattr(src, key)

        if type(prop) == M3AnimHeaderProp:
            dst_prop = getattr(dst, key)
            dst_prop.hex_id = m3_anim_id_gen()
            dst_prop.interpolation = prop.interpolation
            dst_prop.flags = prop.flags
        elif str(type(prop)) == '<class \'bpy_prop_collection_idprop\'>':
            for item in prop:
                m3_item_duplicate(prop, item, dup_action_keyframes, dst_collection=getattr(dst, key))
        elif 'PointerProp' in str(type(prop)):
            dst_prop = getattr(dst, key)
            dst_prop.value = prop.value
            dst_prop.handle = prop.handle
        elif key != 'name':
            setattr(dst, key, prop)

            rna_props = src.bl_rna.properties[key]

            if not rna_props.is_animatable or type(prop) == str:
                continue

            src_path = f'{src_path_base}.{key}'
            dst_path = f'{dst_path_base}.{key}'

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

    dst['name'] = ''
    dst['name'] = m3_item_get_name(dst_collection, src.name if not src.name.isdigit() else '', suggest=False)

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


def m3_pointer_get(search_data, pointer):
    handle = pointer.handle if type(pointer) != str else pointer
    if not handle:
        return None
    for item in search_data:
        if item.bl_handle == handle:
            return item
    return None


def select_bones_handles(ob, pointers):
    m3_data_handles_verify(ob.pose.bones)
    bl_handles = [pointer.handle for pointer in pointers]
    if ob.m3_options.update_bone_selection and bl_handles:
        for pb in ob.pose.bones:
            db = ob.data.bones.get(pb.name)
            db.select = pb.bl_handle in bl_handles
            db.select_tail = db.select
            if pb.bl_handle == bl_handles[0]:
                ob.data.bones.active = db


class ArmatureObjectPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE'


def get_armature_parent(ob):
    while ob.type != 'ARMATURE' or ob.parent:
        ob = ob.parent
    return ob


def get_bone_value(self):
    return self.bone.value


def infer_data_path(ob, data_path):
    collections = data_path.split('[')
    inferred_data_path = ''

    for col in collections[:-1]:
        inferred_data_path += col
        inferred_data_path += ob.path_resolve(inferred_data_path + '_index')
    inferred_data_path += collections[-1]

    data = ob.path_resolve(inferred_data_path)

    if type(data) == bpy.types.ArmatureBones or type(data) == bpy.types.ArmatureEditBones:
        data = get_ob_bones(self.id_data)

    return data


def pointer_val_get(self, data_path, to_armature=True):
    ob = get_armature_parent(self.id_data) if to_armature else self.id_data
    datem = m3_pointer_get(infer_data_path(ob, data_path), self)
    if datem:
        self['value'] = datem.name
    return self.get('value', '')


def pointer_val_set(self, value, data_path, exclusive=False, to_armature=True):
    ob = get_armature_parent(self.id_data) if to_armature else self.id_data

    if value:
        data = infer_data_path(ob, data_path)
        if type(data) == bpy.types.ArmatureBones:
            m3_data_handles_verify(get_ob_bones(ob))
        else:
            m3_data_handles_verify(data)

        if exclusive:

            collection = ob.path_resolve(self.path_from_id().rsplit('[', 1)[0])
            test = collection[0]
            for key in type(test).__annotations__.keys():
                if type(getattr(test, key)) == type(self):
                    self_propname = key
                    break

            used_values = {getattr(item, self_propname).value for item in collection if getattr(item, self_propname) != self}
            # ensure unique value
            if value in used_values:
                rsplit = value.rsplit('.', 1)
                prefix = rsplit[0] if rsplit[-1].isdigit() else value
                value = prefix
                num = 1
                while True:
                    if value not in used_values:
                        break
                    value = prefix + '.' + ('0' if num < 100 else '') + ('0' if num < 10 else '') + str(num)
                    num += 1

        for item in data:
            if item.name == value:
                self['handle'] = item.bl_handle
                break
        else:
            self['handle'] = ''

    else:
        self['handle'] = ''

    self['value'] = value


def pointer_get_args(*args):
    return lambda x: pointer_val_get(x, *args)


def pointer_set_args(*args):
    return lambda x, y: pointer_val_set(x, y, *args)


class M3BonePointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=pointer_get_args('data.bones'), set=pointer_set_args('data.bones', False))
    handle: bpy.props.StringProperty(options=set())


class M3BonePointerPropExclusive(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=pointer_get_args('data.bones'), set=pointer_set_args('data.bones', True))
    handle: bpy.props.StringProperty(options=set())


class M3MatRefPointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=pointer_get_args('m3_materialrefs'), set=pointer_set_args('m3_materialrefs', False))
    handle: bpy.props.StringProperty(options=set())


def draw_prop_pointer_search(layout, data, search_data, search_prop, text='', icon=None):
    search_prop = 'edit_bones' if search_prop == 'bones' and getattr(search_data, 'is_editmode') else search_prop
    layout.prop_search(data, 'value', search_data, search_prop, text=text, icon=icon)


class M3BonePointerList(bpy.types.UIList):
    bl_idname = 'UI_UL_M3_bone_user'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            bone = m3_pointer_get(get_ob_bones(item.id_data), item.bone)
            row = layout.row()
            row.prop(item.bone, 'value', text='', emboss=False, icon='BONE_DATA')
            if not bone:
                row.label(icon='ERROR', text='Invalid bone name')


def hex_id_get(self):
    return self['hex_id']


def hex_id_set(self, value):
    try:
        self['hex_id'] = hex(int(value, 16))[2:]
    except ValueError:
        self['hex_id'] = m3_anim_id_gen()


class M3AnimHeaderProp(bpy.types.PropertyGroup):
    hex_id: bpy.props.StringProperty(options=set(), maxlen=8, get=hex_id_get, set=hex_id_set, default='')
    interpolation: bpy.props.EnumProperty(options=set(), items=bl_enum.anim_header_interp, default='AUTO')
    flags: bpy.props.IntProperty(options=set(), min=-1, default=-1)  # -1 means automatic


class M3PropertyGroup(bpy.types.PropertyGroup):
    bl_handle: bpy.props.StringProperty(options=set())
    m3_export: bpy.props.BoolProperty(options=set(), default=True)
    name: bpy.props.StringProperty(options=set())


class M3VolumePropertyGroup(M3PropertyGroup):
    bone: bpy.props.PointerProperty(type=M3BonePointerProp)
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

        m3_collection_index_set(collection, self.index - (1 if (self.index == 0 and len(collection) == 0) or self.index == len(collection) else 0))

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


def m3_data_handles_verify(data):
    handles = set()
    for item in data:
        if not item.bl_handle or item.bl_handle in handles:
            item.bl_handle = m3_handle_gen()
        handles.add(item.bl_handle)


def m3_data_handles_enum(self, context):
    search_data_id = bpy.data.objects.get(self.search_data_id_name)
    search_data = search_data_id.path_resolve(self.search_data_path)
    for item in search_data:
        yield item.bl_handle, item.name, ''


class M3PropHandleSearch(bpy.types.Operator):
    bl_idname = 'm3.prophandle_search'
    bl_label = 'Search'
    bl_description = 'Search for an object to point to for the m3 property'
    bl_property = 'enum'

    prop_id_name: bpy.props.StringProperty()
    prop_path: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    search_data_id_name: bpy.props.StringProperty()
    search_data_path: bpy.props.StringProperty()
    enum: bpy.props.EnumProperty(items=m3_data_handles_enum)

    def invoke(self, context, event):
        self.search_data_id = bpy.data.objects.get(self.search_data_id_name)
        m3_data_handles_verify(self.search_data_id.path_resolve(self.search_data_path))
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.prop_id = bpy.data.objects.get(self.prop_id_name)
        self.prop_owner = self.prop_id.path_resolve(self.prop_path)
        setattr(self.prop_owner, self.prop_name, self.enum)
        return {'FINISHED'}


class M3PropHandleUnlink(bpy.types.Operator):
    bl_idname = 'm3.prophandle_unlink'
    bl_label = 'Unlink'
    bl_description = 'Removes the pointer to this object from the m3 property'
    bl_options = {'UNDO'}

    prop_id_name: bpy.props.StringProperty()
    prop_path: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def invoke(self, context, event):
        prop_id = bpy.data.objects.get(self.prop_id_name)
        prop_owner = prop_id.path_resolve(self.prop_path)
        setattr(prop_owner, self.prop_name, '')
        return {'FINISHED'}


class M3EditAnimHeader(bpy.types.Operator):
    bl_idname = 'm3.edit_anim_header'
    bl_label = 'Edit M3 Animation Header'
    bl_description = 'Opens a window for editing M3 animation header properties'

    prop_id_name: bpy.props.StringProperty()
    prop_path: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=360)

    def draw(self, context):
        m3_anim_header = getattr(bpy.data.objects.get(self.prop_id_name).path_resolve(self.prop_path), self.prop_name + '_header')
        main = self.layout.row(align=True)
        split = main.split(factor=0.275)
        row = split.row()
        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text='Animation ID')
        col.label(text='Interpolation')
        col.label(text='Flags')
        row = split.row()
        col = row.column()
        col.prop(m3_anim_header, 'hex_id', text='')
        col.prop(m3_anim_header, 'interpolation', text='')
        col.prop(m3_anim_header, 'flags', text='')


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


def draw_prop_items(layout, data, prop, items=[]):
    rna_props = data.bl_rna.properties[prop]

    for ii in range(rna_props.array_length):
        if not items or ii in items:
            layout.prop(data, prop, index=ii, text='')


def draw_prop_split(layout, flow='row', align=True, text='', sep=3.5):
    main = layout.row(align=align)
    main.use_property_split = False

    split = main.split(factor=0.4, align=align)
    row = split.row()
    col = row.column(align=align)
    col.alignment = 'RIGHT'
    col.label(text=text)
    if layout.use_property_decorate:
        main.separator(factor=sep)
    return split.row(align=align) if flow == 'row' else split.column(align=align)


def draw_op_anim_header(layout, data, field):
    op = layout.operator('m3.edit_anim_header', text='', icon='PREFERENCES')
    op.prop_id_name = data.id_data.name
    op.prop_path = data.path_from_id()
    op.prop_name = field


def draw_op_anim_prop(layout, data, field, index=-1, draw_op=True):
    row = layout.row(align=True)
    if draw_op:
        draw_op_anim_header(row, data, field)
    else:
        row.separator(factor=3.6)
    col = row.column(align=True)

    rna_props = data.bl_rna.properties[field]
    if rna_props.array_length and rna_props.subtype != 'COLOR' and index == -1:
        for ii in range(rna_props.array_length):
            col.prop(data, field, index=ii, text='')
    else:
        col.prop(data, field, index=index, text='')

    return col


def draw_var_props(layout, data, field, text=''):
    row = draw_prop_split(layout, text=text)
    sub = row.row(align=True)
    sub.ui_units_x = 70
    sub.prop(data, field + '_var_shape', text='')
    sub = row.row(align=True)
    sub.active = getattr(data, field + '_var_shape') != 'NONE'
    sub.ui_units_x = 80
    draw_op_anim_prop(sub, data, field + '_var_amplitude')
    draw_op_anim_prop(sub, data, field + '_var_frequency')


def draw_prop_anim(layout, data, field, index=-1, style='col', split=True, text=''):
    main = layout.row(align=True)
    main.use_property_split = False

    rna_props = data.bl_rna.properties[field]

    vec_name_items = None
    if rna_props.array_length and rna_props.subtype != 'COLOR' and index == -1:
        vec_name_items = 'XYZ'

    if layout.use_property_split:
        if split:
            split = main.split(factor=0.4, align=True)
            row = split.row(align=True)
        else:
            split = main.row(align=True)
        if vec_name_items and style == 'col':
            col = row.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text=(text or rna_props.name or field) + ' ' + vec_name_items[0])
            for ii in range(1, rna_props.array_length):
                col.label(text=vec_name_items[ii])
        else:
            row.alignment = 'RIGHT'
            row.label(text=text or rna_props.name or field)

        row = split.row(align=True)
    else:
        row = main

    if index < 1:
        draw_op_anim_header(row, data, field)
    else:
        row.separator(factor=3.6)

    sub = row.row(align=True) if style == 'row' else row.column(align=True)
    sub.use_property_decorate = False
    if vec_name_items:
        for ii in range(max(1, rna_props.array_length)):
            sub.prop(data, field, index=ii, text='' if layout.use_property_split else text)
    else:
        sub.prop(data, field, index=index, text='' if layout.use_property_split else text)

    if layout.use_property_split and layout.use_property_decorate:
        row = main.row()
        row.prop_decorator(data, field, index=index)


def draw_volume_props(volume, layout):
    col = layout.column(align=True)
    col.prop(volume, 'shape', text='Shape Type')
    if volume.shape == 'CUBE':
        row = draw_prop_split(col, text='Size')
        draw_prop_items(row, volume, 'size')
    elif volume.shape == 'SPHERE':
        col.prop(volume, 'size', index=0, text='Radius')
    elif volume.shape in ['CAPSULE', 'CYLINDER']:
        row = draw_prop_split(col, text='Radius/Height')
        draw_prop_items(row, volume, 'size', (0, 1))
    elif volume.shape == 'MESH':
        col.prop(volume, 'mesh_object', text='Mesh Object')
    layout.separator()
    draw_prop_items(draw_prop_split(layout, text='Location'), volume, 'location')
    layout.separator()
    draw_prop_items(draw_prop_split(layout, text='Rotation'), volume, 'rotation')
    layout.separator()
    draw_prop_items(draw_prop_split(layout, text='Scale'), volume, 'scale')


def draw_gen_op_add(layout, collection_path, index):
    op = layout.operator('m3.collection_add', icon='ADD', text='')
    op.collection, op.index = collection_path, index


def draw_gen_op_del(layout, collection_path, index):
    op = layout.operator('m3.collection_remove', icon='REMOVE', text='')
    op.collection, op.index = collection_path, index


def draw_gen_op_mov(layout, collection_path, index):
    op = layout.operator('m3.collection_move', icon='TRIA_UP', text='')
    op.collection, op.index, op.shift = collection_path, index, -1
    op = layout.operator('m3.collection_move', icon='TRIA_DOWN', text='')
    op.collection, op.index, op.shift = collection_path, index, 1


def draw_collection_list(layout, collection, draw_func, ui_list_id='', menu_id='', ops={}, label=''):
    ob = collection.id_data
    collection_path = collection.path_from_id()
    index = ob.path_resolve(collection_path + '_index')
    rows = 5 if len(collection) else 3

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

    row.template_list(ui_list_id or 'UI_UL_list', list_str, list_obj, list_str, list_obj, list_str + '_index', rows=rows)
    col = row.column(align=True)

    try:
        ops['add'](col)
    except KeyError:
        draw_gen_op_add(col, collection_path, index)

    try:
        ops['del'](col)
    except KeyError:
        draw_gen_op_del(col, collection_path, index)

    if menu_id:
        col.separator(factor=1.666)
        col.menu(menu_id, icon='DOWNARROW_HLT', text='')

    if len(collection):
        col.separator(factor=1.666)
        try:
            ops['mov'](col)
        except KeyError:
            draw_gen_op_mov(col, collection_path, index)

    if not len(collection):
        return

    item_ii = sorted((-1, index, len(collection) - 1))[1]

    if item_ii >= 0:
        item = collection[item_ii]
        if item and draw_func:
            col = layout.column()
            col.use_property_split = True
            draw_func(item, col)


def remove_m3_action_keyframes(ob, prefix, index):
    update_actions = {ob.m3_animations_default} if ob.m3_animations_default else {}

    for anim_group in ob.m3_animation_groups:
        for anim in anim_group.animations:
            if anim.action:
                update_actions.add(anim.action)

    for action in update_actions:
        path = f'{prefix}[{index}]'
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            action.fcurves.remove(fcurve)


def shift_m3_action_keyframes(ob, prefix, index, offset=-1):
    update_actions = {ob.m3_animations_default} if ob.m3_animations_default else {}

    for anim_group in ob.m3_animation_groups:
        for anim in anim_group.animations:
            if anim.action:
                update_actions.add(anim.action)

    for action in update_actions:
        path = f'{prefix}[{index}]'
        for fcurve in [fcurve for fcurve in action.fcurves if prefix in fcurve.data_path and path in fcurve.data_path]:
            fcurve.data_path = fcurve.data_path.replace(path, f'{prefix}[{index + offset}]')


def swap_m3_action_keyframes(ob, prefix, old, new):

    update_actions = {ob.m3_animations_default} if ob.m3_animations_default else {}

    for anim_group in ob.m3_animation_groups:
        for anim in anim_group.animations:
            if anim.action:
                update_actions.add(anim.action)

    for action in update_actions:
        path = f'{prefix}[{old}]'
        path_new = f'{prefix}[{new}]'

        fcurves = [fcurve for fcurve in action.fcurves if path in fcurve.data_path]
        fcurves_new = [fcurve for fcurve in action.fcurves if path_new in fcurve.data_path]

        for fcurve in fcurves:
            fcurve.data_path = fcurve.data_path.replace(path, path_new)

        for fcurve in fcurves_new:
            fcurve.data_path = fcurve.data_path.replace(path_new, path)


classes = (
    M3BonePointerProp,
    M3BonePointerPropExclusive,
    M3MatRefPointerProp,
    M3BonePointerList,
    M3AnimHeaderProp,
    M3PropertyGroup,
    M3VolumePropertyGroup,
    M3ObjectPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3CollectionOpDuplicate,
    M3HandleListOpAdd,
    M3HandleListOpRemove,
    M3EditAnimHeader,
    M3PropHandleUnlink,
    M3PropHandleSearch,
)
