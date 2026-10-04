"""Imagens dos 3 serviços: o carro preto do estúdio com a área protegida pela película marcada em dourado.

usage: python3 render_servicos.py full|parcial|pontual WIDTH HEIGHT SAMPLES OUT.jpg
(reaproveita a cena de render_topo.py: estúdio, piso espelhado, tinta preta)
"""
import sys, math
import bpy
from mathutils import Vector

which, W, H, SAMPLES, OUTFILE = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
HERE = __file__.rsplit('/', 1)[0]
src = open(HERE + '/render_topo.py').read()
sys.argv = [sys.argv[0], '0', '0', str(W), str(H), str(SAMPLES), '/tmp']
scene_code = src.split('# ── camera')[0].replace("HERE = __file__.rsplit('/', 1)[0]", 'HERE = %r' % HERE)
exec(scene_code)
exec(src.split('# ── render settings ──')[1].split('for i in range')[0])

# ── película: brilho dourado só na área do serviço (posição no mundo: +Y = frente, Z = altura) ──
mat = M['Body_Color']
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
geo = nt.nodes.new('ShaderNodeNewGeometry')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(geo.outputs['Position'], sep.inputs[0])
X, Y, Z = sep.outputs['X'], sep.outputs['Y'], sep.outputs['Z']

def math(op, a, b=0.0):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op
    for i, v in enumerate((a, b)):
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]

def between(v, lo, hi):
    return math('MULTIPLY', math('GREATER_THAN', v, lo), math('LESS_THAN', v, hi))

def band(v, at, width):            # linha fina na borda da área protegida
    return math('LESS_THAN', math('ABSOLUTE', math('SUBTRACT', v, at)), width)

if which == 'full':
    area_mask = 1.0
    edge = None
elif which == 'parcial':
    area_mask = math('GREATER_THAN', Y, 0.85)                       # capô, para-lamas e para-choque
    edge = band(Y, 0.85, 0.02)
else:
    sill = math('MULTIPLY', math('LESS_THAN', Z, 0.36), between(Y, -1.25, 0.95))      # soleiras
    handle = math('MULTIPLY', between(Z, 0.66, 0.86), between(Y, -0.55, -0.05))      # região da maçaneta
    trunk = math('MULTIPLY', math('LESS_THAN', Y, -1.95), between(Z, 0.72, 0.9))      # borda do porta-malas
    area_mask = math('MAXIMUM', math('MAXIMUM', sill, handle), trunk)
    edge = None

# brilho fraco de base + reflexo dourado nas curvas (onde a superfície vira de lado para a câmera), como película
lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
facing = math('POWER', lw.outputs['Facing'], 4.0)
base = {'full': 0.012, 'parcial': 0.03, 'pontual': 0.22}[which]   # áreas pequenas (pontual) precisam de mais brilho para aparecer
sheen = math('ADD', math('MULTIPLY', facing, 0.6), base)
strength = sheen if isinstance(area_mask, float) else math('MULTIPLY', area_mask, sheen)
if edge is not None:
    strength = math('ADD', strength, math('MULTIPLY', edge, 3.5))
emi = nt.nodes.new('ShaderNodeEmission')
emi.inputs['Color'].default_value = (1.0, 0.74, 0.3, 1)
if isinstance(strength, float): emi.inputs['Strength'].default_value = strength
else: nt.links.new(strength, emi.inputs['Strength'])
add = nt.nodes.new('ShaderNodeAddShader')
nt.links.new(bsdf.outputs[0], add.inputs[0]); nt.links.new(emi.outputs[0], add.inputs[1])
nt.links.new(add.outputs[0], out.inputs['Surface'])

# ── câmera de cada serviço ──
cam_data = bpy.data.cameras.new('cam'); cam_data.sensor_width = 36
cam = bpy.data.objects.new('cam', cam_data); sc.collection.objects.link(cam); sc.camera = cam
shots = {
    'full':    dict(az=-35, r=8.2, z=1.5, target=(0, 0, 0.5), lens=50),
    'parcial': dict(az=-28, r=6.2, z=2.3, target=(0, 1.3, 0.55), lens=50),
    'pontual': dict(az=95, r=5.2, z=1.1, target=(0, -0.4, 0.55), lens=45),
}[which]
a = math_rad = __import__('math').radians(shots['az'])
cam.location = Vector((shots['r'] * __import__('math').sin(a), shots['r'] * __import__('math').cos(a), shots['z']))
d = Vector(shots['target']) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = shots['lens']

sc.render.filepath = OUTFILE
bpy.ops.render.render(write_still=True)
print('ok', which, flush=True)
