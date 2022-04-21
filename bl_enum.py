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

world_forces = [
    (0, 'Wind'),
    (1, 'Explosion'),
    (2, 'Energy'),
    (3, 'Blood'),
    (4, 'Magnetic'),
    (5, 'Grass'),
    (6, 'Brush'),
    (7, 'Trees'),
]

anim_smoothing = [
    ('LINEAR', 'Linear', 'Linear interpolation. No usage of hold time'),
    ('SMOOTH', 'Smooth', 'Smooth interpolation. No usage of hold time'),
    ('BEZIER', 'Bezier', 'Bezier interpolation. No usage of hold time'),
    ('LINEARHOLD', 'Linear (Hold)', 'Linear interpolation. Uses hold time'),
    ('BEZIERHOLD', 'Bezier (Hold)', 'Bezier interpolation. Uses hold time'),
]

lod = [
    ('NULL', 'None', 'LOD has no effect'),
    ('LOW', 'Low', 'LOD cutoff or reduction takes effect if graphics are Low'),
    ('MEDIUM', 'Medium', 'LOD cutoff or reduction takes effect if graphics are Medium'),
    ('HIGH', 'High', 'LOD cutoff or reduction takes effect if graphics are High'),
    ('ULTRA', 'Ultra', 'LOD cutoff or reduction takes effect if graphics are Ultra'),
]

volume_shape = [
    ('CUBE', 'Cube', 'Volume with a cuboid shape'),
    ('SPHERE', 'Sphere', 'Volume with a spherical shape'),
    ('CAPSULE', 'Capsule', 'Volume with a capsular shape'),
    ('UNKNOWN_3', 'Unknown 3', 'Unknown volumetric shape'),
    ('UNKNOWN_4', 'Unknown 4', 'Unknown volumetric shape'),
]

billboard_type = [
    ('WORLDX', 'World X', 'Aligns the bone\'s X axis to the world view'),
    ('WORLDX', 'World Y', 'Aligns the bone\'s Y axis to the world view'),
    ('WORLDX', 'World Z', 'Aligns the bone\'s Z axis to the world view'),
    ('LOCALX', 'Local X', 'Aligns the bone\'s X axis to the local view'),
    ('LOCALY', 'Local Y', 'Aligns the bone\'s Y axis to the local view'),
    ('LOCALZ', 'Local Z', 'Aligns the bone\'s Z axis to the local view'),
    ('FULL', 'Full', 'Aligns all of the bone\'s axis to the world view'),
]

force_type = [
    ('DIRECTIONAL', 'Directional', 'Particles get accelerated in a particular direction'),
    ('RADIAL', 'Radial', 'Particles get accelerated away from the force'),
    ('DAMPENING', 'Dampening', 'Particles get decelerated by the force'),
    ('VORTEX', 'Vortex', 'Particles get accelerated around the force. This type does not work when the shape is cubical'),
]

force_shape = [
    ('SPHERE', 'Sphere', 'This force has a volume with a spherical shape'),
    ('CYLINDER', 'Cylinder', 'This force has a volume with a cylindrical shape'),
    ('CUBE', 'Cube', 'This force has a volume with a cubical shape'),
    ('HEMISPHERE', 'Hemisphere', 'This force has a volume with a half spherical shape'),
    ('CONEDOME', 'Cone Dome', 'This force has a volume with conical shape that is rounded on one end'),
]

light_shape = [
    ('POINT', 'Point', 'Light is generated around a point'),
    ('SPOT', 'Spot', 'Light is generated from a point'),
]

particle_type = [
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
]

particle_shape = [
    ('POINT', 'Point', 'Particles spawn at a certain point'),
    ('PLANE', 'Plane', 'Particles spawn within the area of the defined plane'),
    ('SPHERE', 'Sphere', 'Particles spawn within the area of the defined sphere'),
    ('CUBE', 'Cube', 'Particles spawn within the area of the defined cube'),
    ('CYLINDER', 'Cylinder', 'Particles spawn within the area of the defined cylinder'),
    ('DISC', 'Disc', 'Particles spawn within the area of the defined disc'),
    ('SPLINE', 'Spline', 'Particles spawn on the vertices of a mesh'),
    ('MESH', 'Mesh', 'Particles spawn on areas of a mesh. The probability of spawning at a particular vertex depends on the red value in its vertex color'),
]

