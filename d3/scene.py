"""3D test clip in Blender (run with python3.11 + bpy):
python3.11 d3/scene.py still 60,250,350      -> build_3d/still_<f>.png
python3.11 d3/scene.py render 1 396           -> build_3d/frames/####.png
Characters are built from simple rounded shapes on a joint hierarchy of empties (Abdul Bari-like toy look)."""
import bpy, math, json, os, sys
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build_3d')
FPS = 24
LINES = json.load(open(os.path.join(OUT, 'lines.json')))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS

# ------------------------------------------------------------------ helpers
_mats = {}
def mat(name, rgb, rough=0.55, emit=0.0, sss=0.0, metal=0.0, alpha=1.0):
    if name in _mats: return _mats[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.3, 0.12, 0.08)
        b.inputs['Subsurface Scale'].default_value = 0.03
    if emit:
        b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
    _mats[name] = m; return m

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)   # sRGB -> linear

def empty(name, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o)
    o.empty_display_size = 0.05; o.parent = parent; o.location = loc; o.rotation_mode = 'XYZ'
    return o

def _finish(o, parent, m, smooth=True, sub=0):
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    if sub:
        mo = o.modifiers.new('s', 'SUBSURF'); mo.levels = sub; mo.render_levels = sub
    if m: o.data.materials.append(m)
    if parent: o.parent = parent
    return o

