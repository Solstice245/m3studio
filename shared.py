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
from . import bl_enum
from . import mesh_gen


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
        obj = m3_ob_getter(rsp[0], obj=obj)
        if obj is not None:
            setattr(obj, rsp[1], value)
    else:
        setattr(obj, rsp[0], value)


def m3_item_get_name(collection_name, prefix='', obj=None):
    collection = m3_ob_getter(collection_name, obj=obj)
    suggested_names = m3_collections_suggested_names.get(collection_name)
    used_names = {item.name for item in collection}

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


def m3_item_add(collection_name, item_name='', obj=None):
    collection = m3_ob_getter(collection_name, obj=obj)
    item = collection.add()
    item.bl_display = True
    item.bl_handle = m3_handle_gen()
    item.bl_index = len(collection) - 1
    item.name = m3_item_get_name(collection_name, item_name, obj=obj)
    return item


def m3_item_duplicate(collection_name, src, obj=None):
    collection = m3_ob_getter(collection_name, obj=obj)
    dst = m3_item_add(collection_name, obj=obj)

    if (type(dst) != type(src)):
        collection.remove(len(collection) - 1)
        return None

    for key in type(dst).__annotations__.keys():
        prop = getattr(src, key)
        if str(type(prop)) != '<class \'bpy_prop_collection_idprop\'>':
            setattr(dst, key, prop)
        else:
            for item in prop:
                m3_item_duplicate(key, item, obj=dst)

    dst.name = ''
    dst.name = m3_item_get_name(collection_name, src.name, obj=obj)

    return dst


def m3_item_find_bones(item):
    bone_list = []

    if hasattr(item, 'bone'):
        bone_list.append(getattr(item, 'bone'))

    if hasattr(item, 'bone1'):
        bone_list.append(getattr(item, 'bone1'))

    if hasattr(item, 'bone2'):
        bone_list.append(getattr(item, 'bone2'))

    for key in type(item).__annotations__.keys():
        prop = getattr(item, key)
        if str(type(prop)) == '<class \'bpy_prop_collection_idprop\'>':
            for sub_item in prop:
                bone_list += m3_item_find_bones(sub_item)

    return bone_list


def m3_pointer_get(ob, search_prop, prop_name, prop_resolved=False):
    prop = m3_ob_getter(prop_name, obj=ob) if not prop_resolved else prop_name
    if not prop or not ob:
        return None
    data = m3_ob_getter(search_prop, obj=ob)
    for item in data:
        if item.bl_handle == prop:
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


def bone_shape_update_event(self, context):
    set_bone_shape(context.object, m3_pointer_get(context.object, 'data.bones', self.bone, True))


def bone1_shape_update_event(self, context):
    set_bone_shape(context.object, m3_pointer_get(context.object, 'data.bones', self.bone1, True))


def bone2_shape_update_event(self, context):
    set_bone_shape(context.object, m3_pointer_get(context.object, 'data.bones', self.bone2, True))


def select_bones_handles(ob, bl_handles):
    if ob.m3_options.auto_select_bones:
        for bone in ob.data.bones:
            bone.select = bone.bl_handle in bl_handles
            bone.select_tail = bone.select
            if bone.bl_handle == bl_handles[0]:
                ob.data.bones.active = bone


def auto_update_bone_shapes(ob, setting):
    if ob.m3_options.auto_update_bone_shapes:
        if ob.m3_options.bone_shapes != setting:
            ob.m3_options.bone_shapes = setting


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
    bl_index: bpy.props.IntProperty(options=set())
    bl_handle: bpy.props.StringProperty(options=set())
    name: bpy.props.StringProperty(options=set())


class M3HandlePropertyGroup(bpy.types.PropertyGroup):
    handle: bpy.props.StringProperty(options=set())


class M3BoneUserPropertyGroup(M3PropertyGroup):
    bone: bpy.props.StringProperty(options=set())


class M3VolumePropertyGroup(M3BoneUserPropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape, update=bone_shape_update_event)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, update=bone_shape_update_event)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, update=bone_shape_update_event)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)
    mesh_object: bpy.props.PointerProperty(type=bpy.types.Object, update=bone_shape_update_event)


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
        item = m3_item_add(self.collection)

        m3_ob_setter(self.collection + '_index', item.bl_index)

        return {'FINISHED'}


