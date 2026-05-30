# Python OpenGL Renderer

A 3D model viewer built with Python and OpenGL, featuring multiple light sources and custom GLSL shaders (Phong, Gouraud, Toon).

## Setup

- 'classic' venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- uv
```bash
# install uv on your machine
uv sync
source .venv/bin/activate
```

## Run example

```bash
python main.py \
  --model assets/models/cube.obj \
  --diffuse assets/textures/diffuse.jpg \
  --light POINT \
  --light-pos 1.2 1 2 \
  --cam-pos 2 2 2 \
  --speed 20 \
  --far 100
```

## Lights

- `--light` - light type: `NONE`, `POINT`, `DIRECTIONAL` or `SPOT`
- `--light-pos X Y Z` - light position (point and spot)
- `--light-dir X Y Z` - light direction (directional and spot)
- `--light-color R G B` - light color

Each light is drawn as a small sphere. The bigger white sphere is the selected light.

## Controls

- `W/A/S/D` - move the camera
- Mouse - look around
- `1/2/3` - Phong/Gouraud/toon shading
- `L` - add a light at the camera position
- `K` - remove the selected light
- `N` - select the next light
- `T` - change the type of the selected light
- Arrows - move the selected light on X/Z
- `E` / `Q` - move the selected light up / down
- `ESC` - quit
