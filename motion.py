"""Livelier 2D movement for the chars2 characters, added on top of any scene function without rewriting it.

1. Smooth changes: the scene is sampled at a few nearby times, and each character's numbers (arm angles, lean,
   position, facing, expression) are averaged with a bell-shaped weight, so a pose that used to snap now eases in
   and out over about 0.3 s. Fast things (mouth, blinks, walking, bouncing) are not averaged.
2. Idle life: breathing, a slow body sway, small head tilts, glances, natural irregular blinks, nods and raised
   brows while talking. During salah poses only breathing and blinks are added, so the prayer stays still.

Use:  import motion; motion.install(render_module)  then  name, cam, lay, over, texts = motion.scene(t)
"""
import math
import chars2 as C

NAMES = ('ali', 'bilal', 'zaid', 'maryam', 'nana')
KIND = {'ali': 'kid', 'bilal': 'kid', 'zaid': 'kid', 'maryam': 'girl', 'nana': 'nana'}
ORIG = {n: getattr(C, n) for n in NAMES}
ORIG['bilal'] = lambda st, _a=ORIG['ali']: _a(st, C.BILAL_LOOK)     # chars2.bilal calls the (patched) module-level ali
ORIG['zaid'] = lambda st, _a=ORIG['ali']: _a(st, C.ZAID_LOOK)
FAST = {'talk', 'blink', 'walk', 'bob'}                 # never averaged
STILL_POSES = {'takbir', 'qiyam', 'ruku', 'sajda', 'jalsa'}       # salah: no sway, no head movement
SIGMA = 2.6                                             # frames
REACH = 6                                               # frames each side

_rec = None          # list while recording, None while drawing for real
_M = None            # the render module


def _wrap(n):
    def f(st):
        if _rec is None: return ORIG[n](st)
        _rec.append((n, dict(st))); return f'\x00{len(_rec) - 1}\x00'
    f.__name__ = n
    return f


def register(mod, n, kind='nana'):
    """add a character drawn by mod.<n>(st) (e.g. Nesting Stories people) to the motion layer; call before install()"""
    global NAMES
    if n in ORIG: return
    ORIG[n] = getattr(mod, n); KIND[n] = kind; NAMES = NAMES + (n,); setattr(mod, n, _wrap(n))


def install(mod):
    """patch chars2 and the render module so scene() records characters instead of drawing them"""
    global _M
    _M = mod
    for n in NAMES: setattr(C, n, _wrap(n))
    if hasattr(mod, 'KIDS'):
        mod.KIDS = tuple((w, getattr(C, fn.__name__)) for w, fn in mod.KIDS)


def _record(t):
    global _rec
    _rec = []
    try: out = _M.scene(t)
    finally: rec, _rec = _rec, None
    return out, rec


# ------------------------------------------------------------------ helpers
def _h(*a):
    """deterministic 0..1 hash"""
    x = math.sin(sum((i + 1) * 12.9898 * v for i, v in enumerate(a))) * 43758.5453
    return x - math.floor(x)


def _ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def _expr_dict(e):
    if isinstance(e, dict): return dict(e)
    return C.ex(e)


def _full(n, st):
    """the state after the pose is applied, with defaults filled in, so two states can be averaged"""
    q = C.apply_pose(st, KIND[n])
    if q.get('pose') not in STILL_POSES and q.get('pose') != 'sit' and q.get('walk') is None:
        # standing: both arms in front of the body so neither hand disappears behind it,
        # the far arm hanging a little out at the side
        q.setdefault('arm_f', 6); q.setdefault('arm_b', -10); q['arms_front'] = True
        for k, a in (('elb_f', 'arm_f'), ('elb_b', 'arm_b')):
            v = q[a]; q.setdefault(k, 12 if v < 40 else (25 if v < 120 else 30))
    if not q.get('profile') and q.get('walk') is None and q.get('pose') != 'sit' and 'foot' not in q:
        q['foot'] = 'front'                                   # toes point at the viewer when standing
    for k, v in (('lean', 0), ('head_tilt', 0), ('look_y', 0), ('face', 1), ('s', 1)): q.setdefault(k, v)
    q['_expr'] = _expr_dict(q.get('expr'))
    return q


