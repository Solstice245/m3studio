#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
from bpy.app.handlers import persistent
from . import shared
from . import m3_bone
from . import m3_vertex_groups
from . import m3_attachmentpoints
from . import m3_billboards
from . import m3_cameras
from . import m3_forces
from . import m3_hittests
from . import m3_ik
from . import m3_lights
from . import m3_particles
from . import m3_physicsjoints
from . import m3_ribbons
from . import m3_rigidbodies
from . import m3_warps
from . import m3_import

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
        m3_import.M3Import(self.test_vertexalpha)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        m3_import.M3Import(self.test_vertexalpha)
        return {'FINISHED'}


def top_bar_import(self, context):
    self.layout.operator('m3.import', text='StarCraft 2 Model/Animation (.m3/.m3a)')


def top_bar_export(self, context):
    self.layout.operator('m3.import', text='StarCraft 2 Model (.m3)')


m3_collection_modules = (
    m3_attachmentpoints,
    m3_billboards,
    m3_cameras,
    m3_forces,
    m3_hittests,
    m3_ik,
    m3_lights,
    m3_particles,
    m3_physicsjoints,
    m3_ribbons,
    m3_rigidbodies,
    m3_warps,
)


def m3_collection_module_classes():
    classes = []
    for collection in m3_collection_modules:
        for cls in collection.classes:
            classes.append(cls)
    return classes


classes = (
    *shared.classes,
    *m3_bone.classes,
    *m3_vertex_groups.classes,
    *m3_collection_module_classes(),
    M3ImportOperator,
    M3ScenePanel,
)


@persistent
def init_msgbus(*args):
    for arm in [ob if ob.type == 'ARMATURE' else None for ob in bpy.context.scene.objects]:
        if arm:
            for collection in m3_collection_modules:
                collection.init_msgbus(arm, bpy.context)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for collection in m3_collection_modules:
        collection.register_props()
    bpy.types.TOPBAR_MT_file_import.append(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.append(top_bar_export)
    bpy.app.handlers.load_post.append(init_msgbus)


def unregister():
    for cls in reversed(classes):
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(top_bar_import)
    bpy.types.TOPBAR_MT_file_export.remove(top_bar_export)


if __name__ == '__main__':
    register()