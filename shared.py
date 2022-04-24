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
from . import mesh_gen


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


def m3_item_find_name(collections=[], suggested_names=[], prefix=''):
    used_names = [item.name for item in collection for collection in collections]
    num = 1
    while True:
        for name in [name for name in suggested_names if name not in used_names]:
            return name

        name = prefix + ' 0' + str(num) if num < 10 else str(num)

        if name not in used_names:
            return name

        num += 1


def m3_item_new(collection):
    item = collection.add()
    item.bl_display = True
    item.bl_handle = '%064x' % random.getrandbits(256)
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


def m3_get_bone_handle(bone):
    bone.m3.handle = bone.m3.handle if bone.m3.handle else '%064x' % random.getrandbits(256)
    return bone.m3.handle


def m3_get_handle_bone(bones, handle):
    if not handle:
        return None
    for bone in bones:
        if bone.m3.handle == handle:
            return bone
    return None


def m3_msgbus_callback(self, context, sub, key, owner):
    self.bl_update = False
    setattr(self, owner, getattr(sub, key))
    self.bl_update = True


def m3_msgbus_sub(self, context, sub, key, owner):
    if sub:
        bpy.msgbus.subscribe_rna(
            key=sub.path_resolve(key, False),
            owner=self.bl_handle + owner,
            args=(self, context, sub, key, owner),
            notify=m3_msgbus_callback,
            options={'PERSISTENT'}
        )


def bone_update(self, context, prop):
    if not self.bl_update:
        return

    set_bone_shape(context.object, m3_get_handle_bone(context.object.data.bones, getattr(self, prop + '_handle')))
    bone = context.object.data.bones.get(getattr(self, prop))
    setattr(self, prop + '_handle', m3_get_bone_handle(bone))
    set_bone_shape(context.object, bone)

    bpy.msgbus.clear_by_owner(self.bl_handle + prop)
    m3_msgbus_sub(self, context, bone, 'name', prop)


def bone_update_event(self, context):
    bone_update(self, context, 'bone')


def bone1_update_event(self, context):
    bone_update(self, context, 'bone1')


def bone2_update_event(self, context):
    bone_update(self, context, 'bone2')


def bone_shape_update_event(self, context):
    bone = context.object.data.bones.get(self.bone)
    set_bone_shape(context.object, bone)


def bone1_shape_update_event(self, context):
    bone = context.object.data.bones.get(self.bone1)
    set_bone_shape(context.object, bone)


def bone2_shape_update_event(self, context):
    bone = context.object.data.bones.get(self.bone2)
    set_bone_shape(context.object, bone)


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
    bone_handle: bpy.props.StringProperty(options=set())


class M3VolumePropertyGroup(M3BoneUserPropertyGroup):
    shape: bpy.props.EnumProperty(options=set(), items=bl_enum.volume_shape, update=bone_shape_update_event)
    size: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)
    location: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, update=bone_shape_update_event)
    rotation: bpy.props.FloatVectorProperty(options=set(), subtype='EULER', unit='ROTATION', size=3, update=bone_shape_update_event)
    scale: bpy.props.FloatVectorProperty(options=set(), subtype='XYZ', size=3, min=0, default=(1, 1, 1), update=bone_shape_update_event)


class M3CollectionOpBase(bpy.types.Operator):
    bl_idname = 'm3.collection_base'
    bl_label = 'Base Collection Operator'
    bl_options = {'UNDO'}

    collection: bpy.props.StringProperty(default='m3_generics')
    index: bpy.props.IntProperty()
    shift: bpy.props.IntProperty()
    set_name: bpy.props.BoolProperty(default=False)


class M3CollectionOpAdd(M3CollectionOpBase):
    bl_idname = 'm3.collection_add'
    bl_label = 'Add Collection Item'
    bl_description = 'Adds a new item to the collection'

    def invoke(self, context, event):
        collection = m3_ob_getter(self.collection)
        item = m3_item_new(collection)

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

        m3_item_duplicate(collection, collection[self.index])

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


def draw_collection_list(layout, collection_path, draw_func, can_duplicate=True):
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
    if can_duplicate:
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

    col = layout.column()
    col.use_property_split = True
    col.prop(item, 'name', text='Identifier')

    draw_bone_prop(item, bpy.context.object, col)
    draw_func(item, col)


