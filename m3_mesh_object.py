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
import bmesh
from . import shared


class SignOpSet(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_set'
    bl_label = 'Set faces'
    bl_description = 'Sets the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = m3_get_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 1 if face.select else 0

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpSelect(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_select'
    bl_label = 'Select faces'
    bl_description = 'Selects the assigned faces of the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = m3_get_vertex_sign(bm)
            for face in bm.faces:
                face.select = True if face[group] else face.select

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpAdd(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_add'
    bl_label = 'Add faces'
    bl_description = 'Adds the selected faces to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = m3_get_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 1 if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpRemove(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_remove'
    bl_label = 'Remove faces'
    bl_description = 'Removes the selected faces from the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = m3_get_vertex_sign(bm)
            for face in bm.faces:
                face[group] = 0 if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpInvert(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_invert'
    bl_label = 'Invert faces'
    bl_description = 'Inverts the value of the sign inversion group for the selected faces.'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = m3_get_vertex_sign(bm)
            for face in bm.faces:
                face[group] = (1 if face[group] == 0 else 0) if face.select else face[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def m3_get_vertex_sign(bm):
    return bm.faces.layers.int.get('m3sign') or bm.faces.layers.int.new('m3sign')


class Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_GENERAL'
    bl_label = 'M3 Properties'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_mode = 'edit'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        ob = context.object

        col = layout.column()
        col.label(text='M3 Material:')
        row = col.row(align=True)
        row.use_property_split = False
        pointer_ob = shared.m3_pointer_get(ob.parent, 'm3_materialrefs', ob.m3_material_ref, prop_resolved=True)
        op = row.operator('m3.proppointer_search', text='' if pointer_ob else 'Select', icon='VIEWZOOM')
        op.ob_name = ob.name
        op.search_ob_name = ob.parent.name if ob.parent else ''
        op.prop = 'm3_material_ref'
        op.search_prop = 'm3_materialrefs'
        if pointer_ob:
            row.prop(pointer_ob, 'name', text='', icon='MATERIAL')
            op = row.operator('m3.proppointer_unlink', text='', icon='X')
            op.prop = 'm3_material_ref'

        if ob.mode == 'EDIT':
            layout.separator()
            col = layout.column()
            col.label(text='M3 Vertex Normal Sign:')
            col.operator('m3.vertex_sign_select', text='Select')
            col = layout.column_flow(columns=2)
            col.operator('m3.vertex_sign_set', text='Set To Selected')
            col.operator('m3.vertex_sign_invert', text='Invert Selected')
            col.operator('m3.vertex_sign_add', text='Add Selected')
            col.operator('m3.vertex_sign_remove', text='Remove Selected')


classes = (
    Panel,
    SignOpSet,
    SignOpSelect,
    SignOpAdd,
    SignOpRemove,
    SignOpInvert,
)
