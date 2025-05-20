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
- Animation group names should only contain words from a specific dictionary. This dictionary is defined in the `bl_enum.py` file.
- Actions are referenced, but are not automatically generated when a new sub-animation is added to a group. Take care to create new actions rather than referencing an action from multiple sub-animations unless this is strictly intended.

#### M3 Material Layers
- Lists the M3 material layers that are defined for the M3 model.
- Material layers define the texture mappings or colors of materials.
- Material layers can be referenced by multiple materials.

#### M3 Materials
- Lists the M3 materials of the M3 model. The material type is displayed on the right side of each list item.
- Layer slots are listed, with the option to assign an existing layer, create a new one, or duplicate the layer currently in the slot, if applicable.
- Materials are assigned to meshes via the M3 Properties panel when a mesh object is selected.

#### M3 Attachment Points
- Lists the attachment points of the M3 model.
- Attachment points are used in the game to position effect models such as weapon launches or impacts.
- Attachment point names must be picked from a dictionary, and should be unique from each other.
- The Volume sub list allows definition of areas, generally used by Target and Shield attachments. It is recommended to only ever have 1 volume defined in this list for a given attachment point.

#### M3 Hit Test Volumes
- Contains the definition for the model's tight hit test volume, and lists the model's fuzzy hit test volumes.
- "Tight" hit test volume determines the area by which an in-game unit can be selected via operations such as drag select or screen wide select.
- "Fuzzy" hit test volumes determine which areas the mouse must hover over to allow a click based selection. If no fuzzy hit test volumes are defined, the entire unit model is used for click hit testing.
- NOTE: Do not use the "Cylinder" volume shape for hit test volumes. While technically allowed by the game renderer, they will not function properly in-game.

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
- A list of bone names to be enlisted by the engine as billboards.
- The given bones are aligned to the camera based on the type of alignment assiged.
- Intended for elements where you want a consistent appearance from varying model angles and/or camera perspectives.

#### M3 Turrets
- TODO

#### M3 Cameras
- TODO

#### M3 Cloths
- TODO

#### M3 Cloth Constraint Sets
- TODO

#### M3 Inverse Kinematics
- A list of bone names, which are the target bones of engine driven inverse kinematics. 
- The target bone should be parented to the end point of a chain of bones which you wish to have procedurally transformed, so that the end is positioned on the terrain. (Such as Collosus legs while cliff walking.)
- The "Joint Length" property should match the number of bones in the chain which you wish to be affected by the repositioning of the target bone.

#### M3 Vertex Warpers
- Lists the vertex warpers of the M3 model.
- An experimental feature that was used exclusively for the Mothership Black Hole spell, where the mesh of units in the area are distorted based on proximity to the center. This visual effect applies only to the model of units with a behavior that enables the "Warpable" Modify Flag.

#### M3 Shadow Boxes
- Lists the shadow boxes of the M3 model.
- Niche feature that affects how shadows are rendered on screen. When visible, shadows are rendered only in the box's defined area, and at a relatively higher quality. There should probably only be one shadow box in a given scene.
<br><br>

## Advanced Topic Explainers

### Data Structure Versions
- TODO

### Bind Scale
- Bind scale is an M3 specific property that exists on bones, and is accessible in the M3 Properties panel of the Bone Properties tab, or in the Item tab of the Context Menu while in Pose mode.
- Affects the scaling of M3 defined elements such as attachment/hit test volumes, particles, ribbons, etc.
- The scaling factor is applied as a denominator, rather than as a multiplier. `0.5` means twice as large, `2.0` means half as large.
- When applied to attachment points that are used as turrets, it also influences the scale of any mesh which is weighted to a bone that is parented to the attachment point's bone.

### Animation Headers
- All M3 properties which can be animated have an animation header.
- Animation headers have 3 components:
  - `Animation ID`: An essentially random integer, represented as a hex string. Must be unique from all other IDs within the model
  - `Interpolation`: Can be set to `Linear`, `Constant` or `Automatic`. `Automatic` is converted to `Linear` or `Constant` when exported, according to convention for a given property.
  - `Flags`: The functionality of this field is unknown
- Animation headers should have an exact match between an M3 file and any M3A file applied to the model.
- In the case you need to change an animation header ID, set the ID value to an empty string and a new random integer will be assigned.
- To access animation IDs for bones, use the "Edit M3 Animation Headers" button in the Bone Properties tab, or in the Item tab of the Context Menu while in Pose mode.