class M3CollectionOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.collection_remove'
    bl_label = 'Remove Collection Item'
    bl_description = 'Removes the active item from the collection'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)

        if self.index not in range(len(collection)):
            return {'FINISHED'}

        bone_list = m3_item_find_bones(collection[self.index])
        collection.remove(self.index)

        remove_m3_action_keyframes(context.object, self.collection, self.index)
        for ii in range(self.index, len(collection)):
            collection[ii].bl_index -= 1
            shift_m3_action_keyframes(context.object, self.collection, ii + 1)

        m3_ob_setter(self.collection + '_index', self.index - (1 if self.index == len(collection) else 0))

        for bone in context.object.data.bones:
            if bone.bl_handle in bone_list:
                set_bone_shape(context.object, bone)

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
            swap_m3_action_keyframes(context.object, self.collection, self.index, self.index + self.shift)
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

        m3_item_duplicate(self.collection, collection[self.index])

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


class M3HandleOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.handle_add'
    bl_label = 'Add Handle To List'
    bl_description = 'Adds a new item to the li'

    def invoke(self, context, event):
        m3_item_add(self.collection)
        return {'FINISHED'}


class M3HandleOpRemove(M3CollectionOpBase):
    bl_idname = 'm3.handle_remove'
    bl_label = 'Remove Handle From List'
    bl_description = 'Removes the item from the collection'

    index: bpy.props.IntProperty(options=set())

    def invoke(self, context, event):
        m3_ob_getter(self.collection).remove(self.index)
        return {'FINISHED'}


def m3_prop_pointer_enum(self, context):
    search_ob = bpy.data.objects.get(self.search_ob_name if self.search_ob_name else self.ob_name)
    for item in m3_ob_getter(self.search_prop, obj=search_ob):
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
            m3_bone_handles_verify(context.object)
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ob = bpy.data.objects.get(self.ob_name)
        search_ob = bpy.data.objects.get(self.search_ob_name) if self.search_ob_name else ob

        is_bone_search_prop = self.search_prop in ['data.bones', 'data.edit_bones']

        if is_bone_search_prop:
            bone_before = m3_pointer_get(search_ob, 'data.bones', self.prop)

        m3_ob_setter(self.prop, self.enum, obj=ob)

        if is_bone_search_prop:
            bone_after = m3_pointer_get(search_ob, 'data.bones', self.prop)
            set_bone_shape(search_ob, bone_before)
            set_bone_shape(search_ob, bone_after)

        return {'FINISHED'}


class M3PropPointerOpUnlink(bpy.types.Operator):
    bl_idname = 'm3.proppointer_unlink'
    bl_label = 'Unlink'
    bl_description = 'Removes the pointer to this object from the m3 property'

    prop: bpy.props.StringProperty()

    def invoke(self, context, event):
        is_bone_search_prop = hasattr(context.object.data, 'bones')
        if is_bone_search_prop:
            bone = m3_pointer_get(context.object, 'data.bones', self.prop)
        m3_ob_setter(self.prop, '')
        if is_bone_search_prop:
            set_bone_shape(context.object, bone)
        return {'FINISHED'}


# TODO Make it so that handle list items must be unique
def draw_handle_list(ob, layout, search_prop, collection_name, prop_label=''):
    op = layout.operator('m3.handle_add', text=('Add ' + prop_label) if prop_label else None)
    op.collection = collection_name
    for ii, item in enumerate(m3_ob_getter(collection_name)):
        draw_handle_list_item(bpy.context.object, layout, ii, search_prop, collection_name, prop_label)


def draw_handle_list_item(ob, layout, index, search_prop, collection_name, prop_label=''):

    pointer_ob = m3_pointer_get(ob, search_prop, '{}[{}].handle'.format(collection_name, index))

    row = layout.row(align=True)
    row.use_property_split = False
    op = row.operator('m3.proppointer_search', text=pointer_ob.name if pointer_ob else 'Select ' + prop_label, icon='VIEWZOOM')
    op.prop = '{}[{}].handle'.format(collection_name, index)
    op.search_prop = search_prop
    op = row.operator('m3.handle_remove', text='', icon='X')
    op.collection = collection_name
    op.index = index