def sphere(name, parent, loc, scale, m, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    return _finish(o, parent, m)

def cyl(name, parent, loc, r, depth, m, rot=(0, 0, 0), verts=32, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    return _finish(o, parent, m)

def limb(name, parent, length, r, m, r_end=None, cap_m=None):
    """a rounded capsule hanging down (-Z) from the pivot"""
    c = cyl(name, parent, (0, 0, -length / 2), r, length, m, r2=(r_end if r_end else r))
    sphere(name + '_j', parent, (0, 0, 0), (r, r, r), cap_m or m)
    return c

def torus(name, parent, loc, R, r, m, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=12)
    o = bpy.context.object; o.name = name; o.scale = scale
    return _finish(o, parent, m)

def curve_line(name, parent, pts, bevel, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = bevel; cu.bevel_resolution = 4
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.parent = parent; cu.materials.append(m)
    return o

# ------------------------------------------------------------------ materials
SKIN_A = mat('skinA', hexc('#E7B48C'), 0.5, sss=0.15)
SKIN_N = mat('skinN', hexc('#C9906A'), 0.5, sss=0.15)
WHITE = mat('white', hexc('#f7f7f2'), 0.6)
KURTA = mat('kurta', hexc('#f4f4ee'), 0.75)
RED = mat('red', hexc('#D52B31'), 0.7)
NAVY = mat('navy', hexc('#33456b'), 0.8)
SHOE_W = mat('shoeW', hexc('#f0f0f0'), 0.4)
SHOE_B = mat('shoeB', hexc('#5a3b28'), 0.45)
HAIR_K = mat('hairK', hexc('#16110e'), 0.45)
HAIR_G = mat('hairG', hexc('#b4b1ad'), 0.6)
BEARD = mat('beard', hexc('#ecebe6'), 0.85)
EYE_W = mat('eyeW', (0.95, 0.95, 0.95), 0.15)
IRIS = mat('iris', hexc('#6b3d22'), 0.2)
PUPIL = mat('pupil', (0.01, 0.01, 0.01), 0.1)
SHINE = mat('shine', (1, 1, 1), 0.1, emit=3.0)
MOUTH = mat('mouth', hexc('#6e1f2a'), 0.5)
LIP = mat('lip', hexc('#c26a6a'), 0.5)
BROW_K = mat('browK', hexc('#22150f'), 0.6)
BROW_G = mat('browG', hexc('#8f8a85'), 0.6)
BLUSH = mat('blush', hexc('#f29a9a'), 0.6)
FRAME = mat('frame', hexc('#3a2a22'), 0.3, metal=0.3)
GOLD = mat('gold', hexc('#d4a640'), 0.3, metal=0.8)
LENS = mat('lens', hexc('#cfe6f2'), 0.05, alpha=0.25)


# ------------------------------------------------------------------ characters
def build_face(name, head, r, skin, kid=True, brow=BROW_K):
    """eyes, brows, nose, mouth on the front (-Y) of a head of radius r. Returns parts to animate."""
    P = {}
    for sx, side in ((-1, 'R'), (1, 'L')):
        ex, ez = sx * r * 0.36, r * 0.08
        eye = empty(f'{name}_eye{side}', head, (ex, -r * 0.86, ez))
        sphere(f'{name}_eyew{side}', eye, (0, 0, 0), (r * 0.2, r * 0.12, r * 0.24), EYE_W)
        look = empty(f'{name}_look{side}', eye, (0, 0, 0))
        sphere(f'{name}_iris{side}', look, (0, -r * 0.09, -r * 0.02), (r * 0.13, r * 0.05, r * 0.15), IRIS)
        sphere(f'{name}_pup{side}', look, (0, -r * 0.125, -r * 0.02), (r * 0.07, r * 0.03, r * 0.08), PUPIL)
        sphere(f'{name}_shine{side}', look, (r * 0.05, -r * 0.15, r * 0.05), (r * 0.03, r * 0.02, r * 0.03), SHINE, seg=12)
        # eyelid: a skin shell that slides down to blink / look down
        lid = empty(f'{name}_lid{side}', eye, (0, 0, 0))
        lid_mesh = sphere(f'{name}_lidm{side}', lid, (0, -r * 0.01, r * 0.2), (r * 0.215, r * 0.135, r * 0.13), skin)
        P['lid' + side] = lid
        P['look' + side] = look
        P['eye' + side] = eye
        # eyebrow
        b = empty(f'{name}_brow{side}', head, (ex, -r * 0.9, ez + r * 0.36))
        curve_line(f'{name}_browc{side}', b, [(-r * 0.17, 0, -r * 0.02), (0, 0, r * 0.04), (r * 0.17, 0, -r * 0.01)], r * (0.024 if kid else 0.03), brow)
        P['brow' + side] = b
        sphere(f'{name}_blush{side}', head, (sx * r * 0.55, -r * 0.72, -r * 0.22), (r * 0.17, r * 0.06, r * 0.1), BLUSH)
    sphere(f'{name}_nose', head, (0, -r * 0.98, -r * 0.12), (r * 0.12, r * 0.11, r * 0.1), skin)
    mouth = empty(f'{name}_mouth', head, (0, -r * 0.9, -r * 0.42))
    sphere(f'{name}_mouthm', mouth, (0, 0, 0), (r * 0.2, r * 0.08, r * 0.06), MOUTH)
    curve_line(f'{name}_smile', head, [(-r * 0.24, -r * 0.93, -r * 0.36), (0, -r * 0.99, -r * 0.47), (r * 0.24, -r * 0.93, -r * 0.36)], r * 0.025, LIP)
    P['mouth'] = mouth
    return P


def hand(name, wrist, skin, s):
    """palm + 4 fingers + thumb hanging down from the wrist pivot"""
    h = empty(name, wrist, (0, 0, 0))
    sphere(name + '_palm', h, (0, 0, -s * 0.9), (s * 0.95, s * 0.5, s * 1.0), skin)
    for i, fx in enumerate((-0.6, -0.2, 0.2, 0.6)):
        L = s * (1.0 if i in (1, 2) else 0.85)
        f = empty(f'{name}_f{i}', h, (fx * s, 0, -s * 1.7))
        limb(f'{name}_fm{i}', f, L, s * 0.24, skin)
        sphere(f'{name}_ft{i}', f, (0, 0, -L), (s * 0.24, s * 0.24, s * 0.24), skin)
    th = empty(name + '_th', h, (s * 0.85, -s * 0.25, -s * 0.6)); th.rotation_euler = (0, math.radians(-35), 0)
    limb(name + '_thm', th, s * 0.8, s * 0.26, skin)
    sphere(name + '_tht', th, (0, 0, -s * 0.8), (s * 0.26,) * 3, skin)
    return h


def build_person(name, kind):
    """kind 'ali' or 'nana'. Faces -Y. Returns dict of pivots."""
    J = {}
    if kind == 'ali':
        hipH, torsoL, headR, headUp, shW = 0.56, 0.40, 0.21, 0.22, 0.17
        L1, L2, T, S, limbR = 0.21, 0.19, 0.27, 0.25, 0.052
        skin = SKIN_A
    else:
        hipH, torsoL, headR, headUp, shW = 0.86, 0.58, 0.155, 0.2, 0.21
        L1, L2, T, S, limbR = 0.31, 0.28, 0.42, 0.40, 0.055
        skin = SKIN_N
    root = empty(name, None, (0, 0, 0)); J['root'] = root
    hips = empty(name + '_hips', root, (0, 0, hipH)); J['hips'] = hips
    # legs
    for sx, side in ((-1, 'R'), (1, 'L')):
        th = empty(f'{name}_thigh{side}', hips, (sx * shW * 0.5, 0, 0))
        limb(f'{name}_thm{side}', th, T, limbR * (1.25 if kind == 'ali' else 1.55), NAVY if kind == 'ali' else KURTA)
        kn = empty(f'{name}_knee{side}', th, (0, 0, -T))
        limb(f'{name}_shm{side}', kn, S, limbR * (1.15 if kind == 'ali' else 1.4), NAVY if kind == 'ali' else KURTA, r_end=limbR * (1 if kind == 'ali' else 1.2))
        ft = empty(f'{name}_foot{side}', kn, (0, 0, -S))
        sphere(f'{name}_shoe{side}', ft, (0, -0.05, -0.035), (0.065 if kind == 'ali' else 0.07, 0.12 if kind == 'ali' else 0.14, 0.045), SHOE_W if kind == 'ali' else SHOE_B)
        J['thigh' + side] = th; J['knee' + side] = kn; J['foot' + side] = ft
    torso = empty(name + '_torso', hips, (0, 0, 0)); J['torso'] = torso
    if kind == 'ali':
        # chubby red T-shirt body
        sphere(name + '_belly', torso, (0, 0, 0.2), (0.2, 0.16, 0.27), RED)
        sphere(name + '_pelvis', torso, (0, 0, 0.0), (0.17, 0.14, 0.09), NAVY)
        torus(name + '_collar', torso, (0, 0, 0.43), 0.07, 0.016, mat('redD', hexc('#a81e24'), 0.7))
    else:
        # long white kurta with button placket and a chest pocket
        cyl(name + '_kurta', torso, (0, 0, 0.06), 0.25, 0.74, KURTA, r2=0.19)
        sphere(name + '_chest', torso, (0, 0, 0.42), (0.21, 0.15, 0.17), KURTA)
        sphere(name + '_hem', torso, (0, 0, -0.31), (0.255, 0.21, 0.03), KURTA)
        for i in range(5): sphere(f'{name}_btn{i}', torso, (0, -0.165 + i * 0.006, 0.52 - i * 0.07), (0.012, 0.008, 0.012), WHITE, seg=12)
        cyl(name + '_pocket', torso, (0.1, -0.16, 0.42), 0.045, 0.004, mat('kd', hexc('#e2e2da'), 0.8), rot=(math.radians(90), 0, 0), verts=4)
        torus(name + '_collar', torso, (0, 0, 0.58), 0.065, 0.015, KURTA)
    sh = torsoL
    # neck + head
    neck = empty(name + '_neck', torso, (0, 0, sh)); J['neck'] = neck
    cyl(name + '_neckm', neck, (0, 0, 0.04), 0.05 if kind == 'ali' else 0.045, 0.08, skin)
    head = empty(name + '_head', neck, (0, 0, headUp)); J['head'] = head
    if kind == 'ali':
        sphere(name + '_headm', head, (0, 0, 0), (headR * 1.02, headR * 0.98, headR * 0.98), skin)
        sphere(name + '_cheeks', head, (0, -headR * 0.2, -headR * 0.35), (headR * 0.85, headR * 0.7, headR * 0.55), skin)
        for sx in (-1, 1): sphere(f'{name}_ear{sx}', head, (sx * headR * 1.0, 0.0, -0.01), (0.03, 0.02, 0.045), skin)
        # spiky black hair under a white topi
        for i in range(16):
            a = math.radians(-160 + i * 21)
            x, y = math.cos(a) * headR * 0.95, math.sin(a) * headR * 0.95
            cyl(f'{name}_spike{i}', head, (x, y, headR * 0.42), 0.035, 0.09, HAIR_K, rot=(math.atan2(-y, 1) * 0 + (-y / headR) * 0.9, (x / headR) * 0.9, 0), verts=8, r2=0.0)
        sphere(name + '_hair', head, (0, 0.02, headR * 0.3), (headR * 1.0, headR * 1.0, headR * 0.62), HAIR_K)
        topi = sphere(name + '_topi', head, (0, 0.01, headR * 0.55), (headR * 0.96, headR * 0.96, headR * 0.62), WHITE)
        torus(name + '_topib', head, (0, 0.01, headR * 0.48), headR * 0.93, 0.012, mat('topiR', hexc('#e3dfd0'), 0.7))
        J['face'] = build_face(name, head, headR, skin, True)
    else:
        sphere(name + '_headm', head, (0, 0, 0), (headR, headR * 0.98, headR * 1.12), skin)
        for sx in (-1, 1): sphere(f'{name}_ear{sx}', head, (sx * headR * 1.0, 0.01, 0.0), (0.022, 0.016, 0.04), skin)
        sphere(name + '_hair', head, (0, 0.025, headR * 0.35), (headR * 1.04, headR * 1.02, headR * 0.82), HAIR_G)
        J['face'] = build_face(name, head, headR, skin, False, BROW_G)
        # short white beard round the jaw, moustache
        sphere(name + '_beard', head, (0, -headR * 0.35, -headR * 0.72), (headR * 0.92, headR * 0.75, headR * 0.55), BEARD)
        sphere(name + '_must', head, (0, -headR * 0.92, -headR * 0.32), (headR * 0.32, headR * 0.08, headR * 0.07), BEARD)
        # aviator glasses
        for sx in (-1, 1):
            torus(f'{name}_lensr{sx}', head, (sx * headR * 0.36, -headR * 0.99, headR * 0.06), headR * 0.22, 0.006, FRAME, rot=(math.radians(90), 0, 0), scale=(1, 1, 1.12))
            sphere(f'{name}_lens{sx}', head, (sx * headR * 0.36, -headR * 0.985, headR * 0.06), (headR * 0.21, 0.004, headR * 0.24), LENS)
            cyl(f'{name}_arm{sx}', head, (sx * headR * 0.85, -headR * 0.5, headR * 0.1), 0.004, headR * 0.95, GOLD, rot=(math.radians(90), 0, 0), verts=8)
        cyl(name + '_bridge', head, (0, -headR * 1.0, headR * 0.16), 0.004, headR * 0.3, GOLD, rot=(0, math.radians(90), 0), verts=8)
    # arms
    for sx, side in ((-1, 'R'), (1, 'L')):
        shp = empty(f'{name}_shoulder{side}', torso, (sx * (shW + 0.015), 0, sh - 0.06))
        if kind == 'ali':
            limb(f'{name}_uam{side}', shp, L1, limbR, skin)
            cyl(f'{name}_sleeve{side}', shp, (0, 0, -0.05), limbR * 1.55, 0.12, RED, r2=limbR * 1.35)
            sphere(f'{name}_shcap{side}', shp, (0, 0, -0.01), (limbR * 1.35,) * 3, RED)
        else:
            limb(f'{name}_uam{side}', shp, L1, limbR * 1.25, KURTA)
        el = empty(f'{name}_elbow{side}', shp, (0, 0, -L1))
        if kind == 'ali': limb(f'{name}_fam{side}', el, L2, limbR * 0.95, skin, r_end=limbR * 0.8)
        else:
            limb(f'{name}_fam{side}', el, L2 * 0.85, limbR * 1.2, KURTA, r_end=limbR * 1.05)
            cyl(f'{name}_wristm{side}', el, (0, 0, -L2 * 0.92), limbR * 0.8, L2 * 0.18, skin)
        wr = empty(f'{name}_wrist{side}', el, (0, 0, -L2))
        hand(f'{name}_hand{side}', wr, skin, 0.028 if kind == 'ali' else 0.032)
        J['shoulder' + side] = shp; J['elbow' + side] = el; J['wrist' + side] = wr
    J['dims'] = dict(hipH=hipH, T=T, S=S)
    return J


# ------------------------------------------------------------------ masjid
def build_masjid():
    W_ = 14
    floor = cyl('floor', None, (0, 0, -0.01), 1, 0.02, mat('carpet', hexc('#b5383a'), 0.9), verts=4)
    floor.scale = (W_ / 1.41, W_ / 1.41, 1); floor.rotation_euler = (0, 0, math.radians(45))
    for i, y in enumerate((-2.2, -1.0, 0.25, 1.5, 2.75)):
        cyl(f'saff{i}', None, (0, y, 0.003), 0.02, W_, GOLD, rot=(0, math.radians(90), 0), verts=6).scale = (1, 1.6, 1)
        for k in range(-8, 9):
            o = sphere(f'dia{i}_{k}', None, (k * 0.8, y + 0.6, 0.002), (0.12, 0.12, 0.004), mat('carpet2', hexc('#d4573f'), 0.9), seg=8)
            o.rotation_euler = (0, 0, math.radians(45))
    wall_m = mat('wall', hexc('#f3e6cc'), 0.9)
    back = cyl('backwall', None, (0, 4.2, 2), 1, 0.2, wall_m, rot=(math.radians(90), 0, 0), verts=4)
    back.scale = (W_ / 1.41, 3 / 1.41 * 2, 1); back.rotation_euler = (math.radians(90), math.radians(45), 0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.2, 2)); bw = bpy.context.object; bw.scale = (W_, 0.2, 4.2); bw.data.materials.append(wall_m)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(side * 5.5, 0, 2)); sw = bpy.context.object; sw.scale = (0.2, 10, 4.2); sw.data.materials.append(wall_m)
    bpy.data.objects.remove(back)
    win = mat('win', hexc('#8fc8ea'), 0.2, emit=0.35)
    trim = mat('trim', hexc('#8a6d3b'), 0.5)
    for i, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 4.09, 1.55)); o = bpy.context.object; o.scale = (0.9, 0.02, 1.3); o.data.materials.append(win)
        sphere(f'arch{i}', None, (x, 4.09, 2.2), (0.45, 0.015, 0.45), win)
        torus(f'archT{i}', None, (x, 4.07, 2.2), 0.46, 0.03, trim, rot=(math.radians(90), 0, 0))
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 4.075, 1.55)); o = bpy.context.object; o.scale = (0.04, 0.02, 1.3); o.data.materials.append(trim)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 4.075, 1.6)); o = bpy.context.object; o.scale = (0.9, 0.02, 0.04); o.data.materials.append(trim)
    # columns and lamps
    col = mat('col', hexc('#e8d7b4'), 0.7)
    for x in (-2.4, 2.4):
        cyl(f'col{x}', None, (x, 3.6, 2), 0.16, 4, col)
        cyl(f'colb{x}', None, (x, 3.6, 0.08), 0.22, 0.16, col)
    lampm = mat('lamp', hexc('#ffd77a'), 0.3, emit=6.0)
    for x, y in ((-2.0, 1.4), (0.0, 2.2), (2.0, 1.4), (-3.5, -1.0), (3.5, -1.0)):
        cyl(f'cord{x}{y}', None, (x, y, 3.3), 0.006, 1.6, GOLD, verts=6)
        sphere(f'lamp{x}{y}', None, (x, y, 2.45), (0.13, 0.13, 0.16), lampm)
        cyl(f'lampc{x}{y}', None, (x, y, 2.62), 0.1, 0.08, GOLD, r2=0.04)
        bpy.ops.object.light_add(type='POINT', location=(x, y, 2.3)); L = bpy.context.object; L.data.energy = 25; L.data.color = (1, 0.82, 0.55); L.data.shadow_soft_size = 0.3
    # a green mihrab panel on the back wall between the columns (decorative)
    green = mat('green', hexc('#2f7d5b'), 0.6)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.08, 1.25)); o = bpy.context.object; o.scale = (1.3, 0.04, 2.0); o.data.materials.append(green)
    sphere('mihrabA', None, (0, 4.07, 2.25), (0.65, 0.03, 0.65), green)
    torus('mihrabT', None, (0, 4.05, 2.25), 0.66, 0.035, GOLD, rot=(math.radians(90), 0, 0))
    for k in range(7):
        sphere(f'star{k}', None, (-0.45 + k * 0.15, 4.04, 1.85 + 0.12 * (k % 2)), (0.035, 0.01, 0.035), mat('starm', hexc('#f5d06b'), 0.3, emit=2.0), seg=8)


