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

"""Action API differences between Blender versions.

Blender 5.0 removed the legacy ``Action.fcurves``. F-Curves now live in a channelbag
that belongs to one of the action's slots. Assigning an action to an ID also no longer
binds a slot by itself unless the slot's identifier matches, so its animation would
silently not play. M3Studio's actions each animate a single armature object, so each
one gets a single OBJECT slot, and every assignment binds it.
"""

import bpy

LEGACY_ACTIONS = 'fcurves' in bpy.types.Action.bl_rna.properties

SLOT_NAME = 'M3'


def action_slot(action):
    """The action's slot for M3Studio's armature, created if the action has none."""
    for slot in action.slots:
        if slot.target_id_type == 'OBJECT':
            return slot
    return action.slots.new('OBJECT', SLOT_NAME)


def action_fcurves(action):
    """The F-Curve collection of @p action: ``find``, ``new``, ``remove`` and iteration
    behave the same on every Blender version (``new`` group argument: see fcurve_new)."""
    if LEGACY_ACTIONS:
        return action.fcurves
    from bpy_extras import anim_utils
    return anim_utils.action_ensure_channelbag_for_slot(action, action_slot(action)).fcurves


def fcurve_new(fcurves, data_path, index=0, group=''):
    """``fcurves.new`` with an F-Curve group: the keyword is ``action_group`` on legacy
    actions and ``group_name`` on channelbags."""
    if LEGACY_ACTIONS:
        return fcurves.new(data_path, index=index, action_group=group)
    return fcurves.new(data_path, index=index, group_name=group)


def action_assign(anim_data, action):
    """Assign @p action to @p anim_data and bind the action's slot."""
    anim_data.action = action
    if action is not None and not LEGACY_ACTIONS:
        anim_data.action_slot = action_slot(action)