def _blend(samples):
    """samples: [(weight, state)] with the current state first"""
    cur = dict(samples[0][1]); tw = sum(w for w, _ in samples)
    for k, v in samples[0][1].items():
        if k in FAST or k.startswith('_') or isinstance(v, bool) or not isinstance(v, (int, float)): continue
        acc = 0.0
        for w, s in samples:
            sv = s.get(k, v)
            acc += w * (sv if isinstance(sv, (int, float)) and not isinstance(sv, bool) else v)
        cur[k] = acc / tw
    if 'legs' in cur and all('legs' in s for _, s in samples):
        cur['legs'] = tuple(sum(w * s['legs'][i] for w, s in samples) / tw for i in range(6))
    e = dict(samples[0][1]['_expr'])
    for k, v in e.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            e[k] = sum(w * s['_expr'].get(k, v) for w, s in samples) / tw
    cur['_expr'] = e
    return cur


def _blink(t, seed):
    """irregular blinks every 2-5 s, now and then a double blink"""
    T, k = (seed * 1.7) % 3.0, 0
    while True:
        nxt = T + 2.0 + 3.0 * _h(seed, k)
        if nxt > t: break
        T, k = nxt, k + 1
    d = t - T
    def one(x): return 1.0 if 0.03 <= x < 0.10 else (0.5 if 0 <= x < 0.03 or 0.10 <= x < 0.14 else 0.0)
    v = one(d)
    if _h(seed, k, 7) < 0.25: v = max(v, one(d - 0.2))
    return v


def _glance(t, seed):
    """the eyes rest on something for 1-3 s, then flick to something else"""
    seg = 1.0 + 2.0 * _h(seed, 3)
    k = math.floor((t + seed) / seg); x = (t + seed) - k * seg
    a = (_h(seed, k) - 0.5) * 0.7; b = (_h(seed, k - 1) - 0.5) * 0.7
    return b + (a - b) * _ease(x / 0.09)


def _alive(n, raw, st, t, seed):
    s = dict(st)
    pose = raw.get('pose')
    still = pose in STILL_POSES or raw.get('profile')
    breath = math.sin(2 * math.pi * (t / 3.4) + seed)
    s['bob'] = s.get('bob', 0) - 1.6 * (0.5 + 0.5 * breath)
    talk = s.get('talk', 0) or 0
    if 'blink' in raw:
        s['blink'] = _blink(t, seed)
    e = s['_expr']
    if not still:
        walking = raw.get('walk') is not None
        if not walking and pose in (None, 'stand'):
            s['lean'] = s.get('lean', 0) + 1.3 * math.sin(2 * math.pi * t / 5.3 + seed * 2)
        nod = 3.2 * talk * math.sin(t * 5.2 + seed) + 2.0 * math.sin(2 * math.pi * t / 4.4 + seed * 3)
        s['head_tilt'] = s.get('head_tilt', 0) + nod
        if 'look' not in raw: s['look'] = 0.3 + _glance(t, seed)
        e = dict(e); e['raise_'] = e.get('raise_', 0) + 0.35 * min(1, talk) * (0.5 + 0.5 * math.sin(t * 3.1 + seed))
    s['expr'] = e
    return s


# ------------------------------------------------------------------ main entry
def scene(t, fps=None):
    fps = fps or _M.FPS
    out, rec = _record(t)
    name0 = _M.shot_at(t)['name']
    near = []
    for d in range(-REACH, REACH + 1):
        if d == 0: continue
        tt = t + d / fps
        if tt < 0 or _M.shot_at(tt)['name'] != name0: continue
        _, r2 = _record(tt)
        if [n for n, _ in r2] != [n for n, _ in rec]: continue
        near.append((math.exp(-0.5 * (d / SIGMA) ** 2), r2))
    states = []
    for i, (n, raw) in enumerate(rec):
        cur = _full(n, raw)
        samples = [(1.0, cur)] + [(w, _full(n, r2[i][1])) for w, r2 in near]
        st = _blend(samples)
        if abs(st.get('face', 1)) < 0.12: st['face'] = 0.12 if st['face'] >= 0 else -0.12
        st = _alive(n, raw, st, t, seed=i * 1.618 + NAMES.index(n) * 0.7)
        st.pop('pose', None); st.pop('_expr', None)
        states.append((n, st))
    name, cam, lay, over, texts = out
    if lay:
        parts = lay.split('\x00')
        lay = ''.join(ORIG[states[int(p)][0]](states[int(p)][1]) if k % 2 else p for k, p in enumerate(parts))
    return name, cam, lay, over, texts
