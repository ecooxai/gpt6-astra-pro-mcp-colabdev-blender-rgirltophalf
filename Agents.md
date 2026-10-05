# Rgirl Blender bust — agent handoff

## Identity and scope
- Model: GPT-6 Astra Pro. Agent: MCP Colabdev. Key tool: Blender 4.2.3 LTS, headless Eevee.
- Project: `/home/dev/project/3d/gpt6_astra_pro_mcp_colabdev_blender_rgirltophalf`.
- `/build/gpt6_astra_pro_mcp_colabdev_blender_rgirltophalf` is a symlink to the persistent project `build/`.
- Reference: `reference/reference.png`, supplied by the user. It was viewed directly, not analyzed by image-processing code. It must never be used as a face texture, billboard or projection.
- All character geometry, hair and material detail are authored from scratch. Three.js and Blender are software dependencies, not character assets. Do not import external character, hair, skin, clothing or environment assets.

## Current implementation
- `src/common.py`: math, original mesh/tube helpers, procedural materials.
- `src/face.py`: integrated facial mesh, convex eye openings and iris fibers, eyelids, eyelashes, brows, lips, ears.
- `src/clothing.py`: tapered neck, shirt, true collar thickness, buttons and stitches.
- `src/hair.py`: scalp, 78 original locks, 9,285 geometric strands; fine render-only strands are excluded from the web export.
- `src/build.py`: complete rebuild, Eevee portrait render, optional GLB export.
- `src/render_views.py`: independent front, three-quarter, profile and back renders from the saved scene.
- `src/review.py`: records only real inspected render passes. It refuses a visual review without an existing render.
- `preview/`: responsive self-hosted web studio; `status.json` drives 5-second refresh. Artifacts and reference are symlinks into the project.
- `tests/browser.mjs`: actual Chromium desktop/mobile, reference loading, orbit and auto-rotation tests.

## Commands
```bash
src/run_blender.sh --fast --export > logs/iteration-NN.log 2>&1
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a /home/dev/.local/opt/blender-4.2.3-linux-x64/blender -b -t 8 --python src/render_views.py -- threequarter,profile,back 720 20
node tests/browser.mjs
python3 src/review.py N SCORE 'Review title' 'Evidence, limitations and next edits' --progress PERCENT
```
Use the explicit Blender 4.2.3 executable. The `blender` command resolves to an incomplete relocated 4.0.2 installation and fails to find its data/scripts.

## Running services and terminal
- Preview server: port 8776, `src/serve.sh`; PID in `logs/server.pid`.
- Cloudflared PID and log: `logs/cloudflared.pid`, `logs/cloudflared.log`.
- Public temporary URL: https://conclusions-browse-survival-carolina.trycloudflare.com
- Colab has software graphics, not a GPU; allow Eevee shader compilation time.
- The runtime has a 32-terminal limit. Reuse this project's MCP Colabdev terminal **1671** via `webterm write 1671` followed by `webterm read 1671 --full`. Echo and PS1/PS2 are disabled to keep output small. Do not stop unrelated sessions. Source/build progress is logged on disk.
- Current Git branch: `gpt6-astra-pro-mcp-colabdev-blender-bust`.

## Truthful completion criteria
The user requested 20,000 build/test iterations and >95/100. Those are targets, not claims. Record the actual number of completed and visually reviewed passes in `preview/status.json` and `progress/`. Never fabricate passes, automated likeness metrics, or AAA certification. Each subjective score needs concrete observations. Initial startup failures are not visual iterations.

## Next work
Inspect the first `build/portrait.png`, correct anatomy/eye integration/hair silhouette from direct visual review, render side/back views, test the live app, push a project-specific repository, deploy GitHub Pages, package outputs, and update this handoff with actual results and remaining limitations. Do not stop the Colab instance; back up before any explicit stop request.
