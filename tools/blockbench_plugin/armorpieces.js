/*
 * Armor Pieces - a Blockbench front end for this repo's authoring tools.
 *
 * The plugin deliberately contains no geometry maths and no colour maths. Every conversion it needs
 * already exists, verified, in tools/*.py - bb_geo's flip is covered by a round-trip test over all
 * nineteen parts, and preview_material.py is a literal port of the mod's own DecorationPalette. A
 * JavaScript reimplementation of either would be a second source of truth that drifts the first time
 * an offset is tuned, which is the one failure this toolchain is built to prevent. So the plugin
 * shells out to Python and spends its own code on the things Blockbench can actually do better than
 * a command line: finding the packs, showing the piece on an animated figure, and painting it.
 *
 * The one thing it does with pixels itself is index a lookup table. A material preview has to follow
 * the brush, and a Python process per brush movement cannot, so preview_material.py prints its
 * finished 256-entry ramps once and the plugin composites master, static layer and fitting masks
 * through them - the same table lookup the game performs, with none of the arithmetic that fills
 * the table.
 *
 * What it changes about Blockbench while a piece is open ("the workspace"):
 *
 *   - the project is in its own format, `armorpieces`, which is `free` with the modes and panels a
 *     part author never needs conditioned away. Other projects are untouched, because every change
 *     is a condition that asks "is the current project a piece?" rather than a layout edit.
 *   - one panel, "Armor Piece", holds every control: which piece and anchor, master, static or
 *     fitting-mask edit mode, material preview with the fittings filled or empty, walk/sprint pose
 *     and phase, and the reference toggles.
 *   - the Textures panel is gone. Which PNG the brush lands on is decided by the edit-mode switch,
 *     and a material preview is only ever a thing you look at: strokes over it are routed to the
 *     layer being edited, and the preview is recomposited under the brush.
 *
 * That means Python must be on PATH, which it already must be for every other tool here.
 *
 * Install: Blockbench > File > Plugins > Load Plugin from File, and pick this file. Then set
 * "Armor Pieces repository" in Settings to the repo root if it is not found automatically.
 */
