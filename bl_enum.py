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

options_bone_display = (
    ('NONE', 'None', ''),
    ('ATT_', 'Attachment Points', ''),
    ('SHBX', 'Shadow Boxes', ''),
    ('CAM_', 'Cameras', ''),
    ('FOR_', 'Forces', ''),
    ('FTHT', 'Hit Test Volumes', ''),
    ('LITE', 'Lights', ''),
    ('PAR_', 'Particles', ''),
    ('PROJ', 'Projections', ''),
    ('RIB_', 'Ribbons', ''),
    ('PHRB', 'Physics Rigid Bodies', ''),
    ('PHCL', 'Physics Cloths', ''),
    ('WRP_', 'Vertex Warpers', ''),
)

attachmentpoint_keys = (
    ('None', '(None)', ''),
    ('Air', 'Air', ''),
    ('Alternate', 'Alternate', ''),
    ('Armor', 'Armor', ''),
    ('Attacher', 'Attacher', ''),
    ('Back', 'Back', ''),
    ('Bottom', 'Bottom', ''),
    ('Cargo', 'Cargo', ''),
    ('Center', 'Center', ''),
    ('Channel', 'Channel', ''),
    ('Chest', 'Chest', ''),
    ('Chin', 'Chin', ''),
    ('CustomA', 'Custom A', ''),
    ('CustomB', 'Custom B', ''),
    ('CustomC', 'Custom C', ''),
    ('Damage', 'Damage', ''),
    ('Death', 'Death', ''),
    ('EatTree', 'Eat Tree', ''),
    ('Effector', 'Effector', ''),
    ('Engine', 'Engine', ''),
    ('Face', 'Face', ''),
    ('Final', 'Final', ''),
    ('Foot', 'Foot', ''),
    ('Forearm', 'Forearm', ''),
    ('Front', 'Front', ''),
    ('Ground', 'Ground', ''),
    ('Hand', 'Hand', ''),
    ('Hardpoint', 'Hardpoint', ''),
    ('Head', 'Head', ''),
    ('Heavy', 'Heavy', ''),
    ('Hit', 'Hit', ''),
    ('HitPointBar', 'Hit Point Bar', ''),
    ('Knee', 'Knee', ''),
    ('Left', 'Left', ''),
    ('Light', 'Light', ''),
    ('Lip', 'Lip', ''),
    ('MacGuffin', 'Mac Guffin', ''),
    ('Medium', 'Medium', ''),
    ('Mount', 'Mount', ''),
    ('Movement', 'Movement', ''),
    ('Origin', 'Origin', ''),
    ('Overhead', 'Overhead', ''),
    ('Primary', 'Primary', ''),
    ('RallyPoint', 'Rally Point', ''),
    ('Rear', 'Rear', ''),
    ('Right', 'Right', ''),
    ('Secondary', 'Secondary', ''),
    ('SetA', 'Set A', ''),
    ('SetB', 'Set B', ''),
    ('SetC', 'Set C', ''),
    ('Shield', 'Shield', ''),
    ('Shoulder', 'Shoulder', ''),
    ('StatusBar', 'Status Bar', ''),
    ('Target', 'Target', ''),
    ('TargetShield', 'Target Shield', ''),
    ('Top', 'Top', ''),
    ('Transmission', 'Transmission', ''),
    ('Turret', 'Turret', ''),
    ('TurretY', 'Turret Y', ''),
    ('TurretZ', 'Turret Z', ''),
    ('Upgrade', 'Upgrade', ''),
    ('Upper', 'Upper', ''),
    ('Waist', 'Waist', ''),
    ('Weapon', 'Weapon', ''),
    ('Work', 'Work', ''),
)

world_forces = (
    (0, 'Wind'),
    (1, 'Explosion'),
    (2, 'Energy'),
    (3, 'Blood'),
    (4, 'Magnetic'),
    (5, 'Grass'),
    (6, 'Brush'),
    (7, 'Trees'),
)

