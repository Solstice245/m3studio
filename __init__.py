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

# from timeit import timeit
import bpy
from bpy.app.handlers import persistent
from . import shared
from . import m3_bone
from . import m3_vertex_groups
from . import m3_options
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
# from . import m3_import

bl_info = {
    'name': 'M3: Used by Blizzard\'s StarCraft 2 and Heroes of the Storm',
    'author': 'Solstice245',
    'version': (0, 1, 0),
    'blender': (3, 0, 0),
    'location': 'Properties Editor -> Object Data -> M3 Panels',
    'description': 'Allows to export and import models in M3 format.',
    'category': 'Import-Export',
    'doc_url': 'https://github.com/Solstice245/m3studio/blob/master/README.md',
    'tracker_url': 'https://github.com/Solstice245/m3studio/issues',
}


class M3ScenePanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_ScenePanel'
    bl_label = 'M3 Scene Panel'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout

        layout.operator('m3.import')


class M3ImportOperator(bpy.types.Operator):
    bl_idname = 'm3.import'
    bl_label = 'Import M3'
    bl_options = {'UNDO'}

    filename_ext = '.m3'
    filter_glob: bpy.props.StringProperty(options={'HIDDEN'}, default='*.m3;*.m3a')
    filepath: bpy.props.StringProperty(name='File Path', description='File path for import operation', maxlen=1023, default='')

    test_missile = 'C:\\Users\\John Wharton\\Documents\\_Base Assets\\Effects\\Protoss\\Phalanx Missle\\PhalanxMissile.m3'
    test_goliath = 'C:\\Users\\John Wharton\\Documents\\_Base Assets\\Terran\\Units\\Goliath\\Goliath.m3'
    test_vertexalpha = 'C:\\Users\\John Wharton\\Documents\\_Base Assets\\Protoss\\Effects\\Mothership_Taldarim_Shield.m3'

    def invoke(self, context, event):
        # print(timeit(lambda: m3_import.M3Import(self.test_goliath), number=1))
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # print(timeit(lambda: m3_import.M3Import(self.test_goliath), number=1))
        return {'FINISHED'}


def top_bar_import(self, context):
    self.layout.operator('m3.import', text='StarCraft 2 Model/Animation (.m3/.m3a)')


def top_bar_export(self, context):
    self.layout.operator('m3.import', text='StarCraft 2 Model (.m3)')


m3_modules = (
    m3_bone,
    m3_options,
    m3_animations,
    m3_materiallayers,
    m3_materials,
    m3_attachmentpoints,
    m3_hittests,
    m3_particles,
    m3_ribbons,
    m3_lights,
    m3_forces,
    m3_rigidbodies,
    m3_physicsjoints,
    m3_turrets,
    m3_projections,
    m3_billboards,
    m3_cameras,
    m3_ik,
    m3_physicscloths,
    m3_warps,
)


def m3_module_classes():
    classes = []
    for module in m3_modules:
        for clss in module.classes:
            classes.append(clss)
    return classes


classes = (
    *shared.classes,
    *m3_vertex_groups.classes,
    *m3_module_classes(),
    M3ImportOperator,
    M3ScenePanel,
)


@persistent
def init_msgbus(*args):
    for arm in [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']:
        for module in m3_modules:
            if module.init_msgbus:
                module.init_msgbus(arm, bpy.context)


def register():
    for clss in classes:
        bpy.utils.register_class(clss)
    for module in m3_modules:
        module.register_props()
    bpy.types.TOPBAR_MT_file_import.append(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.append(top_bar_export)
    bpy.app.handlers.load_post.append(init_msgbus)


def unregister():
    for clss in reversed(classes):
        bpy.utils.unregister_class(clss)
    bpy.types.TOPBAR_MT_file_import.remove(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.remove(top_bar_export)
    bpy.app.handlers.load_post.remove(init_msgbus)


if __name__ == '__main__':
    register()
