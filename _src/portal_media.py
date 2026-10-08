# -*- coding: utf-8 -*-
"""写真・画像を縮小して base64 にする共通関数（ローカルの元写真は公開リポジトリに置かない）。"""
import base64, glob, io, os
from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

HERE = os.path.dirname(os.path.abspath(__file__))
SYMPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "70 Mtg", "20261003 シンポジウム", "写真"))
if not os.path.isdir(SYMPO):
    SYMPO = r"C:\Users\keima\OneDrive\Documents\Work\40 Still Modelling The World (SMTW)\70 Mtg\20261003 シンポジウム\写真"
TSHIRT = r"C:\Users\keima\ObsidianVault\10 work\40 Still Modelling The World(SMTW)\川口先生Tシャツ"
if not os.path.isdir(TSHIRT):  # 2026-10-08 に「川口先生Tシャツ デザイン案」から改名
    TSHIRT += " デザイン案"


def heic(stamp):
    return os.path.join(SYMPO, f"20261003_{stamp}_iOS.heic")


def session(i):
    fs = sorted(glob.glob(os.path.join(SYMPO, "*_n*.jpg")))
    return fs[i]


def load(path, box=None):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if box:  # 比率 (l, t, r, b)
        w, h = im.size
        im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    return im


def jpeg(im, edge, q, fmt="JPEG"):
    im = im.copy()
    im.thumbnail((edge, edge), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return buf.getvalue(), im.size


def data_uri(path, edge, q, box=None):
    raw, size = jpeg(load(path, box), edge, q)
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode(), size, len(raw)
