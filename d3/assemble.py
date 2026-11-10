"""Put Roman Urdu captions on the rendered 3D frames and add the voices. python3 d3/assemble.py"""
import os, json, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'build_3d')
FPS = 24
LINES = json.load(open(f'{B}/lines.json'))
TIMES = [2.5, 4.7, 11.0]          # must match d3/scene.py
NAMES = {'ALI': ('Ali', (213, 43, 49)), 'NANA': ('Nana Jaan', (123, 90, 60))}
F_REG = '/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf'
F_BOLD = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
W, H = 1280, 720
f_cap, f_tag = ImageFont.truetype(F_REG, 32), ImageFont.truetype(F_BOLD, 24)


def caption_at(t):
    for ln, t0 in zip(LINES, TIMES):
        if t0 <= t < t0 + ln['d'] + 0.2: return ln
    return None


def draw(im, ln):
    d = ImageDraw.Draw(im, 'RGBA'); text = ln['text']
    tw = d.textlength(text, font=f_cap); bw, bh = tw + 60, 58; x0, y0 = (W - bw) / 2, H - bh - 18
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], 20, fill=(255, 255, 255, 235), outline=(59, 42, 32), width=4)
    d.text((W / 2, y0 + 10), text, font=f_cap, fill=(40, 30, 24), anchor='ma')
    nm, col = NAMES[ln['who']]; nw = d.textlength(nm, font=f_tag) + 30
    d.rounded_rectangle([x0 + 20, y0 - 26, x0 + 20 + nw, y0 + 12], 14, fill=col, outline=(59, 42, 32), width=3)
    d.text((x0 + 20 + nw / 2, y0 - 7), nm, font=f_tag, fill='white', anchor='mm')


frames = sorted(os.listdir(f'{B}/frames'))
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', f'{B}/video.mp4'], stdin=subprocess.PIPE)
for i, fn in enumerate(frames):
    im = Image.open(f'{B}/frames/{fn}').convert('RGB')
    ln = caption_at(i / FPS)
    if ln: draw(im, ln)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait()
total = len(frames) / FPS
inputs, filt = [], []
for k, (ln, t0) in enumerate(zip(LINES, TIMES)):
    inputs += ['-i', ln['file']]; ms = int(t0 * 1000)
    filt.append(f'[{k}:a]aresample=48000,adelay={ms}|{ms}[a{k}]')
filt.append(''.join(f'[a{k}]' for k in range(len(LINES))) + f'amix=inputs={len(LINES)}:normalize=0,apad,atrim=0:{total:.2f}[out]')
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-ac', '2', f'{B}/audio.wav'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/video.mp4', '-i', f'{B}/audio.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                f'{B}/ali_nana_3d_test.mp4'], check=True)
print('done', f'{B}/ali_nana_3d_test.mp4', round(total, 2))
