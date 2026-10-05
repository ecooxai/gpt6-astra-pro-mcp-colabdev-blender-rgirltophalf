const $ = selector => document.querySelector(selector);
const stem = 'gpt6_astra_pro_mcp_colabdev_blender_rgirltophalf';
const projectPath = '/home/dev/project/3d/' + stem;
const buildPath = '/build/' + stem + '/';
let mode = 'render', view = 'portrait', state = {}, version = '';
let viewer = null, viewerLoading = false, polling = false;
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

function selectView(name) {
  view = name;
  document.querySelectorAll('[data-view]').forEach(button => {
    button.classList.toggle('active', button.dataset.view === name);
  });
  if (mode === 'orbit' && viewer) viewer.setView(name);
  else showCurrentView();
}

function showCurrentView() {
  const image = $('#hero');
  $('#three').hidden = mode !== 'orbit';
  $('#orbit-controls').hidden = mode !== 'orbit';
  image.hidden = mode === 'orbit';
  if (mode === 'orbit') {
    $('#view-label').textContent = 'INTERACTIVE / ' + view.toUpperCase();
    $('#hero-path').textContent = buildPath + (state.files?.glb || stem + '.glb');
    $('#stage-caption').textContent = 'Drag to orbit · scroll or pinch to zoom';
    if (!viewer) initializeViewer();
    else if (viewer.build !== state.iteration) viewer.refresh();
    return;
  }
  const reference = mode === 'reference';
  const available = reference || state.views?.includes(view);
  $('#empty').hidden = Boolean(available);
  image.hidden = !available;
  if (available) {
    const url = reference ? 'reference/reference.png' : 'artifacts/' + view + '.png?v=' + version;
    if (image.getAttribute('src') !== url) image.src = url;
  }
  image.alt = reference ? 'Supplied portrait reference' : 'Actual Blender Eevee ' + view + ' render';
  image.title = 'Open the full-resolution image';
  image.onclick = () => window.open(image.src, '_blank', 'noopener');
  $('#view-label').textContent = reference ? 'SUPPLIED REFERENCE' : 'EEVEE / ' + view.toUpperCase();
  $('#hero-path').textContent = reference ? projectPath + '/reference/reference.png' : buildPath + view + '.png';
  $('#stage-caption').textContent = reference ? 'Reference only · never projected onto the model' : 'Actual Eevee render · click to open full resolution';
}

document.querySelectorAll('[data-mode]').forEach(button => {
  button.onclick = () => {
    mode = button.dataset.mode;
    document.querySelectorAll('[data-mode]').forEach(tab => {
      tab.classList.toggle('active', tab === button);
      tab.setAttribute('aria-selected', String(tab === button));
    });
    showCurrentView();
  };
});
document.querySelectorAll('[data-view]').forEach(button => {
  button.onclick = () => selectView(button.dataset.view);
});

function updateJournal(history) {
  if (!history?.length) return;
  $('#history').innerHTML = [...history].reverse().map(pass => {
    const id = String(Number(pass.iteration)).padStart(3, '0');
    const path = 'history/iteration-' + id + '.png';
    return `<article><span>PASS ${String(Number(pass.iteration)).padStart(2, '0')}</span>
      <div class="passcontent"><a href="${path}" target="_blank" rel="noopener">
      <img loading="lazy" src="${path}" alt="Actual Eevee render from pass ${Number(pass.iteration)}"></a>
      <div><h3>${escapeHTML(pass.title)}</h3><p>${escapeHTML(pass.notes)}</p>
      <code class="history-path">${projectPath}/progress/iteration-${id}.png</code></div></div>
      <b>${pass.quality == null ? '—' : escapeHTML(pass.quality)}</b></article>`;
  }).join('');
}