anim_smoothing = (
    ('LINEAR', 'Linear', 'Linear interpolation. No usage of hold time'),
    ('SMOOTH', 'Smooth', 'Smooth interpolation. No usage of hold time'),
    ('BEZIER', 'Bezier', 'Bezier interpolation. No usage of hold time'),
    ('LINEARHOLD', 'Linear (Hold)', 'Linear interpolation. Uses hold time'),
    ('BEZIERHOLD', 'Bezier (Hold)', 'Bezier interpolation. Uses hold time'),
)

lod = (
    ('NULL', 'None', 'LOD has no effect'),
    ('LOW', 'Low', 'LOD cutoff or reduction takes effect if graphics are Low'),
    ('MEDIUM', 'Medium', 'LOD cutoff or reduction takes effect if graphics are Medium'),
    ('HIGH', 'High', 'LOD cutoff or reduction takes effect if graphics are High'),
    ('ULTRA', 'Ultra', 'LOD cutoff or reduction takes effect if graphics are Ultra'),
)

volume_shape = (
    ('CUBE', 'Cube', 'Volume with a cubical shape'),
    ('SPHERE', 'Sphere', 'Volume with a spherical shape'),
    ('CAPSULE', 'Capsule', 'Volume with a capsular shape'),
    ('CYLINDER', 'Cylinder', 'Volume with a cylindrical shape'),
    ('MESH', 'Mesh', 'Volume with a shape matching the assigned mesh'),
)

billboard_type = (
    ('WORLDX', 'World X', 'Aligns the bone\'s X axis to the world view'),
    ('WORLDX', 'World Y', 'Aligns the bone\'s Y axis to the world view'),
    ('WORLDX', 'World Z', 'Aligns the bone\'s Z axis to the world view'),
    ('LOCALX', 'Local X', 'Aligns the bone\'s X axis to the local view'),
    ('LOCALY', 'Local Y', 'Aligns the bone\'s Y axis to the local view'),
    ('LOCALZ', 'Local Z', 'Aligns the bone\'s Z axis to the local view'),
    ('FULL', 'Full', 'Aligns all of the bone\'s axis to the world view'),
)

force_type = (
    ('DIRECTIONAL', 'Directional', 'Particles get accelerated in a particular direction'),
    ('RADIAL', 'Radial', 'Particles get accelerated away from the force'),
    ('DAMPENING', 'Dampening', 'Particles get decelerated by the force'),
    ('VORTEX', 'Vortex', 'Particles get accelerated around the force. This type does not work when the shape is cubical'),
)

force_shape = (
    ('SPHERE', 'Sphere', 'This force has a volume with a spherical shape'),
    ('CYLINDER', 'Cylinder', 'This force has a volume with a cylindrical shape'),
    ('CUBE', 'Cube', 'This force has a volume with a cubical shape'),
    ('HEMISPHERE', 'Hemisphere', 'This force has a volume with a half spherical shape'),
    ('CONEDOME', 'Cone Dome', 'This force has a volume with conical shape that is rounded on one end'),
)

light_shape = (
    ('UNKNOWN', 'Unknown', 'Placeholder value for unused light shape value'),
    ('POINT', 'Point', 'Light is generated around a point'),
    ('SPOT', 'Spot', 'Light is generated from a point'),
)

particle_type = (
    ('BILLBOARD', 'Square Billboards', 'The emitted particles are square shaped and always face the camera'),
    ('SPEED_ROTSCALE_BILLBOARD', 'Speed Scaled and Rotated Billboards', 'The emitted particles are scaled and rotated according to their speed'),
    ('UNKNOWN_02', 'Unknown Particle Type 2', ''),
    ('UNKNOWN_03', 'Unknown Particle Type 3', ''),
    ('UNKNOWN_04', 'Unknown Particle Type 4', ''),
    ('UNKNOWN_05', 'Unknown Particle Type 5', ''),
    ('RECT_BILLBOARD', 'Rectangular Bollboards', 'The emitted particles are rectgularly shaped and always face the camera'),
    ('SPEEDNORMAL_BILLBOARD', 'Square Billboards with Speed Normals', 'The emitted particles are square shaped and face their speed vector'),
    ('UNKNOWN_08', 'Unknown Particle Type 8', ''),
    ('RAY', 'Ray from Spawn Location', 'The emitted particles are stretched from the spawn location'),
    ('UNKNOWN_10', 'Unknown Particle Type 10', ''),
)