# ------------------------------------------------------------------ build scene
build_masjid()
ALI = build_person('ali', 'ali')
NANA = build_person('nana', 'nana')

bpy.ops.object.light_add(type='SUN', location=(2, -3, 6)); sun = bpy.context.object
sun.data.energy = 1.6; sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30)); sun.data.angle = math.radians(8)
bpy.ops.object.light_add(type='AREA', location=(1.5, -4, 2.6)); key = bpy.context.object
key.data.energy = 140; key.data.size = 3; key.rotation_euler = (math.radians(70), 0, math.radians(20))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (*hexc('#f6e3c0'), 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.4

bpy.ops.object.camera_add(location=(2.6, -4.6, 1.35)); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 38
tgt = empty('camTarget', None, (0.0, 0.0, 0.85))
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'

# ------------------------------------------------------------------ animation helpers
R = math.radians
def key(o, frame, rot=None, loc=None, scale=None):
    if rot is not None: o.rotation_euler = [R(a) for a in rot]; o.keyframe_insert('rotation_euler', frame=frame)
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=frame)
    if scale is not None: o.scale = scale; o.keyframe_insert('scale', frame=frame)

def F(t): return int(round(t * FPS)) + 1

def pose(J, frame, p, kind):
    """named body poses. Arms: X rotation negative = forward, Y rotation = out to the side."""
    sR, sL, eR, eL = J['shoulderR'], J['shoulderL'], J['elbowR'], J['elbowL']
    d = dict(
        stand=dict(sR=(0, 6, 0), sL=(0, -6, 0), eR=(-12, 0, 0), eL=(-12, 0, 0), torso=(0, 0, 0)),
        wave=dict(sR=(0, 6, 0), sL=(-15, -160, 0), eR=(-12, 0, 0), eL=(-20, 0, -40), torso=(0, 0, 0)),
        talk=dict(sR=(0, 6, 0), sL=(-45, -10, 0), eR=(-12, 0, 0), eL=(-60, 0, 0), torso=(0, 0, 0)),
        takbir=dict(sR=(-18, 72, 0), sL=(-18, -72, 0), eR=(0, 100, 0), eL=(0, -100, 0), torso=(0, 0, 0)),
        qiyam=dict(sR=(-18, -14, 0), sL=(-22, 14, 0), eR=(-100, 0, 35), eL=(-96, 0, -35), torso=(0, 0, 0)),
        ruku=dict(sR=(-30, 4, 0), sL=(-30, -4, 0), eR=(0, 0, 0), eL=(0, 0, 0), torso=(85, 0, 0)),
    )[p]
    key(sR, frame, d['sR']); key(sL, frame, d['sL']); key(eR, frame, d['eR']); key(eL, frame, d['eL'])
    key(J['torso'], frame, d['torso'])
    # head in line with the back in ruku, looking at the floor
    key(J['neck'], frame, (12, 0, 0) if p == 'ruku' else (0, 0, 0))
    for side in 'RL': key(J['wrist' + side], frame, (0, 0, 0))