async function poll() {
  if (polling) return;
  polling = true;
  try {
    const response = await fetch('status.json?t=' + Date.now(), { cache: 'no-store' });
    if (!response.ok) throw new Error('Status HTTP ' + response.status);
    const next = await response.json();
    const changed = version !== next.updated;
    state = next;
    version = state.updated;
    $('#iteration').textContent = String(state.iteration || 0).padStart(2, '0');
    $('#iteration-chip').textContent = 'ITERATION ' + String(state.iteration || 0).padStart(2, '0');
    $('#quality').textContent = state.quality == null ? 'Not yet reviewed' : state.quality + ' / 100';
    $('#status').textContent = state.status;
    $('#updated').textContent = 'Updated ' + new Date(state.updated).toLocaleString();
    $('#progress').style.width = (state.progress || 9) + '%';
    $('#live-state').textContent = state.complete ? 'Latest saved build' : 'Live build';
    const paths = [];
    for (const type of ['blend', 'glb', 'archive']) {
      const link = $('#' + type + '-link');
      if (state.files?.[type]) {
        link.href = state.downloads?.[type] || 'artifacts/' + state.files[type];
        link.classList.remove('disabled');
        link.setAttribute('aria-disabled', 'false');
        link.setAttribute('download', '');
        paths.push(buildPath + state.files[type]);
      }
    }
    $('#file-paths').textContent = paths.join('\n\n') || 'Build files appear here after export.';
    if (changed) {
      updateJournal(state.history);
      showCurrentView();
    }
  } catch (error) {
    $('#live-state').textContent = 'Reconnecting';
    console.warn(error.message);
  } finally {
    polling = false;
  }
}

