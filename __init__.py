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
from . import shared
from . import m3_bone
from . import m3_object_armature
from . import m3_object_mesh
from . import m3_animations
from . import m3_attachmentpoints
from . import m3_billboards
from . import m3_cameras
from . import m3_forces
from . import m3_hittests
from . import m3_ik
from . import m3_lights
from . import m3_materiallayers
from . import m3_materials
from . import m3_particles
from . import m3_physicscloths
from . import m3_physicsjoints
from . import m3_projections
from . import m3_ribbons
from . import m3_rigidbodies
from . import m3_turrets
from . import m3_warps
from . import m3_shadowboxes
from . import m3_tmd
from . import io_m3_import
from . import io_m3_export
from . import bl_graphics_draw

bl_info = {
    'name': 'M3: Used by Blizzard\'s StarCraft 2 and Heroes of the Storm',
    'author': 'Solstice245',
    'version': (0, 1, 0),
    'blender': (3, 0, 0),
    'location': 'Properties Editor -> Object Data -> M3 Panels',
    'description': 'Allows import and export of models in the M3 format.',
    'category': 'Import-Export',
    'doc_url': 'https://github.com/Solstice245/m3studio/blob/master/README.md',
    'tracker_url': 'https://github.com/Solstice245/m3studio/issues',
}


def m3_import_id_names(self, context):
    yield '(New Object)', '(New Object)', 'Creates a new object to hold the imported M3 data.'
    for ob in bpy.data.objects:
        if ob.type == 'ARMATURE':
            yield ob.name, ob.name, 'Imports the M3 data into the selected object. Note that various data such as animations will not be imported.'


class M3ImportOperator(bpy.types.Operator):
    '''Load an M3 file into a new armature or an existing armature'''
    bl_idname = 'm3.import'
    bl_label = 'Import M3'
    bl_options = {'UNDO'}

    filename_ext = '.m3'
    filter_glob: bpy.props.StringProperty(options={'HIDDEN'}, default='*.m3;*.m3a')
    filepath: bpy.props.StringProperty(name='File Path', description='File path for import operation', maxlen=1023, default='')
    id_name: bpy.props.EnumProperty(items=m3_import_id_names, name='Armature Object', description='The armature object to add m3 data into. Select an existing armature object to import m3 data directly into it')

    get_mesh: bpy.props.BoolProperty(default=True, name='Mesh Data', description='Imports mesh data and their associated materials. Applies only to m3 (not m3a) import')
    get_effects: bpy.props.BoolProperty(default=False, name='Effects', description='Imports effect data, such as particle systems or ribbons, and their associated materials. Applies only to m3 (not m3a) import')
    get_rig: bpy.props.BoolProperty(default=False, name='Rig', description='Imports bones and various bone related data. (Attachment points, hit test volumes, etc.) Applies only to m3 (not m3a) import')
    get_anims: bpy.props.BoolProperty(default=False, name='Animations', description='Imports animation data. Applies only to m3 (not m3a) import')

    def draw(self, context):
        layout = self.layout
        layout.label(text='Armature Object')
        layout.prop(self, 'id_name', text='')
        if self.id_name != '(New Object)':
            layout.separator()
            layout.label(text='Import Options')
            col = layout.column()
            col.prop(self, 'get_rig')
            row = col.row()
            row.active = self.get_rig
            row.prop(self, 'get_anims')
            col.prop(self, 'get_mesh')
            col.prop(self, 'get_effects')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        opts = (self.get_rig, self.get_anims, self.get_mesh, self.get_effects)
        io_m3_import.m3_import(filename=self.filepath, ob=bpy.data.objects.get(self.id_name), bl_op=self, opts=opts)
        return {'FINISHED'}


class M3ExportOperator(bpy.types.Operator):
    '''Saves an M3 file from an armature'''
    bl_idname = 'm3.export'
    bl_label = 'Export M3'

    filename_ext = '.m3'
    filter_glob: bpy.props.StringProperty(options={'HIDDEN'}, default='*.m3;*.m3a')
    filepath: bpy.props.StringProperty(name='File Path', description='File path for export operation', maxlen=1023, default='')

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def invoke(self, context, event):
        if context.active_object.m3_filepath_export:
            self.filepath = context.active_object.m3_filepath_export
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        io_m3_export.m3_export(ob=context.active_object, filename=self.filepath, bl_op=self)
        context.active_object.m3_filepath_export = self.filepath
        return {'FINISHED'}


def top_bar_import(self, context):
    self.layout.operator('m3.import', text='StarCraft 2 Model (.m3)')


def top_bar_export(self, context):
    col = self.layout.column()
    if not context.object or (context.object and context.object.type != 'ARMATURE'):
        col.active = False
    col.operator('m3.export', text='StarCraft 2 Model (.m3)')


m3_modules = (
    m3_bone,
    m3_object_armature,
    m3_object_mesh,
    m3_animations,
    m3_materiallayers,
    m3_materials,
    m3_attachmentpoints,
    m3_hittests,
    m3_particles,
    m3_ribbons,
    m3_projections,
    m3_lights,
    m3_forces,
    m3_rigidbodies,
    m3_physicsjoints,
    m3_billboards,
    m3_turrets,
    m3_cameras,
    m3_physicscloths,
    m3_ik,
    m3_warps,
    m3_shadowboxes,
    m3_tmd,
)


def m3_module_classes():
    classes = []
    for module in m3_modules:
        for clss in module.classes:
            classes.append(clss)
    return classes


classes = (
    *shared.classes,
    *m3_module_classes(),
    M3ImportOperator,
    M3ExportOperator,
)


def register():
    global M3_SHADER
    for clss in classes:
        bpy.utils.register_class(clss)
    for module in m3_modules:
        module.register_props()
    bpy.types.TOPBAR_MT_file_import.append(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.append(top_bar_export)
    M3_SHADER = bpy.types.SpaceView3D.draw_handler_add(bl_graphics_draw.draw, (), 'WINDOW', 'POST_VIEW')

    # populate search list for attachment point name
    bpy.app.handlers.load_post.append(m3_attachmentpoints.attachment_name_list_verify)
    # for backwards compatibility with the names of attachment points from previous importer versions
    bpy.app.handlers.load_post.append(m3_attachmentpoints.attachmentpoint_names_fix)


def unregister():
    global M3_SHADER
    for clss in reversed(classes):
        bpy.utils.unregister_class(clss)
    bpy.types.TOPBAR_MT_file_import.remove(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.remove(top_bar_export)
    bpy.types.SpaceView3D.draw_handler_remove(M3_SHADER, 'WINDOW')


if __name__ == '__main__':
    register()