(function () {
	const fs = require('fs');
	const path = require('path');
	const os = require('os');
	const { execFileSync } = require('child_process');

	const ID = 'armorpieces';
	// Everything created in onload that has a delete(), so unload can take it all down.
	let registered = [];
	// Everything else unload has to undo: wrapped conditions, patched methods, event listeners.
	let undo_hooks = [];
	let anchorCache = null;
	// Re-entry guard: folding the master to greyscale is itself a texture edit.
	let greyscaleGuard = false;
	// Re-entry guard: pushing state into the panel form fires the form's change event.
	let syncingForm = false;
	// The author's own palette, stashed while the greyscale one is in.
	let userPalette = null;
	// Ramps from preview_material.py, keyed by material and by static colour. Session-wide: a
	// material's ramp never changes, and a static colour's ramp depends only on the colour.
	const ramps = { material: {}, static: {} };

	// ---- per-project state --------------------------------------------------------------------

	// The piece the current project came from, so Save knows where to put it back. Kept on the
	// Project rather than in a module variable because Blockbench keeps several projects open.
	function currentPiece() {
		return Project && Project[ID + '_piece'] || null;
	}

	function defaultState() {
		return {
			anchor: '',
			edit: 'master',
			preview: false,
			material: 'iron',
			animation: 'idle',
			phase: 0,
			show_player: true,
			show_armor: true,
			part_only: true,
			recipe_focus: '',
			recipe_ring: 'minecraft:paper',
			// The fitting whose mask is under the brush while edit is 'fitting'.
			fitting: '',
			// The preview's fitting values by fitting name, '' for empty.
			fittings: {},
		};
	}

	function state() {
		if (!Project) return defaultState();
		if (!Project[ID + '_state']) Project[ID + '_state'] = defaultState();
		return Project[ID + '_state'];
	}

	/* True while the selected project is a piece opened by this plugin. Every hook keys off it. */
	function isWorkspace() {
		return !!(Project && Format && Format.id === ID && currentPiece());
	}

	function tex(id) {
		return Texture.all.find(function (t) { return t.id === id; }) || null;
	}

	/*
	 * The sheets a part is painted on, each linked to a file beside the master: `part` (the
	 * greyscale master), `part_static` (the colour opt-out) and `part_<fitting>` (one greyscale
	 * mask per masked fitting). Everything that grows, moves, saves or folds paint walks this list,
	 * so a new kind of sheet is a new id here and nothing else.
	 */
	function isSheetId(id) {
		return id === 'part' || (typeof id === 'string' && id.indexOf('part_') === 0);
	}

	/* Greyscale by definition: the master and the masks. The static layer is colour. */
	function isGreyId(id) {
		return isSheetId(id) && id !== 'part_static';
	}

	function sheets() {
		return Texture.all.filter(function (t) { return isSheetId(t.id); });
	}

	function maskId(name) {
		return 'part_' + name;
	}

	// ---- repo + python ------------------------------------------------------------------------

	function looksLikeRepo(dir) {
		return !!dir && fs.existsSync(path.join(dir, 'tools', 'bb_rig.py'));
	}

	/*
	 * Resolved lazily, not in onload. This file normally sits at <root>/tools/blockbench_plugin/, so
	 * the plugin's own path gives the repo away - but Blockbench only records that path AFTER the
	 * plugin's onload has run, so guessing there finds nothing on a first install. Doing it on first
	 * use instead means the record exists by the time anyone looks.
	 */
	function repoRoot() {
		const configured = Settings.get(ID + '_root');
		if (looksLikeRepo(configured)) return configured;

		const self = Plugins.all.find(function (p) { return p.id === ID; });
		if (self && self.path) {
			const guess = path.resolve(path.dirname(self.path), '..', '..');
			if (looksLikeRepo(guess)) {
				settings[ID + '_root'].set(guess);
				return guess;
			}
		}
		return null;
	}

	function python(args, options) {
		const root = repoRoot();
		if (!root) throw new Error('Set "Armor Pieces repository" in Settings to the repo root.');
		const exe = Settings.get(ID + '_python') || 'python';
		return execFileSync(exe, args, Object.assign({
			cwd: root, encoding: 'utf8', windowsHide: true,
		}, options || {}));
	}

	function tool(name, args) {
		return python([path.join('tools', name)].concat(args || []));
	}

	function anchors() {
		if (!anchorCache) anchorCache = JSON.parse(tool('bb_rig.py', ['--list-anchors']));
		return anchorCache;
	}

	// ---- pack discovery -----------------------------------------------------------------------

	/*
	 * A pack is any directory holding either half of a piece: the datapack half under
	 * data/<ns>/armorpieces/armor_decoration/, or the resourcepack half under
	 * assets/<ns>/armorpieces/decoration/. Both halves usually live in one directory - the mod's own
	 * src/main/resources does - but a pack that ships only one half is still worth listing, because
	 * a piece missing its other half is exactly the thing you want to see and fix.
	 */
	const DATA_REL = ['armorpieces', 'armor_decoration'];
	const ASSET_REL = ['armorpieces', 'decoration'];

	function searchRoots() {
		const root = repoRoot();
		if (!root) return [];
		const roots = [path.join(root, 'src', 'main', 'resources')];
		for (const relative of [['run', 'resourcepacks'], ['run', 'saves']]) {
			const dir = path.join(root, ...relative);
			if (!fs.existsSync(dir)) continue;
			for (const entry of fs.readdirSync(dir)) {
				const candidate = path.join(dir, entry);
				if (!fs.statSync(candidate).isDirectory()) continue;
				roots.push(candidate);
				// A world's datapacks sit one level deeper than the world folder.
				const datapacks = path.join(candidate, 'datapacks');
				if (fs.existsSync(datapacks)) {
					for (const pack of fs.readdirSync(datapacks)) {
						roots.push(path.join(datapacks, pack));
					}
				}
			}
		}
		return roots;
	}

	function namespacesIn(packDir, kind) {
		const base = path.join(packDir, kind);
		if (!fs.existsSync(base)) return [];
		return fs.readdirSync(base).filter(function (entry) {
			return fs.statSync(path.join(base, entry)).isDirectory();
		});
	}

	function listJson(dir) {
		if (!fs.existsSync(dir)) return [];
		return fs.readdirSync(dir)
			.filter(function (f) { return f.endsWith('.json'); })
			.map(function (f) { return f.slice(0, -5); });
	}

	function pieceRecord(packDir, namespace, name) {
		const dataDir = path.join(packDir, 'data', namespace, ...DATA_REL);
		const assetDir = path.join(packDir, 'assets', namespace, ...ASSET_REL);
		return {
			name: name,
			namespace: namespace,
			key: namespace + ':' + name,
			pack: packDir,
			data: path.join(dataDir, name + '.json'),
			geometry: path.join(assetDir, name + '.json'),
			texture: path.join(packDir, 'assets', namespace, 'textures', 'entity', 'decoration',
				name + '.png'),
		};
	}

	function piecesIn(packDir) {
		const found = {};
		for (const namespace of new Set(
			namespacesIn(packDir, 'data').concat(namespacesIn(packDir, 'assets')))) {
			const dataDir = path.join(packDir, 'data', namespace, ...DATA_REL);
			const assetDir = path.join(packDir, 'assets', namespace, ...ASSET_REL);
			for (const name of new Set(listJson(dataDir).concat(listJson(assetDir)))) {
				found[namespace + ':' + name] = pieceRecord(packDir, namespace, name);
			}
		}
		return Object.values(found);
	}

	function allPieces() {
		const out = [];
		for (const packDir of searchRoots()) out.push(...piecesIn(packDir));
		return out;
	}

	function pieceLabel(piece) {
		const root = repoRoot();
		const where = path.relative(root, piece.pack).replace(/\\/g, '/') || '.';
		const half = (fs.existsSync(piece.data) ? '' : ' [no data]') +
			(fs.existsSync(piece.geometry) ? '' : ' [no model]');
		return piece.key + '  (' + where + ')' + half;
	}

	/*
	 * Which PNG to actually edit. In this repo the file inside the pack is an INSTALLED COPY - the
	 * master in tools/decoration_masters is the source of truth, and sync_decoration_masters.py
	 * copies it in. Painting the installed copy would put the edit in the place the next sync
	 * overwrites. So a piece with a master edits the master; a piece in someone else's pack, which
	 * has no master, edits the pack file directly.
	 */
	function masterFor(piece) {
		const root = repoRoot();
		const master = path.join(root, 'tools', 'decoration_masters', piece.name + '.png');
		if (fs.existsSync(master)) return { file: master, isMaster: true };
		return { file: piece.texture, isMaster: false };
	}

	/* The anchors the piece's datapack half lists, first one first. Empty when there is no data. */
	function anchorsOf(piece) {
		if (!piece || !fs.existsSync(piece.data)) return [];
		const data = JSON.parse(fs.readFileSync(piece.data, 'utf8'));
		return (data.anchors || []).filter(function (a) { return typeof a === 'string'; });
	}

	/*
	 * The fittings the piece's datapack half lists, resolved by preview_material.py: the mask name,
	 * the type, whether it is a mask over the texture, a display name, and the values it can take,
	 * each with the colour it asks the baker for. Resolving means reading fitting files, tags and
	 * language files across the pack and the mod, which is Python's job, not this file's. Cached on
	 * the project: a piece's fittings change only when its data file does, and Rebuild rereads it.
	 */
	function fittingsOf(piece) {
		if (!piece || !Project || !fs.existsSync(piece.data)) return [];
		if (!Project[ID + '_fittings']) {
			try {
				Project[ID + '_fittings'] = JSON.parse(tool('preview_material.py', ['--fittings', piece.data]));
			} catch (err) {
				console.error(err);
				Project[ID + '_fittings'] = [];
			}
		}
		return Project[ID + '_fittings'];
	}

	/* The fittings that are a region of the texture - the ones with a sheet to paint and preview. */
	function maskedFittings() {
		return fittingsOf(currentPiece()).filter(function (f) { return f.masked; });
	}

	// ---- the template recipe ------------------------------------------------------------------

	/*
	 * How a player gets a part: a template item for its socket, carrying the part as a component.
	 * Every shipped part hands its template out the same way - a ring of one item around one centre
	 * item - so a recipe is two choices, and the file is written from them on Save. The centre item
	 * is what makes the recipe read as the part's; the ring is paper unless there is a reason.
	 */
	const RING_PATTERN = [' # ', '#F#', ' # '];
	const ITEM_ID = /^[a-z0-9_.-]+:[a-z0-9_\/.-]+$/;
	let itemCache = null;

	function recipeFileFor(piece) {
		return path.join(piece.pack, 'data', piece.namespace, 'recipe', 'template_' + piece.name + '.json');
	}

	/* Every vanilla item id with its name, read out of the game jar by vanilla_assets.py. */
	function vanillaItems() {
		if (!itemCache) {
			try {
				itemCache = JSON.parse(tool('vanilla_assets.py', ['--list-items']));
			} catch (err) {
				console.error(err);
				itemCache = {};
			}
		}
		return itemCache;
	}

	function ingredientId(value) {
		if (typeof value === 'string') return value;
		if (value && typeof value.item === 'string') return value.item;
		return '';
	}

	/* The two choices an existing recipe file was written from, or null if there is no such file
	 * or it is not shaped the way this plugin writes it (then it is somebody's hand-made recipe and
	 * is left alone). */
	function readRecipe(piece) {
		const file = recipeFileFor(piece);
		if (!fs.existsSync(file)) return null;
		try {
			const recipe = JSON.parse(fs.readFileSync(file, 'utf8'));
			if (recipe.type !== 'minecraft:crafting_shaped') return null;
			if (JSON.stringify(recipe.pattern) !== JSON.stringify(RING_PATTERN)) return null;
			const focus = ingredientId(recipe.key && recipe.key.F);
			const ring = ingredientId(recipe.key && recipe.key['#']);
			if (!focus || !ring) return null;
			return { focus: focus, ring: ring };
		} catch (err) {
			return null;
		}
	}

	function knownItem(id) {
		if (!ITEM_ID.test(id)) return false;
		// Only vanilla ids can be checked; another mod's item is taken on trust.
		if (!id.startsWith('minecraft:')) return true;
		return !!vanillaItems()[id];
	}

	/* Write the recipe for the current choices. Returns what was done, for the Save message. */
	function writeRecipe(piece) {
		const s = state();
		const focus = (s.recipe_focus || '').trim();
		const ring = (s.recipe_ring || '').trim() || 'minecraft:paper';
		if (!focus) return 'no recipe (no centre item)';
		for (const id of [focus, ring]) {
			if (!knownItem(id)) {
				Blockbench.showMessageBox({
					title: 'Unknown item',
					message: id + ' is not a vanilla item id, so the recipe was not written. Use ' +
						'namespace:name, e.g. minecraft:feather.',
				});
				return 'recipe not written';
			}
		}
		const socket = anchorsOf(piece)[0] || s.anchor;
		const recipe = {
			type: 'minecraft:crafting_shaped',
			category: 'equipment',
			pattern: RING_PATTERN,
			key: { '#': ring, F: focus },
			result: {
				id: 'armorpieces:' + socket + '_template',
				components: { 'armorpieces:decoration': piece.key },
			},
		};
		writeJson(recipeFileFor(piece), recipe);
		return 'recipe: ' + focus + ' in ' + ring;
	}

	/*
	 * The autocomplete behind the two item fields. Filled once, on first use rather than when the
	 * panel is built, because the repository - and so the game jar - is not known until then.
	 */
	let itemListFilled = false;

	function fillItemLists() {
		if (itemListFilled || !panel || !panel.form) return;
		const items = vanillaItems();
		const ids = Object.keys(items);
		if (!ids.length) return;
		for (const field of ['recipe_focus', 'recipe_ring']) {
			const element = panel.form.form_data[field];
			const input = element && element.input;
			if (!input) continue;
			const listId = panel.form.uuid + '_' + field + '_list';
			input.setAttribute('list', listId);
			let list = document.getElementById(listId);
			if (!list) {
				list = Interface.createElement('datalist', { id: listId });
				input.parentElement.append(list);
			}
			list.innerHTML = '';
			for (const id of ids) list.append(Interface.createElement('option', { value: id }, items[id]));
		}
		itemListFilled = true;
	}

	// ---- opening ------------------------------------------------------------------------------

	function tempDir() {
		const dir = path.join(os.tmpdir(), 'armorpieces-bb');
		if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
		return dir;
	}

	function openPiece(piece, anchor) {
		const listed = anchorsOf(piece);
		anchor = anchor || listed[0];
		if (!anchor) {
			Blockbench.showMessageBox({
				title: 'No anchor',
				message: 'This piece has no datapack half, so there is nothing saying where on the ' +
					'body it goes. Add ' + piece.data + ' with an "anchors" list first.',
			});
			return false;
		}
		if (!fs.existsSync(piece.geometry)) {
			Blockbench.showMessageBox({
				title: 'No geometry',
				message: 'This piece has no resourcepack half yet: ' + piece.geometry,
			});
			return false;
		}

		const out = tempDir();
		const texture = masterFor(piece);
		const args = [anchor, '--part', piece.geometry, '--out-dir', out,
			'--material', Settings.get(ID + '_material') || 'iron'];
		if (fs.existsSync(texture.file)) args.push('--master', texture.file);
		tool('bb_rig.py', args);

		const file = path.join(out, anchor + '.bbmodel');
		const content = JSON.parse(fs.readFileSync(file, 'utf8'));
		// The rig is written as `free`, which is what it is. Loading it as the plugin's own format
		// is what turns the trimmed-down workspace on; the format shares every flag with `free`.
		content.meta.model_format = ID;
		Codecs.project.load(content, { path: file, content: content });

		Project[ID + '_piece'] = piece;
		Project[ID + '_texture'] = texture;
		Project[ID + '_fittings'] = null;
		Project[ID + '_state'] = Object.assign(defaultState(), { anchor: anchor });
		const recipe = readRecipe(piece);
		if (recipe) {
			Project[ID + '_state'].recipe_focus = recipe.focus;
			Project[ID + '_state'].recipe_ring = recipe.ring;
		}
		Project.name = piece.name;
		// The rig is scratch; saving it would put a rig where the piece should go. Save Piece is the
		// only correct way out, so the project is left without a save path on purpose.
		Project.save_path = '';
		Project.export_path = '';

		// Format activation ran inside load(), before the piece was attached, so it saw an ordinary
		// project. Now that this is a piece, bring the workspace up.
		enterWorkspace();
		Blockbench.showQuickMessage(piece.name + ' on ' + anchor, 2000);
		return true;
	}

	/*
	 * Rebuild the rig for the piece from what is on disk. Used by the anchor selector and the
	 * Rebuild button. It is a reload, not a re-pose: unsaved geometry would be lost, so it refuses
	 * while there is anything to lose.
	 */
	function reopen(anchor) {
		const piece = currentPiece();
		if (!piece) return;
		if (Project.undo && Project.undo.history.length) {
			Blockbench.showMessageBox({
				title: 'Unsaved edits',
				message: 'Rebuilding reloads ' + piece.name + ' from disk. Save the piece first, or ' +
					'undo the edits.',
			});
			syncForm();
			return;
		}
		const old = Project;
		if (!openPiece(piece, anchor) || !old || old === Project) return;
		// close() selects the project it closes on the way out, and Blockbench then lands on
		// whichever tab it likes; the rebuilt one is the one to be on.
		const fresh = Project;
		old.close(true).then(function () { if (fresh !== Project) fresh.select(); });
	}

	function pickPiece(title, onPick) {
		const pieces = allPieces();
		if (!pieces.length) {
			Blockbench.showMessageBox({
				title: 'No packs found',
				message: 'Nothing under src/main/resources or run/. Check the repository path in ' +
					'Settings.',
			});
			return;
		}
		const options = {};
		pieces.forEach(function (piece, i) { options[i] = pieceLabel(piece); });
		new Dialog({
			id: ID + '_pick',
			title: title,
			form: { piece: { label: 'Piece', type: 'select', options: options, value: '0' } },
			onConfirm: function (result) {
				this.hide();
				onPick(pieces[parseInt(result.piece, 10)]);
			},
		}).show();
	}

	// ---- saving -------------------------------------------------------------------------------

	function savePiece() {
		const piece = currentPiece();
		if (!piece) {
			Blockbench.showQuickMessage('This project did not come from a pack', 2500);
			return;
		}

		// Geometry: write the live project to a scratch file and let bb_geo do the conversion, so
		// the export path here is the same one the command line uses.
		const scratch = path.join(tempDir(), 'save.bbmodel');
		fs.writeFileSync(scratch, Codecs.project.compile(), 'utf8');
		tool('bb_geo.py', ['export', scratch, '--out', piece.geometry]);

		// Texture: the master is a linked file, so Blockbench writes it back where it came from.
		const texture = Project[ID + '_texture'];
		const part = tex('part');
		if (part && texture) {
			// save() writes back to the linked path; save(true) is "save as" and opens a native
			// file picker, which blocks the whole app. Every sheet is a real authored file linked
			// the same way: the master, the static layer, and each fitting mask.
			for (const sheet of sheets()) sheet.save();
			if (texture.isMaster) {
				// Installing is the sync script's job, and it is also what checks the master against
				// the geometry - the check that catches paint sliding off a face it was drawn for.
				const report = tool('sync_decoration_masters.py', [piece.name]);
				if (report.trim()) console.log('[armorpieces] ' + report.trim());
			}
		}

		const recipe = writeRecipe(piece);
		Blockbench.showQuickMessage('Saved ' + piece.name + ' to ' + piece.namespace + ' - ' + recipe, 3000);
	}

	// ---- new piece ----------------------------------------------------------------------------

	// One bone with one small cube, sitting on the anchor. A new piece opens as something visible
	// and movable rather than an empty group, because an empty group in Blockbench looks broken.
	function starterGeometry() {
		return {
			texture_width: 64,
			texture_height: 32,
			bones: [{
				name: 'main',
				pivot: [0, 0, 0],
				cubes: [{ origin: [-2, -2, -1], size: [4, 2, 2], uv: [0, 0] }],
			}],
		};
	}

	function writeJson(file, value) {
		fs.mkdirSync(path.dirname(file), { recursive: true });
		fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
	}

	function blankPng(width, height) {
		const canvas = document.createElement('canvas');
		canvas.width = width;
		canvas.height = height;
		return canvas.toDataURL('image/png');
	}

	function newPiece() {
		const packs = searchRoots().filter(function (d) { return fs.existsSync(d); });
		if (!packs.length) {
			Blockbench.showMessageBox({ title: 'No packs found', message: 'Check the repository path.' });
			return;
		}
		const root = repoRoot();
		const packOptions = {};
		packs.forEach(function (p, i) {
			packOptions[i] = path.relative(root, p).replace(/\\/g, '/') || '.';
		});
		const anchorOptions = {};
		for (const name of Object.keys(anchors())) {
			anchorOptions[name] = name + '  (' + anchors()[name].part + ')';
		}

		new Dialog({
			id: ID + '_new',
			title: 'New Armor Piece',
			form: {
				name: { label: 'Name', type: 'text', value: '', placeholder: 'gorget' },
				namespace: { label: 'Namespace', type: 'text', value: 'armorpieces' },
				anchor: { label: 'Anchor', type: 'select', options: anchorOptions },
				pack: { label: 'Pack', type: 'select', options: packOptions, value: '0' },
			},
			onConfirm: function (result) {
				const name = (result.name || '').trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
				if (!name) {
					Blockbench.showQuickMessage('Name a piece first', 2000);
					return;
				}
				this.hide();

				const packDir = packs[parseInt(result.pack, 10)];
				const namespace = result.namespace.trim() || 'armorpieces';
				const piece = pieceRecord(packDir, namespace, name);
				if (fs.existsSync(piece.data) || fs.existsSync(piece.geometry)) {
					Blockbench.showMessageBox({
						title: 'Already exists',
						message: namespace + ':' + name + ' is already in that pack.',
					});
					return;
				}

				writeJson(piece.data, {
					asset_id: namespace + ':' + name,
					description: { translate: 'decoration.' + namespace + '.' + name },
					anchors: [result.anchor],
				});
				writeJson(piece.geometry, starterGeometry());

				// A blank master, so the piece has a texture to paint rather than sampling nothing.
				fs.mkdirSync(path.dirname(piece.texture), { recursive: true });
				fs.writeFileSync(piece.texture, Buffer.from(blankPng(64, 32).split(',')[1], 'base64'));

				const lang = path.join(packDir, 'assets', namespace, 'lang', 'en_us.json');
				if (fs.existsSync(lang)) {
					const entries = JSON.parse(fs.readFileSync(lang, 'utf8'));
					const key = 'decoration.' + namespace + '.' + name;
					if (!entries[key]) {
						entries[key] = name.replace(/_/g, ' ').replace(/\b\w/g, function (c) {
							return c.toUpperCase();
						});
						writeJson(lang, entries);
					}
				}

				Blockbench.showQuickMessage('Created ' + namespace + ':' + name, 2500);
				openPiece(piece, result.anchor);
			},
		}).show();
	}

	// ---- textures: what the model shows, and what the brush edits ------------------------------

	/*
	 * A part is authored as one greyscale master - luminance is shading, alpha is silhouette - plus
	 * an optional RGBA companion whose opaque pixels keep their own colour instead of taking the
	 * material's, plus one greyscale mask per masked fitting: the region that takes the second
	 * material, shaded by its own values. Three kinds of thing can be edited, and one looked at:
	 *
	 *   part            the greyscale you paint. Everything opaque here takes the material's colour.
	 *   part_static     the opt-out layer, painted in real colours. Only exists if the part has one.
	 *   part_<fitting>  a fitting's mask, greyscale like the master. Only exists once painted.
	 *   preview         a composite of all of them through a material's ramp, with the fittings
	 *                   filled as the panel says. Never edited: strokes over it are routed to
	 *                   whichever of the others is the edit target.
	 */
	const MATERIALS = ['amethyst', 'copper', 'diamond', 'emerald', 'gold', 'iron', 'lapis',
		'netherite', 'quartz', 'redstone', 'resin', 'copper_darker', 'diamond_darker', 'gold_darker',
		'iron_darker', 'netherite_darker'];

	/*
	 * The static layer and the masks are optional, so a piece starts without them. The first switch
	 * to editing one creates it: a blank sheet the size of the master, next to the master, linked
	 * the same way, so Save writes it back and the sync script installs it with the master.
	 */
	function createSheet(id, suffix) {
		const piece = currentPiece();
		const master = tex('part');
		if (!piece || !master || !master.canvas.width) return null;
		const file = masterFor(piece).file.replace(/\.png$/i, suffix + '.png');
		if (!fs.existsSync(file)) {
			fs.writeFileSync(file, Buffer.from(
				blankPng(master.canvas.width, master.canvas.height).split(',')[1], 'base64'));
		}
		const sheet = new Texture({
			name: id, id: id,
			uv_width: master.uv_width, uv_height: master.uv_height,
		}).fromPath(file).add(false);
		Blockbench.showQuickMessage('Created ' + path.basename(file), 2500);
		return sheet;
	}

	function createStaticLayer() {
		return createSheet('part_static', '_static');
	}

	function createMaskLayer(name) {
		return createSheet(maskId(name), '_' + name);
	}

	/* The texture the brush lands on. Falls back to the master when the chosen sheet is missing. */
	function editTarget() {
		const s = state();
		if (s.edit === 'static') {
			const statics = tex('part_static');
			if (statics) return statics;
			s.edit = 'master';
		}
		if (s.edit === 'fitting') {
			const mask = s.fitting ? tex(maskId(s.fitting)) : null;
			if (mask) return mask;
			s.edit = 'master';
		}
		return tex('part');
	}

	function pointPartAt(texture) {
		for (const cube of Cube.all) {
			if (cube.locked) continue;
			for (const face of Object.keys(cube.faces)) cube.faces[face].texture = texture.uuid;
		}
		Canvas.updateAllFaces();
	}

	/*
	 * Put the right texture on the model and the right one under the brush. They differ exactly
	 * when a material preview is on: the model shows the composite, the UV editor and the brush
	 * stay on the layer being edited.
	 */
	function applyTextures() {
		if (!isWorkspace()) return;
		const target = editTarget();
		if (!target) return;
		const s = state();
		let shown = target;
		if (s.preview) {
			shown = ensurePreview() || target;
			if (shown === target) s.preview = false;
		}
		pointPartAt(shown);
		if (Texture.selected !== target) target.select();
		if (UVEditor.vue && typeof UVEditor.vue.updateTexture === 'function') UVEditor.vue.updateTexture();
		if (UVEditor.vue) UVEditor.vue.updateTextureCanvas();
	}

	// ---- material preview ---------------------------------------------------------------------

	/*
	 * Ramps come from preview_material.py, which is the port of DecorationPalette. The plugin
	 * asks once per material and once per static colour, and only ever indexes the answer.
	 */
	function fetchRamps(material, staticColours) {
		const need = staticColours.filter(function (c) { return !ramps.static[c]; });
		if (ramps.material[material] !== undefined && !need.length) return;
		const args = ['--ramp', material];
		if (need.length) args.push('--static-colours', need.join(','));
		const result = JSON.parse(tool('preview_material.py', args));
		ramps.material[material] = result.material;
		for (const key of Object.keys(result.static || {})) ramps.static[key] = result.static[key];
	}

	function hex(r, g, b) {
		return '#' + ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1);
	}

	function staticColoursIn(statics) {
		const found = new Set();
		if (!statics || !statics.canvas.width) return [];
		const data = statics.ctx.getImageData(0, 0, statics.canvas.width, statics.canvas.height).data;
		for (let i = 0; i < data.length; i += 4) {
			if (data[i + 3] !== 0) found.add(hex(data[i], data[i + 1], data[i + 2]));
		}
		return Array.from(found);
	}

	/*
	 * What a fitting's chosen value asks the baker for, as preview_material.py listed it:
	 * 'palette:<material>' for a second trim material, 'solid:#rrggbb' for a dye. '' when empty.
	 */
	function fittingColour(fitting, value) {
		const option = (fitting.options || []).find(function (o) { return o.value === value; });
		return option ? option.colour : '';
	}

	/*
	 * The filled masked fittings as the compositor lays them: in the part's own order, each with
	 * its mask sheet and the ramp its value indexes - a material's, or a dye colour's static ramp,
	 * both from preview_material.py. A fitting whose mask is not in the project changes nothing,
	 * as in the game; a ramp not fetched yet is null and the mask shows at its own greys until
	 * fetchFittingRamps has run.
	 */
	function previewMasks() {
		const s = state();
		const out = [];
		for (const fitting of maskedFittings()) {
			const value = s.fittings[fitting.name];
			if (!value) continue;
			const mask = tex(maskId(fitting.name));
			if (!mask || !mask.canvas.width) continue;
			const colour = fittingColour(fitting, value);
			let ramp = null;
			if (colour.indexOf('palette:') === 0) ramp = ramps.material[colour.slice(8)] || null;
			else if (colour.indexOf('solid:') === 0) ramp = ramps.static[colour.slice(6)] || null;
			out.push({ texture: mask, ramp: ramp });
		}
		return out;
	}

	/* Ask for the ramps the filled fittings index, the same way and to the same cache. */
	function fetchFittingRamps() {
		const s = state();
		for (const fitting of maskedFittings()) {
			const colour = fittingColour(fitting, s.fittings[fitting.name] || '');
			if (colour.indexOf('palette:') === 0) fetchRamps(colour.slice(8), []);
			else if (colour.indexOf('solid:') === 0) fetchRamps(s.material, [colour.slice(6)]);
		}
	}

	/*
	 * DecorationTextureManager.recolour as a table lookup: alpha from the master, colour from the
	 * static layer's own ramp where it is opaque, else from the material's ramp, both indexed by
	 * the master's red channel - exactly as the game reads it. Then applyMask per filled fitting,
	 * in order: the mask's own red channel through the fitting's ramp, the master's alpha still the
	 * silhouette. Returns the static colours that had no ramp yet, which are drawn flat until
	 * fetchRamps has been asked for them.
	 */
	function compositeInto(canvas, master, statics, material, masks) {
		const w = master.canvas.width, h = master.canvas.height;
		const src = master.ctx.getImageData(0, 0, w, h).data;
		const sw = statics && statics.canvas.width ? statics.canvas.width : 0;
		const sh = statics ? statics.canvas.height : 0;
		const sdata = sw ? statics.ctx.getImageData(0, 0, sw, sh).data : null;
		const ramp = ramps.material[material] || null;
		const missing = new Set();

		const out = new ImageData(w, h);
		const dst = out.data;
		for (let y = 0; y < h; y++) {
			for (let x = 0; x < w; x++) {
				const i = (y * w + x) * 4;
				const alpha = src[i + 3];
				if (alpha === 0) continue;
				const lum = src[i];
				let colour = null;
				if (sdata && x < sw && y < sh) {
					const j = (y * sw + x) * 4;
					if (sdata[j + 3] !== 0) {
						const key = hex(sdata[j], sdata[j + 1], sdata[j + 2]);
						const table = ramps.static[key];
						if (table) {
							colour = table[lum];
						} else {
							colour = [sdata[j], sdata[j + 1], sdata[j + 2]];
							missing.add(key);
						}
					}
				}
				if (!colour) colour = ramp ? ramp[lum] : [src[i], src[i + 1], src[i + 2]];
				dst[i] = colour[0];
				dst[i + 1] = colour[1];
				dst[i + 2] = colour[2];
				dst[i + 3] = alpha;
			}
		}
		for (const mask of masks || []) {
			const mw = mask.texture.canvas.width, mh = mask.texture.canvas.height;
			const mdata = mask.texture.ctx.getImageData(0, 0, mw, mh).data;
			const cw = Math.min(w, mw), ch = Math.min(h, mh);
			for (let y = 0; y < ch; y++) {
				for (let x = 0; x < cw; x++) {
					const j = (y * mw + x) * 4;
					if (mdata[j + 3] === 0) continue;
					const i = (y * w + x) * 4;
					const alpha = src[i + 3];
					if (alpha === 0) continue;
					const colour = mask.ramp ? mask.ramp[mdata[j]] : [mdata[j], mdata[j + 1], mdata[j + 2]];
					dst[i] = colour[0];
					dst[i + 1] = colour[1];
					dst[i + 2] = colour[2];
					dst[i + 3] = alpha;
				}
			}
		}
		if (canvas.width !== w || canvas.height !== h) {
			canvas.width = w;
			canvas.height = h;
		}
		canvas.getContext('2d').putImageData(out, 0, 0);
		return Array.from(missing);
	}

	/*
	 * The preview texture, created on first use from a finished composite. Created from the
	 * composite rather than blank because Blockbench redraws a texture's canvas from its image once
	 * that image has loaded, and that load is asynchronous - a blank first image would wipe the
	 * first composite the moment it arrived.
	 */
	function ensurePreview() {
		const master = tex('part');
		if (!master || !master.canvas.width) return null;
		const s = state();
		const statics = tex('part_static');
		try {
			fetchRamps(s.material, staticColoursIn(statics));
			fetchFittingRamps();
		} catch (err) {
			console.error(err);
			Blockbench.showQuickMessage('No ramp for ' + s.material + ' - run tools/vanilla_assets.py', 3000);
			return null;
		}
		let preview = tex('preview');
		if (preview) {
			refreshPreview(false);
			return preview;
		}
		const scratch = document.createElement('canvas');
		compositeInto(scratch, master, statics, s.material, previewMasks());
		preview = new Texture({
			name: 'preview', id: 'preview', internal: true,
			uv_width: master.uv_width, uv_height: master.uv_height,
		}).fromDataURL(scratch.toDataURL('image/png')).add(false);
		return preview;
	}

	/*
	 * Recomposite the preview from whatever the master and static canvases hold right now,
	 * including the stroke in progress. `settle` is for the end of a stroke: a static colour seen
	 * for the first time gets its ramp fetched then, not under the brush.
	 */
	function refreshPreview(settle) {
		if (!isWorkspace() || !state().preview) return;
		const preview = tex('preview');
		const master = tex('part');
		if (!preview || !master || !master.canvas.width) return;
		const s = state();
		const statics = tex('part_static');
		let missing = compositeInto(preview.canvas, master, statics, s.material, previewMasks());
		if (missing.length && settle) {
			try {
				fetchRamps(s.material, missing);
				compositeInto(preview.canvas, master, statics, s.material, previewMasks());
			} catch (err) {
				console.error(err);
			}
		}
		const material = preview.getOwnMaterial();
		if (material && material.map) material.map.needsUpdate = true;
	}

	// ---- greyscale master ---------------------------------------------------------------------

	/*
	 * The master is greyscale by definition - the game reads a pixel's value as a position on the
	 * material's ramp, so a coloured pixel there is not a colour, it is a wrong shade. Rather than
	 * ask an author to remember that, any colour painted onto the master is folded to its luma
	 * under the brush. A fitting mask is read the same way and folds the same way. The static
	 * layer is left alone: colour is the whole point of it.
	 *
	 * Folding happens inside the stroke, on the canvas the paint tool just drew on, rather than
	 * after it. That is what keeps the undo history legal: the snapshot Blockbench takes when the
	 * stroke ends already holds grey pixels, so a redo brings back grey, not the colour that was
	 * never allowed on the sheet.
	 */
	function foldCanvasToGreyscale(canvas) {
		const ctx = canvas.getContext('2d');
		const image = ctx.getImageData(0, 0, canvas.width, canvas.height);
		const data = image.data;
		let changed = false;
		for (let i = 0; i < data.length; i += 4) {
			if (data[i + 3] === 0) continue;
			// Rec. 601 luma, which is what "desaturate" means to anyone painting.
			const v = Math.round(data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114);
			if (data[i] !== v || data[i + 1] !== v || data[i + 2] !== v) changed = true;
			data[i] = data[i + 1] = data[i + 2] = v;
		}
		if (changed) ctx.putImageData(image, 0, 0);
		return changed;
	}

	function foldsMaster() {
		return isWorkspace() && Settings.get(ID + '_greyscale');
	}

	/* The safety net for anything that reaches the master without passing under the brush. */
	function enforceGreyscale(texture) {
		if (greyscaleGuard || !texture.canvas.width) return;
		greyscaleGuard = true;
		try {
			const probe = document.createElement('canvas');
			probe.width = texture.canvas.width;
			probe.height = texture.canvas.height;
			probe.getContext('2d').drawImage(texture.canvas, 0, 0);
			if (!foldCanvasToGreyscale(probe)) return;
			texture.edit(function (canvas) { foldCanvasToGreyscale(canvas); }, { no_undo: true });
			Blockbench.showQuickMessage((texture.id === 'part' ? 'Master' : 'Mask')
				+ ' is greyscale - colour folded to value', 1500);
		} finally {
			greyscaleGuard = false;
		}
	}

	function onEditTexture(data) {
		if (!data || !data.texture || !isWorkspace()) return;
		const id = data.texture.id;
		if (!isSheetId(id)) return;
		if (isGreyId(id) && foldsMaster() && data.canvas) foldCanvasToGreyscale(data.canvas);
		refreshPreview(false);
	}

	function onFinishEdit(data) {
		if (!isWorkspace()) return;
		const textures = (data && data.aspects && data.aspects.textures) || [];
		let touched = false;
		for (const texture of textures) {
			if (isGreyId(texture.id) && foldsMaster()) enforceGreyscale(texture);
			if (isSheetId(texture.id)) touched = true;
		}
		if (touched) refreshPreview(true);
	}

	/*
	 * Undo puts a texture back by reloading its image, which lands a moment later. Recomposite
	 * now for the common case and once more after the reload has had time to draw.
	 */
	function onUndoRedo() {
		if (!isWorkspace()) return;
		syncSheetSize();
		refreshPreview(true);
		setTimeout(function () { refreshPreview(true); }, 200);
	}

	// ---- palette ------------------------------------------------------------------------------

	/*
	 * Master and mask modes paint values, so the palette offers values: the ramp's three stops and
	 * the steps between them. Static mode gets the author's own palette back.
	 *
	 * Blockbench writes the live palette to its own storage whenever a colour is picked, so the
	 * greys can end up persisted as if they were the author's. The author's palette is therefore
	 * stashed in storage too, for as long as the greys are in, and put back on every way out:
	 * switching mode, leaving the piece, unloading the plugin, closing Blockbench, and - should
	 * none of those have run - the next time the plugin loads and finds the greys still there.
	 */
	const GREYS = [0, 32, 64, 96, 127, 160, 192, 224, 255].map(function (v) { return hex(v, v, v); });
	const STASH_KEY = ID + '_user_palette';

	function stashedPalette() {
		try {
			const raw = localStorage.getItem(STASH_KEY);
			const list = raw ? JSON.parse(raw) : null;
			return list instanceof Array && list.length ? list : null;
		} catch (err) {
			return null;
		}
	}

	function stashPalette(list) {
		try {
			if (list) localStorage.setItem(STASH_KEY, JSON.stringify(list));
			else localStorage.removeItem(STASH_KEY);
		} catch (err) {
			// Storage is a convenience here, not a requirement.
		}
	}

	function isGreyPalette(list) {
		return list.join() === GREYS.join();
	}

	function restorePalette() {
		if (!ColorPanel.palette) return;
		const saved = userPalette || stashedPalette();
		userPalette = null;
		stashPalette(null);
		if (saved && isGreyPalette(ColorPanel.palette)) ColorPanel.palette.replace(saved);
	}

	function applyPalette() {
		if (!ColorPanel.palette) return;
		const greys = isWorkspace() && state().edit !== 'static';
		if (greys) {
			if (userPalette === null && !isGreyPalette(ColorPanel.palette)) {
				userPalette = ColorPanel.palette.slice();
				stashPalette(userPalette);
			}
			if (!isGreyPalette(ColorPanel.palette)) ColorPanel.palette.replace(GREYS);
			const current = ColorPanel.get();
			if (typeof current === 'string' && !/^#(..)\1\1$/i.test(current)) ColorPanel.set('#7f7f7f');
		} else {
			restorePalette();
		}
	}

	// ---- reference figure ---------------------------------------------------------------------

	const ARMOR_NAME = /_(helmet|chestplate|leggings|boots)$/;

	function isArmorCube(cube) {
		return cube.locked && ARMOR_NAME.test(cube.name);
	}

	function isPlayerCube(cube) {
		return cube.locked && !ARMOR_NAME.test(cube.name);
	}

	function applyVisibility() {
		if (!isWorkspace()) return;
		const s = state();
		for (const cube of Cube.all) {
			if (isArmorCube(cube)) cube.visibility = s.show_armor;
			else if (isPlayerCube(cube)) cube.visibility = s.show_player;
		}
		Canvas.updateVisibility();
	}

	/*
	 * The outliner shows the part and nothing else. The part hangs under the bone it is attached
	 * to, so the chain of locked groups above it has to stay - a hidden parent hides its subtree -
	 * but every locked cube and every locked group with nothing of the author's inside it goes.
	 */
	function hasUnlocked(group) {
		return group.children.some(function (child) {
			return !child.locked || (child instanceof Group && hasUnlocked(child));
		});
	}

	const outlinerRule = {
		id: ID + '_part_only',
		test: function (node) {
			if (!isWorkspace() || !state().part_only) return true;
			if (!node.locked) return true;
			return node instanceof Group && hasUnlocked(node);
		},
	};

	/* The painting grid is drawn on every visible cube. The reference is not being painted. */
	function onPaintingGrid(data) {
		const element = data && data.element;
		if (!element || !isWorkspace() || !element.locked) return;
		if (element.mesh && element.mesh.grid_box) element.mesh.grid_box.visible = false;
	}

	// ---- box UV layout ------------------------------------------------------------------------

	/*
	 * The mod's geometry format is box UV only - a cube is an addBox() at a texOffs() - so a cube
	 * with hand-placed faces exports as nonsense, and two cubes at the same offset paint over each
	 * other. Blockbench will happily create both. So after every edit that adds, converts or
	 * resizes a part cube, the plugin lays those cubes out itself: box UV on, an offset in free
	 * space on the sheet, and the sheet grown when it is full. The paint on a moved cube's faces
	 * moves with it, face by face, so a resize does not strand what was already drawn.
	 *
	 * Only the cubes the edit touched are placed. Cubes an author left alone keep their offsets,
	 * overlapping or not, because two mirrored cubes sharing one net is a thing authors do on
	 * purpose.
	 *
	 * The net is the one sync_decoration_masters.py checks against, whole pixels rounded up: the
	 * up and down faces on the first row starting one depth in, then east, north, west, south.
	 */
	function net(cube) {
		return cube.size().map(function (v) { return Math.ceil(v - 1e-9); });
	}

	function faceRects(size, offset) {
		const w = size[0], h = size[1], d = size[2];
		const u = offset[0], v = offset[1];
		return {
			up: [u + d, v, w, d],
			down: [u + d + w, v, w, d],
			east: [u, v + d, d, h],
			north: [u + d, v + d, w, h],
			west: [u + d + w, v + d, d, h],
			south: [u + d + w + d, v + d, w, h],
		};
	}

	function footprint(size, offset) {
		return [offset[0], offset[1], 2 * (size[0] + size[2]), size[1] + size[2]];
	}

	function sameRect(a, b) {
		return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3];
	}

	function overlaps(a, b) {
		return a[0] < b[0] + b[2] && b[0] < a[0] + a[2] && a[1] < b[1] + b[3] && b[1] < a[1] + a[3];
	}

	function fits(rect, width, height, taken) {
		if (rect[0] < 0 || rect[1] < 0 || rect[0] + rect[2] > width || rect[1] + rect[3] > height) {
			return false;
		}
		return !taken.some(function (t) { return overlaps(rect, t); });
	}

	/* First free spot in raster order, or null when the sheet has none. */
	function findSpot(size, width, height, taken) {
		const w = 2 * (size[0] + size[2]), h = size[1] + size[2];
		for (let v = 0; v + h <= height; v++) {
			for (let u = 0; u + w <= width; u++) {
				const rect = [u, v, w, h];
				if (!taken.some(function (t) { return overlaps(rect, t); })) return [u, v];
			}
		}
		return null;
	}

	function sheetSize() {
		const master = tex('part');
		if (master && master.uv_width && master.uv_height) return [master.uv_width, master.uv_height];
		return [Project.texture_width, Project.texture_height];
	}

	/*
	 * Move each face's pixels from where the cube used to sample to where it samples now. Reads
	 * from a snapshot so a face landing on its own old spot does not read what another face just
	 * wrote. Grows the canvas first when the layout asked for a taller sheet.
	 */
	function movePaint(texture, moves, width, height) {
		texture.edit(function (canvas) {
			const ctx = canvas.getContext('2d');
			const snapshot = document.createElement('canvas');
			snapshot.width = canvas.width;
			snapshot.height = canvas.height;
			snapshot.getContext('2d').drawImage(canvas, 0, 0);
			if (width > canvas.width || height > canvas.height) {
				canvas.width = Math.max(width, canvas.width);
				canvas.height = Math.max(height, canvas.height);
				ctx.drawImage(snapshot, 0, 0);
			}
			for (const move of moves) {
				if (move.clear) {
					ctx.clearRect(move.clear[0], move.clear[1], move.clear[2], move.clear[3]);
				}
				for (const face of Object.keys(move.from)) {
					const a = move.from[face], b = move.to[face];
					const w = Math.min(a[2], b[2]), h = Math.min(a[3], b[3]);
					if (w <= 0 || h <= 0) continue;
					ctx.clearRect(b[0], b[1], w, h);
					ctx.drawImage(snapshot, a[0], a[1], w, h, b[0], b[1], w, h);
				}
			}
		}, { no_undo: true });
	}

	function growSheet(width, height) {
		Project.texture_width = width;
		Project.texture_height = height;
		for (const texture of sheets().concat(tex('preview') || [])) {
			texture.uv_width = width;
			texture.uv_height = height;
		}
	}

	/*
	 * The project's resolution is what bb_geo exports as the geometry's texture size, and undo
	 * does not track it. The master's UV size is tracked, so after an undo the project follows it.
	 */
	function syncSheetSize() {
		const master = tex('part');
		if (!master || !master.uv_width || !master.uv_height) return;
		if (Project.texture_width === master.uv_width && Project.texture_height === master.uv_height) return;
		Project.texture_width = master.uv_width;
		Project.texture_height = master.uv_height;
		Canvas.updateAllUVs();
	}

	/*
	 * Runs inside the edit, before Blockbench snapshots its result, so the offsets and the moved
	 * paint are part of the same undo entry as the resize or the added cube that caused them.
	 * `save` is the undo record being finished; its `elements` hold every touched cube as it was.
	 */
	function autoLayout(save, aspects) {
		const touched = new Set(aspects.elements || []);
		const placing = [];
		for (const cube of Cube.all) {
			if (cube.locked) continue;
			// A cube with hand-placed faces cannot be authored in this format, so it is converted
			// whichever edit finds it; a box-UV cube is only reconsidered when the edit touched it.
			if (cube.box_uv && !touched.has(cube)) continue;
			const before = save.elements && save.elements[cube.uuid];

			const size = net(cube);
			const oldSize = before && before.box_uv && before.from && before.to
				? [0, 1, 2].map(function (i) { return Math.ceil(before.to[i] - before.from[i] - 1e-9); })
				: null;
			const oldOffset = oldSize ? (before.uv_offset || [0, 0]).slice() : null;
			const sizeChanged = !oldSize || oldSize.some(function (v, i) { return v !== size[i]; });
			// A cube that merely moved keeps its net; nothing about its texture changed.
			if (cube.box_uv && oldSize && !sizeChanged) continue;
			placing.push({ cube: cube, size: size, oldSize: oldSize, oldOffset: oldOffset });
		}
		if (!placing.length) return;

		const sheet = sheetSize();
		let width = sheet[0];
		let height = sheet[1];
		const placingCubes = new Set(placing.map(function (p) { return p.cube; }));
		const taken = [];
		for (const cube of Cube.all) {
			if (cube.locked || placingCubes.has(cube) || !cube.box_uv) continue;
			taken.push(footprint(net(cube), cube.uv_offset));
		}

		// Biggest first packs tighter; the current offset is tried first so a cube that still fits
		// where it is stays where it is.
		placing.sort(function (a, b) {
			return (b.size[1] + b.size[2]) - (a.size[1] + a.size[2]);
		});
		for (const item of placing) {
			const current = item.cube.box_uv ? item.cube.uv_offset.slice() : null;
			let spot = null;
			if (current && fits(footprint(item.size, current), width, height, taken)) spot = current;
			while (!spot) {
				spot = findSpot(item.size, width, height, taken);
				if (!spot) {
					if (height >= 4096 && width >= 4096) {
						Blockbench.showQuickMessage('No room left on the texture for ' + item.cube.name, 3000);
						return;
					}
					// A net wider than the sheet needs a wider sheet; anything else needs a taller one.
					if (2 * (item.size[0] + item.size[2]) > width) width *= 2;
					else height *= 2;
				}
			}
			item.offset = spot;
			item.rect = footprint(item.size, spot);
			taken.push(item.rect);
		}

		// Paint moves: any placed cube that had a net before and does not have the same net now.
		const moves = [];
		for (const item of placing) {
			if (!item.oldSize) continue;
			const old = footprint(item.oldSize, item.oldOffset);
			if (sameRect(old, item.rect)) continue;
			// The old net is cleared unless something else still samples from it.
			const stillUsed = taken.some(function (t) { return t !== item.rect && overlaps(old, t); });
			moves.push({
				from: faceRects(item.oldSize, item.oldOffset),
				to: faceRects(item.size, item.offset),
				clear: stillUsed ? null : old,
			});
		}

		// Everything about to change has to be in the undo record: cubes the edit did not list
		// (a converted one), the pixels, and the sheet size. Their before-state is captured here,
		// while it still is the before-state; the after-state is captured by finishEdit.
		const unlisted = placing.map(function (p) { return p.cube; })
			.filter(function (cube) { return !touched.has(cube); });
		if (unlisted.length) {
			save.addElements(unlisted);
			aspects.elements = (aspects.elements || []).concat(unlisted);
		}
		const grew = width > sheet[0] || height > sheet[1];
		const textures = sheets();
		if (moves.length || grew) {
			// finishEdit may have been handed its own aspects object, distinct from the one the
			// record was opened with; the record reads the latter, the after-snapshot the former.
			// Both must list the textures, or undo restores one side and not the other.
			const record = save.aspects;
			record.bitmap = aspects.bitmap = true;
			if (!record.textures) record.textures = [];
			for (const texture of textures) save.addTextureOrLayer(texture);
			aspects.textures = record.textures;
			if (grew) {
				if (!save.uv_mode) {
					save.uv_mode = { box_uv: Project.box_uv, width: sheet[0], height: sheet[1] };
				}
				aspects.uv_mode = true;
			}
			for (const texture of textures) movePaint(texture, moves, width, height);
			if (grew) growSheet(width, height);
		}

		const target = editTarget();
		for (const item of placing) {
			const cube = item.cube;
			if (!cube.box_uv) cube.setUVMode(true);
			cube.uv_offset = item.offset.slice();
			cube.mirror_uv = false;
			if (target) {
				for (const face of Object.keys(cube.faces)) cube.faces[face].texture = target.uuid;
			}
		}
		if (grew) Canvas.updateAllUVs();
		Canvas.updateView({
			elements: placing.map(function (p) { return p.cube; }),
			element_aspects: { uv: true, faces: true },
		});
		UVEditor.loadData();
		refreshPreview(true);
		Blockbench.showQuickMessage('Laid out ' + placing.length + ' cube' + (placing.length === 1 ? '' : 's')
			+ (grew ? ', texture is now ' + width + 'x' + height : ''), 2000);
	}

	let layoutGuard = false;

	function onFinishEditWithLayout(save, aspects) {
		if (layoutGuard || !save || !isWorkspace()) return;
		if (!aspects.elements && !aspects.outliner) return;
		layoutGuard = true;
		try {
			autoLayout(save, aspects);
		} catch (err) {
			console.error('[armorpieces] auto layout failed', err);
			Blockbench.showQuickMessage('Auto UV layout failed - see console', 3000);
			window[ID + '_last_error'] = err && err.stack;
		} finally {
			layoutGuard = false;
		}
	}

	// ---- pose ---------------------------------------------------------------------------------

	/*
	 * The walk and sprint cycles baked into the rig are shown without leaving edit or paint mode:
	 * mark one animation as playing, set the time, and ask the animator to display that frame.
	 * Blockbench resets the pose whenever it rebuilds bones or switches mode, so the same call is
	 * repeated from those hooks. In animate mode the timeline owns the pose and this stays out.
	 */
	function applyPose() {
		if (!isWorkspace() || Animator.open) return;
		const s = state();
		let chosen = null;
		for (const animation of Animation.all) {
			animation.playing = animation.name === s.animation;
			if (animation.playing) chosen = animation;
		}
		if (!chosen) {
			Timeline.time = 0;
			Animator.showDefaultPose();
			return;
		}
		Timeline.time = Math.max(0, Math.min(1, s.phase)) * chosen.length;
		Animator.preview();
	}

	function onSelectMode() {
		applyPose();
	}

	function onUpdateView(options) {
		if (options && options.groups && options.groups.length) applyPose();
	}

	// ---- the panel ----------------------------------------------------------------------------

	let panel = null;

	function pieceOptions() {
		const options = {};
		for (const piece of allPieces()) options[piece.key] = pieceLabel(piece);
		const current = currentPiece();
		if (current && !options[current.key]) options[current.key] = current.key;
		return options;
	}

	function anchorOptions() {
		const options = {};
		const piece = currentPiece();
		const table = anchors();
		for (const name of anchorsOf(piece)) {
			options[name] = table[name] ? name + '  (' + table[name].part + ')' : name;
		}
		if (!Object.keys(options).length) options[state().anchor || ''] = state().anchor || '-';
		return options;
	}

	function animationOptions() {
		return { idle: 'Idle', walk: 'Walk', sprint: 'Sprint' };
	}

	/*
	 * The fittings are two sets of controls: which mask the brush paints, and what each fitting
	 * holds in the preview. A piece has any number of fittings and a form has a fixed set of
	 * fields, so the preview gets three slots, one per masked fitting in the part's order, hidden
	 * past the last one; three is one more than any shipped part has. Each slot's label is the
	 * fitting's own name, set on the built label element by syncForm, because a form label is
	 * a string fixed at build time and the fitting behind a slot is not.
	 */
	const FITTING_SLOTS = 3;

	function fittingEditOptions() {
		const options = {};
		for (const fitting of maskedFittings()) options[fitting.name] = fitting.label;
		if (!Object.keys(options).length) options[''] = '- no masked fittings -';
		return options;
	}

	function fittingSlot(index) {
		return {
			label: 'Fitting ' + (index + 1), type: 'select',
			options: function () {
				const fitting = maskedFittings()[index];
				const options = { '': fitting ? '(empty)' : '-' };
				for (const option of (fitting ? fitting.options : [])) options[option.value] = option.label;
				return options;
			},
			condition: function (result) {
				return !!result.preview && maskedFittings().length > index;
			},
		};
	}

	function panelForm() {
		const materialOptions = MATERIALS.reduce(function (all, m) { all[m] = m; return all; }, {});
		return {
			piece: { label: 'Piece', type: 'select', options: pieceOptions },
			anchor: { label: 'Anchor', type: 'select', options: anchorOptions },
			actions: {
				type: 'buttons', buttons: ['New...', 'Save', 'Rebuild'],
				click: function (index) {
					if (index === 0) newPiece();
					else if (index === 1) savePiece();
					else reopen(state().anchor);
				},
			},
			_1: '_',
			edit: {
				label: 'Editing', type: 'inline_select',
				options: { master: 'Master (grey)', static: 'Static (colour)', fitting: 'Mask (grey)' },
			},
			fitting: {
				label: 'Fitting', type: 'select', options: fittingEditOptions,
				condition: function (result) { return result.edit === 'fitting'; },
				description: 'Whose mask the brush paints: the region of the part that takes the ' +
					'second material, shaded by its own values. Created blank on first use.',
			},
			preview: { label: 'Material preview', type: 'checkbox', style: 'toggle_switch', value: false },
			material: {
				label: 'Material', type: 'select', options: materialOptions, value: 'iron',
				condition: function (result) { return !!result.preview; },
			},
			fitting_0: fittingSlot(0),
			fitting_1: fittingSlot(1),
			fitting_2: fittingSlot(2),
			_2: '_',
			animation: { label: 'Pose', type: 'inline_select', options: animationOptions() },
			phase: {
				label: 'Phase', type: 'range', min: 0, max: 1, step: 0.01, value: 0,
				condition: function (result) { return result.animation !== 'idle'; },
			},
			_3: '_',
			show_player: { label: 'Show player', type: 'checkbox', style: 'toggle_switch', value: true },
			show_armor: { label: 'Show armor', type: 'checkbox', style: 'toggle_switch', value: true },
			part_only: { label: 'Outliner: part only', type: 'checkbox', style: 'toggle_switch', value: true },
			_4: '_',
			// No `list` here on purpose: Blockbench 5.1's own datalist never reaches the page and
			// leaves the text "undefined" beside the field. fillItemLists attaches a working one.
			recipe_focus: {
				label: 'Recipe centre', type: 'text', value: '', placeholder: 'minecraft:feather',
				description: 'The item in the middle of the template recipe. Written on Save.',
			},
			recipe_ring: {
				label: 'Recipe ring', type: 'text', value: 'minecraft:paper',
				description: 'The four items around it.',
			},
		};
	}

	/* Push the project's state into the form. The form fires change on that; syncingForm mutes it. */
	function syncForm() {
		if (!panel || !panel.form) return;
		const piece = currentPiece();
		const s = state();
		const masked = maskedFittings();
		syncingForm = true;
		try {
			const values = {
				piece: piece ? piece.key : '',
				anchor: s.anchor,
				edit: s.edit,
				fitting: s.fitting,
				preview: s.preview,
				material: s.material,
				animation: s.animation,
				phase: s.phase,
				show_player: s.show_player,
				show_armor: s.show_armor,
				part_only: s.part_only,
				recipe_focus: s.recipe_focus,
				recipe_ring: s.recipe_ring,
			};
			for (let i = 0; i < FITTING_SLOTS; i++) {
				const fitting = masked[i];
				values['fitting_' + i] = fitting ? (s.fittings[fitting.name] || '') : '';
				const element = panel.form.form_data['fitting_' + i];
				const label = element && element.bar && element.bar.querySelector('label');
				if (label) label.textContent = fitting ? fitting.label : 'Fitting ' + (i + 1);
			}
			// Select inputs resolve their option lists lazily, but the displayed label of the
			// current value is looked up when it is set, so the lists must be current first.
			panel.form.setValues(values);
		} finally {
			syncingForm = false;
		}
	}

	function onFormChange(event) {
		if (syncingForm || !isWorkspace()) return;
		const result = event.result;
		const changed = event.changed_keys || [];
		const s = state();
		const piece = currentPiece();

		if (changed.includes('piece') && result.piece && result.piece !== piece.key) {
			const target = allPieces().find(function (p) { return p.key === result.piece; });
			if (target) openPiece(target);
			else syncForm();
			return;
		}
		if (changed.includes('anchor') && result.anchor && result.anchor !== s.anchor) {
			reopen(result.anchor);
			return;
		}

		s.edit = result.edit;
		s.preview = !!result.preview;
		s.material = result.material;
		s.animation = result.animation;
		s.phase = result.phase;
		s.show_player = !!result.show_player;
		s.show_armor = !!result.show_armor;
		s.part_only = !!result.part_only;
		s.recipe_focus = result.recipe_focus || '';
		s.recipe_ring = result.recipe_ring || '';
		s.fitting = result.fitting || '';
		const masked = maskedFittings();
		for (let i = 0; i < masked.length && i < FITTING_SLOTS; i++) {
			s.fittings[masked[i].name] = result['fitting_' + i] || '';
		}

		if (changed.includes('edit') || changed.includes('fitting')) {
			if (s.edit === 'static' && !tex('part_static')) createStaticLayer();
			if (s.edit === 'fitting') {
				if (!s.fitting && masked.length) s.fitting = masked[0].name;
				if (s.fitting && !tex(maskId(s.fitting))) createMaskLayer(s.fitting);
			}
			applyTextures();
			applyPalette();
			// The chosen sheet may be missing, in which case editTarget fell back to the master.
			if (s.edit !== result.edit) {
				Blockbench.showQuickMessage(piece.name + ' has no '
					+ (result.edit === 'static' ? 'static layer' : 'masked fitting'), 2500);
			}
			syncForm();
		}
		const fittingChanged = changed.some(function (key) { return key.indexOf('fitting_') === 0; });
		if (changed.includes('preview') || changed.includes('material') || fittingChanged) {
			if (s.preview && (changed.includes('material') || fittingChanged)) {
				// A new material or fitting means a new ramp; rebuild the preview through it.
				refreshPreviewMaterial();
			}
			applyTextures();
			if (s.preview !== !!result.preview) syncForm();
		}
		if (changed.includes('animation') || changed.includes('phase')) applyPose();
		if (changed.includes('show_player') || changed.includes('show_armor')) applyVisibility();
		if (changed.includes('part_only')) Outliner.updateNodeDisplayRules();
	}

	function refreshPreviewMaterial() {
		const s = state();
		try {
			fetchRamps(s.material, staticColoursIn(tex('part_static')));
			fetchFittingRamps();
		} catch (err) {
			console.error(err);
			Blockbench.showQuickMessage('No ramp for ' + s.material + ' - run tools/vanilla_assets.py', 3000);
			s.preview = false;
			return;
		}
		refreshPreview(true);
	}

	// ---- workspace on/off ---------------------------------------------------------------------

	/*
	 * Panels a part author never needs while a piece is open. Their conditions are wrapped, not
	 * their positions changed, so the author's layout for every other project is exactly as it was.
	 */
	const HIDDEN_PANELS = ['textures', 'layers', 'animations', 'keyframe', 'timeline',
		'variable_placeholders', 'bone', 'collections', 'animation_controllers'];

	function wrapCondition(owner) {
		const original = owner.condition;
		owner.condition = function () {
			if (isWorkspace()) return false;
			return Condition(original);
		};
		undo_hooks.push(function () { owner.condition = original; });
	}

	function enterWorkspace() {
		if (!isWorkspace()) return;
		if (typeof updateInterfacePanels === 'function') updateInterfacePanels();
		if (Modes.vue) Modes.vue.$forceUpdate();
		Outliner.updateNodeDisplayRules();
		fillItemLists();
		syncForm();
		applyTextures();
		applyPalette();
		applyVisibility();
		applyPose();
	}

	function leaveWorkspace() {
		// Called with the piece still selected, so applyPalette would keep the greys; restore
		// explicitly. Panels and the outliner re-evaluate on the next project's activation.
		restorePalette();
	}

	// ---- registration -------------------------------------------------------------------------

	Plugin.register(ID, {
		title: 'Armor Pieces',
		author: 'mattjes',
		icon: 'shield',
		description: 'Browse, edit and save Armor Pieces on an animated vanilla player wearing real armor.',
		version: '0.2.0',
		variant: 'desktop',
		tags: ['Minecraft: Java Edition'],

		onload() {
			registered.push(new Setting(ID + '_root', {
				name: 'Armor Pieces repository',
				description: 'Path to the repo root (the folder holding tools/ and src/).',
				category: 'edit',
				type: 'text',
				value: '',
			}));
			registered.push(new Setting(ID + '_python', {
				name: 'Armor Pieces Python',
				description: 'Python executable used to run the repo tools.',
				category: 'edit',
				type: 'text',
				value: 'python',
			}));
			registered.push(new Setting(ID + '_material', {
				name: 'Armor Pieces rig material',
				description: 'Which armor set the rig figure wears.',
				category: 'edit',
				type: 'text',
				value: 'iron',
			}));
			registered.push(new Setting(ID + '_greyscale', {
				name: 'Armor Pieces: keep masters greyscale',
				description: 'Fold any colour painted on a part master down to its value, since ' +
					'the game reads that value as a position on the material ramp.',
				category: 'edit',
				type: 'toggle',
				value: true,
			}));

			/*
			 * The workspace format: `free` (the only animation-capable format with several textures
			 * at their own UV sizes, which a rig needs) with nothing added. What makes it different
			 * is that every trim-down below asks whether the current format is this one.
			 */
			const format = Formats[ID] || new ModelFormat(ID, {
				name: 'Armor Piece',
				description: 'A decoration part on its reference rig, opened by the Armor Pieces plugin.',
				icon: 'shield',
				category: 'minecraft',
				show_on_start_screen: false,
				show_in_new_list: false,
				can_convert_to: false,
				rotate_cubes: true,
				bone_rig: true,
				centered_grid: true,
				optional_box_uv: true,
				per_texture_uv_size: true,
				per_texture_wrap_mode: true,
				uv_rotation: true,
				animation_mode: true,
				per_animator_rotation_interpolation: true,
				model_identifier: false,
			});
			// Bound here rather than in the constructor so a reloaded plugin rebinds them on the
			// format object that any already-open piece still points at. The format itself is never
			// deleted on unload for the same reason: a project cannot outlive its format.
			format.onActivation = enterWorkspace;
			format.onDeactivation = leaveWorkspace;

			const open = new Action(ID + '_open', {
				name: 'Open Armor Piece...',
				description: 'Browse the packs and open a piece on the player rig.',
				icon: 'shield',
				click: function () { pickPiece('Open Armor Piece', function (piece) { openPiece(piece); }); },
			});
			const save = new Action(ID + '_save', {
				name: 'Save Armor Piece to Pack',
				description: 'Write the model and texture back where they came from.',
				icon: 'save',
				click: savePiece,
			});
			const create = new Action(ID + '_new', {
				name: 'New Armor Piece...',
				description: 'Create the data, model and texture files for a new piece.',
				icon: 'add_box',
				click: newPiece,
			});

			// One submenu, not three loose entries in Tools. `children` is also what makes cleanup
			// tractable: there is exactly one menu node to remove on unload, and forgetting it is
			// how a reloaded plugin ends up listed twice.
			const menu = new Action(ID + '_menu', {
				name: 'Armor Pieces',
				description: 'Browse, edit and preview Armor Pieces.',
				icon: 'shield',
				children: [open, create, save],
			});
			registered.push(open, save, create, menu);
			MenuBar.addAction(menu, 'tools');

			panel = new Panel(ID + '_panel', {
				name: 'Armor Piece',
				icon: 'shield',
				condition: function () { return isWorkspace(); },
				default_position: {
					slot: 'right_bar',
					float_position: [0, 0],
					float_size: [320, 480],
					height: 460,
					sidebar_index: 0,
				},
				form: panelForm(),
			});
			registered.push(panel);
			panel.form.on('change', onFormChange);

			for (const id of HIDDEN_PANELS) {
				if (Interface.Panels[id]) wrapCondition(Interface.Panels[id]);
			}
			// Animate mode is where the rig's cycles would be edited, and they are baked from the
			// game's own arithmetic - the pose controls above are the whole of what a part needs.
			if (Modes.options.animate) wrapCondition(Modes.options.animate);

			/*
			 * Strokes over the preview go to the layer being edited. This is the one function every
			 * paint tool asks before it touches a texture, so one answer covers the brush, fill,
			 * shapes and gradients alike.
			 */
			const originalTextureToEdit = Painter.getTextureToEdit;
			Painter.getTextureToEdit = function (input) {
				if (input && input.id === 'preview' && isWorkspace()) {
					return editTarget() || input;
				}
				return originalTextureToEdit.call(this, input);
			};
			undo_hooks.push(function () { Painter.getTextureToEdit = originalTextureToEdit; });

			// The UV editor follows the selected cubes' texture, which is the preview while one is
			// shown. The author paints the greyscale, so that is what the UV editor should show.
			if (UVEditor.vue && typeof UVEditor.vue.updateTexture === 'function') {
				const originalUpdateTexture = UVEditor.vue.updateTexture;
				UVEditor.vue.updateTexture = function () {
					originalUpdateTexture.call(this);
					if (isWorkspace() && this.texture && this.texture.id === 'preview') {
						const target = editTarget();
						if (target) {
							this.texture = target;
							this.layer = target.selected_layer || null;
							UVEditor.updateSelectionOutline();
							this.updateTextureCanvas();
						}
					}
				};
				undo_hooks.push(function () { UVEditor.vue.updateTexture = originalUpdateTexture; });
			}

			/*
			 * Box UV layout runs inside finishEdit, before the after-snapshot is taken, so that the
			 * offsets it sets and the paint it moves belong to the same undo step as the edit.
			 */
			const originalFinishEdit = UndoSystem.prototype.finishEdit;
			UndoSystem.prototype.finishEdit = function (message, aspects) {
				if (this.current_save) {
					onFinishEditWithLayout(this.current_save, aspects || this.current_save.aspects);
				}
				return originalFinishEdit.call(this, message, aspects);
			};
			undo_hooks.push(function () { UndoSystem.prototype.finishEdit = originalFinishEdit; });

			Outliner.node_display_rules.push(outlinerRule);
			undo_hooks.push(function () { Outliner.node_display_rules.remove(outlinerRule); });

			Cube.preview_controller.on('update_painting_grid', onPaintingGrid);
			undo_hooks.push(function () {
				Cube.preview_controller.removeListener('update_painting_grid', onPaintingGrid);
			});

			Blockbench.on('finish_edit', onFinishEdit);
			Blockbench.on('edit_texture', onEditTexture);
			Blockbench.on('select_mode', onSelectMode);
			Blockbench.on('update_view', onUpdateView);
			Blockbench.on('undo', onUndoRedo);
			Blockbench.on('redo', onUndoRedo);
			Blockbench.on('before_closing', restorePalette);

			// A previous session may have ended with the greys still in. Put the author's palette
			// back before anything else can persist the greys again.
			if (ColorPanel.palette && stashedPalette() && isGreyPalette(ColorPanel.palette)) {
				restorePalette();
			}

			// A small scripting surface, so the piece list and opener can be driven from outside
			// (the MCP bridge, a test) without going through the dialogs.
			window[ID + '_api'] = {
				pieces: allPieces,
				open: function (key, anchor) {
					const piece = allPieces().find(function (p) { return p.key === key; });
					if (!piece) throw new Error('no piece ' + key);
					return openPiece(piece, anchor);
				},
				state: state,
				fittings: function () { return fittingsOf(currentPiece()); },
				isWorkspace: isWorkspace,
				save: savePiece,
				readRecipe: readRecipe,
				refresh: enterWorkspace,
			};
		},

		onunload() {
			Blockbench.removeListener('finish_edit', onFinishEdit);
			Blockbench.removeListener('edit_texture', onEditTexture);
			Blockbench.removeListener('select_mode', onSelectMode);
			Blockbench.removeListener('update_view', onUpdateView);
			Blockbench.removeListener('undo', onUndoRedo);
			Blockbench.removeListener('redo', onUndoRedo);
			Blockbench.removeListener('before_closing', restorePalette);
			leaveWorkspace();
			undo_hooks.reverse().forEach(function (fn) { fn(); });
			undo_hooks = [];
			// Deleting a BarItem does not take its menu entry with it, so the menu node has to go
			// explicitly - otherwise every reload leaves another copy behind in Tools.
			MenuBar.removeAction('tools.' + ID + '_menu');
			registered.forEach(function (item) { item.delete(); });
			registered = [];
			panel = null;
			anchorCache = null;
			delete window[ID + '_api'];
			if (typeof updateInterfacePanels === 'function') updateInterfacePanels();
			Outliner.updateNodeDisplayRules();
		},
	});
})();
