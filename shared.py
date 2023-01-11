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
import math
import mathutils
from . import bl_enum
from . import bl_mesh_gen


m3_collections_suggested_names = {
    'm3_animations': ['Stand_full', 'Walk_full', 'Attack_full', 'Birth_full', 'Spell_full'],
    'm3_animation_groups': ['Stand', 'Walk', 'Attack', 'Birth', 'Spell'],
    'm3_attachmentpoints': ['Origin', 'Center', 'Overhead', 'Target'],
    'm3_billboards': ['Billboard'],
    'm3_cameras': ['CameraPortrait', 'CameraAvatar', 'Camera'],
    'm3_forces': ['Force'],
    'm3_fuzzyhittests': ['Fuzzy Hit Test'],
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
    'm3_turrets': ['Turret'],
    'm3_warps': ['Warp'],
}


def m3_handle_gen():
    return '%064x' % random.getrandbits(256)


def m3_item_get_name(collection, prefix=''):
    # TODO restore name suggestion functionality
    suggested_names = None  # m3_collections_suggested_names.get(collection_name)
    used_names = {item.name for item in collection}

    if prefix not in used_names:
        return prefix

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


def m3_item_duplicate(collection, src):
    dst = m3_item_add(collection)

    if (type(dst) != type(src)):
        collection.remove(len(collection) - 1)
        return None

    for key in type(dst).__annotations__.keys():
        prop = getattr(src, key)
        if str(type(prop)) != '<class \'bpy_prop_collection_idprop\'>':
            setattr(dst, key, prop)
        else:
            for item in prop:
                m3_item_duplicate(prop, item)

    dst.name = ''
    dst.name = m3_item_get_name(collection, src.name)

    return dst


def m3_item_find_bones(item):
    bone_list = []

    if hasattr(item, 'bone'):
        bone_list.append(getattr(item, 'bone'))

    if hasattr(item, 'bone1'):
        bone_list.append(getattr(item, 'bone1'))

    if hasattr(item, 'bone2'):
        bone_list.append(getattr(item, 'bone2'))

    if hasattr(type(item), '__annotations__'):
        for key in type(item).__annotations__.keys():
            prop = getattr(item, key)
            if str(type(prop)) == '<class \'bpy_prop_collection_idprop\'>':
                for sub_item in prop:
                    bone_list += m3_item_find_bones(sub_item)

    return bone_list


def m3_collection_index_set(bl, value):
    ob = bl.id_data
    rsp = bl.path_from_id().rsplit('.', 1)
    if len(rsp) == 1:
        setattr(ob, rsp[0] + '_index', value)
    else:
        setattr(ob.path_resolve(rsp[0]), rsp[1] + '_index', value)


def bl_resolved_set(ob, bl, value):
    rsp = bl.rsplit('.', 1)
    if len(rsp) == 1:
        setattr(ob, rsp[0], value)
    else:
        setattr(ob.path_resolve(rsp[0]), rsp[1], value)


def m3_pointer_get(search_data, handle):
    if not handle:
        return None
    for item in search_data:
        if item.bl_handle == handle:
            return item
    return None


def m3_bone_handles_verify(ob):
    handles = set()
    for bone in ob.data.edit_bones if ob.mode == 'EDIT' else ob.data.bones:
        if not bone.bl_handle or bone.bl_handle in handles:
            bone.bl_handle = m3_handle_gen()
        handles.add(bone.bl_handle)


def m3_msgbus_callback(self, sub, key, owner):
    setattr(self, owner, getattr(sub, key))


def m3_msgbus_sub(self, sub, key, owner):
    bpy.msgbus.subscribe_rna(
        key=sub.path_resolve(key, False),
        owner=self.bl_handle + owner,
        args=(self, sub, key, owner),
        notify=m3_msgbus_callback,
        options={'PERSISTENT'}
    )


def select_bones_handles(ob, bl_handles):
    if ob.m3_options.auto_update_bone_selection and bl_handles:
        for bone in ob.data.bones:
            bone.select = bone.bl_handle in bl_handles
            bone.select_tail = bone.select
            if bone.bl_handle == bl_handles[0]:
                ob.data.bones.active = bone


# TODO rework this system
def auto_update_bone_display_mode(ob, setting):
    if ob.m3_options.auto_update_bone_display_mode:
        if ob.m3_options.bone_display_mode != setting:
            ob.m3_options.bone_display_mode = setting


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

        bone_list = m3_item_find_bones(collection[self.index])
        collection.remove(self.index)

        remove_m3_action_keyframes(context.object, self.collection, self.index)
        for ii in range(self.index, len(collection)):
            shift_m3_action_keyframes(context.object, self.collection, ii + 1)

        m3_collection_index_set(collection, self.index - (1 if self.index == len(collection) else 0))

        for bone in context.object.data.bones:
            if bone.bl_handle in bone_list:
                set_bone_shape(context.object, bone)

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

    def invoke(self, context, event):
        collection = context.object.path_resolve(self.collection)

        if self.index == -1:
            return {'FINISHED'}

        m3_item_duplicate(collection, collection[self.index])
        m3_collection_index_set(collection, len(collection) - 1)

        return {'FINISHED'}