def legs_stand(J, frame):
    for s in 'RL':
        key(J['thigh' + s], frame, (0, 0, 0)); key(J['knee' + s], frame, (0, 0, 0)); key(J['foot' + s], frame, (0, 0, 0))

def walk(J, f0, f1, x0, x1, y, facing, step_len):
    """walk from x0 to x1 (in X), facing angle (deg about Z)"""
    n = f1 - f0
    for f in range(f0, f1 + 1, 2):
        u = (f - f0) / n
        x = x0 + (x1 - x0) * (u * u * (3 - 2 * u))
        ph = (f - f0) / FPS * 1.8 * 2 * math.pi
        a = math.sin(ph) * 24
        key(J['root'], f, rot=(0, 0, facing), loc=(x, y, 0))
        key(J['hips'], f, loc=(0, 0, J['dims']['hipH'] - abs(math.sin(ph)) * 0.012))
        key(J['thighR'], f, (a, 0, 0)); key(J['thighL'], f, (-a, 0, 0))
        key(J['kneeR'], f, (-max(0, math.sin(ph + 1.6)) * 38 - 4, 0, 0)); key(J['kneeL'], f, (-max(0, -math.sin(ph + 1.6)) * 38 - 4, 0, 0))
        key(J['shoulderR'], f, (-a * 0.8, 6, 0)); key(J['shoulderL'], f, (a * 0.8, -6, 0))
        key(J['elbowR'], f, (-20, 0, 0)); key(J['elbowL'], f, (-20, 0, 0))
        key(J['torso'], f, (4, 0, math.sin(ph) * 3))

