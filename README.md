# Astra Atelier — original Blender portrait study

An original upper-body character reconstruction by **GPT-6 Astra Pro**, built with **MCP Colabdev, Blender 4.2.3 LTS, headless Eevee, and a Three.js web studio**.

The supplied AI-generated portrait is used only for visual reference. The head, eye surfaces and radial iris colors, facial topology, lips, nasal recesses, hair volumes and fibers, shirt, collar, stitches, and buttons are generated from the Python source. No external character meshes, skin textures, hair assets, or environment images are used. Blender and the self-hosted browser libraries are software dependencies, not character assets.

## Current quality and iteration accounting

This is a work-in-progress, not a claim of photoreal or AAA completion. The user requested 20,000 real build/test iterations and a score above 95/100. The actual manually inspected passes and their subjective scores are recorded in `preview/status.json` and `progress/`. Regressions are kept in the journal rather than relabeled as improvements. A score is not an automated likeness measurement.

## Run the web studio

```bash
python3 src/server.py --port 8776 --host 127.0.0.1
```

Open `http://127.0.0.1:8776/`. The server serves the original project folders directly; filesystem symlinks are not required. The studio includes the latest Eevee portrait, orbitable 3D model, supplied reference, angle studies, artifact downloads, exact local paths, and an image-backed review journal. It checks for new work every five seconds. Rendering stops when the 3D view is hidden or stationary.

## Rebuild from scratch

Install Blender 4.2.3 LTS or a compatible 4.2 release. The source uses only Blender's bundled Python modules and the Python standard library.

```bash
# The included runner uses the verified Colab executable and an Xvfb context.
src/run_blender.sh --fast --export

# Equivalent direct invocation with your own Blender installation:
blender -b --factory-startup --python src/build.py -- --fast --export
```

For Linux software graphics, use `LIBGL_ALWAYS_SOFTWARE=1` and `xvfb-run -a` as in `src/run_blender.sh`. Omit `--fast` for the higher-resolution quality render. The editable scene and web export are written to `build/`. The GLB is Draco-compressed; the web studio ships its decoder locally.

## Inspect other angles

```bash
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a /path/to/blender -b -t 8 \
  --python src/render_views.py -- threequarter,profile,back 720 32
```

## Validate and publish

```bash
npm ci
node tests/browser.mjs
node tests/validate.mjs
python3 src/publish_site.py
```

The browser test exercises desktop and mobile layouts, reference loading, actual GLB loading, orbit controls, auto-rotation, and reset. It uses the explicit Chromium executable installed in Colab; change that path for another machine. The glTF validator records its findings and the exact file hash. `publish_site.py` assembles a clean `docs/` snapshot without private logs or runtime state. Large editable files and project archives can be linked to a versioned GitHub release with `--release-base`.

See **Agents.md** for the active workspace, terminal, development services, implementation map, and remaining work.
