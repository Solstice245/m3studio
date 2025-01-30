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

anim_header_interp = (
    ('CONSTANT', 'Constant', ''),
    ('LINEAR', 'Linear', ''),
    ('AUTO', 'Automatic', 'The exporter will determine this value based on the conventional configuration of this property'),
)

anim_tokens = {
    # action
    'Attack', 'Birth', 'Blink', 'Block', 'Build', 'Burrow', 'Channel', 'Cloak', 'Corrupted', 'Creep', 'Dance', 'Death',
    'Detect', 'Dialogue', 'Fidget', 'Flail', 'Fling', 'Freeze', 'Gather', 'Jump', 'Kill', 'Land', 'Listen', 'Load',
    'Morph', 'NearImpact', 'Penetrate', 'Pickup', 'Placement', 'Pose', 'Reload', 'Restart', 'Run', 'Shield',
    'Spell', 'Stand', 'Standup', 'Talk', 'Taunt', 'Turn', 'Unburrow', 'Unload', 'Victory', 'Walk', 'Work',
    # state
    'Attached', 'Cover', 'Dead', 'Fly', 'Thrown', 'Ready', 'Unpowered', 'Wounded',
    # death type
    'Blast', 'Disintegrate', 'Eat', 'Electrocute', 'Eviscerate', 'Fire', 'Silentkill', 'Squish',
    # directional
    'Forward', 'Back', 'Left', 'Right', 'Inferior', 'Equal', 'Superior',
    # emotional
    'Angry', 'Dominant', 'Happy', 'Scared', 'AngryEyes', 'FearEyes', 'HappyEyes', 'SadEyes', 'SeriousEyes', 'SurpriseEyes',
    # body
    'Arm', 'Chest', 'Eye', 'Leg',
    # character
    'Adjutant', 'Dehaka', 'Evomaster', 'Horner', 'Kerrigan', 'Lasarra', 'Raynor', 'Stukov', 'Valerian', 'Zagara',
    # interface
    'Click', 'Highlight', 'Hover',
    # miscellaneous
    'Close', 'Far', 'Double', 'Alternate', 'Complex', 'Simple', 'Small', 'Medium',
    'Large', 'Slow', 'Fast', 'Turbo', 'Enemy', 'Lighting', 'Glow', 'Portrait', 'Custom',
    # global loops
    'GLBirth', 'GLStand', 'GLDeath', 'GLDead',
    #special
    'Default', 'Protoss', 'Terran', 'Zerg', *[str(ii).zfill(2) for ii in range(1, 100)], 'Start', 'End',
    *[chr(ii) for ii in range(ord('A'), ord('Z') + 1)], 'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    # legacy
    'Alternateex', 'Berserk', 'Bone', 'Chain', 'Complete', 'Critical', 'Decay', 'Defend', 'Drain', 'EatTree', 'Entangle',
    'Fill', 'Flesh', 'Gold', 'Hit', 'Light', 'Looping', 'Lumber', 'Moderate', 'Off', 'Puke', 'Severe', 'Slam', 'Spiked',
    'Spin', 'StageFirst', 'StageSecond', 'StageThird', 'StageFourth', 'StageFifth', 'Swim', 'Throw', 'Upgrade',
}

