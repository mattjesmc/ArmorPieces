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
 *     and phase, and the reference toggles. The datapack half - name, anchors, fittings and
 *     effects - is a dialog behind the panel's Part... button, and a summary line on the panel.
 *     What the effect fields are comes from effect_schema.py, which reads them out of the Java.
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

	// ---- the datapack half ----------------------------------------------------------------------

	/*
	 * The part's data JSON is held on the project as the object it parsed to, edited by the Part
	 * dialog and written back whole on Save. Holding the whole object is what keeps a field the
	 * editor has no control for - an effect, a key another mod reads - exactly as it was: the file
	 * is never rebuilt from the controls, only changed where a control changed it. And nothing is
	 * written unless something changed, so a file the author formatted by hand is not reformatted
	 * for having been opened.
	 */
	function partData() {
		return Project && Project[ID + '_data'] || null;
	}

	function markDirty() {
		if (Project) Project[ID + '_dirty'] = true;
	}

	/*
	 * The anchors the piece lists, first one first: the open project's own copy while the piece is
	 * the one open - unsaved edits included - else the file's. Empty when there is no data.
	 */
	function anchorsOf(piece) {
		if (!piece) return [];
		const data = piece === currentPiece() && partData() ? partData() : readJsonOr(piece.data, null);
		if (!data) return [];
		return (data.anchors || []).filter(function (a) { return typeof a === 'string'; });
	}

	/*
	 * The part's name as a player reads it. `description` comes in three shapes: a translation
	 * key, which every shipped part and every part made here uses, whose text lives in the pack's
	 * language file; a bare string; and any other text component, which the editor shows but does
	 * not touch. Returns the text, whether it can be edited, and the key the text lives under.
	 */
	function displayName(piece, data) {
		const description = data && data.description;
		if (typeof description === 'string') return { text: description, editable: true, key: null };
		if (description && typeof description.translate === 'string') {
			const entries = readJsonOr(langFile(piece.pack, piece.namespace), {});
			const text = entries[description.translate];
			return {
				text: typeof text === 'string' ? text : titleCase(piece.name),
				editable: true,
				key: description.translate,
			};
		}
		return { text: description ? JSON.stringify(description) : '', editable: false, key: null };
	}

	/*
	 * The fittings the piece lists, resolved by preview_material.py: the mask name, the type,
	 * whether it is a mask over the texture, a display name, and the values it can take, each with
	 * the colour it asks the baker for. Resolving means reading fitting files, tags and language
	 * files across the pack and the mod, which is Python's job, not this file's. The open piece's
	 * list is the project's own copy, unsaved edits included, handed over as a scratch file with
	 * the pack named beside it. Cached on the project until the list changes.
	 */
	function fittingsOf(piece) {
		if (!piece || !Project) return [];
		if (!Project[ID + '_fittings']) {
			let args = null;
			if (piece === currentPiece() && partData()) {
				const scratch = path.join(tempDir(), 'fittings.json');
				fs.writeFileSync(scratch, JSON.stringify(partData()), 'utf8');
				args = ['--fittings', scratch, '--pack', piece.pack];
			} else if (fs.existsSync(piece.data)) {
				args = ['--fittings', piece.data];
			}
			if (!args) return [];
			try {
				Project[ID + '_fittings'] = JSON.parse(tool('preview_material.py', args));
			} catch (err) {
				console.error(err);
				Project[ID + '_fittings'] = [];
			}
		}
		return Project[ID + '_fittings'];
	}

	/* Every fitting a part in the piece's pack could declare: the pack's definitions and the mod's. */
	function availableFittings(piece) {
		try {
			return JSON.parse(tool('preview_material.py', ['--list-fittings', piece.pack]));
		} catch (err) {
			console.error(err);
			return [];
		}
	}

	/* The fittings that are a region of the texture - the ones with a sheet to paint and preview. */
	function maskedFittings() {
		return fittingsOf(currentPiece()).filter(function (f) { return f.masked; });
	}

	/* The fittings the preview can fill: the masked ones, and a bone fitting as a flat fill. */
	function previewFittings() {
		return fittingsOf(currentPiece()).filter(function (f) { return f.masked || f.bone; });
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
		// Only the fields the two choices decide are replaced. Anything else in an existing file - a
		// group, a notification flag - is somebody's authoring and stays.
		const file = recipeFileFor(piece);
		const recipe = Object.assign(readJsonOr(file, {}), {
			type: 'minecraft:crafting_shaped',
			pattern: RING_PATTERN,
			key: { '#': ring, F: focus },
			result: {
				id: 'armorpieces:' + socket + '_template',
				components: { 'armorpieces:decoration': piece.key },
			},
		});
		if (!recipe.category) recipe.category = 'equipment';
		writeJson(file, recipe);
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

	/*
	 * `carry` is what a rebuild brings across from the project it replaces: the datapack half as
	 * edited but not yet saved, since a rebuild reloads the rig, not the author's decisions.
	 */
	function openPiece(piece, anchor, carry) {
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
		Project[ID + '_data'] = carry && carry.data ? carry.data : readJsonOr(piece.data, null);
		Project[ID + '_dirty'] = !!(carry && carry.dirty);
		// A display name changed in the Part dialog, held until Save writes the language line.
		Project[ID + '_name'] = carry && carry.name ? carry.name : null;
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
		const carry = { data: partData(), dirty: old[ID + '_dirty'], name: old[ID + '_name'] };
		if (!openPiece(piece, anchor, carry) || !old || old === Project) return;
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

		// The datapack half, only when the Part dialog changed it: the whole object as edited, so
		// whatever the dialog has no control for is written back as it was read.
		const notes = [];
		if (Project[ID + '_dirty'] && partData()) {
			writeJson(piece.data, partData());
			Project[ID + '_dirty'] = false;
			notes.push('data');
		}
		if (Project[ID + '_name']) {
			const shown = displayName(piece, partData());
			if (shown.key) writeLang(piece.pack, piece.namespace, shown.key, Project[ID + '_name']);
			Project[ID + '_name'] = null;
			notes.push('name');
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

		notes.push(writeRecipe(piece));
		// The summary line reads the name from the file it was just written to.
		syncForm();
		Blockbench.showQuickMessage('Saved ' + piece.name + ' to ' + piece.namespace + ' - ' + notes.join(', '), 3000);
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

	function readJsonOr(file, fallback) {
		try {
			if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, 'utf8'));
		} catch (err) {
			console.error('[armorpieces] could not read ' + file, err);
		}
		return fallback;
	}

	function titleCase(name) {
		return name.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
	}

	function langFile(packDir, namespace) {
		return path.join(packDir, 'assets', namespace, 'lang', 'en_us.json');
	}

	/* Set one line in a pack's English language file, creating the file when there is none. */
	function writeLang(packDir, namespace, key, value) {
		const file = langFile(packDir, namespace);
		const entries = readJsonOr(file, {});
		if (entries[key] === value) return;
		entries[key] = value;
		writeJson(file, entries);
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

				// The name a player reads, so the piece is not "decoration.ns.name" in a tooltip.
				const key = 'decoration.' + namespace + '.' + name;
				if (!readJsonOr(langFile(packDir, namespace), {})[key]) {
					writeLang(packDir, namespace, key, titleCase(name));
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

	function cubesUnder(group) {
		const out = [];
		for (const child of group.children) {
			if (child instanceof Cube && !child.locked) out.push(child);
			else if (child instanceof Group && !child.locked) out.push(...cubesUnder(child));
		}
		return out;
	}

	/*
	 * A bone fitting is drawn by the game in place of the bone's own texture: the banner's pattern
	 * layers over every cube of the named bone. The preview stands in for that with the flat base
	 * colour of the banner chosen, over the bone's whole nets - enough to see which bone the fitting
	 * takes and how the flag reads on the body, without a second banner renderer here. Returns one
	 * fill per filled bone fitting: the colour, and the face rects to paint it over.
	 */
	function previewBones() {
		const s = state();
		const out = [];
		for (const fitting of previewFittings()) {
			if (!fitting.bone) continue;
			const value = s.fittings[fitting.name];
			const colour = value ? fittingColour(fitting, value) : '';
			if (colour.indexOf('solid:') !== 0) continue;
			const rects = [];
			for (const group of Group.all) {
				if (group.locked || group.name !== fitting.bone) continue;
				for (const cube of cubesUnder(group)) {
					if (!cube.box_uv) continue;
					const faces = faceRects(net(cube), cube.uv_offset);
					for (const face of Object.keys(faces)) rects.push(faces[face]);
				}
			}
			const rgb = parseInt(colour.slice(7), 16);
			out.push({ colour: [(rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255], rects: rects });
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
	function compositeInto(canvas, master, statics, material, masks, bones) {
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
		// A bone fitting's fill covers the bone's whole faces, opaque, as the game's banner does.
		for (const bone of bones || []) {
			for (const rect of bone.rects) {
				const x0 = Math.max(0, rect[0]), y0 = Math.max(0, rect[1]);
				const x1 = Math.min(w, rect[0] + rect[2]), y1 = Math.min(h, rect[1] + rect[3]);
				for (let y = y0; y < y1; y++) {
					for (let x = x0; x < x1; x++) {
						const i = (y * w + x) * 4;
						dst[i] = bone.colour[0];
						dst[i + 1] = bone.colour[1];
						dst[i + 2] = bone.colour[2];
						dst[i + 3] = 255;
					}
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
		compositeInto(scratch, master, statics, s.material, previewMasks(), previewBones());
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
		const bones = previewBones();
		let missing = compositeInto(preview.canvas, master, statics, s.material, previewMasks(), bones);
		if (missing.length && settle) {
			try {
				fetchRamps(s.material, missing);
				compositeInto(preview.canvas, master, statics, s.material, previewMasks(), bones);
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

	// ---- the Part dialog ----------------------------------------------------------------------

	/*
	 * Name, anchors and fittings: what the datapack half says that the rig cannot show, behind one
	 * button so the panel stays the one place. The dialog edits the project's copy of the data and
	 * the panel reflects it at once - the Anchor list, the Fitting list, the preview rows, the
	 * summary line - and Save writes it. A fitting is picked from the definitions the resolver
	 * finds in the pack and the mod, with the label and kind it reports, so a fitting that does not
	 * exist cannot be named here; defining one is the next dialog's job.
	 */
	function fittingKind(fitting) {
		if (!fitting.type) return 'missing';
		if (fitting.masked) return 'mask';
		if (fitting.type === 'armorpieces:banner') return 'bone';
		return fitting.type;
	}

	/* A resolved fitting as the dialog's list holds it; type and options are for the effect gates. */
	function fittingRow(fitting) {
		return {
			id: fitting.id, label: fitting.label, kind: fittingKind(fitting),
			type: fitting.type, options: fitting.options || [],
		};
	}

	// ---- effects ------------------------------------------------------------------------------

	/*
	 * An effect is a row of fields, and the fields come from the Java that defines the effect
	 * type: effect_schema.py parses each built-in record's codec and javadoc into names, kinds,
	 * ranges, defaults and descriptions, so a default tuned in Java is the default here. The one
	 * built-in that is not a row is if_fitting, which gates another effect on a fitting; the dialog
	 * shows that as a switch on the row it wraps, "only while <fitting> holds <value>".
	 */
	const GATE_TYPE = 'armorpieces:if_fitting';
	let schemaCache = null;
	let idsCache = null;

	function effectSchema() {
		if (!schemaCache) {
			try {
				schemaCache = JSON.parse(tool('effect_schema.py'));
			} catch (err) {
				console.error(err);
				schemaCache = {};
			}
		}
		return schemaCache;
	}

	/* Ids an effect's fields can name, out of the game jar: attributes, mob effects, damage tags. */
	function registryIds() {
		if (!idsCache) {
			try {
				const listed = JSON.parse(tool('vanilla_assets.py', ['--list-ids']));
				const tags = {};
				for (const tag of listed.damage_type_tags || []) tags[tag] = tag;
				idsCache = { attribute: listed.attribute || {}, mob_effect: listed.mob_effect || {}, damage_type: tags };
			} catch (err) {
				console.error(err);
				idsCache = { attribute: {}, mob_effect: {}, damage_type: {} };
			}
		}
		return idsCache;
	}

	function blankValue(field) {
		if (field.default !== undefined) return field.default;
		if (field.kind === 'bool') return false;
		if (field.kind === 'enum') return field.options[0];
		return '';
	}

	/*
	 * An effect from the data file as a dialog row: its type, its fields with the schema's defaults
	 * filled in for the ones it omits, any key the schema does not know kept aside, and an
	 * if_fitting wrapper folded into the gate. Whatever this cannot represent - a type from another
	 * mod, a gate over a tag or a list of materials, a gate inside a gate - is kept whole and shown
	 * read-only, so it round-trips through the dialog untouched.
	 */
	function effectRow(effect) {
		const schema = effectSchema();
		let inner = effect;
		let gate = null;
		if (effect && effect.type === GATE_TYPE && effect.if && effect.then
			&& typeof effect.if.fitting === 'string' && effect.then.type !== GATE_TYPE) {
			const keys = Object.keys(effect.if);
			if (!keys.every(function (k) { return k === 'fitting' || k === 'material' || k === 'dye'; })) {
				return { raw: effect };
			}
			const value = effect.if.material !== undefined ? effect.if.material : effect.if.dye;
			if (value !== undefined && typeof value !== 'string') return { raw: effect };
			gate = { fitting: effect.if.fitting, value: value || '' };
			inner = effect.then;
		}
		const def = inner && schema[inner.type];
		if (!def || inner.type === GATE_TYPE) return { raw: effect };
		const fields = {};
		const extra = {};
		for (const key of Object.keys(inner)) {
			if (key === 'type') continue;
			if (def.fields.some(function (f) { return f.name === key; })) fields[key] = inner[key];
			else extra[key] = inner[key];
		}
		for (const field of def.fields) {
			if (!(field.name in fields)) fields[field.name] = blankValue(field);
		}
		return {
			raw: null, type: inner.type, fields: fields, extra: extra, present: Object.keys(inner),
			gated: !!gate, gate: gate || { fitting: '', value: '' },
		};
	}

	function blankEffect(type) {
		const fields = {};
		for (const field of effectSchema()[type].fields) fields[field.name] = blankValue(field);
		return { raw: null, type: type, fields: fields, extra: {}, present: [], gated: false, gate: { fitting: '', value: '' } };
	}

	/*
	 * The row back as the file's effect. A field is written when it is required, when it is not
	 * at its default, or when the file already spelled it out - so a file that named a default
	 * keeps naming it. `fittings` decides whether a gate's value is a material or a dye.
	 */
	function effectFromRow(row, fittings) {
		if (row.raw) return row.raw;
		const out = { type: row.type };
		for (const field of effectSchema()[row.type].fields) {
			let value = row.fields[field.name];
			if (field.kind === 'int' || field.kind === 'number') {
				value = Number(value);
				if (isNaN(value)) value = field.default !== undefined ? field.default : 0;
				if (field.kind === 'int') value = Math.round(value);
			} else if (field.kind === 'bool') {
				value = !!value;
			} else if (typeof value === 'string') {
				value = value.trim();
			}
			const isDefault = field.default !== undefined && value === field.default;
			if (field.required || !isDefault || row.present.includes(field.name)) out[field.name] = value;
		}
		Object.assign(out, row.extra);
		if (!row.gated || !row.gate.fitting) return out;
		const condition = { fitting: row.gate.fitting };
		if (row.gate.value) {
			const fitting = fittings.find(function (f) { return f.id === row.gate.fitting; });
			condition[fitting && fitting.type === 'armorpieces:dye' ? 'dye' : 'material'] = row.gate.value;
		}
		return { type: GATE_TYPE, if: condition, then: out };
	}

	/* The first thing wrong with a row the game would refuse to load, or '' when it is fine. */
	function effectProblem(row) {
		if (row.raw) return '';
		const def = effectSchema()[row.type];
		for (const field of def.fields) {
			const value = row.fields[field.name];
			if (field.required && (field.kind === 'id' || field.kind === 'tag') && !String(value || '').trim()) {
				return def.label + ' needs ' + field.name;
			}
		}
		return '';
	}

	/* JSON with keys in a fixed order, so two spellings of the same effect compare equal. */
	function canonical(value) {
		if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
		if (value && typeof value === 'object') {
			return '{' + Object.keys(value).sort().map(function (k) {
				return JSON.stringify(k) + ':' + canonical(value[k]);
			}).join(',') + '}';
		}
		return JSON.stringify(value);
	}

	function effectLabel(effect) {
		const schema = effectSchema();
		const inner = effect && effect.type === GATE_TYPE && effect.then ? effect.then : effect;
		const def = inner && schema[inner.type];
		return (def ? def.label : String(inner && inner.type)) + (inner !== effect ? ' (gated)' : '');
	}

	function partSummary(piece) {
		const data = partData();
		if (!piece || !data) return 'No datapack half.';
		const fittings = fittingsOf(piece).map(function (f) { return f.label; });
		const effects = (data.effects || []).map(effectLabel);
		const name = Project[ID + '_name'] || displayName(piece, data).text;
		return name + '  ·  ' + anchorsOf(piece).join(', ')
			+ '  ·  ' + (fittings.length ? 'fittings: ' + fittings.join(', ') : 'no fittings')
			+ (effects.length ? '  ·  effects: ' + effects.join(', ') : '');
	}

	const PART_DIALOG_TEMPLATE = [
		'<div class="armorpieces_part">',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Name</label>',
		'		<input type="text" class="dark_bordered" v-model="name" :disabled="!editable"',
		'			:title="editable ? \'\' : \'A text component the editor cannot edit\'">',
		'	</div>',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Anchors</label>',
		'		<div class="ap_column">',
		'			<div class="ap_anchor_group" v-for="g in groups" :key="g.armor">',
		'				<span class="ap_dim">{{ g.label }}</span>',
		'				<label v-for="a in g.anchors" :key="a.id" :title="\'on the \' + a.part">',
		'					<input type="checkbox" v-model="a.checked"> {{ a.id }}',
		'				</label>',
		'			</div>',
		'		</div>',
		'	</div>',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Fittings</label>',
		'		<div class="ap_column">',
		'			<ul>',
		'				<li v-for="(f, i) in fittings" :key="f.id">',
		'					<span>{{ f.label }}</span>',
		'					<span class="ap_dim">{{ f.id }} · {{ f.kind }}</span>',
		'					<i class="material-icons" title="Earlier" @click="move(i, -1)">arrow_upward</i>',
		'					<i class="material-icons" title="Later" @click="move(i, 1)">arrow_downward</i>',
		'					<i class="material-icons" title="Remove" @click="remove(i)">clear</i>',
		'				</li>',
		'			</ul>',
		'			<div class="ap_add">',
		'				<select class="dark_bordered" :value="\'\'" @change="add($event)">',
		'					<option value="">Add a fitting...</option>',
		'					<option v-for="f in available" :key="f.id" :value="f.id" :disabled="has(f.id)">',
		'						{{ f.label }}  ({{ f.id }}, {{ f.kind }})',
		'					</option>',
		'				</select>',
		'				<button type="button" @click="create" title="Define a fitting this pack does not have yet">New...</button>',
		'			</div>',
		'			<p class="ap_dim">The smithing table offers an item to the fittings in this order; ',
		'			the first to accept it wins. A mask is painted in Mask mode; a bone fitting draws on ',
		'			the bone of that name.</p>',
		'		</div>',
		'	</div>',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Effects</label>',
		'		<div class="ap_column">',
		'			<div class="ap_effect" v-for="(e, i) in effects" :key="i">',
		'				<div class="ap_effect_head">',
		'					<span v-if="e.raw">{{ e.raw.type }} <span class="ap_dim">- not editable here, kept as it is</span></span>',
		'					<span v-else :title="schema[e.type].summary">{{ schema[e.type].label }}</span>',
		'					<i class="material-icons" title="Remove" @click="removeEffect(i)">clear</i>',
		'				</div>',
		'				<pre v-if="e.raw" class="ap_dim">{{ JSON.stringify(e.raw, null, 1) }}</pre>',
		'				<template v-else>',
		'					<div class="ap_field" v-for="f in schema[e.type].fields" :key="f.name" :title="f.description">',
		'						<label>{{ f.name }}</label>',
		'						<input v-if="f.kind === \'bool\'" type="checkbox" v-model="e.fields[f.name]">',
		'						<select v-else-if="f.kind === \'enum\'" class="dark_bordered" v-model="e.fields[f.name]">',
		'							<option v-for="o in f.options" :key="o" :value="o">{{ o }}</option>',
		'						</select>',
		'						<input v-else-if="f.kind === \'int\' || f.kind === \'number\'" type="number" class="dark_bordered"',
		'							:min="f.min" :max="f.max" :step="f.kind === \'int\' ? 1 : \'any\'" v-model.number="e.fields[f.name]">',
		'						<input v-else type="text" class="dark_bordered" v-model="e.fields[f.name]" :list="listFor(f)"',
		'							:placeholder="f.required ? \'required\' : \'\'">',
		'					</div>',
		'					<div class="ap_field ap_gate">',
		'						<label><input type="checkbox" v-model="e.gated" @change="gateOn(e)"> only while</label>',
		'						<select class="dark_bordered" v-model="e.gate.fitting" :disabled="!e.gated">',
		'							<option v-for="f in fittings" :key="f.id" :value="f.id">{{ f.label }}</option>',
		'						</select>',
		'						<span>holds</span>',
		'						<select class="dark_bordered" v-model="e.gate.value" :disabled="!e.gated">',
		'							<option value="">anything</option>',
		'							<option v-for="o in gateOptions(e)" :key="o.id" :value="o.id">{{ o.label }}</option>',
		'						</select>',
		'					</div>',
		'				</template>',
		'			</div>',
		'			<select class="dark_bordered" :value="\'\'" @change="addEffect($event)">',
		'				<option value="">Add an effect...</option>',
		'				<option v-for="t in types" :key="t.id" :value="t.id">{{ t.label }} - {{ t.summary }}</option>',
		'			</select>',
		'			<datalist v-for="(list, name) in ids" :key="name" :id="\'armorpieces_ids_\' + name">',
		'				<option v-for="(label, id) in list" :key="id" :value="id">{{ label }}</option>',
		'			</datalist>',
		'			<p class="ap_dim">Parts are cosmetic unless they carry an effect. Hover a field for what it does.</p>',
		'		</div>',
		'	</div>',
		'</div>',
	].join('\n');

	const PART_DIALOG_CSS = [
		'.armorpieces_part .dialog_bar.form_bar { display: flex; align-items: flex-start; }',
		'.armorpieces_part .form_bar > label { flex-shrink: 0; width: 100px; padding-top: 4px; }',
		'.armorpieces_part .form_bar > input { flex: 1; }',
		'.armorpieces_part .ap_column { flex: 1; min-width: 0; }',
		'.armorpieces_part .ap_dim { color: var(--color-subtle_text); }',
		'.armorpieces_part .ap_anchor_group { display: flex; flex-wrap: wrap; gap: 2px 12px; margin-bottom: 4px; }',
		'.armorpieces_part .ap_anchor_group > span { width: 80px; }',
		'.armorpieces_part .ap_anchor_group label { display: inline-flex; gap: 4px; align-items: center; cursor: pointer; }',
		'.armorpieces_part ul { list-style: none; margin: 0 0 4px; padding: 0; }',
		'.armorpieces_part li { display: flex; align-items: center; gap: 8px; padding: 2px 6px; margin-bottom: 2px; background: var(--color-back); }',
		'.armorpieces_part li .ap_dim { flex: 1; font-size: 0.9em; }',
		'.armorpieces_part li .material-icons { cursor: pointer; opacity: 0.6; }',
		'.armorpieces_part li .material-icons:hover { opacity: 1; }',
		'.armorpieces_part .ap_add { display: flex; gap: 6px; }',
		'.armorpieces_part .ap_add select { flex: 1; min-width: 0; }',
		'.armorpieces_part .ap_add button { flex-shrink: 0; margin: 0; }',
		'.armorpieces_part p { margin: 6px 0 0; font-size: 0.9em; }',
		'.armorpieces_part .ap_effect { background: var(--color-back); padding: 4px 6px; margin-bottom: 4px; }',
		'.armorpieces_part .ap_effect_head { display: flex; align-items: center; gap: 8px; font-weight: bold; }',
		'.armorpieces_part .ap_effect_head > span { flex: 1; }',
		'.armorpieces_part .ap_effect_head span span { font-weight: normal; }',
		'.armorpieces_part .ap_effect_head .material-icons { cursor: pointer; opacity: 0.6; }',
		'.armorpieces_part .ap_effect_head .material-icons:hover { opacity: 1; }',
		'.armorpieces_part .ap_effect pre { white-space: pre-wrap; margin: 4px 0 0; font-size: 0.85em; }',
		'.armorpieces_part .ap_field { display: flex; align-items: center; gap: 6px; margin-top: 3px; }',
		'.armorpieces_part .ap_field > label { width: 110px; flex-shrink: 0; }',
		'.armorpieces_part .ap_field > input[type=text], .armorpieces_part .ap_field > input[type=number], .armorpieces_part .ap_field > select { flex: 1; min-width: 0; }',
		'.armorpieces_part .ap_gate { margin-top: 6px; border-top: 1px solid var(--color-border); padding-top: 4px; }',
		'.armorpieces_part .ap_gate > label { display: inline-flex; align-items: center; gap: 4px; width: auto; }',
	].join('\n');

	function editPart() {
		const piece = currentPiece();
		const data = partData();
		if (!piece || !data) {
			Blockbench.showQuickMessage('This piece has no datapack half to edit', 2500);
			return;
		}
		const table = anchors();
		const listed = anchorsOf(piece);
		const groups = [];
		for (const name of Object.keys(table)) {
			const armor = table[name].armor_type;
			let group = groups.find(function (g) { return g.armor === armor; });
			if (!group) {
				group = { armor: armor, label: titleCase(armor.toLowerCase()), anchors: [] };
				groups.push(group);
			}
			group.anchors.push({ id: name, part: table[name].part, checked: listed.includes(name) });
		}
		const shown = displayName(piece, data);

		// Assigned below, so the New... button can hand the dialog to newFitting, which hides it
		// behind its own and shows it again - Vue state intact - when that one is done.
		let dialog = null;
		dialog = new Dialog({
			id: ID + '_part',
			title: 'Part ' + piece.key,
			width: 560,
			component: {
				data: function () {
					const schema = effectSchema();
					return {
						name: Project[ID + '_name'] || shown.text,
						editable: shown.editable,
						groups: groups,
						fittings: fittingsOf(piece).map(fittingRow),
						available: availableFittings(piece).map(fittingRow),
						effects: (data.effects || []).map(effectRow),
						schema: schema,
						types: Object.keys(schema).filter(function (id) { return id !== GATE_TYPE; })
							.map(function (id) { return { id: id, label: schema[id].label, summary: schema[id].summary }; }),
						ids: registryIds(),
					};
				},
				methods: {
					has: function (id) {
						return this.fittings.some(function (f) { return f.id === id; });
					},
					removeEffect: function (i) {
						this.effects.splice(i, 1);
					},
					addEffect: function (event) {
						const type = event.target.value;
						if (this.schema[type]) this.effects.push(blankEffect(type));
						event.target.value = '';
					},
					gateOn: function (effect) {
						if (effect.gated && !effect.gate.fitting && this.fittings.length) {
							effect.gate.fitting = this.fittings[0].id;
						}
					},
					gateOptions: function (effect) {
						const fitting = this.fittings.find(function (f) { return f.id === effect.gate.fitting; });
						if (!fitting) return [];
						if (fitting.type === 'armorpieces:dye') {
							return fitting.options.map(function (o) { return { id: o.value, label: o.label }; });
						}
						if (fitting.type === 'armorpieces:material') {
							return fitting.options.map(function (o) { return { id: o.id, label: o.label }; });
						}
						return [];
					},
					listFor: function (field) {
						return (field.kind === 'id' || field.kind === 'tag') && field.registry && this.ids[field.registry]
							? 'armorpieces_ids_' + field.registry : null;
					},
					move: function (i, by) {
						const j = i + by;
						if (j < 0 || j >= this.fittings.length) return;
						const item = this.fittings.splice(i, 1)[0];
						this.fittings.splice(j, 0, item);
					},
					remove: function (i) {
						this.fittings.splice(i, 1);
					},
					add: function (event) {
						const id = event.target.value;
						const found = this.available.find(function (f) { return f.id === id; });
						if (found && !this.has(id)) this.fittings.push(Object.assign({}, found));
						event.target.value = '';
					},
					create: function () {
						newFitting(piece, dialog);
					},
				},
				template: PART_DIALOG_TEMPLATE,
			},
			onConfirm: function () {
				const vue = this.content_vue;
				const chosen = [];
				for (const group of vue.groups) {
					for (const anchor of group.anchors) if (anchor.checked) chosen.push(anchor.id);
				}
				if (!chosen.length) {
					Blockbench.showQuickMessage('A part needs at least one anchor', 2500);
					return false;
				}
				for (const row of vue.effects) {
					const problem = effectProblem(row);
					if (problem) {
						Blockbench.showQuickMessage(problem, 2500);
						return false;
					}
				}
				this.hide();
				applyPartEdit(piece, data, shown, vue.name, chosen,
					vue.fittings.map(function (f) { return f.id; }),
					vue.effects.map(function (row) { return effectFromRow(row, vue.fittings); }));
			},
		});
		dialog.show();
	}

	// ---- the New Fitting dialog ---------------------------------------------------------------

	/*
	 * A fitting definition is one datapack file, a language line and - for a material fitting with
	 * a set of its own - a trim-material tag. All written once, when the dialog confirms, the way
	 * New Armor Piece writes a piece; the Part dialog then lists it like any other. The three
	 * built-in types are the whole of what can be made here: a type another mod registers has
	 * fields this dialog does not know, and a file it cannot read is a file it should not write.
	 */
	const FITTING_TYPES = {
		material: 'Material - a mask that takes a trim material',
		dye: 'Dye - a mask that takes a dye',
		banner: 'Banner - a bone that wears a banner',
	};
	const DIRECTIONS = ['south', 'north', 'east', 'west', 'up', 'down'];
	const CUSTOM_SET = 'custom';

	/* The trim materials and trim-material tags a new fitting could take, from preview_material.py. */
	function fittingChoices(piece) {
		try {
			return JSON.parse(tool('preview_material.py', ['--fitting-choices', piece.pack]));
		} catch (err) {
			console.error(err);
			return { materials: [], tags: [] };
		}
	}

	function fittingFileFor(piece, namespace, name) {
		return path.join(piece.pack, 'data', namespace, 'armorpieces', 'fitting', name + '.json');
	}

	/* The bones of the part as modelled: every unlocked group but the `part` root itself. */
	function partBones() {
		return Group.all
			.filter(function (g) { return !g.locked && g.name !== 'part'; })
			.map(function (g) { return g.name; });
	}

	function newFitting(piece, partDialog) {
		const choices = fittingChoices(piece);
		const tagOptions = {};
		for (const tag of choices.tags) {
			const members = tag.members.map(function (m) { return m.replace(/^minecraft:/, ''); });
			tagOptions[tag.id] = tag.id + '  (' + (members.length ? members.join(', ') : 'empty') + ')';
		}
		// Vanilla has no trim-material tags of its own, so the default is a tag written in this
		// pack over every material known here, which another pack can then add its own to.
		tagOptions[CUSTOM_SET] = 'These materials  (a tag written in this pack)';
		const fieldOf = function (material) {
			return 'material_' + material.value.replace(/[^a-z0-9]/g, '_');
		};
		const boneOptions = {};
		for (const bone of partBones()) boneOptions[bone] = bone;
		const directionOptions = {};
		for (const direction of DIRECTIONS) directionOptions[direction] = direction;
		const isMaterial = function (result) { return result.type === 'material'; };
		const isBanner = function (result) { return result.type === 'banner'; };

		const form = {
			name: {
				label: 'Name', type: 'text', value: '', placeholder: 'pommel',
				description: 'The id, and the mask file suffix: <part>_<name>.png',
			},
			namespace: { label: 'Namespace', type: 'text', value: piece.namespace },
			label: {
				label: 'Display name', type: 'text', value: '', placeholder: 'Pommel',
				description: 'Shown in tooltips; written to the language file.',
			},
			type: { label: 'Type', type: 'select', options: FITTING_TYPES, value: 'material' },
			materials: {
				label: 'Takes', type: 'select', options: tagOptions, value: CUSTOM_SET,
				condition: isMaterial,
				description: 'A trim-material tag, or the ticked materials as a new tag in this pack.',
			},
		};
		for (const material of choices.materials) {
			form[fieldOf(material)] = {
				label: material.label, type: 'checkbox', value: true,
				condition: function (result) { return isMaterial(result) && result.materials === CUSTOM_SET; },
			};
		}
		form.bone = {
			label: 'Bone', type: 'select', options: boneOptions, condition: isBanner,
			description: 'The bone of the part the banner is drawn on, in place of its own texture.',
		};
		form.sheet = {
			label: 'Pattern sheet', type: 'select', value: 'shield', condition: isBanner,
			options: { shield: 'shield  (finer, as on a shield)', banner: 'banner  (as on a banner block)' },
		};
		form.front = {
			label: 'Front face', type: 'select', options: directionOptions, value: 'south', condition: isBanner,
			description: 'Which face of the bone shows the design the right way round.',
		};

		new Dialog({
			id: ID + '_new_fitting',
			title: 'New Fitting',
			form: form,
			onConfirm: function (result) {
				const name = (result.name || '').trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
				const namespace = (result.namespace || '').trim() || piece.namespace;
				if (!name) {
					Blockbench.showQuickMessage('Name the fitting first', 2000);
					return false;
				}
				const file = fittingFileFor(piece, namespace, name);
				if (fs.existsSync(file)) {
					Blockbench.showMessageBox({
						title: 'Already exists',
						message: namespace + ':' + name + ' is already defined in that pack: ' + file,
					});
					return false;
				}
				const definition = {
					type: 'armorpieces:' + result.type,
					description: { translate: 'fitting.' + namespace + '.' + name },
				};
				if (result.type === 'material') {
					if (result.materials === CUSTOM_SET) {
						const chosen = choices.materials
							.filter(function (m) { return result[fieldOf(m)]; })
							.map(function (m) { return m.value; });
						if (!chosen.length) {
							Blockbench.showQuickMessage('Tick at least one material', 2500);
							return false;
						}
						writeJson(path.join(piece.pack, 'data', namespace, 'tags', 'trim_material', name + '.json'),
							{ values: chosen });
						definition.materials = '#' + namespace + ':' + name;
					} else {
						definition.materials = result.materials;
					}
				} else if (result.type === 'banner') {
					if (!result.bone) {
						Blockbench.showQuickMessage('Add a bone to the part first', 2500);
						return false;
					}
					definition.bone = result.bone;
					definition.sheet = result.sheet;
					definition.front = result.front;
				}
				writeJson(file, definition);
				writeLang(piece.pack, namespace, 'fitting.' + namespace + '.' + name,
					(result.label || '').trim() || titleCase(name));
				this.hide();

				// Listed the way every other fitting is: resolved by Python from the file just written.
				const id = namespace + ':' + name;
				const entry = availableFittings(piece).find(function (f) { return f.id === id; });
				const vue = partDialog && partDialog.content_vue;
				if (vue && entry) {
					const row = fittingRow(entry);
					vue.available.push(row);
					if (!vue.has(id)) vue.fittings.push(Object.assign({}, row));
				}
				Blockbench.showQuickMessage('Created fitting ' + id, 2500);
				if (partDialog) partDialog.show();
			},
			onCancel: function () {
				if (partDialog) partDialog.show();
			},
		}).show();
	}

	function applyPartEdit(piece, data, shown, name, chosen, fittingIds, effects) {
		const s = state();
		let changed = false;

		// Effects: compared with keys in a fixed order, so a row that merely re-spells what the
		// file said does not count as a change. Absent stays absent while the list is empty.
		if (effects && canonical(effects) !== canonical(data.effects || [])) {
			if (effects.length || 'effects' in data) data.effects = effects;
			markDirty();
			changed = true;
		}

		// Anchors keep their order: the first one is the socket the recipe's template item is for,
		// so it only changes when the author unticks it. New ones follow in body order.
		const kept = (data.anchors || []).filter(function (a) { return chosen.includes(a); });
		const anchorsNow = kept.concat(chosen.filter(function (a) { return !kept.includes(a); }));
		if (JSON.stringify(anchorsNow) !== JSON.stringify(data.anchors || [])) {
			data.anchors = anchorsNow;
			markDirty();
			changed = true;
		}

		// The field stays absent while the list is empty, so a part without fittings is written
		// exactly as it was read.
		if (JSON.stringify(fittingIds) !== JSON.stringify(data.fittings || [])) {
			if (fittingIds.length || 'fittings' in data) data.fittings = fittingIds;
			markDirty();
			Project[ID + '_fittings'] = null;
			changed = true;
		}

		name = (name || '').trim();
		if (shown.editable && name && name !== shown.text) {
			if (shown.key) {
				Project[ID + '_name'] = name;
			} else {
				data.description = name;
				markDirty();
			}
			changed = true;
		} else if (shown.key && Project[ID + '_name'] && name === shown.text) {
			Project[ID + '_name'] = null;
		}

		// The panel follows: a fitting taken off the part is no longer under the brush or in the
		// preview, and the anchor list is whatever the part now says.
		const masked = maskedFittings();
		if (s.edit === 'fitting' && !masked.some(function (f) { return f.name === s.fitting; })) {
			s.edit = 'master';
			s.fitting = '';
		}
		const previewed = previewFittings();
		for (const key of Object.keys(s.fittings)) {
			if (!previewed.some(function (f) { return f.name === key; })) delete s.fittings[key];
		}
		syncForm();
		applyTextures();
		applyPalette();
		refreshPreview(true);
		if (changed) Blockbench.showQuickMessage('Part changed - written on Save', 2000);
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
		// The rig stays on its anchor after the Part dialog took that anchor off the part.
		const current = state().anchor;
		if (current && !options[current]) options[current] = current + '  (not on the part)';
		if (!Object.keys(options).length) options[''] = '-';
		return options;
	}

	function animationOptions() {
		return { idle: 'Idle', walk: 'Walk', sprint: 'Sprint' };
	}

	/*
	 * The fittings are two sets of controls: which mask the brush paints, and what each fitting
	 * holds in the preview. A piece has any number of fittings and a form has a fixed set of
	 * fields, so the preview gets six slots, one per masked fitting in the part's order, hidden
	 * past the last one; no shipped part has more than two, and the Part dialog can add more. Each
	 * slot's label is the fitting's own name, set on the built label element by syncForm, because
	 * a form label is a string fixed at build time and the fitting behind a slot is not.
	 */
	const FITTING_SLOTS = 6;

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
				const fitting = previewFittings()[index];
				const options = { '': fitting ? '(empty)' : '-' };
				for (const option of (fitting ? fitting.options : [])) options[option.value] = option.label;
				return options;
			},
			condition: function (result) {
				return !!result.preview && previewFittings().length > index;
			},
		};
	}

	function panelForm() {
		const materialOptions = MATERIALS.reduce(function (all, m) { all[m] = m; return all; }, {});
		return {
			piece: { label: 'Piece', type: 'select', options: pieceOptions },
			anchor: { label: 'Anchor', type: 'select', options: anchorOptions },
			actions: {
				type: 'buttons', buttons: ['New...', 'Part...', 'Save', 'Rebuild'],
				click: function (index) {
					if (index === 0) newPiece();
					else if (index === 1) editPart();
					else if (index === 2) savePiece();
					else reopen(state().anchor);
				},
			},
			// What the datapack half says, in one line; syncForm writes it into the built element.
			summary: { type: 'info', text: '' },
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
			fitting_3: fittingSlot(3),
			fitting_4: fittingSlot(4),
			fitting_5: fittingSlot(5),
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
		const masked = previewFittings();
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
			const summary = panel.form.form_data.summary;
			const box = summary && summary.bar && summary.bar.querySelector('.small_text');
			if (box) box.textContent = partSummary(piece);
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
		const shown = previewFittings();
		for (let i = 0; i < shown.length && i < FITTING_SLOTS; i++) {
			s.fittings[shown[i].name] = result['fitting_' + i] || '';
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
				// The mod's cube has no rotation field and bb_geo drops one silently, so the format
				// does not offer it; a rotated cube is a rotated bone, which does export.
				rotate_cubes: false,
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
			// Likewise for a flag a format object from an earlier load of the plugin still carries.
			format.rotate_cubes = false;

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
			registered.push(Blockbench.addCSS(PART_DIALOG_CSS));

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

			// A piece open across a reload of the plugin keeps its resolved fittings from before it,
			// which may be missing what the resolver now reports. Resolve them again on first use.
			for (const project of ModelProject.all) project[ID + '_fittings'] = null;

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
				data: partData,
				fittings: function () { return fittingsOf(currentPiece()); },
				availableFittings: function () { return availableFittings(currentPiece()); },
				editPart: editPart,
				applyPartEdit: function (name, anchors, fittingIds, effects) {
					const piece = currentPiece();
					const data = partData();
					applyPartEdit(piece, data, displayName(piece, data), name, anchors, fittingIds, effects);
				},
				effectSchema: effectSchema,
				effectRow: effectRow,
				effectFromRow: effectFromRow,
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