particle_shape = (
    ('POINT', 'Point', 'Particles spawn at a certain point'),
    ('PLANE', 'Plane', 'Particles spawn within the area of the defined plane'),
    ('SPHERE', 'Sphere', 'Particles spawn within the area of the defined sphere'),
    ('CUBE', 'Cube', 'Particles spawn within the area of the defined cube'),
    ('CYLINDER', 'Cylinder', 'Particles spawn within the area of the defined cylinder'),
    ('DISC', 'Disc', 'Particles spawn within the area of the defined disc'),
    ('SPLINE', 'Spline', 'Particles spawn on the vertices of a mesh'),
    ('MESH', 'Mesh', 'Particles spawn on faces of a mesh. A mesh using vertex colors can control the probability of emission using the red channel'),
)

particle_emit_type = (
    ('CONSTANT', 'Constant', 'Emitted particles move along the normal of the emitter with configurable spread'),
    ('RADIAL', 'Radial', 'Emitted particles move in all outward directions from the emitter'),
    ('ZAXIS', 'Z-Axis', 'Emitted particles move in a random direction along the Z axis of the emitter'),
    ('RANDOM', 'Random', 'Emitted particles move in an entirely arbitrary direction'),
    ('MESH', 'Mesh Normal', 'Emitted particles move along the normal of the face being used as the emitter'),
)

projection_type = (
    ('ORTHONORMAL', 'Orthonormal', 'Makes the projector behave like a box. It will be the same width no matter how close it is to the target surface'),
    ('PERSPECTIVE', 'Perspective', 'Makes the projector behave like a camera. The closer the projector is to the surface, the smaller the effect will be'),
)

projection_layer = (
    ('GENERIC1', 'Layer 1', 'Is a generic layer that occurs above creep, that is open for use as the user sees fit'),
    ('GENERIC2', 'Layer 2', 'Is a generic layer that occurs above creep, that is open for use as the user sees fit'),
    ('GENERIC2', 'Layer 3', 'Is a generic layer that occurs above creep, that is open for use as the user sees fit'),
    ('GENERIC4', 'Layer 4', 'Is a generic layer that occurs above creep, that is open for use as the user sees fit'),
    ('BUILDING', 'Building', 'Is most often used for the dark shadow that occurs under buildings'),
    ('AOE', 'Area of Effect', 'Conventionally used for AoE cursors and some special spell effects'),
    ('POWER', 'Power', 'Used for rarely active effects such as the Protoss power fields which should be above most other splats'),
    ('UI', 'UI', 'Used for in-world effects that are part of the user interface, such as selection circles'),
    ('UNDERCREEP', 'Under Creep', 'Is a general use layer that occurs below creep. Is most often used for effects that appear above roads, but below creep'),
    ('HARDTILE', 'Hardtile', 'Is the most common layer for terrain decoration. Roads are also drawn on this layer'),
)

physics_materials = (
    ('BONE', 'Bone', ''),
    ('CLOTHHVY', 'Cloth Heavy', ''),
    ('CLOTHLGT', 'Cloth Light', ''),
    ('CREEP', 'Creep', ''),
    ('DIRT', 'Dirt', ''),
    ('ENERGY', 'Energy Shield', ''),
    ('FLESH', 'Flesh', ''),
    ('HAIR', 'Hair', ''),
    ('ICE', 'Ice', ''),
    ('LAVA', 'Lava', ''),
    ('ARMORLGT', 'Light Armor', ''),
    ('METALHVY', 'Metal Heavy', ''),
    ('METALLGT', 'Metal Light', ''),
    ('METALPRO', 'Metal Protoss', ''),
    ('PAPER', 'Paper', ''),
    ('PLASTIC', 'Plastic', ''),
    ('ROCK', 'Rock', ''),
    ('RUBBER', 'Rubber', ''),
    ('SAND', 'Sand', ''),
    ('SNOW', 'Snow', ''),
    ('WATER', 'Water', ''),
    ('WOOD', 'Wood', ''),
)

