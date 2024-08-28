## m3studio - Blender addon for StarCraft 2 Model File Input/Output
Created by [_John Wharton_](https://github.com/Solstice245) (aka. Solstice245), with credits to the contributors of [_m3addon_](https://github.com/SC2Mapster/m3addon) for making this project possible.

## Usage
This addon adds the following operations to Blender:

#### File > Import > StarCraft 2 Model (.m3, .m3a)
- Imports the selected .m3 file into your scene. An armature is created to represent the root of the model, and to contain all of the M3 specific data for the model.
- Meshes are parented to the armature. Then they can reference M3 materials which are defined by the parent armature.
- While importing, you can select an existing armature to import M3 data and mesh objects into, rather than creating a new armature. This feature is primarily intended for importing `.m3a` data into an `.m3` model.
#### File > Export > StarCraft 2 Model (.m3, .m3a)
- Requires that there be an active or selected armature object.
- The data inside the armature defines the properties of the `.m3` or `.m3a` file. Only mesh objects parented to the armature will be exported as the mesh data of the `.m3` file.
- Includes an option to disable the export of animation data to the `.m3` file. (This option is overriden in the case of exporting `.m3a`.)
<br><br>

This addon adds the following panels to the __Object__ tab of the properties editor for *__armature objects__*:

#### M3 Import/Export
- Contains the same import/export operators as the main import/export operators, as well as model specific export settings.
- Import will default the `Armature Object` property to the selected armature.
- Export will default to the last file export location of the specific M3 model, rather than the last export operation in general.
- Versions of various M3 data structures can be configured here. More information on this can be found in the _Advanced Topic Explainers_ section.

#### M3 Object Options
- Contains various flags for the purpose of adjusting the workflow in the Blender interface.

#### M3 Bounds
- Contains properties relating to the bounding box of the M3 model. Includes a preview toggle.

#### M3 Animation Groups
- Lists the animation groups of the M3 model. Each animation group should have at least one sub-animation, which can each be assigned an action.
- Action group names must only contain words from a specific dictionary. This dictionary is defined in the `bl_enum.py` file.
- Actions are referenced, but are not automatically generated when a new sub-animation is added to the list. Take care to create new actions rather than referencing an action from multiple sub-animations unless this is strictly intended.

#### M3 Material Layers
- Lists the M3 material layers that are defined for the M3 model.
- Material layers define the texture mappings or colors of materials.
- Material layers can be referenced by multiple materials.

#### M3 Materials
- Lists the M3 materials of the M3 model. The material type is listed on the right side of each item.
- Layer slots are listed, with the option to assign an existing layer, create a new one, or duplicate the layer currently in the slot, if applicable.
- Materials are assigned to meshes via the M3 Properties panel when a mesh object is selected.

#### M3 Attachment Points
- Lists the attachment points of the M3 model.
- Attachment points are used in the game to position effect models such as weapon launches or impacts.
- Attachment point names must be picked from a dictionary, and should be unique from each other.
- The Volume sub list allows definition of areas, generally used by Target and Shield attachments. It is recommended to only ever have 1 volume defined in this list for a given attachment point.

#### M3 Hit Test Volumes
- TODO

#### M3 Particle Systems
- TODO

#### M3 Particle Copies
- TODO

#### M3 Ribbons
- TODO

#### M3 Ribbon Splines
- TODO

#### M3 Projections
- TODO

#### M3 Lights
- TODO

#### M3 Forces
- TODO

#### M3 Physics Shapes
- TODO

#### M3 Physics Rigid Bodies
- TODO

#### M3 Physics Joints
- TODO

#### M3 Billboards
- TODO

#### M3 Turrets
- TODO

#### M3 Cameras
- TODO

#### M3 Cloths
- TODO

#### M3 Cloth COnstraint Sets
- TODO

#### M3 Inverse Kinematics
- TODO

#### M3 Vertex Warpers
- TODO

#### M3 Shadow Boxes
- TODO

#### M3 TMD Data
- TODO
<br><br>

## Advanced Topic Explainers

### Data Structure Versions
- TODO

### Animation Headers
- All M3 properties which can be animated have an animation header.
- Animation headers have 3 components:
  - `Animation ID`: An essentially random integer, represented as a hex string. Must be unique from all other IDs within the model
  - `Interpolation`: Can be set to `Linear`, `Constant` or `Automatic`. `Automatic` is converted to `Linear` or `Constant` when exported, according to convention for a given property.
  - `Flags`: The functionality of this field is unknown
- Animation headers should have an exact match between an M3 file and any M3A file applied to the model.
- In the case you need to change an animation header ID, set the ID value to an empty string and a new random integer will be assigned.
- To access animation IDs for bones, use the "Edit M3 Animation Headers" button in the Bone tab of the properties editor, or in the Item tab of the Context Menu while in Pose mode.
