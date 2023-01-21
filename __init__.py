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
    id_name: bpy.props.EnumProperty(items=m3_import_id_names, name='Armature Object')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        io_m3_import.m3_import(self.filepath, bpy.data.objects.get(self.id_name))
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
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        io_m3_export.m3_export(context.active_object, self.filepath)
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


def unregister():
    global M3_SHADER
    for clss in reversed(classes):
        bpy.utils.unregister_class(clss)
    bpy.types.TOPBAR_MT_file_import.remove(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.remove(top_bar_export)
    bpy.types.SpaceView3D.draw_handler_remove(M3_SHADER, 'WINDOW')


if __name__ == '__main__':
    register()