physics_shape = (
    ('CUBE', 'Cube', 'Cubical physics shape'),
    ('SPHERE', 'Sphere', 'Spherical physics shape'),
    ('CAPSULE', 'Capsule', 'Capsular physics shape'),
    ('CYLINDER', 'Cylinder', 'Cylindrical physics shape'),
    ('CONVEXHULL', 'Convex Hull', 'The physics shape is the convex hull of the selected object\'s mesh'),
    ('MESH', 'Mesh', 'The physics shape is the same shape as the selected object\'s mesh'),
)

physics_joint_type = (
    ('SPHERE', 'Spherical', 'Allows the joint to move freely on any axis'),
    ('REVOLVE', 'Revolute', 'Allows the joint to move only on the Z axis, like a door hinge'),
    ('CONE', 'Conical', 'Allows the joint to move freely like a spherical joint, but constrains movement to the cone angle around the Z axis'),
    ('WELD', 'Welded', 'Restrains the joint\'s movement, but is not perfectly rigid'),
)

ribbon_type = (
    ('PLANAR_BILLBOARD', 'Planar Billboard', 'The ribbon\'s shape is that of plane, and the rotation is adjusted to face the camera as much as possible'),
    ('PLANAR', 'Planar', 'The ribbon\'s shape is of that of a plane'),
    ('CYLINDER', 'Cylinder', 'The ribbon\'s shape is that of a cylinder'),
    ('STAR', 'Star', 'The ribbon\'s shape is a mixture between the planar and cylinder shape.\nThe ratio is determined by the "Inner Radius" property'),
)

ribbon_cull = (
    ('TIME', 'Lifespan', 'Ribbon elements are destroyed after having existed for the specified lifespan.'),
    ('LENGTH', 'Length Based', 'Ribbon elements are destroyed after reaching the specified maximum length'),
)

ribbon_variation_shape = (
    ('NONE', 'None', ''),
    ('SIN', 'Sin', ''),
    ('COS', 'Cos', ''),
    ('SAW', 'Saw', ''),
    ('SQUARE', 'Square', ''),
    ('NOISE_RANDOM', 'Noise (Random)', ''),
    ('NOISE_CONTINUOUS', 'Noise (Continuous)', ''),
)

camera_dof = (
    ('0x0', 'Unknown 0x0', ''),
    ('0x1', 'Unknown 0x1', ''),
)

matref_type = (
    ('m3_materials_standard', 'Standard', 'Used for most purposes'),
    ('m3_materials_displacement', 'Displacement', 'Used to create rippling effects'),
    ('m3_materials_composite', 'Composite', 'Used to combine multiple materials into one'),
    ('m3_materials_terrain', 'Terrain', 'Used to draw terrain textures in the game map over the mesh'),
    ('m3_materials_creep', 'Creep', 'Used to draw creep which exists in the game map over the mesh'),
    ('m3_materials_volume', 'Volume', 'Used to draw volumetric shapes'),
    ('m3_materials_volumenoise', 'Volume Noise (MV25+)', 'Used to draw volumetric shapes. Has additional functionality compared to the Volume material type'),
    ('m3_materials_stb', 'Splat Terrain Bake (MV26+)', 'Used typically for static shapes drawn over terrain'),
    ('m3_materials_reflection', 'Reflection (MV28+)', 'Used for special reflection effects. Currently not supported'),
    ('m3_materials_lensflare', 'Lens Flare (MV29+)', 'Used for lens flare effects. Currently not supported'),
)

mat_blend = (
    ('OPAQUE', 'Opaque', 'Render output has no transparency except where the alpha mask value exceeds the cutout threshold'),
    ('ALPHAB', 'Alpha Blend', 'Render output is blended on the basis of the alpha mask'),
    ('ADD', 'Add', 'Render output is transparent on the basis of color value'),
    ('ALPHAA', 'Alpha Add', 'Render output is transparent on the basis of the alpha mask'),
    ('MOD', 'Mod', 'Render output is similar to Opaque, but the alpha mask cutout is applied with greater fidelity'),
    ('MOD2', 'Mod 2x', 'Render output is similar to Opaque, but the alpha mask cutout is applied with greater fidelity'),
    ('UNK6', 'Unknown 0x06', 'Undocumented'),
    ('UNK7', 'Unknown 0x07', 'Undocumented'),
)