def draw_collection_stack(layout, collection_path, label, draw_func, use_name=False, can_duplicate=True):
    collection = m3_ob_getter(collection_path)

    box = layout.box()
    op = box.operator('m3.collection_add', text='Add ' + label)
    op.collection = collection_path

    if len(collection):
        for index, item in enumerate(collection):

            row = box.row(align=True)
            col = row.column(align=True)

            if not item.bl_display:
                toggle_label = '"{}"'.format(item.name) if use_name else label
                op = col.operator('m3.collection_displaytoggle', icon='TRIA_RIGHT', text='Toggle ' + toggle_label + ' Display')
                op.collection, op.index = (collection_path, index)
            else:
                op = col.operator('m3.collection_displaytoggle', icon='TRIA_DOWN', text='')
                op.collection, op.index = (collection_path, index)
                col = row.column()
                if use_name:
                    col.prop(item, 'name', text='Name')
                draw_bone_prop(item, bpy.context.object, col)
                draw_func(item, col)

            col = row.column(align=True)
            op = col.operator('m3.collection_remove', icon='X', text='')
            op.collection, op.index = (collection_path, index)

            if item.bl_display:
                if can_duplicate:
                    col.separator()
                    op = col.operator('m3.collection_duplicate', icon='DUPLICATE', text='')
                    op.collection, op.index = (collection_path, index)
                col.separator()
                op = col.operator('m3.collection_move', icon='TRIA_UP', text='')
                op.collection, op.index, op.shift = (collection_path, index, -1)
                op = col.operator('m3.collection_move', icon='TRIA_DOWN', text='')
                op.collection, op.index, op.shift = (collection_path, index, 1)


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


def set_bone_shape(ob, bone):
    if not bone:
        return

    data = [[], [], []]
    pose_bone = ob.pose.bones.get(bone.name)

    def add_mesh_data(prop, new_data, matrix=None):

        if ob.data.bones.get(prop) != bone:
            return

        # TODO Apply matrix to new_data before appending to src_data

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
            add_mesh_data(point.bone, mesh_gen.attachment_point())
            for volume in point.volumes:
                if volume.shape == 'CUBE':
                    add_mesh_data(volume.bone, mesh_gen.cube(volume.size))
                elif volume.shape == 'SPHERE':
                    add_mesh_data(volume.bone, mesh_gen.sphere(volume.size[0]))
                elif volume.shape == 'CAPSULE':
                    add_mesh_data(volume.bone, mesh_gen.capsule(volume.size, volume.size[0]))

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
        for particle in ob.m3_particles:

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
                if shape.shape == 'CUBE':
                    add_mesh_data(rigid_body.bone, mesh_gen.cube(shape.size))
                elif shape.shape == 'SPHERE':
                    add_mesh_data(rigid_body.bone, mesh_gen.sphere(shape.size[0]))
                elif shape.shape == 'CAPSULE':
                    add_mesh_data(rigid_body.bone, mesh_gen.capsule(shape.size, shape.size[0]))
                elif shape.shape == 'CYLINDER':
                    add_mesh_data(rigid_body.bone, mesh_gen.cylinder(shape.size, shape.size[0]))
                elif shape.shape == 'CONVEXHULL' or shape.shape == 'MESH':
                    pass  # TODO

    elif ob.m3_options.bone_shapes == 'FTHT':
        if ob.m3_tighthittest.shape == 'CUBE':
            add_mesh_data(ob.m3_tighthittest.bone, mesh_gen.cube(ob.m3_tighthittest.size))
        elif ob.m3_tighthittest.shape == 'SPHERE':
            add_mesh_data(ob.m3_tighthittest.bone, mesh_gen.sphere(ob.m3_tighthittest.size[0]))
        elif ob.m3_tighthittest.shape == 'CYLINDER':
            add_mesh_data(ob.m3_tighthittest.bone, mesh_gen.cylinder(hittest.size, hittest.size[0]))
        for hittest in ob.m3_hittests:
            if hittest.shape == 'CUBE':
                add_mesh_data(hittest.bone, mesh_gen.cube(hittest.size))
            elif hittest.shape == 'SPHERE':
                add_mesh_data(hittest.bone, mesh_gen.sphere(hittest.size[0]))
            elif hittest.shape == 'CYLINDER':
                add_mesh_data(hittest.bone, mesh_gen.cylinder(hittest.size, hittest.size[0]))

    elif ob.m3_options.bone_shapes == 'WRP_':
        for warp in ob.m3_warps:
            add_mesh_data(warp.bone, sphere(warp.radius))

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
    M3VolumePropertyGroup,
    M3BoneUserPropertyGroup,
    M3CollectionOpBase,
    M3CollectionOpAdd,
    M3CollectionOpRemove,
    M3CollectionOpMove,
    M3CollectionOpDuplicate,
    M3CollectionOpDisplayToggle,
}
