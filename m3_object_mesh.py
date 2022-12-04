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


desc_mesh_export = 'The mesh will be exported to m3. If disabled, this object may still be used as a volume'


def register_props():
    bpy.types.Object.m3_mesh_material_refs = bpy.props.CollectionProperty(type=shared.M3PropertyGroup)
    bpy.types.Object.m3_mesh_export = bpy.props.BoolProperty(options=set(), default=True, description=desc_mesh_export)


class SignOpSelect(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_select'
    bl_label = 'Select verts'
    bl_description = 'Selects the assigned verts of the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for vert in bm.verts:
                vert.select = True if vert[group] else vert.select

            bm.select_flush(True)

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpSet(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_set'
    bl_label = 'Set verts'
    bl_description = 'Sets the selected verts to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for vert in bm.verts:
                vert[group] = 1 if vert.select else 0

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpAdd(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_add'
    bl_label = 'Add verts'
    bl_description = 'Adds the selected verts to the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for vert in bm.verts:
                vert[group] = 1 if vert.select else vert[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpRemove(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_remove'
    bl_label = 'Remove verts'
    bl_description = 'Removes the selected verts from the sign inversion group'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for vert in bm.verts:
                vert[group] = 0 if vert.select else vert[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class SignOpInvert(bpy.types.Operator):
    bl_idname = 'm3.vertex_sign_invert'
    bl_label = 'Invert verts'
    bl_description = 'Inverts the value of the sign inversion group for the selected verts.'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_vertex_sign(bm)
            for vert in bm.verts:
                vert[group] = (1 if vert[group] == 0 else 0) if vert.select else vert[group]

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def bm_layer_vertex_sign(bm):
    return bm.verts.layers.int.get('m3sign') or bm.verts.layers.int.new('m3sign')


class ClothSimOpSelect(bpy.types.Operator):
    bl_idname = 'm3.cloth_sim_select'
    bl_label = 'Select vertices'
    bl_description = 'Selects the assigned vertices of the cloth simulation'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_cloth_sim(bm)
            for vert in bm.verts:
                vert.select = True if vert[group] else vert.select

            bm.select_flush(True)

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class ClothSimOpSet(bpy.types.Operator):
    bl_idname = 'm3.cloth_sim_set'
    bl_label = 'Set vertices'
    bl_description = 'Sets the selected vertices to the cloth simulation'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        for ob in context.selected_objects:
            if ob.type != 'MESH':
                continue

            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            group = bm_layer_cloth_sim(bm)
            for vert in bm.verts:
                vert[group] = 1 if vert.select else 0

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


def bm_layer_cloth_sim(bm):
    return bm.verts.layers.int.get('m3clothsim') or bm.verts.layers.int.new('m3clothsim')


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
        layout.use_property_split = True
        ob = context.object
        parent = ob.parent if ob.parent.type == 'ARMATURE' else None

        layout.prop(ob, 'm3_mesh_export', text='Export To M3')

        if parent:
            box = layout.box()
            box.use_property_decorate = False
            op = box.operator('m3.handle_add', text='Add Material Reference')
            op.collection = ob.m3_mesh_material_refs.path_from_id()
            for ii, matref in enumerate(ob.m3_mesh_material_refs):
                row = box.row()
                shared.draw_pointer_prop(row, parent.m3_materialrefs, matref, 'bl_handle', icon='MATERIAL')
                op = row.operator('m3.handle_remove', text='', icon='X')
                op.collection = ob.m3_mesh_material_refs.path_from_id()
                op.index = ii

        if ob.mode == 'EDIT':
            layout.separator()
            layout.label(text='M3 Vertex Normal Sign:')
            layout.operator('m3.vertex_sign_select', text='Select')
            col = layout.column_flow(columns=2)
            col.operator('m3.vertex_sign_set', text='Set To Selected')
            col.operator('m3.vertex_sign_invert', text='Invert Selected')
            col.operator('m3.vertex_sign_add', text='Add Selected')
            col.operator('m3.vertex_sign_remove', text='Remove Selected')

        mesh_cloth = None
        if parent:
            for cloth in parent.m3_cloths:
                if ob == cloth.simulator_object:
                    mesh_cloth = cloth
                    break

        if mesh_cloth and ob.mode == 'EDIT':
            layout.separator()
            layout.label(text='M3 Cloth Simulation Flag:')
            row = layout.row()
            row.operator('m3.cloth_sim_select', text='Select')
            row.operator('m3.cloth_sim_set', text='Set To Selected')


classes = (
    Panel,
    SignOpSelect,
    SignOpSet,
    SignOpAdd,
    SignOpRemove,
    SignOpInvert,
    ClothSimOpSelect,
    ClothSimOpSet,
)