mat_layer_blend = (
    ('MOD', 'Mod', 'No description yet'),
    ('MOD2', 'Mod 2x', 'No description yet'),
    ('ADD', 'Add', 'Render output is transparent on the basis of color value'),
    ('BLEND', 'Blend', 'Render output is layered over previous layers'),
    ('TEAMEMIS', 'Team Color Emissive Add', 'Render output is team colored from the alpha channel (or single color channel)'),
    ('TEAMDIFF', 'Team Color Diffuse Add', 'No description yet'),
)

mat_spec = (
    ('RGB', 'RGB', 'Mode for multi-channel specular maps'),
    ('A', 'Alpha', 'Mode for single channel specular maps'),
)

material_layer_type = (
    ('BITMAP', 'Bitmap', 'Renders using the image defined in the image path property'),
    ('COLOR', 'Color', 'Renders using the color defined in the color value property'),
)

material_layer_channel = (
    ('RGB', 'RGB', 'Use red, green and blue color channels'),
    ('ARGB', 'ARGB', 'Use alpha, red, green, and blue color channels'),
    ('A', 'Alpha Only', 'Use alpha channel only'),
    ('R', 'Red Only', 'Use red color channel only'),
    ('G', 'Green Only', 'Use green color channel only'),
    ('B', 'Blue Only', 'Use blue color channel only')
)

uv_source = (
    ('UV1', 'Default', 'First UV layer of mesh or generated whole image UVs for particles'),
    ('UV2', 'UV Layer 2', 'Second UV layer which can be used for decals'),
    ('REFCUBE', 'Ref Cubic Env', 'For Env. Layer: Reflective Cubic Environment'),
    ('REFSPHERE', 'Ref Spherical Env', 'For Env. Layer: Reflective Spherical Environemnt'),
    ('PLANARLZ', 'Planar Local Z', 'Planar Local Z'),
    ('PLANARWZ', 'Planar World Z', 'Planar World Z'),
    ('PARTICLE', 'Animated Particle UV', 'The flip book of the particle system is used to determine the UVs'),
    ('CUBE', 'Cubic Environment', 'For Env. Layer: Cubic Environment'),
    ('SPHERE', 'Spherical Environment', 'For Env. Layer: Spherical Environment'),
    ('UV3', 'UV Layer 3', 'UV Layer 3'),
    ('UV4', 'UV Layer 4', 'UV Layer 4'),
    ('PLANARLX', 'Planar Local X', 'Planar Local X'),
    ('PLANARLY', 'Planar Local Y', 'Planar Local Y'),
    ('PLANARWX', 'Planar World X', 'Planar World X'),
    ('PLANARWY', 'Planar World Y', 'Planar World Y'),
    ('SCREEN', 'Screen space', 'Screen space'),
    ('TRIPLANARW', 'Tri Planar World (V24+)', 'Tri Planar World. Only functional on layers at or above version 24'),
    ('TRIPLANARL', 'Tri Planar Local (V24+)', 'Tri Planar Local. Only functional on layers at or above version 24'),
    ('TRIPLANARLZ', 'Tri Planar Local Z (V24+)', 'Tri Planar Local Z. Only functional on layers at or above version 24')
)

fresnel_type = (
    ('DISABLED', 'Disabled', 'Fresnel is disabled'),
    ('ENABLED', 'Enabled', 'Strength of layer is based on fresnel formula'),
    ('INVERTED', 'Enabled; Inverted', 'Strenth of layer is based on inverted fresnel formula')
)

rtt_channel = (
    ('0', 'Layer 0', 'Render To Texture Layer 0'),
    ('1', 'Layer 1', 'Render To Texture Layer 1'),
    ('2', 'Layer 2', 'Render To Texture Layer 2'),
    ('3', 'Layer 3', 'Render To Texture Layer 3'),
    ('4', 'Layer 4', 'Render To Texture Layer 4'),
    ('5', 'Layer 5', 'Render To Texture Layer 5'),
    ('6', 'Layer 6', 'Render To Texture Layer 6'),
    ('NONE', 'None', 'None'),
)

video_mode = (
    ('LOOP', 'Loop', 'Loop'),
    ('HOLD', 'Hold', 'Hold')
)