def talk_mouth(face, line, t0):
    m = face['mouth']; env = line['env']
    for i, v in enumerate(env):
        if i % 2: continue
        key(m, F(t0 + i / FPS), scale=(1 + 0.15 * v, 1, 0.35 + 3.4 * v))
    key(m, F(t0 + line['d'] + 0.08), scale=(1, 1, 0.35))

def blink(face, frames):
    for f in frames:
        for s in 'RL':
            key(face['lid' + s], f - 2, loc=(0, 0, 0)); key(face['lid' + s], f, loc=(0, 0, -face['eye' + s].scale.z * 0.0 - 0.035)); key(face['lid' + s], f + 3, loc=(0, 0, 0))

def eyes_down(face, frame, amount, r):
    for s in 'RL':
        key(face['lid' + s], frame, loc=(0, 0, -r * 0.13 * amount))
        key(face['look' + s], frame, rot=(-28 * amount, 0, 0))

def brows(face, frame, up):
    for s in 'RL': key(face['brow' + s], frame, loc=(face['brow' + s].location.x, face['brow' + s].location.y, face['brow' + s].location.z + up))

# ------------------------------------------------------------------ the 15-second scene

B_AKBAR = None
A_SALAM, N_REPLY, N_AKBAR = LINES[0], LINES[1], LINES[2]
T_SALAM, T_REPLY, T_AKBAR = 2.5, 4.7, 11.0
END = 16.5
sc.frame_start, sc.frame_end = 1, F(END)