class M3HandleOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.handle_add'
    bl_label = 'Add Item To List'
    bl_description = 'Adds a new item to the list'

    def invoke(self, context, event):
        m3_item_add(context.object.path_resolve(self.collection))
        return {'FINISHED'}


class M3HandleOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.handle_remove'
    bl_label = 'Remove Item From List'
    bl_description = 'Removes the item from the list'

    index: bpy.props.IntProperty(options=set())

    def invoke(self, context, event):
        context.object.path_resolve(self.collection).remove(self.index)
        return {'FINISHED'}


def m3_prop_pointer_enum(self, context):
    search_ob = bpy.data.objects.get(self.search_ob_name if self.search_ob_name else self.ob_name) or bpy.context.object
    for item in search_ob.path_resolve(self.search_prop):
        yield item.bl_handle, item.name, ''


class M3PropPointerOpSearch(bpy.types.Operator):
    bl_idname = 'm3.proppointer_search'
    bl_label = 'Search'
    bl_description = 'Search for an object to point to for the m3 property'
    bl_property = 'enum'

    ob_name: bpy.props.StringProperty()
    prop: bpy.props.StringProperty()
    search_ob_name: bpy.props.StringProperty()
    search_prop: bpy.props.StringProperty()
    enum: bpy.props.EnumProperty(items=m3_prop_pointer_enum)

    def invoke(self, context, event):
        if self.search_prop in ['data.bones', 'data.edit_bones']:
            search_ob = bpy.data.objects.get(self.search_ob_name) if self.search_ob_name else context.object
            m3_bone_handles_verify(search_ob)
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ob = bpy.data.objects.get(self.ob_name) or bpy.context.object
        search_ob = bpy.data.objects.get(self.search_ob_name) if self.search_ob_name else ob

        is_bone_search_prop = self.search_prop in ['data.bones', 'data.edit_bones']

        if is_bone_search_prop:
            bone_before = m3_pointer_get(search_ob.path_resolve(self.search_prop), ob.path_resolve(self.prop))

        bl_resolved_set(ob, self.prop, self.enum)

        if is_bone_search_prop:
            bone_after = m3_pointer_get(search_ob.path_resolve(self.search_prop), ob.path_resolve(self.prop))

            set_bone_shape(search_ob, bone_before)
            set_bone_shape(search_ob, bone_after)

        return {'FINISHED'}


class M3PropPointerOpUnlink(bpy.types.Operator):
    bl_idname = 'm3.proppointer_unlink'
    bl_label = 'Unlink'
    bl_description = 'Removes the pointer to this object from the m3 property'
    bl_options = {'UNDO'}

    prop: bpy.props.StringProperty()

    def invoke(self, context, event):
        ob = context.object
        is_bone_search_prop = hasattr(ob.data, 'bones')
        if is_bone_search_prop:
            bone = m3_pointer_get(ob.data.bones, ob.path_resolve(self.prop))
        bl_resolved_set(ob, self.prop, '')
        if is_bone_search_prop:
            set_bone_shape(ob, bone)
        return {'FINISHED'}


# TODO Make it so that handle list items must be unique
def draw_handle_list(layout, search_data, collection, label=''):
    op = layout.operator('m3.handle_add', text=('Add ' + label) if label else None)
    op.collection = collection.path_from_id()
    for ii, item in enumerate(collection):
        draw_handle_list_item(layout, search_data, collection, label, item, ii)


def draw_handle_list_item(layout, search_data, collection, label, item, index):
    pointer_ob = m3_pointer_get(search_data, item.bl_handle)

    row = layout.row(align=True)
    row.use_property_split = False
    op = row.operator('m3.proppointer_search', text=pointer_ob.name if pointer_ob else 'Select ' + label, icon='VIEWZOOM')
    op.prop = item.path_from_id('bl_handle')
    op.search_prop = search_data.path_from_id()
    op = row.operator('m3.handle_remove', text='', icon='X')
    op.collection = collection.path_from_id()
    op.index = index


def draw_pointer_prop(layout, search_data, data, prop, bone_search=False, label='', icon=''):

    arm = None
    if bone_search:
        arm = search_data.id_data
        search_data = arm.edit_bones if arm.is_editmode else arm.bones

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

    pointer_ob = m3_pointer_get(search_data, getattr(data, prop))

    op = row.operator('m3.proppointer_search', text='' if pointer_ob else 'Select', icon='VIEWZOOM')
    op.prop = data.path_from_id(prop)
    op.search_prop = search_data.path_from_id() if not arm else 'data.' + search_data.path_from_id()
    op.search_ob_name = search_data.id_data.name

    if pointer_ob:
        if icon:
            row.prop(pointer_ob, 'name', text='', icon=icon)
        else:
            row.prop(pointer_ob, 'name', text='')
        op = row.operator('m3.proppointer_unlink', text='', icon='CANCEL')
        op.prop = data.path_from_id(prop)

    if layout.use_property_split and layout.use_property_decorate:
        row = main.row()
        row.alignment = 'RIGHT'
        row.separator(factor=3.6)


