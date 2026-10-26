#!/usr/bin/env python3
"""Klidná hudba k videu: pomalý pad (C dur / Am), jemné zvonkohry na klíčová slova a změny scén, reverb.
Použití: python3 publikace_hudba.py timeline.json out.wav [cilove_LUFS=-30]"""
import sys, json, numpy as np
from scipy.signal import fftconvolve
from scipy.io import wavfile
tl = json.load(open(sys.argv[1])); out = sys.argv[2]
SR = 48000; D = tl['duration'] + 1.0; n = int(D * SR); t = np.arange(n) / SR
rng = np.random.default_rng(26)
def tone(f, dur, att=0.8, rel=1.5, vol=1.0, start=0.0, buf=None):
    i0 = int(start * SR); m = int(dur * SR); tt = np.arange(m) / SR
    env = np.minimum(1, tt / att) * np.minimum(1, np.maximum(0, (dur - tt) / rel))
    s = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt + 0.3) + 0.08 * np.sin(2 * np.pi * 3 * f * tt)) * env * vol
    buf[i0:i0 + m] += s[:max(0, len(buf) - i0)]
pad = np.zeros(n)
# akordy po 8 s: C - Am - F - G (pomalu, klidně)
chords = [[130.81, 164.81, 196.00, 261.63], [110.00, 164.81, 220.00, 261.63], [87.31, 174.61, 220.00, 261.63], [98.00, 146.83, 196.00, 246.94]]
step = 8.0; k = 0; pos = 0.0
while pos < D:
    for f in chords[k % 4]:
        tone(f * (1 + 0.0015 * rng.standard_normal()), step + 3, att=2.5, rel=3.0, vol=0.10, start=pos, buf=pad)
    k += 1; pos += step
# jemný šum/vzduch
air = np.convolve(rng.standard_normal(n), np.ones(200) / 200, mode='same') * 0.02
pent = [523.25, 587.33, 659.25, 783.99, 880.00]  # C pentatonika
cues = np.zeros(n)
def bell(tm, f, vol):
    if tm < 0 or tm > D - 2: return
    tone(f, 2.6, att=0.01, rel=2.4, vol=vol, start=tm, buf=cues)
ki = 0
for s in tl['scenes']:
    bell(s['start'] - tl['fade'] * 0.5, 392.0, 0.10)          # změna scény: nízký jemný tón
    for kt in s['keys']:
        bell(kt + 0.12, pent[ki % 5], 0.16); ki += 1           # klíčové slovo
# rámcový reverb
ir_len = int(2.2 * SR); ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / (0.55 * SR)); ir /= np.abs(ir).sum() * 0.12
mix = pad + air + cues
wet = fftconvolve(mix, ir)[:n]
sig = 0.65 * mix + 0.55 * wet
fade = np.minimum(1, t / 2.0) * np.minimum(1, np.maximum(0, (D - t) / 2.5)); sig *= fade
target = float(sys.argv[3]) if len(sys.argv) > 3 else -30.0
rms = np.sqrt(np.mean(sig ** 2)) + 1e-9
sig *= (10 ** (target / 20)) / rms * 10 ** (0 / 20) * 1.0
sig = np.tanh(sig * 1.0)
stereo = np.stack([sig, np.roll(sig, int(0.012 * SR))], 1)
wavfile.write(out, SR, (stereo * 32767).astype(np.int16))
print('hudba', out, round(D, 1), 's')