for J in (ALI, NANA):
    for s in 'RL':
        for o in (J['face']['lid' + s], J['face']['look' + s]): key(o, 1, loc=(0, 0, 0), rot=(0, 0, 0))
    key(J['face']['mouth'], 1, scale=(1, 1, 0.35))

# Nana stands waiting, slightly turned toward Ali's side
key(NANA['root'], 1, rot=(0, 0, -25), loc=(0.22, 0.05, 0)); key(NANA['hips'], 1, loc=(0, 0, NANA['dims']['hipH']))
legs_stand(NANA, 1); pose(NANA, 1, 'stand', 'nana')
key(NANA['head'], 1, rot=(0, 0, 0))
# Ali walks in from the left, toward Nana
walk(ALI, 1, F(2.3), -2.6, -0.75, 0.05, 90, 0.3)
legs_stand(ALI, F(2.4)); key(ALI['hips'], F(2.4), loc=(0, 0, ALI['dims']['hipH'])); key(ALI['torso'], F(2.4), (0, 0, 0))
pose(ALI, F(2.4), 'stand', 'ali')
key(ALI['root'], F(2.4), rot=(0, 0, 70), loc=(-0.75, 0.05, 0))
# salam with a wave
pose(ALI, F(T_SALAM + 0.2), 'wave', 'ali')
for k in range(4):
    key(ALI['elbowL'], F(T_SALAM + 0.35 + k * 0.3), (0, 0, -40 if k % 2 == 0 else -10))