def draw_pointer_prop(ob, layout, search_prop, prop_name, prop_label='', icon=''):

    if m3_ob_getter(prop_name, obj=ob) is None:
        return

    if search_prop == 'data.bones' and ob.mode == 'EDIT':
        search_prop = 'data.edit_bones'

    pointer_ob = m3_pointer_get(ob, search_prop, prop_name)

    main = layout.row(align=True)
    main.use_property_split = False

    if prop_label:
        split = main.split(factor=0.4)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text=prop_label)
        row = split.row(align=True)
    else:
        row = main
    op = row.operator('m3.proppointer_search', text='' if pointer_ob else 'Select', icon='VIEWZOOM')
    op.prop = prop_name
    op.search_prop = search_prop

    if pointer_ob:
        if icon:
            row.prop(pointer_ob, 'name', text='', icon=icon)
        else:
            row.prop(pointer_ob, 'name', text='')
        op = row.operator('m3.proppointer_unlink', text='', icon='X')
        op.prop = prop_name

    if layout.use_property_split and layout.use_property_decorate:
        row = main.row()
        row.alignment = 'RIGHT'
        row.separator(factor=3.6)


def draw_volume_props(volume, layout):
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


def draw_collection_list(layout, collection_path, draw_func, can_duplicate=True, ops=[], label=''):
    collection = m3_ob_getter(collection_path)
    index = m3_ob_getter(collection_path + '_index')
    rows = 5 if len(collection) else 3

    if not ops:
        ops = ['m3.collection_add', 'm3.collection_remove', 'm3.collection_move', 'm3.collection_duplicate']

    rsp = collection_path.rsplit('.', 1)
    if len(rsp) == 1:
        list_str = collection_path
        list_obj = bpy.context.object
    else:
        list_str = rsp[1]
        list_obj = m3_ob_getter(rsp[0])

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

    item = collection[sorted((0, index, len(collection) - 1))[1]]

    col = layout.column()
    col.use_property_split = True
    draw_pointer_prop(bpy.context.object, col, 'data.bones', '{}[{}].{}'.format(collection_path, index, 'bone'), 'Bone', 'BONE_DATA')
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


