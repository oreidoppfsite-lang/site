"""Render the hero orbit with Cycles: studio softboxes, glossy black floor, black paint with clearcoat.

usage: python3 render.py START END WIDTH HEIGHT SAMPLES OUTDIR
"""
import sys, math
import bpy
from mathutils import Vector

start, end, W, H, SAMPLES = map(int, sys.argv[1:6])
OUT = sys.argv[6]
FRAMES = 120
HERE = __file__.rsplit('/', 1)[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=HERE + '/three-ferrari.glb')
sc = bpy.context.scene
car = bpy.data.collections.new('car_only')
for o in list(sc.objects):
    if o.type == 'MESH':
        car.objects.link(o)

# ── materials ──
def principled(mat):
    mat.use_nodes = True
    return next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def setp(p, **kw):
    names = {'base': 'Base Color', 'metal': 'Metallic', 'rough': 'Roughness', 'coat': 'Coat Weight',
             'coat_rough': 'Coat Roughness', 'trans': 'Transmission Weight', 'ior': 'IOR',
             'emit': 'Emission Color', 'emit_s': 'Emission Strength', 'alpha': 'Alpha'}
    for k, v in kw.items():
        inp = p.inputs[names[k]]
        for l in list(inp.links):
            p.id_data.links.remove(l)
        inp.default_value = (*v, 1) if isinstance(v, tuple) else v

M = bpy.data.materials
setp(principled(M['Body_Color']), base=(0.002, 0.002, 0.0025), metal=0.0, rough=0.42, coat=1.0, coat_rough=0.012)
setp(principled(M['Glass_Gray']), base=(0.02, 0.02, 0.022), metal=0.0, rough=0.0, trans=0.0)
setp(principled(M['metal_chrome']), base=(0.9, 0.9, 0.9), metal=1.0, rough=0.05)
setp(principled(M['metal_gray']), base=(0.55, 0.55, 0.56), metal=1.0, rough=0.28)
setp(principled(M['Tires']), base=(0.015, 0.015, 0.015), metal=0.0, rough=0.75)
setp(principled(M['Taillight_Glass']), base=(0.5, 0.0, 0.0), rough=0.05, emit=(1, 0.02, 0.01), emit_s=1.5)
setp(principled(M['Projector_Glass']), base=(0.8, 0.8, 0.8), rough=0.02, emit=(1, 0.97, 0.9), emit_s=0.6)

# ── floor: glossy black studio floor ──
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
floor = bpy.context.object
fm = M.new('Floor'); floor.data.materials.append(fm)
setp(principled(fm), base=(0.003, 0.003, 0.003), metal=0.0, rough=0.22)

# ── world: almost black ──
world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.004, 0.005, 1)

# ── lights ──
def area(name, loc, size, size_y, power, color=(1, 1, 1), target=(0, 0, 0.5)):
    l = bpy.data.lights.new(name, 'AREA'); l.shape = 'RECTANGLE'
    l.size, l.size_y, l.energy, l.color = size, size_y, power, color
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    o.visible_camera = False
    o.light_linking.receiver_collection = car   # light only the car: the floor stays black and just mirrors it
    return o

area('top', (0, 0, 5.0), 3.0, 7.0, 700)                                   # big overhead softbox
area('stripL', (-4.2, 0, 2.6), 0.3, 7.5, 420)                               # long side strips: the long highlight lines
area('stripR', (4.2, 0, 2.6), 0.3, 7.5, 420)
area('rimGold', (-1.5, -6.5, 1.8), 4.0, 1.2, 900, color=(1.0, 0.70, 0.30))       # warm brand rim from behind
area('kick', (0, 7.0, 1.2), 3.0, 0.6, 90)                                  # low front kick for the nose

# ── camera: orbit from front 3/4 around the rear to the far profile ──
cam_data = bpy.data.cameras.new('cam'); cam_data.lens = 55; cam_data.sensor_width = 36
cam_data.dof.use_dof = True; cam_data.dof.aperture_fstop = 5.6
cam = bpy.data.objects.new('cam', cam_data); sc.collection.objects.link(cam); sc.camera = cam
target = Vector((0, 0, 0.52))
cam_data.dof.focus_distance = 8.5

def ease(t):
    return t * t * (3 - 2 * t)

def place(i):
    t = i / (FRAMES - 1)
    e = ease(t)
    az = math.radians(-40 + 250 * e)        # 0 = looking at the nose (-Y), positive = around the car's right side
    r = 7.6 + 2.6 * t
    z = 1.05 + 0.35 * math.sin(math.pi * t)
    cam.location = Vector((r * math.sin(az), r * math.cos(az), z))   # nose points to +Y
    d = target - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam_data.dof.focus_distance = d.length

# ── render settings ──
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_adaptive_sampling = True
sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 6
sc.cycles.glossy_bounces = 4
sc.cycles.transmission_bounces = 4
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 88
sc.render.threads_mode = 'AUTO'

for i in range(start, end + 1):
    place(i)
    sc.render.filepath = f'{OUT}/f{i:03d}.jpg'
    bpy.ops.render.render(write_still=True)
    print('done', i, flush=True)
