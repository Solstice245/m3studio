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
desc_mesh_uv = 'Specifies the exact UV map that should be used on the given M3 UV layer slot. Leave blank for automatic UV map selection'


def register_props():
    bpy.types.Object.m3_mesh_batches = bpy.props.CollectionProperty(type=BatchPropertyGroup)
    bpy.types.Object.m3_mesh_export = bpy.props.BoolProperty(options=set(), default=True, description=desc_mesh_export)
    bpy.types.Object.m3_mesh_uv0 = bpy.props.StringProperty(options=set(), description=desc_mesh_uv)
    bpy.types.Object.m3_mesh_uv1 = bpy.props.StringProperty(options=set(), description=desc_mesh_uv)
    bpy.types.Object.m3_mesh_uv2 = bpy.props.StringProperty(options=set(), description=desc_mesh_uv)
    bpy.types.Object.m3_mesh_uv3 = bpy.props.StringProperty(options=set(), description=desc_mesh_uv)


class BatchPropertyGroup(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(type=shared.M3MatRefPointerProp)
    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)


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
        if not context.object:
            return False
        if not context.object.type == 'MESH':
            return False
        if not context.object.parent:
            return False
        if not context.object.parent.type == 'ARMATURE':
            return False
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        ob = context.object
        parent = ob.parent if ob.parent and ob.parent.type == 'ARMATURE' else None

        layout.prop(ob, 'm3_mesh_export', text='Export To M3')

        if parent:
            box = layout.box()
            box.use_property_decorate = False
            op = box.operator('m3.handle_add', text='Add M3 Material Batch')
            op.collection = ob.m3_mesh_batches.path_from_id()

            for ii, batch in enumerate(ob.m3_mesh_batches):
                row = box.row()
                col = row.column()
                shared.draw_prop_pointer_search(col, batch.material, parent, 'm3_materialrefs', text='Material', icon='MATERIAL')
                shared.draw_prop_pointer_search(col, batch.bone, parent.data, 'bones', text='Batching Toggle', icon='BONE_DATA')
                op = row.operator('m3.handle_remove', text='', icon='X')
                op.collection = ob.m3_mesh_batches.path_from_id()
                op.index = ii

        box = layout.box()
        box.label(text='Custom M3 UV Mapping')
        box.prop(ob, 'm3_mesh_uv0', text='UV Layer 0')
        box.prop(ob, 'm3_mesh_uv1', text='UV Layer 1')
        box.prop(ob, 'm3_mesh_uv2', text='UV Layer 2')
        box.prop(ob, 'm3_mesh_uv3', text='UV Layer 3')

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
    BatchPropertyGroup,
    Panel,
    ClothSimOpSelect,
    ClothSimOpSet,
)