def set_bone_shape(ob, bone):
    if not bone:
        return

    data = [[], [], []]
    pose_bone = ob.pose.bones.get(bone.name)

    def add_mesh_data(prop, new_data, matrix=None):

        if not prop or bone.bl_handle != prop:
            return

        if str(type(new_data)) == '<class \'bpy_types.Mesh\'>':
            me = new_data
            new_data = [[vert.co for vert in me.vertices], [], [poly.vertices for poly in me.polygons]]
            for ii, v in enumerate(new_data[0]):
                angle = math.pi / 2
                x = (math.cos(angle) * v[0]) - (math.sin(angle) * v[1])
                y = (math.sin(angle) * v[0]) + (math.cos(angle) * v[1])
                z = v[2]
                new_data[0][ii] = (x, y, z)

        if matrix:
            loc, rot, scl = matrix
            for ii, v in enumerate(new_data[0]):
                x, y, z = v

                x *= scl[0]
                y *= scl[1]
                z *= scl[2]

                y0 = (math.cos(rot[0]) * y) - (math.sin(rot[0]) * z)
                z0 = (math.sin(rot[0]) * y) + (math.cos(rot[0]) * z)
                x, y, z = x, y0, z0
                x0 = (math.sin(rot[1]) * z) + (math.cos(rot[1]) * x)
                z0 = (math.cos(rot[1]) * z) - (math.sin(rot[1]) * x)
                x, y, z = x0, y, z0
                x0 = (math.cos(rot[2]) * x) - (math.sin(rot[2]) * y)
                y0 = (math.sin(rot[2]) * x) + (math.cos(rot[2]) * y)
                x, y, z = x0, y0, z

                x += loc[0]
                y += loc[1]
                z += loc[2]

                new_data[0][ii] = (x, y, z)

        for ii in new_data[2]:
            new_face = []
            for jj in ii:
                new_face.append(jj + len(data[0]))
            data[2].append(new_face)

        for ii in new_data[1]:
            data[1].append((ii[0] + len(data[0]), ii[1] + len(data[0])))

        data[0] += new_data[0]

    if ob.m3_options.bone_shapes == 'ATT_':
        for point in ob.m3_attachmentpoints:
            add_mesh_data(point.bone, mesh_gen.point())
            for volume in point.volumes:
                mat = (volume.location, volume.rotation, volume.scale)
                if volume.shape == 'CUBE':
                    add_mesh_data(volume.bone, mesh_gen.cube(volume.size), mat)
                elif volume.shape == 'SPHERE':
                    add_mesh_data(volume.bone, mesh_gen.sphere(volume.size[0]), mat)
                elif volume.shape == 'CAPSULE':
                    add_mesh_data(volume.bone, mesh_gen.capsule(volume.size, volume.size[0]), mat)
                elif volume.shape == 'MESH' and volume.mesh_object:
                    add_mesh_data(volume.bone, volume.mesh_object.data, mat)

    elif ob.m3_options.bone_shapes == 'CAM_':
        for camera in ob.m3_cameras:
            add_mesh_data(camera.bone, mesh_gen.camera(0.5, camera.focal_depth))

    elif ob.m3_options.bone_shapes == 'LITE':
        for light in ob.m3_lights:
            if light.shape == 'POINT':
                add_mesh_data(light.bone, mesh_gen.sphere(light.attenuation_far))
            elif light.shape == 'SPOT':
                add_mesh_data(light.bone, mesh_gen.cone(light.falloff, light.attenuation_far))

    elif ob.m3_options.bone_shapes == 'FOR_':
        for force in ob.m3_forces:
            if force.shape == 'CUBE':
                add_mesh_data(force.bone, mesh_gen.cube(force.size))
            elif force.shape == 'CYLINDER':
                add_mesh_data(force.bone, mesh_gen.cylinder(force.size, force.size[0]))
            elif force.shape == 'SPHERE':
                add_mesh_data(force.bone, mesh_gen.sphere(force.size[0]))
            elif force.shape == 'HEMISPHERE':
                add_mesh_data(force.bone, mesh_gen.hemisphere(force.size[0]))
            elif force.shape == 'CONEDOME':
                add_mesh_data(force.bone, mesh_gen.cone_dome(force.size[1], force.size[0]))

    elif ob.m3_options.bone_shapes == 'PAR_':
        for particle in ob.m3_particle_systems:

            mesh_gen_data = [[], [], []]
            mesh_gen_data_cutout = [[], [], []]

            if particle.emit_shape == 'POINT':
                mesh_gen_data = mesh_gen.point()
            elif particle.emit_shape == 'PLANE':
                mesh_gen_data = mesh_gen.plane(particle.emit_shape_size)
                if particle.emit_shape_cutout:
                    mesh_gen_data_cutout = mesh_gen.plane(particle.emit_shape_size_cutout)
            elif particle.emit_shape == 'CUBE':
                mesh_gen_data = mesh_gen.cube(particle.emit_shape_size)
                if particle.emit_shape_cutout:
                    mesh_gen_data_cutout = mesh_gen.cube(particle.emit_shape_size_cutout)
            elif particle.emit_shape == 'DISC':
                mesh_gen_data = mesh_gen.disc(particle.emit_shape_radius)
                if particle.emit_shape_cutout:
                    mesh_gen_data_cutout = mesh_gen.disc(particle.emit_shape_radius_cutout)
            elif particle.emit_shape == 'CYLINDER':
                mesh_gen_data = mesh_gen.cylinder(particle.emit_shape_size, particle.emit_shape_radius)
                if particle.emit_shape_cutout:
                    mesh_gen_data_cutout = mesh_gen.cylinder(particle.emit_shape_size_cutout, particle.emit_shape_radius_cutout)
            elif particle.emit_shape == 'SPHERE':
                mesh_gen_data = mesh_gen.sphere(particle.emit_shape_radius)
                if particle.emit_shape_cutout:
                    mesh_gen_data_cutout = mesh_gen.sphere(particle.emit_shape_radius_cutout)

            add_mesh_data(particle.bone, mesh_gen_data)
            if particle.emit_shape_cutout:
                add_mesh_data(particle.bone, mesh_gen_data_cutout)

            for copy in particle.copies:
                add_mesh_data(copy.bone, mesh_gen_data)
                if particle.emit_shape_cutout:
                    add_mesh_data(copy.bone, mesh_gen_data_cutout)

    elif ob.m3_options.bone_shapes == 'PHRB':
        for rigid_body in ob.m3_rigidbodies:
            for shape in rigid_body.shapes:
                mat = (shape.location, shape.rotation, shape.scale)
                if shape.shape == 'CUBE':
                    add_mesh_data(rigid_body.bone, mesh_gen.cube(shape.size), mat)
                elif shape.shape == 'SPHERE':
                    add_mesh_data(rigid_body.bone, mesh_gen.sphere(shape.size[0]), mat)
                elif shape.shape == 'CAPSULE':
                    add_mesh_data(rigid_body.bone, mesh_gen.capsule(shape.size, shape.size[0]), mat)
                elif shape.shape == 'CYLINDER':
                    add_mesh_data(rigid_body.bone, mesh_gen.cylinder(shape.size, shape.size[0]), mat)
                elif (shape.shape == 'CONVEXHULL' or shape.shape == 'MESH') and shape.mesh_object:
                    add_mesh_data(volume.bone, volume.mesh_object.data, mat)

    elif ob.m3_options.bone_shapes == 'FTHT':
        mat = (ob.m3_hittest_tight.location, ob.m3_hittest_tight.rotation, ob.m3_hittest_tight.scale)
        if ob.m3_hittest_tight.shape == 'CUBE':
            add_mesh_data(ob.m3_hittest_tight.bone, mesh_gen.cube(ob.m3_hittest_tight.size), mat)
        elif ob.m3_hittest_tight.shape == 'SPHERE':
            add_mesh_data(ob.m3_hittest_tight.bone, mesh_gen.sphere(ob.m3_hittest_tight.size[0]), mat)
        elif ob.m3_hittest_tight.shape == 'CYLINDER':
            add_mesh_data(ob.m3_hittest_tight.bone, mesh_gen.cylinder(hittest.size, hittest.size[0]), mat)
        elif ob.m3_hittest_tight.shape == 'MESH' and ob.m3_hittest_tight.mesh_object:
            add_mesh_data(ob.m3_hittest_tight.bone, ob.m3_hittest_tight.mesh_object.data, mat)
        for hittest in ob.m3_hittests:
            mat = (hittest.location, hittest.rotation, hittest.scale)
            if hittest.shape == 'CUBE':
                add_mesh_data(hittest.bone, mesh_gen.cube(hittest.size), mat)
            elif hittest.shape == 'SPHERE':
                add_mesh_data(hittest.bone, mesh_gen.sphere(hittest.size[0]), mat)
            elif hittest.shape == 'CYLINDER':
                add_mesh_data(hittest.bone, mesh_gen.cylinder(hittest.size, hittest.size[0]), mat)
            elif hittest.shape == 'MESH' and hittest.mesh_object:
                add_mesh_data(hittest.bone, hittest.mesh_object.data, mat)

    elif ob.m3_options.bone_shapes == 'PHCL':
        for cloth in ob.m3_cloths:
            pass  # TODO
            # for constraint in cloth.constraints:
            #     add_mesh_data(constraint.bone, mesh_gen.capsule((0, constraint.height, 0), constraint.radius))

    elif ob.m3_options.bone_shapes == 'WRP_':
        for warp in ob.m3_warps:
            add_mesh_data(warp.bone, mesh_gen.sphere(warp.radius))

    if pose_bone:

        if data[0]:
            bone_mesh_name = bone.name + '_display_helper'
            if bone_mesh_name in bpy.data.meshes:
                bpy.data.meshes.remove(bpy.data.meshes[bone_mesh_name])

            me = bpy.data.meshes.new(bone_mesh_name)
            helper_ob = pose_bone.custom_shape or bpy.data.objects.new(bone_mesh_name, me)
            helper_ob.data = me

            me.from_pydata(data[0], data[1], data[2])
            me.update(calc_edges=True)

            pose_bone.custom_shape = helper_ob
            pose_bone.use_custom_shape_bone_size = False
            bone.show_wire = True
        else:
            pose_bone.custom_shape = None
            pose_bone.use_custom_shape_bone_size = True
            bone.show_wire = False


classes = {
    M3PropertyGroup,
    M3HandlePropertyGroup,
    M3VolumePropertyGroup,
    M3BoneUserPropertyGroup,
    M3ObjectPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3CollectionOpDuplicate,
    M3CollectionOpDisplayToggle,
    M3HandleOpAdd,
    M3HandleOpRemove,
    M3PropPointerOpUnlink,
    M3PropPointerOpSearch,
}