# these are based on the possible values given in the SC2 editor
# this list should never be changed without consulting that list
attachment_names = (
    'Ref_Attacher',
    'Ref_Attacher 01',
    'Ref_Attacher 02',
    'Ref_Attacher 03',
    'Ref_Attacher 04',
    'Ref_Attacher 05',
    'Ref_Attacher 06',
    'Ref_Attacher 07',
    'Ref_Attacher 08',
    'Ref_Attacher 09',
    'Ref_Attacher 10',
    'Ref_Attacher 11',
    'Ref_Attacher 12',
    'Ref_Attacher 13',
    'Ref_Attacher 14',
    'Ref_Attacher 15',
    'Ref_Attacher 16',
    'Ref_Attacher 17',
    'Ref_Attacher 18',
    'Ref_Attacher 19',
    'Ref_Back',
    'Ref_Center',
    'Ref_Center 01',
    'Ref_Chest',
    'Ref_Chest Alternate',
    'Ref_Chest Left',
    'Ref_Chest Mount',
    'Ref_Chest Mount Left',
    'Ref_Chest Mount Rear',
    'Ref_Chest Mount Right',
    'Ref_Chest Right',
    'Ref_Chin',
    'Ref_Damage',
    'Ref_Damage 01',
    'Ref_Damage 02',
    'Ref_Damage 03',
    'Ref_Damage 04',
    'Ref_Damage 05',
    'Ref_Damage 06',
    'Ref_Damage 07',
    'Ref_Damage 08',
    'Ref_Damage 09',
    'Ref_Damage 10',
    'Ref_Damage 11',
    'Ref_Damage 12',
    'Ref_Damage 13',
    'Ref_Damage 14',
    'Ref_Damage 15',
    'Ref_Damage 16',
    'Ref_Damage 17',
    'Ref_Damage 18',
    'Ref_Damage 19',
    'Ref_Elevator',
    'Ref_Engine',
    'Ref_Evolution Master',
    'Ref_Face',
    'Ref_Foot Left',
    'Ref_Foot Left Alternate',
    'Ref_Foot Left Rear',
    'Ref_Foot Right',
    'Ref_Foot Right Alternate',
    'Ref_Foot Right Rear',
    'Ref_Forearm Left',
    'Ref_Forearm Right',
    'Ref_Hand',
    'Ref_Hand Left',
    'Ref_Hand Left Alternate',
    'Ref_Hand Right',
    'Ref_Hand Right Alternate',
    'Ref_Hardpoint',
    'Ref_Hardpoint 01',
    'Ref_Hardpoint 01 Alternate',
    'Ref_Hardpoint 02',
    'Ref_Hardpoint 02 Alternate',
    'Ref_Hardpoint 03',
    'Ref_Hardpoint 03 Alternate',
    'Ref_Hardpoint 04',
    'Ref_Hardpoint 04 Alternate',
    'Ref_Hardpoint 05',
    'Ref_Hardpoint 06',
    'Ref_Hardpoint 07',
    'Ref_Hardpoint 08',
    'Ref_Hardpoint 09',
    'Ref_Hardpoint 10',
    'Ref_Hardpoint 11',
    'Ref_Hardpoint 12',
    'Ref_Hardpoint 13',
    'Ref_Hardpoint 14',
    'Ref_Hardpoint 15',
    'Ref_Hardpoint 16',
    'Ref_Hardpoint 17',
    'Ref_Hardpoint 18',
    'Ref_Hardpoint 19',
    'Ref_Hardpoint Alternate',
    'Ref_Hardpoint Eat Tree',
    'Ref_Hardpoint Large',
    'Ref_Hardpoint Left',
    'Ref_Hardpoint Medium',
    'Ref_Hardpoint Right',
    'Ref_Hardpoint Small',
    'Ref_Head',
    'Ref_Head Alternate',
    'Ref_Head Mount',
    'Ref_Head Top',
    'Ref_Hit',
    'Ref_Hit 01',
    'Ref_Hit 02',
    'Ref_Hit 03',
    'Ref_Hit 04',
    'Ref_Hit 05',
    'Ref_Hit 06',
    'Ref_Hit 07',
    'Ref_Hit 08',
    'Ref_Hit 09',
    'Ref_Knee Left',
    'Ref_Knee Right',
    'Ref_Lip Upper',
    'Ref_Origin',
    'Ref_Origin 01',
    'Ref_Origin Alternate',
    'Ref_Overhead',
    'Ref_Overhead 01',
    'Ref_Overhead Alternate',
    'Ref_Portrait',
    'Ref_Portrait Chest',
    'Ref_Portrait Hand Left',
    'Ref_Portrait Hand Right',
    'Ref_Portrait Head',
    'Ref_RallyPoint',
    'Ref_Shield',
    'Ref_Shoulder Left',
    'Ref_Shoulder Right',
    'Ref_Sprite First',
    'Ref_Sprite Second',
    'Ref_Sprite Third',
    'Ref_StatusBar',
    'Ref_StatusBar 01',
    'Ref_StatusBar 02',
    'Ref_StatusBar 03',
    'Ref_StatusBar 04',
    'Ref_StatusBar 05',
    'Ref_StatusBar 06',
    'Ref_StatusBar 07',
    'Ref_StatusBar 08',
    'Ref_StatusBar 09',
    'Ref_StatusBar 10',
    'Ref_StatusBar 11',
    'Ref_StatusBar 12',
    'Ref_StatusBar 13',
    'Ref_StatusBar 14',
    'Ref_StatusBar 15',
    'Ref_StatusBar 16',
    'Ref_StatusBar 17',
    'Ref_StatusBar 18',
    'Ref_StatusBar 19',
    'Ref_Target',
    'Ref_Target 01',
    'Ref_Target 02',
    'Ref_Target 03',
    'Ref_Target 04',
    'Ref_Target 05',
    'Ref_Target 06',
    'Ref_Target 07',
    'Ref_Target 08',
    'Ref_Target 09',
    'Ref_Target 10',
    'Ref_Target 11',
    'Ref_Target 12',
    'Ref_Target 13',
    'Ref_Target 14',
    'Ref_Target 15',
    'Ref_Target 16',
    'Ref_Target 17',
    'Ref_Target 18',
    'Ref_Target 19',
    'Ref_Target 20',
    'Ref_Target 21',
    'Ref_Target 22',
    'Ref_Target 23',
    'Ref_Target 24',
    'Ref_Target 25',
    'Ref_Target 26',
    'Ref_Target 27',
    'Ref_Target 28',
    'Ref_Target 29',
    'Ref_Target 30',
    'Ref_Target 30',
    'Ref_Target 31',
    'Ref_Target 32',
    'Ref_Target 33',
    'Ref_Target 34',
    'Ref_Target 35',
    'Ref_Target 36',
    'Ref_Target 37',
    'Ref_Target 38',
    'Ref_Target 39',
    'Ref_Target 40',
    'Ref_Target Final',
    'Ref_Target Heavy',
    'Ref_Target Light',
    'Ref_Target Medium',
    'Ref_Target Shield',
    'Ref_Transmission',
    'Ref_Turret',
    'Ref_TurretY',
    'Ref_TurretZ',
    'Ref_Upgrade',
    'Ref_Upgrade Armor',
    'Ref_Upgrade Engine',
    'Ref_Upgrade Engine Bottom',
    'Ref_Upgrade Engine Left',
    'Ref_Upgrade Engine Right',
    'Ref_Upgrade Weapon',
    'Ref_Upgrade Weapon Bottom',
    'Ref_Upgrade Weapon Left',
    'Ref_Upgrade Weapon Right',
    'Ref_Waist',
    'Ref_Waist Back',
    'Ref_Waist Front',
    'Ref_Waist Left',
    'Ref_Waist Right',
    'Ref_Weapon',
    'Ref_Weapon 01',
    'Ref_Weapon 02',
    'Ref_Weapon 03',
    'Ref_Weapon 04',
    'Ref_Weapon 05',
    'Ref_Weapon 06',
    'Ref_Weapon 07',
    'Ref_Weapon 08',
    'Ref_Weapon 09',
    'Ref_Weapon 10',
    'Ref_Weapon 11',
    'Ref_Weapon 12',
    'Ref_Weapon 13',
    'Ref_Weapon 14',
    'Ref_Weapon 15',
    'Ref_Weapon 16',
    'Ref_Weapon 17',
    'Ref_Weapon 18',
    'Ref_Weapon 19',
    'Ref_Weapon 20',
    'Ref_Weapon 21',
    'Ref_Weapon 22',
    'Ref_Weapon 23',
    'Ref_Weapon 24',
    'Ref_Weapon 25',
    'Ref_Weapon 26',
    'Ref_Weapon 27',
    'Ref_Weapon 28',
    'Ref_Weapon 29',
    'Ref_Weapon 30',
    'Ref_Weapon Alternate',
    'Ref_Weapon Bottom',
    'Ref_Weapon Left',
    'Ref_Weapon Left Alternate',
    'Ref_Weapon Right',
    'Ref_Weapon Right Alternate',
    # campaign utility
    'Ref_Agria',
    'Ref_Albion',
    'Ref_Avernus',
    'Ref_BelShir',
    'Ref_Castanar',
    'Ref_Char',
    'Ref_Dylar',
    'Ref_Haven',
    'Ref_Korhal',
    'Ref_MarSara',
    'Ref_Meinhoff',
    'Ref_Monlyth',
    'Ref_Moria',
    'Ref_Mount',
    'Ref_NewFolsom',
    'Ref_PortZion',
    'Ref_PU72516J',
    'Ref_Redstone',
    'Ref_Tasonis',
    'Ref_Tyrador',
    'Ref_Umoja',
    'Ref_Valhalla',
    'Ref_Xil',
    'Pos_Adjutant',
    'Pos_AdjutantToRaynor',
    'Pos_Banshee',
    'Pos_Bartender',
    'Pos_Dropship',
    'Pos_Firebat',
    'Pos_Ghost',
    'Pos_Hanson',
    'Pos_HansonToRaynor',
    'Pos_Hill',
    'Pos_Horner',
    'Pos_HornerToRaynor',
    'Pos_JessicaHall',
    'Pos_Kerrigan',
    'Pos_Marauder',
    'Pos_MarcusCade',
    'Pos_Marine',
    'Pos_Merc03',
    'Pos_Primal',
    'Pos_ProtossScientist',
    'Pos_Raynor',
    'Pos_RaynorToAdjutant',
    'Pos_RaynorToHanson',
    'Pos_RaynorToHorner',
    'Pos_RaynorToSwann',
    'Pos_RaynorToTosh',
    'Pos_RaynorToTychus',
    'Pos_SetLocation',
    'Pos_SetLocation 01',
    'Pos_SetLocation 02',
    'Pos_SetLocation 03',
    'Pos_SetLocation 04',
    'Pos_SetLocation 05',
    'Pos_SetLocation 06',
    'Pos_SetLocation 07',
    'Pos_SetLocation 08',
    'Pos_SetLocation 09',
    'Pos_SetLocation 10',
    'Pos_SetLocation 11',
    'Pos_SetLocation 12',
    'Pos_SetLocation 13',
    'Pos_SetLocation 14',
    'Pos_SetLocation 15',
    'Pos_SiegeTank',
    'Pos_Spidermine',
    'Pos_Stetmann',
    'Pos_Stukov',
    'Pos_Swann',
    'Pos_SwannToRaynor',
    'Pos_Tosh',
    'Pos_ToshToRaynor',
    'Pos_Tychus',
    'Pos_TychusToRaynor',
    'Pos_Viking',
    'Pos_Warfield',
    'Pos_Zagara',
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

anim_smoothing_basic = (
    ('LINEAR', 'Linear', 'Linear interpolation'),
    ('SMOOTH', 'Smooth', 'Smooth interpolation'),
    ('BEZIER', 'Bezier', 'Bezier interpolation'),
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
    ('WORLDY', 'World Y', 'Aligns the bone\'s Y axis to the world view'),
    ('WORLDZ', 'World Z', 'Aligns the bone\'s Z axis to the world view'),
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
    ('BILLBOARD', 'Billboard', 'Particles will always be square to the camera'),
    ('TAIL', 'Tail', 'Particles will face the camera and be stretched based on Tail Length and velocity'),
    ('EMISSION', 'Emission', 'Particles will face the same direction as their velocity vector'),
    ('WORLD', 'World', 'Particles will face the given yaw and pitch in world space'),
    ('SINGLE', 'Single', 'Particles will face the camera on the Z-axis while using the given yaw and pitch'),
    ('GROUND', 'Ground', 'Particles will face away from the terrain heightmap'),
    ('GROUND_TAIL', 'Ground Tail', 'Particles will face away from the terrain heightmap while being streched based on Tail Length and velocity'),
    ('EMITTER', 'Emitter', 'Particles will face their emitter\'s local Z-axis'),
    ('COLLISION', 'Collision', 'Particles will face a direction based on the collision surface in the collision event they were generated from'),
    ('RAY', 'Ray', 'Particles are stretched from the emitter while facing the camera'),
    ('TAIL_ALT', 'Tail (Alt)', 'Particles will face the camera and be stretched based on Tail Length and velocity'),  # similar to TAIL, but it seems to emit from a point behind the emitter, instead of in front
)

particle_shape = (
    ('POINT', 'Point', 'Particles emit at a certain point'),
    ('PLANE', 'Plane', 'Particles emit within the area of the defined plane'),
    ('SPHERE', 'Sphere', 'Particles emit within the area of the defined sphere'),
    ('CUBE', 'Cube', 'Particles emit within the area of the defined cube'),
    ('CYLINDER', 'Cylinder', 'Particles emit within the area of the defined cylinder'),
    ('DISC', 'Disc', 'Particles emit within the area of the defined disc'),
    ('SPLINE', 'Spline', 'Particles emit on defined points'),
    ('MESH', 'Mesh (V17+)', 'Particles emit on faces of a mesh. A mesh with vertex colors can control the probability of emission using the red channel'),
)

particle_emit_type = (
    ('CONSTANT', 'Constant', 'Emitted particles move along the normal of the emitter with configurable spread'),
    ('RADIAL', 'Radial', 'Emitted particles move in all outward directions from the emitter'),
    ('ZAXIS', 'Z-Axis', 'Emitted particles move in a random direction along the Z axis of the emitter'),
    ('RANDOM', 'Random', 'Emitted particles move in an entirely arbitrary direction'),
    ('MESH', 'Mesh Normal', 'Emitted particles move along the normal of the face being used as the emitter'),
)

particle_tail_type = (
    ('FREE', 'Free', 'The given tail length acts as a general factor for the computed tail length'),
    ('CLAMP', 'Clamped', 'The computed tail length starts at zero and will never exceed the given tail length'),
    ('FIX', 'Fixed', 'The computed tail length is fixed at the given tail length, regardless of velocity'),
)

particle_sort_method = (
    ('NONE', 'None', 'No sorting is applied to the particle instance list'),
    ('DISTANCE', 'Distance', 'Particles are sorted by their distance from the player camera'),
    ('HEIGHT', 'Height', 'Particles are sorted by their height in the game world'),
)

projection_type = (
    ('PERSPECTIVE', 'Perspective', 'Makes the projector behave like a camera. The closer the projector is to the surface, the smaller the effect will be'),
    ('ORTHONORMAL', 'Orthonormal', 'Makes the projector behave like a box. It will be the same width no matter how close it is to the target surface'),
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
    ('BAKED1', 'Baked 1', 'Is a layer commonly used by "terrain baked" doodads, which are intended to appear over only terrain textures'),
    ('BAKED2', 'Baked 2', 'Is a layer commonly used by "terrain baked" doodads, which are intended to appear over only terrain textures'),
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
    ('m3_materials_reflection', 'Reflection (MV28+)', 'Used for special reflection effects.'),
    ('m3_materials_lensflare', 'Lens Flare (MV29+)', 'Used for lens flare effects.'),
    ('m3_materials_buffer', 'Buffer (MADD) (MV30+)', 'Used by newer HotS models. Not currently supported by the addon, and is also unsupported by SC2 itself')
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
    ('UV0', 'Default', 'First UV layer of mesh or generated whole image UVs for particles'),
    ('UV1', 'UV Layer 2', 'Second UV layer which can be used for decals'),
    ('REFCUBE', 'Ref Cubic Env', 'For Env. Layer: Reflective Cubic Environment'),
    ('REFSPHERE', 'Ref Spherical Env', 'For Env. Layer: Reflective Spherical Environemnt'),
    ('PLANARLZ', 'Planar Local Z', 'Planar Local Z'),
    ('PLANARWZ', 'Planar World Z', 'Planar World Z'),
    ('PARTICLE', 'Animated Particle UV', 'The flip book of the particle system is used to determine the UVs'),
    ('CUBE', 'Cubic Environment', 'For Env. Layer: Cubic Environment'),
    ('SPHERE', 'Spherical Environment', 'For Env. Layer: Spherical Environment'),
    ('UV2', 'UV Layer 3', 'UV Layer 3'),
    ('UV3', 'UV Layer 4', 'UV Layer 4'),
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

video_mode = (
    ('LOOP', 'Loop', 'Loop'),
    ('HOLD', 'Hold', 'Hold')
)