talk_mouth(ALI['face'], A_SALAM, T_SALAM)
brows(ALI['face'], F(T_SALAM), 0.0); brows(ALI['face'], F(T_SALAM + 0.3), 0.012); brows(ALI['face'], F(T_SALAM + 1.8), 0.0)
pose(ALI, F(T_SALAM + A_SALAM['d'] + 0.3), 'stand', 'ali')
# Nana turns to Ali and answers
key(NANA['root'], F(T_REPLY - 0.6), rot=(0, 0, -25), loc=(0.22, 0.05, 0))
key(NANA['root'], F(T_REPLY - 0.1), rot=(0, 0, -60), loc=(0.22, 0.05, 0))
pose(NANA, F(T_REPLY - 0.1), 'stand', 'nana')
pose(NANA, F(T_REPLY + 0.4), 'talk', 'nana')
key(NANA['shoulderL'], F(T_REPLY + 1.6), (-55, -14, 0)); key(NANA['shoulderL'], F(T_REPLY + 2.8), (-42, -8, 0))
key(NANA['head'], F(T_REPLY + 0.2), rot=(0, 0, 0)); key(NANA['head'], F(T_REPLY + 1.0), rot=(-6, 0, 0)); key(NANA['head'], F(T_REPLY + 2.0), rot=(2, 0, 0))
talk_mouth(NANA['face'], N_REPLY, T_REPLY)
pose(NANA, F(T_REPLY + N_REPLY['d'] + 0.2), 'stand', 'nana')
# Ali smiles and nods
key(ALI['head'], F(T_REPLY + 3.6), rot=(0, 0, 0)); key(ALI['head'], F(T_REPLY + 3.9), rot=(-10, 0, 0)); key(ALI['head'], F(T_REPLY + 4.2), rot=(0, 0, 0))
# both face the qibla (toward the camera side, -Y), shoulder to shoulder
t_turn = T_REPLY + N_REPLY['d'] + 0.3
key(ALI['root'], F(t_turn), rot=(0, 0, 70), loc=(-0.75, 0.05, 0))
walk(ALI, F(t_turn), F(t_turn + 1.0), -0.75, -0.27, 0.05, 25, 0.2)
legs_stand(ALI, F(t_turn + 1.1)); key(ALI['hips'], F(t_turn + 1.1), loc=(0, 0, ALI['dims']['hipH'])); key(ALI['torso'], F(t_turn + 1.1), (0, 0, 0))
pose(ALI, F(t_turn + 1.1), 'stand', 'ali')
key(ALI['root'], F(t_turn + 1.1), rot=(0, 0, 0), loc=(-0.27, 0.05, 0))
key(NANA['root'], F(t_turn + 0.4), rot=(0, 0, -60), loc=(0.22, 0.05, 0)); key(NANA['root'], F(t_turn + 1.1), rot=(0, 0, 0), loc=(0.22, 0.05, 0))
for J, r in ((ALI, 0.21), (NANA, 0.155)): eyes_down(J['face'], F(t_turn + 1.2), 0.0, r); eyes_down(J['face'], F(t_turn + 1.5), 1.0, r)
# takbir, Allahu Akbar
for J, kind in ((ALI, 'ali'), (NANA, 'nana')):
    pose(J, F(T_AKBAR - 0.1), 'stand', kind)
    pose(J, F(T_AKBAR + 0.5), 'takbir', kind)
    pose(J, F(T_AKBAR + 1.3), 'takbir', kind)
    pose(J, F(T_AKBAR + 1.9), 'qiyam', kind)
    pose(J, F(T_AKBAR + 3.0), 'qiyam', kind)
    pose(J, F(T_AKBAR + 3.7), 'ruku', kind)
