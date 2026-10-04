"""Imagens dos 3 serviços: o carro preto do estúdio, enquadrado na área que cada serviço protege.

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

# ── câmera de cada serviço ──
cam_data = bpy.data.cameras.new('cam'); cam_data.sensor_width = 36
cam = bpy.data.objects.new('cam', cam_data); sc.collection.objects.link(cam); sc.camera = cam
shots = {   # az: 0 = de frente, 90 = lado direito; target = ponto que fica no centro
    'full':    dict(az=-38, r=7.0, z=1.35, target=(0, 0.1, 0.5), lens=50, f=5.6),    # o carro inteiro
    'parcial': dict(az=-22, r=4.1, z=1.55, target=(0, 1.55, 0.55), lens=50, f=4.0),  # frente: capô, para-lamas, para-choque
    'pontual': dict(az=70, r=3.1, z=0.85, target=(1.0, -0.35, 0.48), lens=45, f=2.8), # porta: maçaneta e soleira
}[which]
a = math_rad = __import__('math').radians(shots['az'])
cam.location = Vector((shots['r'] * __import__('math').sin(a), shots['r'] * __import__('math').cos(a), shots['z']))
d = Vector(shots['target']) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = shots['lens']
cam_data.dof.use_dof = True; cam_data.dof.aperture_fstop = shots['f']; cam_data.dof.focus_distance = d.length

sc.render.filepath = OUTFILE
bpy.ops.render.render(write_still=True)
print('ok', which, flush=True)
