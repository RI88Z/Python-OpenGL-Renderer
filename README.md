# Python OpenGL Renderer

A 3D model viewer built with Python and OpenGL, featuring multiple light sources and custom GLSL shaders (Phong, Gouraud, Toon).

## Setup and run

- 'classic' venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

- uv
```bash
# install uv on your machine
uv sync
source .venv/bin/activate
uv run main.py
```

## Controls

- `W/A/S/D` - move the camera
- Mouse - look around
- `1/2/3` - Phong/Gouraud/toon shading
- `ESC` - quit