async function initializeViewer() {
  if (viewerLoading) return;
  if (!state.files?.glb) {
    $('#empty').hidden = false;
    $('#empty-text').textContent = 'The 3D export is being prepared';
    return;
  }
  viewerLoading = true;
  $('#empty').hidden = false;
  $('#empty-text').textContent = 'Loading original geometry…';
  try {
    const THREE = await import('three');
    const { OrbitControls } = await import('./vendor/OrbitControls.js');
    const { GLTFLoader } = await import('./vendor/GLTFLoader.js');
    const { DRACOLoader } = await import('./vendor/DRACOLoader.js');
    const decoder = new DRACOLoader().setDecoderPath('./vendor/draco/').setWorkerLimit(2);
    const loader = new GLTFLoader().setDRACOLoader(decoder);
    const host = $('#three');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x29272a);
    const camera = new THREE.PerspectiveCamera(32, 1, .01, 100);
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(devicePixelRatio, innerWidth < 700 ? 1.25 : 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    host.replaceChildren(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = .08;
    controls.autoRotateSpeed = .7;
    controls.minDistance = 3;
    controls.maxDistance = 20;
    let dirty = true, wireframe = false;
    controls.addEventListener('change', () => { dirty = true; });
    scene.add(new THREE.HemisphereLight(0xf2e5df, 0x5d5a68, 1.65));
    for (const [position, power, color] of [
      [[-4, 5, 6], 2.0, 0xffede4],
      [[4, 3, 4], 1.2, 0xe9eeff],
      [[2, 5, -4], 1.7, 0xffede4]
    ]) {
      const light = new THREE.DirectionalLight(color, power);
      light.position.set(...position);
      scene.add(light);
    }
    // Original studio reflection cards; no external environment image or HDR asset.
    const reflectionScene = new THREE.Scene();
    reflectionScene.background = new THREE.Color(.14, .13, .14);
    for (const [position, size, intensity] of [
      [[-4, 3, 5], [2.5, 4], 2.0], [[4, 2, 4], [2, 3], .8], [[1, 4, -4], [2, 3], 1.1]
    ]) {
      const card = new THREE.Mesh(new THREE.PlaneGeometry(...size), new THREE.MeshBasicMaterial({
        color: new THREE.Color(intensity, intensity * .96, intensity * .93),
        side: THREE.DoubleSide, toneMapped: false
      }));
      card.position.set(...position);
      card.lookAt(0, 0, 0);
      reflectionScene.add(card);
    }
    const generator = new THREE.PMREMGenerator(renderer);
    const environment = generator.fromScene(reflectionScene, .03, .1, 30);
    scene.environment = environment.texture;
    scene.environmentIntensity = .30;
    generator.dispose();
    reflectionScene.traverse(object => {
      if (object.isMesh) { object.geometry.dispose(); object.material.dispose(); }
    });

    function prepare(model) {
      model.traverse(object => {
        if (!object.isMesh) return;
        const old = object.material;
        if (object.name.toLowerCase().includes('hair')) {
          object.material = new THREE.MeshStandardMaterial({
            color: old.color, roughness: .53, metalness: 0,
            vertexColors: old.vertexColors, side: THREE.FrontSide
          });
        }
        for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
          material.wireframe = wireframe;
        }
      });
      return model;
    }
    let model = prepare((await loader.loadAsync('artifacts/' + state.files.glb + '?v=' + version)).scene);
    scene.add(model);
    const bounds = new THREE.Box3().setFromObject(model);
    const center = bounds.getCenter(new THREE.Vector3());
    const distance = bounds.getSize(new THREE.Vector3()).y * 1.85;
    controls.target.copy(center);
    function setView(name) {
      const angle = { portrait: 0, threequarter: .61, profile: Math.PI / 2, back: Math.PI }[name] || 0;
      camera.position.set(center.x + Math.sin(angle) * distance, center.y + .08, center.z + Math.cos(angle) * distance);
      controls.update();
      dirty = true;
      $('#view-label').textContent = 'INTERACTIVE / ' + name.toUpperCase();
    }
    function resize() {
      const width = host.clientWidth, height = host.clientHeight;
      if (!width || !height) return;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      dirty = true;
    }
    new ResizeObserver(resize).observe(host);
    setView(view);
    resize();
    $('#home-view').onclick = () => selectView('portrait');
    $('#rotate').onclick = () => {
      controls.autoRotate = !controls.autoRotate;
      $('#rotate').textContent = controls.autoRotate ? 'Stop rotation' : 'Auto-rotate';
      dirty = true;
    };
    $('#wire').onclick = () => {
      wireframe = !wireframe;
      model.traverse(object => {
        if (object.isMesh) for (const material of (Array.isArray(object.material) ? object.material : [object.material])) material.wireframe = wireframe;
      });
      dirty = true;
    };
    viewer = {
      build: state.iteration, refreshing: false, setView,
      async refresh() {
        if (this.refreshing) return;
        this.refreshing = true;
        const expected = state.iteration;
        try {
          const replacement = prepare((await loader.loadAsync('artifacts/' + state.files.glb + '?v=' + version)).scene);
          const previous = model;
          model = replacement;
          scene.add(model);
          scene.remove(previous);
          const disposed = new Set();
          previous.traverse(object => {
            if (!object.isMesh) return;
            object.geometry.dispose();
            for (const material of (Array.isArray(object.material) ? object.material : [object.material])) {
              if (!disposed.has(material)) { material.dispose(); disposed.add(material); }
            }
          });
          renderer.renderLists.dispose();
          this.build = expected;
          dirty = true;
        } catch (error) { console.error(error); }
        finally { this.refreshing = false; }
      }
    };
    $('#empty').hidden = true;
    function animate() {
      requestAnimationFrame(animate);
      if (mode !== 'orbit' || document.hidden) return;
      controls.update();
      if (dirty || controls.autoRotate) {
        renderer.render(scene, camera);
        dirty = false;
      }
    }
    animate();
  } catch (error) {
    $('#empty').hidden = false;
    $('#empty-text').textContent = '3D preview unavailable: ' + error.message;
    console.error(error);
  } finally {
    viewerLoading = false;
  }
}

poll();
setInterval(poll, 5000);