talk_mouth(NANA['face'], N_AKBAR, T_AKBAR)
blink(ALI['face'], [F(1.3), F(5.6), F(9.2)]); blink(NANA['face'], [F(3.0), F(8.1)])

# ------------------------------------------------------------------ camera move and render settings
key(cam, 1, loc=(-0.6, -4.6, 1.25)); key(cam, F(4.5), loc=(-1.0, -4.3, 1.3)); key(cam, F(10.5), loc=(-1.9, -3.7, 1.25)); key(cam, F(END), loc=(-2.4, -3.3, 1.2))
key(tgt, 1, loc=(-0.7, 0.0, 0.8)); key(tgt, F(4.5), loc=(-0.25, 0.05, 0.85)); key(tgt, F(10.5), loc=(0.0, 0.05, 0.8)); key(tgt, F(END), loc=(0.0, 0.05, 0.7))
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'

sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get('SAMPLES', '14'))
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 4
sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = -0.2

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for fr in [int(x) for x in sys.argv[2].split(',')]:
            sc.frame_set(fr); sc.render.filepath = os.path.join(OUT, f'still_{fr}.png'); bpy.ops.render.render(write_still=True)
    elif mode == 'render':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(os.path.join(OUT, 'frames'), exist_ok=True)
        for fr in range(a, b + 1):
            p = os.path.join(OUT, 'frames', f'{fr:04d}.png')
            if os.path.exists(p): continue
            sc.frame_set(fr); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    elif mode == 'save':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'scene.blend'))
