"""Grown-up characters for Nesting Stories, on the chars2 body (the same skeleton and poses as Nana).

  chacha(st)  Rasheed Chacha: 72, bald on top with grey side hair, big grey moustache, thick black glasses,
              light kameez-shalwar with a brown waistcoat.
  imran(st)   Imran: young Hyderabadi software engineer, black hair, neat short beard, thin glasses,
              light-blue shirt tucked into grey trousers with a belt.
  abba_photo(x, y, s, glow)   Imran's late father in a photo frame on the wall.
State keys are the same as chars2 (x, y, s, face, walk, talk, blink, expr, look, arm_f/arm_b, elb_f/elb_b,
hand_f/hand_b, hold_f, hold_b, lean, head_tilt, bob ...).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chars2 as C
from chars2 import SW, shade, arm, leg, face, ex, gait, apply_pose, _arms_state, _shoulder_lift

CHACHA = dict(skin='#C98E62', kameez='#d7dde0', kameez_d='#b9c2c6', vest='#7a5232', pants='#d7dde0', shoe='#4a3426',
              hair='sidepart', facial='none', glasses=None, kind='nana', outfit='kameez', broad=1.08, shape='square')
IMRAN = dict(skin='#BF845A', shirt='#8fc1e8', shirt_d='#6fa3cc', pants='#434b58', shoe='#2b2b2b', belt='#5a3b25',
             hair='short', facial='none', glasses=None, kind='ali', outfit='shirt')


def _head(L, st, hy):
    sk = L['skin']; g = ''
    if L['hair'] == 'short':   # back hair mass behind the head
        g += f'<path d="M-64,{hy+4} Q-70,{hy-70} 0,{hy-84} Q70,{hy-70} 64,{hy+4} Z" fill="#1c1410" {SW(4)}/>'
    g += f'<ellipse cx="-58" cy="{hy+6}" rx="13" ry="18" fill="{shade(sk,.94)}" {SW(4)}/><ellipse cx="62" cy="{hy+6}" rx="12" ry="17" fill="{sk}" {SW(4)}/>'
    if L.get('shape') == 'square':   # long face, a little squarish at the jaw, with soft rounded corners
        g += (f'<path d="M-60,{hy-24} Q-62,{hy+44} -52,{hy+72} Q-40,{hy+98} 0,{hy+100} Q40,{hy+98} 54,{hy+72} Q64,{hy+44} 62,{hy-24} '
              f'Q60,{hy-94} 0,{hy-96} Q-58,{hy-94} -60,{hy-24}Z" fill="{sk}" {SW()}/>')
        g += f'<path d="M-20,{hy+86} Q0,{hy+92} 22,{hy+86}" fill="none" stroke="#3b2a20" stroke-width="2.5" opacity=".28"/>'
    else:
        g += f'<path d="M-60,{hy-10} Q-62,{hy+56} -30,{hy+74} Q0,{hy+86} 32,{hy+74} Q64,{hy+56} 62,{hy-10} Q58,{hy-74} 0,{hy-76} Q-58,{hy-74} -60,{hy-10}Z" fill="{sk}" {SW()}/>'
    if L['hair'] == 'sidepart':   # grey hair with a side parting, cut short above the ears
        g += (f'<path d="M-58,{hy-34} Q-64,{hy-84} -20,{hy-96} Q20,{hy-108} 50,{hy-88} Q66,{hy-70} 61,{hy-34} '
              f'Q56,{hy-58} 36,{hy-64} Q8,{hy-70} -18,{hy-62} Q-28,{hy-76} -30,{hy-86} Q-40,{hy-60} -58,{hy-34}Z" fill="#c4c0b9" {SW(4)}/>')
        g += f'<path d="M-30,{hy-86} Q-26,{hy-74} -18,{hy-62}" fill="none" stroke="#8f8a85" stroke-width="3"/>'          # the parting
        for k in range(5):
            x0 = -12 + k * 14
            g += f'<path d="M{x0},{hy-90+k*2} Q{x0+18},{hy-86+k*2} {x0+30},{hy-72+k*3}" fill="none" stroke="#e8e6e1" stroke-width="2.6" stroke-linecap="round" opacity=".9"/>'
    else:   # short black hair with a side parting
        g += (f'<path d="M-62,{hy-2} Q-70,{hy-58} -30,{hy-78} Q10,{hy-94} 46,{hy-74} Q70,{hy-58} 63,{hy-4} Q60,{hy-34} 48,{hy-46} '
              f'Q20,{hy-40} -6,{hy-56} Q-30,{hy-44} -54,{hy-30} Z" fill="#1c1410" {SW(4)}/>')
        g += f'<path d="M-6,{hy-56} Q8,{hy-74} 30,{hy-80}" fill="none" stroke="#3a2c24" stroke-width="3"/>'
    g += f'<g transform="translate(0,{hy+2})">' + face(62, st, L['kind'])
    fx = 62 * 0.14
    talk = st.get('talk', 0) + ex(st.get('expr'))['mopen'] * .55; jaw = min(talk, 1) * 8
    if L['facial'] == 'none' and L.get('shape') != 'square':   # clean-shaven: a soft chin line
        g += f'<path d="M-16,{70} Q0,{76} 16,{70}" fill="none" stroke="#3b2a20" stroke-width="2.5" opacity=".3"/>'
    elif L['facial'] == 'moustache':   # big grey handlebar moustache
        g += (f'<path d="M{fx-6},18 Q{fx-30},12 {fx-46},26 Q{fx-54},34 {fx-50},40 Q{fx-40},30 {fx-26},32 Q{fx-12},30 {fx},24 '
              f'Q{fx+12},30 {fx+26},32 Q{fx+40},30 {fx+50},40 Q{fx+54},34 {fx+46},26 Q{fx+30},12 {fx+6},18 Q{fx},16 {fx-6},18Z" fill="#d9d6d0" {SW(3.5)}/>')
    elif L['facial'] == 'beard':   # neat short black beard along the jaw + moustache
        g += (f'<path d="M-57,16 Q-56,{58+jaw} -20,{76+jaw} Q{fx},{84+jaw} 34,{76+jaw} Q60,{58+jaw} 59,16 Q56,40 42,{50+jaw*.5} '
              f'Q{fx},{62+jaw*.8} -28,{50+jaw*.5} Q-52,40 -57,16Z" fill="#2b201a" opacity=".88" {SW(2.5)}/>')
        g += f'<path d="M{fx-22},20 Q{fx},14 {fx+22},20 Q{fx},23 {fx-22},20Z" fill="#2b201a" {SW(2)}/>'
    if L['glasses']:
        for sx in (-1, 1):
            cx = fx + sx * 62 * .36 * (0.92 if sx < 0 else 1)
            if L['glasses'] == 'square':
                g += f'<rect x="{cx-22}" y="-24" width="44" height="34" rx="8" fill="url(#glass)" stroke="#161210" stroke-width="7"/>'
            else:
                g += f'<rect x="{cx-21}" y="-20" width="42" height="28" rx="6" fill="url(#glass)" stroke="#2a2a2e" stroke-width="3.5"/>'
        l, r_ = fx - 62 * .36 * .92 + 22, fx + 62 * .36 - 22
        w = 7 if L['glasses'] == 'square' else 3.5
        g += f'<path d="M{l},-12 Q{(l+r_)/2},-18 {r_},-12" fill="none" stroke="#161210" stroke-width="{w-1}"/>'
        g += f'<path d="M{fx + 62*.36 + 22},-14 L60,-10" stroke="#161210" stroke-width="{w-1}"/>'
    return g + '</g>'


def person(st, L):
    st = apply_pose(st, 'nana')
    x, y, s, f = st['x'], st['y'] + st.get('drop', 0) * st.get('s', 1), st.get('s', 1), st.get('face', 1)
    lA, kA, lB, kB, sw, bob = st['legs'] if 'legs' in st else gait(st, 16)
    bob += st.get('bob', 0)
    lean = st.get('lean', 0) + (2 if st.get('walk') is not None else 0)
    af, ebf, ab, ebb = _arms_state(st, sw, None)
    sk = L['skin']
    top = L['kameez'] if L['outfit'] == 'kameez' else L['shirt']
    sleeve_d = L.get('kameez_d', L.get('shirt_d'))
    g = f'<g transform="translate({x},{y + bob*s}) scale({s*f},{s})">'
    g += leg(-17, -175, lB, kB, 84, 84, 38 if L['outfit'] == 'shirt' else 42, L['pants'], L['shoe'], back=True, foot=st.get('foot_b', st.get('foot')))
    back_arm = lambda behind: arm(-50, -392 + _shoulder_lift(ab), ab, ebb, 86, 80, 32, top, 2, sk, st.get('hand_b', 'relax'),
                                  back=behind, hand_ang=st.get('hand_ang_b'), holding=st.get('hold_b'), hold_tilt=st.get('hold_tilt_b', 0))
    g += f'<g transform="rotate({lean},0,-175)">' + ('' if st.get('arms_front') else back_arm(True)) + '</g>'
    g += leg(17, -175, lA, kA, 84, 84, 38 if L['outfit'] == 'shirt' else 42, L['pants'], L['shoe'], foot=st.get('foot'))
    g += f'<g transform="rotate({lean},0,-175)">'
    if L['outfit'] == 'kameez':
        g += f'<path d="M-62,-410 Q-80,-300 -84,-120 Q0,-104 84,-120 Q80,-300 62,-410 Q0,-426 -62,-410Z" fill="{top}" {SW()}/>'
        g += f'<path d="M-70,-300 Q-76,-220 -78,-130" fill="none" stroke="{sleeve_d}" stroke-width="6"/>'
        g += f'<path d="M0,-412 L0,-330" stroke="{sleeve_d}" stroke-width="4"/>'
        # open brown waistcoat with buttons on one side
        g += f'<path d="M-62,-408 Q-74,-320 -70,-232 Q-40,-226 -14,-236 L-12,-404 Q-36,-414 -62,-408Z" fill="{L["vest"]}" {SW(4.5)}/>'
        g += f'<path d="M62,-408 Q74,-320 70,-232 Q40,-226 14,-236 L12,-404 Q36,-414 62,-408Z" fill="{shade(L["vest"],1.08)}" {SW(4.5)}/>'
        for by in (-380, -340, -300, -262): g += f'<circle cx="22" cy="{by}" r="4.5" fill="#d8b46a" stroke="#3b2a20" stroke-width="2"/>'
        g += f'<path d="M34,-330 L56,-330" stroke="#3b2a20" stroke-width="3" opacity=".6"/>'
    else:
        g += f'<path d="M-62,-410 Q-76,-300 -72,-176 Q0,-166 72,-176 Q76,-300 62,-410 Q0,-426 -62,-410Z" fill="{top}" {SW()}/>'
        g += f'<rect x="-74" y="-190" width="148" height="22" rx="6" fill="{L["belt"]}" {SW(4)}/><rect x="-10" y="-189" width="22" height="20" rx="3" fill="#d6c18b" {SW(3)}/>'
        g += f'<path d="M0,-404 L0,-192" stroke="{sleeve_d}" stroke-width="4"/>'
        for by in (-370, -330, -290, -250, -214): g += f'<circle cx="7" cy="{by}" r="4" fill="#fff" stroke="{sleeve_d}" stroke-width="2"/>'
        g += f'<path d="M-30,-422 L0,-396 L-6,-430Z M30,-422 L0,-396 L6,-430Z" fill="#fff" {SW(3.5)}/>'                    # collar
        g += f'<path d="M30,-350 L54,-350 L53,-322 Q42,-318 31,-322Z" fill="none" stroke="{sleeve_d}" stroke-width="3.5"/>'   # pocket
        g += f'<rect x="38" y="-362" width="6" height="18" rx="2" fill="#2d5aa8"/>'                                           # pen
    hy = -488
    if L.get('shape') == 'square':
        g += f'<path d="M-24,-470 L-26,-414 Q0,-404 26,-414 L24,-470Z" fill="{shade(sk,.9)}" {SW(4)}/>'
        for yy, w_ in ((-452, 14), (-440, 18), (-428, 12)):
            g += f'<path d="M{-w_},{yy} Q0,{yy+5} {w_},{yy}" fill="none" stroke="#3b2a20" stroke-width="2.4" opacity=".45"/>'
        g += f'<path d="M-6,-424 L0,-412 L6,-424" fill="none" stroke="#3b2a20" stroke-width="2" opacity=".35"/>'
    else:
        g += f'<rect x="-17" y="-446" width="34" height="34" fill="{shade(sk,.88)}"/>'
    bw = L.get('broad', 1.0); up = -44 if L.get('shape') == 'square' else 0      # the long face sits higher: his neck shows
    g += (f'<g transform="rotate({st.get("head_tilt",0)},0,-420)"><g transform="translate(0,{hy+up}) scale({bw},1) translate(0,{-hy})">'
          + _head(L, st, hy) + '</g></g>')
    if st.get('arms_front'): g += back_arm(False)
    g += arm(52, -392 + _shoulder_lift(af), af, ebf, 86, 80, 32, top, 2, sk, st.get('hand_f', 'relax'),
             hand_ang=st.get('hand_ang_f'), holding=st.get('hold_f'), hold_tilt=st.get('hold_tilt_f', 0))
    g += f'<ellipse cx="47" cy="{-386 + _shoulder_lift(af)}" rx="20" ry="18" fill="{top}"/>'
    g += '</g></g>'
    return g


def chacha(st): return person(st, CHACHA)
def imran(st): return person(st, IMRAN)


def abba_photo(x, y, s=1.0, glow=0.0):
    """Imran's late father: kind face, white beard, white cap, in a wooden frame. glow 0..1 = soft light around it"""
    g = f'<g transform="translate({x},{y}) scale({s})">'
    if glow > 0:
        g += f'<circle cx="0" cy="0" r="230" fill="url(#halo)" opacity="{glow:.2f}"/>'
    g += f'<rect x="-120" y="-150" width="240" height="300" rx="10" fill="#8a5a33" stroke="#3b2a20" stroke-width="8"/>'
    g += f'<rect x="-98" y="-128" width="196" height="256" fill="#e8dcc4" stroke="#5b3d24" stroke-width="5"/>'
    g += '<svg x="-98" y="-128" width="196" height="256" viewBox="-98 -128 196 256">'
    sk = '#C08A60'
    g += f'<path d="M-90,128 Q-80,40 0,34 Q80,40 90,128Z" fill="#f4f2ea" {SW(4)}/>'
    g += f'<path d="M-46,-40 Q-48,30 -20,48 Q0,58 20,48 Q48,30 46,-40 Q42,-88 0,-90 Q-42,-88 -46,-40Z" fill="{sk}" {SW(4.5)}/>'
    g += f'<path d="M-44,-20 Q-44,40 -16,56 Q0,64 16,56 Q44,40 44,-20 Q38,14 26,18 Q0,10 -26,18 Q-38,14 -44,-20Z" fill="#f2f0ea" {SW(3.5)}/>'
    g += f'<path d="M-46,-56 Q0,-104 46,-56 L44,-46 Q0,-66 -44,-46Z" fill="#fbfbf7" {SW(3.5)}/>'
    for sx in (-1, 1):
        g += f'<path d="M{sx*18-9},-26 Q{sx*18},-31 {sx*18+9},-26" fill="none" {SW(3.5)}/>'          # gentle closed-smile eyes
        g += f'<path d="M{sx*18-10},-40 Q{sx*18},-44 {sx*18+10},-40" fill="none" stroke="#9a958e" stroke-width="4" stroke-linecap="round"/>'
    g += f'<path d="M-10,4 Q0,10 10,4" fill="none" {SW(3)}/>'
    g += '</svg></g>'
    return g


HALO = '<radialGradient id="halo"><stop offset="0" stop-color="#fff6c9" stop-opacity=".95"/><stop offset=".6" stop-color="#ffe9a0" stop-opacity=".35"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></radialGradient>'
