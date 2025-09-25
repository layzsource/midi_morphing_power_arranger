# encoder_stub.py
# Minimal encoder serving collection.json, atlas.png, and stim/{media_id}
# Requires: fastapi uvicorn pillow numpy
# Run:
#   pip install fastapi uvicorn pillow numpy
#   python encoder_stub.py --images ~/media/family_photos --videos ~/media/family_videos --cap 128
import os, io, json, argparse, hashlib, random
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response, PlainTextResponse
import uvicorn
from PIL import Image

HOST="0.0.0.0"; PORT=7071

def color_from_id(s: str):
    h = hashlib.sha1(s.encode()).hexdigest()
    r = int(h[:2],16); g = int(h[2:4],16); b = int(h[4:6],16)
    return (r, g, b)

def scan_media(images_root: str, videos_root: str, cap: int):
    items=[]
    for root in [images_root, videos_root]:
        if not root: continue
        if not os.path.isdir(os.path.expanduser(root)): continue
        for fname in sorted(os.listdir(os.path.expanduser(root))):
            if len(items) >= cap: break
            path = os.path.join(os.path.expanduser(root), fname)
            if not os.path.isfile(path): continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in [".jpg",".jpeg",".png",".gif",".bmp",".mp4",".webm",".mov",".m4v"]:
                continue
            mid = os.path.splitext(fname)[0]
            items.append({"id": mid, "path": path, "type": ("video" if ext in [".mp4",".webm",".mov",".m4v"] else "image")})
    return items

def make_thumb(path: str, size=128):
    try:
        im = Image.open(path).convert("RGB")
    except Exception:
        im = Image.new("RGB", (size, size), (64,64,64))
    im.thumbnail((size,size))
    out = Image.new("RGB", (size, size), (0,0,0))
    x = (size - im.width)//2; y = (size - im.height)//2
    out.paste(im, (x,y))
    return out

def build_atlas(items: List[Dict[str,Any]], size=128, cols=16):
    n = len(items); rows = (n + cols - 1)//cols
    atlas = Image.new("RGB", (cols*size, rows*size), (8,8,8))
    coords={}
    for i,item in enumerate(items):
        r = i//cols; c = i%cols
        thumb = make_thumb(item["path"], size=size)
        atlas.paste(thumb, (c*size, r*size))
        coords[item["id"]] = {"x": c*size, "y": r*size, "w": size, "h": size, "row": r, "col": c}
    return atlas, coords

def palette_hint(rgb_tuple):
    r,g,b = rgb_tuple
    return [r/255.0, g/255.0, b/255.0]

def build_collection(items, coords):
    media=[]
    edges=[]
    ids=[it["id"] for it in items]
    for it in items:
        pid = it["id"]
        pal = palette_hint(color_from_id(pid))
        media.append({
            "id": pid,
            "type": it["type"],
            "thumb": f"/atlas/home_cube.png#{pid}",
            "embed": [0.0,0.0,0.0],  # placeholder
            "palette": pal,
            "tags": []
        })
    # toy similarity edges: neighbors in the atlas grid
    ids_sorted = [it["id"] for it in items]
    for i in range(len(ids_sorted)-1):
        edges.append([ids_sorted[i], ids_sorted[i+1], 0.9])
    return {"collection_id":"home_cube","media":media,"graph_edges":edges,"atlas":"/atlas/home_cube.png","index_version":"v1"}

app = FastAPI()
STATE = {"items": [], "coords": {}, "atlas": None}

@app.get("/", response_class=PlainTextResponse)
def root(): return "Encoder OK. GET /collection/home_cube  GET /atlas/home_cube.png  POST /stim/{id}"

@app.get("/collection/home_cube")
def get_collection():
    coll = build_collection(STATE["items"], STATE["coords"])
    return JSONResponse(coll)

@app.get("/atlas/home_cube.png")
def get_atlas():
    buf = io.BytesIO()
    STATE["atlas"].save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post("/stim/{media_id}")
def stim(media_id: str):
    # simple deterministic mapping
    pal = palette_hint(color_from_id(media_id))
    k = (hash(media_id) % 8) + 1  # avoid k=0 for fun
    return JSONResponse({
        "bias_modes": [k, (k+3)%12],
        "rgb": pal,
        "pulse": {"k": k, "amp": 0.65, "decay": 0.92},
        "pmw_hint": 0.6,
        "shelf_bias": {"500": 0.8, "700": 0.4}
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", default="~/media/family_photos")
    parser.add_argument("--videos", default="~/media/family_videos")
    parser.add_argument("--cap", type=int, default=128)
    args = parser.parse_args()

    items = scan_media(args.images, args.videos, args.cap)
    atlas, coords = build_atlas(items, size=128, cols=16)
    STATE["items"] = items; STATE["coords"]=coords; STATE["atlas"]=atlas
    uvicorn.run(app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()