particle_emit_type = [
    ('CONSTANT', 'Constant', 'Emitted particles move along the normal of the emitter with configurable spread'),
    ('RADIAL', 'Radial', 'Emitted particles move in all outward directions from the emitter'),
    ('ZAXIS', 'Z-Axis', 'Emitted particles move in a random direction along the Z axis of the emitter'),
    ('RANDOM', 'Random', 'Emitted particles move in an entirely arbitrary direction'),
    ('MESH', 'Mesh Normal', 'Emitted particles move along the normal of the face being used as the emitter'),
]

physics_materials = [
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
]

physics_shape = [
    ('CUBE', 'Cube', 'Cubical physics shape'),
    ('SPHERE', 'Sphere', 'Spherical physics shape'),
    ('CAPSULE', 'Capsule', 'Capsular physics shape'),
    ('CYLINDER', 'Cylinder', 'Cylindrical physics shape'),
    ('CONVEXHULL', 'Convex Hull', 'The physics shape is the convex hull of the selected objects mesh'),
    ('MESH', 'Mesh', 'The physics shape is the same shape as the selected objects mesh'),
]

physics_joint_type = [
    ('SPHERE', 'Spherical', 'Allows the joint to move freely on any axis'),
    ('REVOLVE', 'Revolute', 'Allows the joint to move only on the Z axis, like a door hinge'),
    ('CONE', 'Conical', 'Allows the joint to move freely like a spherical joint, but constrains movement to the cone angle around the Z axis'),
    ('WELD', 'Welded', 'Restrains the joint\'s movement, but is not perfectly rigid'),
]

ribbon_type = [
    ('PLANAR_BILLBOARD', 'Planar Billboard', 'The ribbon\'s shape is that of plane, and the rotation is adjusted to face the camera as much as possible'),
    ('PLANAR', 'Planar', 'The ribbon\'s shape is of that of a plane'),
    ('CYLINDER', 'Cylinder', 'The ribbon\'s shape is that of a cylinder'),
    ('STAR', 'Star', 'The ribbon\'s shape is a mixture between the planar and cylinder shape.\nThe ratio is determined by the "Inner Radius" property'),
]

ribbon_cull = [
    ('TIME', 'Lifespan', 'Ribbon elements are destroyed after having existed for the specified lifespan.'),
    ('LENGTH', 'Length Based', 'Ribbon elements are destroyed after reaching the specified maximum length'),
]

material_layer_type = [
    ('BITMAP', 'Bitmap', 'Renders using the image defined in the image path property'),
    ('COLOR', 'Color', 'Renders using the color defined in the color value property'),
]

material_layer_channel = [
    ('RGB', 'RGB', 'Use red, green and blue color channels'),
    ('ARGB', 'ARGB', 'Use alpha, red, green, and blue color channels'),
    ('A', 'Alpha Only', 'Use alpha channel only'),
    ('R', 'Red Only', 'Use red color channel only'),
    ('G', 'Green Only', 'Use green color channel only'),
    ('B', 'Blue Only', 'Use blue color channel only')
]

uv_source = [
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
    ('TRIPLANARW', 'Tri Planar World', 'Tri Planar World'),
    ('TRIPLANARL', 'Tri Planar Local', 'Tri Planar Local'),
    ('TRIPLANARLZ', 'Tri Planar Local Z', 'Tri Planar Local Z')
]

fresnel_type = [
    ('DISABLED', 'Disabled', 'Fresnel is disabled'),
    ('ENABLED', 'Enabled', 'Strength of layer is based on fresnel formula'),
    ('INVERTED', 'Enabled; Inverted', 'Strenth of layer is based on inverted fresnel formula')
]

rtt_channel = [
    ('NONE', 'None', 'None'),
    ('0', 'Layer 0', 'Render To Texture Layer 0'),
    ('1', 'Layer 1', 'Render To Texture Layer 1'),
    ('2', 'Layer 2', 'Render To Texture Layer 2'),
    ('3', 'Layer 3', 'Render To Texture Layer 3'),
    ('4', 'Layer 4', 'Render To Texture Layer 4'),
    ('5', 'Layer 5', 'Render To Texture Layer 5'),
    ('6', 'Layer 6', 'Render To Texture Layer 6'),
]

video_mode = [
    ('LOOP', 'Loop', 'Loop'),
    ('HOLD', 'Hold', 'Hold')
]