def draw_volume_props(volume, layout):
    draw_pointer_prop(layout, volume.id_data.data.bones, volume, 'bone', bone_search=True, label='Bone', icon='BONE_DATA')
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


def draw_collection_list(layout, collection, draw_func, can_duplicate=True, ops=[], label=''):
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
        layout.label(text=label)

    row = layout.row()
    col = row.column()
    col.template_list('UI_UL_list', list_str, list_obj, list_str, list_obj, list_str + '_index', rows=rows)
    col = row.column()
    sub = col.column(align=True)
    op = sub.operator(ops[0], icon='ADD', text='')
    op.collection, op.index = (collection_path, index)
    op = sub.operator(ops[1], icon='REMOVE', text='')
    op.collection, op.index = (collection_path, index)
    if can_duplicate:
        sub.separator()
        op = sub.operator(ops[3], icon='DUPLICATE', text='')
        op.collection, op.index = (collection_path, index)

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


# TODO port all of this to bl_graphics_draw
# def set_bone_shape(ob, bone):
#
#     if ob.m3_options.bone_display_mode == 'PAR_':
#         for particle in ob.m3_particle_systems:
#
#             mesh_gen_data = [[], [], []]
#             mesh_gen_data_cutout = [[], [], []]
#
#             if particle.emit_shape == 'POINT':
#                 mesh_gen_data = bl_mesh_gen.point()
#             elif particle.emit_shape == 'PLANE':
#                 mesh_gen_data = bl_mesh_gen.plane(particle.emit_shape_size)
#                 if particle.emit_shape_cutout:
#                     mesh_gen_data_cutout = bl_mesh_gen.plane(particle.emit_shape_size_cutout)
#             elif particle.emit_shape == 'CUBE':
#                 mesh_gen_data = bl_mesh_gen.cube(particle.emit_shape_size)
#                 if particle.emit_shape_cutout:
#                     mesh_gen_data_cutout = bl_mesh_gen.cube(particle.emit_shape_size_cutout)
#             elif particle.emit_shape == 'DISC':
#                 mesh_gen_data = bl_mesh_gen.disc(particle.emit_shape_radius)
#                 if particle.emit_shape_cutout:
#                     mesh_gen_data_cutout = bl_mesh_gen.disc(particle.emit_shape_radius_cutout)
#             elif particle.emit_shape == 'CYLINDER':
#                 mesh_gen_data = bl_mesh_gen.cylinder(particle.emit_shape_size, particle.emit_shape_radius)
#                 if particle.emit_shape_cutout:
#                     mesh_gen_data_cutout = bl_mesh_gen.cylinder(particle.emit_shape_size_cutout, particle.emit_shape_radius_cutout)
#             elif particle.emit_shape == 'SPHERE':
#                 mesh_gen_data = bl_mesh_gen.sphere(particle.emit_shape_radius)
#                 if particle.emit_shape_cutout:
#                     mesh_gen_data_cutout = bl_mesh_gen.sphere(particle.emit_shape_radius_cutout)
#
#             add_mesh_data(particle.bone, mesh_gen_data)
#             if particle.emit_shape_cutout:
#                 add_mesh_data(particle.bone, mesh_gen_data_cutout)
#
#     elif ob.m3_options.bone_display_mode == 'PHRB':
#         for rigid_body in ob.m3_rigidbodies:
#             shape = m3_pointer_get(ob.m3_physicsshapes, rigid_body.physics_shape)
#             for volume in shape.volumes:
#                 mat = (volume.location, volume.rotation, volume.scale)
#                 if volume.shape == 'CUBE':
#                     add_mesh_data(rigid_body.bone, bl_mesh_gen.cube(volume.size), mat)
#                 elif volume.shape == 'SPHERE':
#                     add_mesh_data(rigid_body.bone, bl_mesh_gen.sphere(volume.size[0]), mat)
#                 elif volume.shape == 'CAPSULE':
#                     add_mesh_data(rigid_body.bone, bl_mesh_gen.capsule(volume.size, volume.size[0]), mat)
#                 elif volume.shape == 'CYLINDER':
#                     add_mesh_data(rigid_body.bone, bl_mesh_gen.cylinder(volume.size, volume.size[0]), mat)
#                 elif (volume.shape == 'CONVEXHULL' or volume.shape == 'MESH') and volume.mesh_object:
#                     add_mesh_data(rigid_body.bone, volume.mesh_object.data, mat)


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
    M3HandleOpAdd,
    M3HandleOpRemove,
    M3PropPointerOpUnlink,
    M3PropPointerOpSearch,
)
