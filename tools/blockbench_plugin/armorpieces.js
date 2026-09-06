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
 * An armor SKIN gets the same three things - see the skin section far below. It is a different
 * project, in `free` rather than the plugin's format, so every one of the changes above asks
 * `isWorkspace() || isSkinWorkspace()` rather than the first alone: a skin's panel is "Armor Skin",
 * its palette is the sixteen levels its ASCII alphabet is written in, and its two previews route
 * the brush back onto the two masters exactly as a piece's one does.
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
	const https = require('https');

	const ID = 'armorpieces';
	/*
	 * The pack library: a hosted list of packs, each pointing at a zip its author hosts, plus the
	 * mod's own. It is read from an index.json (the setting below says which) and written to by
	 * submission - a filled-in issue on the library's repository, approved by a maintainer. The
	 * web build of this plugin is served from LIBRARY_SITE and reads the index beside itself.
	 */
	const LIBRARY_HOME = 'https://github.com/mattjesmc/ArmorPiecesBlockbench';
	const LIBRARY_SITE = 'https://mattjesmc.github.io/ArmorPiecesBlockbench/';
	const LIBRARY_INDEX = LIBRARY_SITE + 'library/index.json';
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
	const skinLights = {};

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
			// Off, the recipe file is written with its type swapped to armorpieces:disabled.
			recipe_craftable: true,
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
		if (!root) {
			throw new Error('The Armor Pieces repository is the toolkit this plugin drives - the rigs, ' +
				'the preview and the game-asset extraction are its Python. Clone it from ' +
				'github.com/mattjesmc/ArmorPieces, install Python 3 with Pillow, and set ' +
				'"Armor Pieces repository" in Settings to the clone. Your own packs can live anywhere.');
		}
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

	/* The folders the author has added through Packs..., kept as JSON in a setting. */
	function userPacks() {
		try {
			const list = JSON.parse(Settings.get(ID + '_packs') || '[]');
			return Array.isArray(list) ? list.filter(function (p) { return typeof p === 'string' && p; }) : [];
		} catch (err) {
			return [];
		}
	}

	function setUserPacks(list) {
		settings[ID + '_packs'].set(JSON.stringify(list));
		Settings.save();
	}

	function subdirs(dir) {
		if (!dir || !fs.existsSync(dir)) return [];
		return fs.readdirSync(dir)
			.map(function (entry) { return path.join(dir, entry); })
			.filter(function (candidate) {
				try { return fs.statSync(candidate).isDirectory(); } catch (err) { return false; }
			});
	}

	/*
	 * The running game's own folder, where its resource packs and worlds live. Only `os`, never
	 * `process`: Blockbench 5.1 runs a plugin file through `new Function` in a scope with no
	 * `process` global (native_apis.ts deletes it), so `process.platform` here is a ReferenceError
	 * that takes every pack dialog down with it. An eval-loaded copy of this file does see
	 * `process`, which is why that check must be a Plugins reload, not an eval.
	 */
	function minecraftDir() {
		const home = os.homedir();
		if (os.platform() === 'win32') return path.join(home, 'AppData', 'Roaming', '.minecraft');
		if (os.platform() === 'darwin') return path.join(home, 'Library', 'Application Support', 'minecraft');
		return path.join(home, '.minecraft');
	}

	// ---- packs: the platform seam ----------------------------------------------------------------

	/*
	 * Pack management is the one part of this plugin that cannot be written once and left alone,
	 * because it is the part that touches things outside the editor: folders, zips, and the file
	 * dialogs that reach them. The desktop has a disk and native pickers. The web build has a
	 * filesystem that the Python shares and the browser persists, no native pickers at all, and
	 * downloads instead of save dialogs.
	 *
	 * These five functions are the ONLY place in this file that asks which of the two it is on.
	 * Everything else - discovery, the manager, new packs, import, export - is the same code
	 * running over the same `fs`, because on both platforms there is a real filesystem underneath
	 * with real pack folders in it. Adding a platform means adding cases here and nowhere else.
	 */

	/* Where a pack goes when the author is not asked where. */
	function packHome() {
		return isApp ? minecraftDir() : '/packs';
	}

	/* Only a desktop file dialog can hand back a folder that already exists elsewhere. */
	function canBrowseFolders() {
		return !!isApp;
	}

	function browseForPack(done) {
		const dir = Blockbench.pickDirectory({ title: 'Add a pack folder', startpath: packHome() });
		if (dir) done(dir);
	}

	/*
	 * A zip from outside, landed somewhere the tools can read it. The desktop hands back a path
	 * and the browser hands back bytes, so both are written to one scratch file and the caller
	 * gets a path either way - which is what import_pack.py takes.
	 */
	function takeZip(done) {
		Blockbench.import({
			title: 'Import a pack zip', extensions: ['zip'], type: 'Pack zip', readtype: 'buffer',
		}, function (files) {
			const file = files && files[0];
			if (!file) return;
			const scratch = path.join(tempDir(), 'import.zip');
			const content = file.content;
			if (content) {
				fs.writeFileSync(scratch, content instanceof ArrayBuffer ? new Uint8Array(content) : content);
				done(scratch, file.name || 'pack.zip');
			} else if (file.path) {
				done(file.path, file.name || path.basename(file.path));
			}
		});
	}

	/*
	 * A zip the tools have just written, put where the author can get at it. On the desktop it is
	 * already there - they chose the path - so this is the browser's half: read it back out of the
	 * filesystem and hand it to the page as a download, since nothing in a tab can reach a disk.
	 */
	function giveZip(file, name) {
		if (isApp) return file;
		Blockbench.export({
			type: 'Pack zip', extensions: ['zip'], name: name || path.basename(file),
			content: fs.readFileSync(file), savetype: 'buffer',
		});
		return file;
	}

	/*
	 * Bytes from a URL. The sixth platform question, and the one the library turns on: the
	 * desktop is a node program and can read from any host, a browser can only read from hosts
	 * that allow a page to (CORS) - GitHub's raw files and jsDelivr do, GitHub release assets and
	 * Google Drive do not. Both hand `done` a Uint8Array and `fail` an Error, so a caller reads
	 * the same either way; where a browser is refused, the caller says so and offers the link.
	 *
	 * `options` is what a request to a site with accounts needs: `headers` (a bearer token on the
	 * desktop) and `credentials` ('include' in a browser, so the page's own session cookie goes
	 * along on its own origin). Both are optional and the library's public index needs neither.
	 */
	function fetchBytes(url, done, fail, options) {
		options = options || {};
		// Plain http is allowed only on this machine - a library served by `npm run serve` while
		// the site is being worked on - and goes through the page's fetch below even on the
		// desktop, because Blockbench's plugin require offers https and not http. That server
		// sends the CORS header the page needs, so it is the same path the browser build takes.
		const local = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?\//i.test(url);
		if (isApp && !local) {
			if (!/^https:\/\//i.test(url)) return fail(new Error('Only https URLs can be fetched: ' + url));
			const headers = Object.assign({ 'user-agent': 'armorpieces-blockbench' }, options.headers || {});
			const follow = function (target, left) {
				https.get(target, { headers: headers }, function (res) {
					const status = res.statusCode || 0;
					if (status >= 300 && status < 400 && res.headers.location && left > 0) {
						res.resume();
						return follow(new URL(res.headers.location, target).href, left - 1);
					}
					if (status !== 200) {
						res.resume();
						return fail(new Error(target + ' answered ' + status));
					}
					const chunks = [];
					res.on('data', function (chunk) { chunks.push(chunk); });
					res.on('end', function () { done(new Uint8Array(Buffer.concat(chunks))); });
					res.on('error', fail);
				}).on('error', fail);
			};
			follow(url, 5);
			return;
		}
		let absolute;
		try {
			absolute = new URL(url, window.location.href).href;
		} catch (err) {
			return fail(new Error('Not a URL: ' + url));
		}
		const init = {};
		if (options.headers) init.headers = options.headers;
		if (options.credentials) init.credentials = options.credentials;
		fetch(absolute, init).then(function (res) {
			if (!res.ok) throw new Error(absolute + ' answered ' + res.status + ' ' + res.statusText);
			return res.arrayBuffer();
		}).then(function (buffer) { done(new Uint8Array(buffer)); }, function (err) {
			fail(err instanceof Error ? err : new Error(String(err)));
		});
	}

	/* Every resource pack folder and every world datapack folder under a game directory. */
	function packsUnderGameDir(dir) {
		const roots = subdirs(path.join(dir, 'resourcepacks'));
		for (const world of subdirs(path.join(dir, 'saves'))) {
			roots.push(...subdirs(path.join(world, 'datapacks')));
		}
		return roots;
	}

	/*
	 * Where packs are looked for: the author's own list first, then the repository's three places
	 * when there is a repository - its resources, its run/ resource packs, its run/ worlds'
	 * datapacks - then the installed game's. The repository is the toolkit, not the workspace, so
	 * content never has to live in it; the game folders are there so a pack made for the launcher
	 * needs no adding.
	 */
	/*
	 * The roots found without being told about: the repository's, the game's, and - off the
	 * desktop - everything under the folder packs live in. The manager needs these separately from
	 * the author's own list, because a pack that is found anyway cannot be un-listed. Offering
	 * "Forget" for one would be a button that appears to work and changes nothing.
	 */
	function autoRoots() {
		const roots = [];
		const root = repoRoot();
		if (root) {
			roots.push(path.join(root, 'src', 'main', 'resources'));
			roots.push(...packsUnderGameDir(path.join(root, 'run')));
		}
		if (!isApp) roots.push(...subdirs(packHome()));
		roots.push(...packsUnderGameDir(minecraftDir()));
		return roots;
	}

	function searchRoots() {
		const roots = userPacks().slice();
		const root = repoRoot();
		if (root) {
			roots.push(path.join(root, 'src', 'main', 'resources'));
			roots.push(...packsUnderGameDir(path.join(root, 'run')));
		}
		// The web build has no game folder to look in. What it has instead is one root that
		// persists between visits, and every folder under it is a pack - the same relationship
		// resourcepacks/ has to the packs inside it.
		if (!isApp) roots.push(...subdirs(packHome()));
		roots.push(...packsUnderGameDir(minecraftDir()));
		const seen = new Set();
		return roots.filter(function (dir) {
			const key = path.resolve(dir).toLowerCase();
			if (seen.has(key) || !fs.existsSync(dir)) return false;
			seen.add(key);
			return true;
		});
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

	/*
	 * A piece has two packs. The datapack half - the part file, its fittings, recipes and tags -
	 * lives in `dataPack`; the resourcepack half - geometry, textures and the language file - in
	 * `assetPack`. In this repository and in a world folder used for both they are the same
	 * directory; for a player's own content they are a folder under resourcepacks/ and one under a
	 * world's datapacks/, and every writer here goes to the right one. `pack` is the datapack, kept
	 * under its old name because every datapack-side writer reads it.
	 */
	// ---- credits --------------------------------------------------------------------------------

	/*
	 * Who made a piece and under what license: `armorpieces-credits.json` at a pack's root, a
	 * file the game ignores, with a pack-level default and a per-piece override. The keys are
	 * namespaced ids and cover pieces, skins and cloths alike; pack_manifest.py reads the same
	 * file and pick_pieces.py carries it along. A pack without the file is all rights reserved by
	 * its author, which is what copyright law says anyway - so `ARR` is the default here too.
	 */
	const CREDITS_FILE = 'armorpieces-credits.json';
	const LICENSE_OPTIONS = {
		'ARR': 'All rights reserved - listed, downloadable as your pack, never composed into another',
		'CC0-1.0': 'CC0 1.0 - public domain',
		'CC-BY-4.0': 'CC BY 4.0 - with credit',
		'CC-BY-SA-4.0': 'CC BY-SA 4.0 - with credit, share alike',
		'CC-BY-NC-4.0': 'CC BY-NC 4.0 - with credit, not commercially',
		'CC-BY-NC-SA-4.0': 'CC BY-NC-SA 4.0 - with credit, not commercially, share alike',
	};

	function readCredits(dirs) {
		const out = { pack: {}, pieces: {} };
		for (const dir of dirs) {
			if (!dir) continue;
			const found = readJsonOr(path.join(dir, CREDITS_FILE), null);
			if (!found || typeof found !== 'object') continue;
			if (found.pack && typeof found.pack === 'object') Object.assign(out.pack, found.pack);
			if (found.pieces && typeof found.pieces === 'object') {
				for (const key of Object.keys(found.pieces)) {
					out.pieces[key] = Object.assign({}, out.pieces[key] || {}, found.pieces[key]);
				}
			}
		}
		return out;
	}

	/* The author and license one id resolves to: its own entry over the pack's default. */
	function creditOf(dirs, key) {
		const credits = readCredits(dirs);
		const own = credits.pieces[key] || {};
		const license = String(own.license || credits.pack.license || 'ARR');
		return {
			author: String(own.author || credits.pack.author || ''),
			license: LICENSE_OPTIONS[license] ? license : 'ARR',
		};
	}

	/* Write one id's credit into the pack's file, keeping everything else in it. The datapack
	   half carries the file: it is the half that names the piece. */
	function writeCredit(dir, key, credit) {
		const file = path.join(dir, CREDITS_FILE);
		const current = readJsonOr(file, null) || {};
		if (!current.pieces || typeof current.pieces !== 'object') current.pieces = {};
		if (!current.pack || typeof current.pack !== 'object') current.pack = {};
		const entry = {};
		if (credit.author) entry.author = credit.author;
		entry.license = credit.license || 'ARR';
		// A piece that only repeats the pack's default needs no line of its own.
		const inherited = { author: String(current.pack.author || ''), license: String(current.pack.license || 'ARR') };
		if (inherited.author === (credit.author || '') && inherited.license === entry.license) {
			delete current.pieces[key];
		} else {
			current.pieces[key] = entry;
		}
		writeJson(file, current);
		return file;
	}

	function pieceRecord(dataPack, assetPack, namespace, name) {
		const dataDir = path.join(dataPack, 'data', namespace, ...DATA_REL);
		const assetDir = path.join(assetPack, 'assets', namespace, ...ASSET_REL);
		return {
			name: name,
			namespace: namespace,
			key: namespace + ':' + name,
			pack: dataPack,
			dataPack: dataPack,
			assetPack: assetPack,
			data: path.join(dataDir, name + '.json'),
			geometry: path.join(assetDir, name + '.json'),
			texture: path.join(assetPack, 'assets', namespace, 'textures', 'entity', 'decoration',
				name + '.png'),
		};
	}

	/* The halves one pack directory holds, by piece key: which of data and assets it has. */
	function halvesIn(packDir) {
		const found = {};
		for (const namespace of new Set(
			namespacesIn(packDir, 'data').concat(namespacesIn(packDir, 'assets')))) {
			const dataDir = path.join(packDir, 'data', namespace, ...DATA_REL);
			const assetDir = path.join(packDir, 'assets', namespace, ...ASSET_REL);
			for (const name of listJson(dataDir)) {
				const key = namespace + ':' + name;
				found[key] = found[key] || { namespace: namespace, name: name };
				found[key].data = true;
			}
			for (const name of listJson(assetDir)) {
				const key = namespace + ':' + name;
				found[key] = found[key] || { namespace: namespace, name: name };
				found[key].assets = true;
			}
		}
		return found;
	}

	/*
	 * Every piece across every root, the two halves of a `namespace:name` paired up wherever they
	 * sit. A root holding both halves wins over a pair split across two; a half that is nowhere
	 * borrows the other half's folder, so the record still says where it WOULD go and the label
	 * can say it is missing.
	 */
	/*
	 * The pack being worked in. Every pack discovery finds is one list by default, keyed by
	 * name with the first pack found winning - which is how the game resolves them too, and
	 * which makes a pack that redefines the mod's pieces invisible next to the mod's own. So an
	 * author can choose one pack, and from then on the piece list, the skin halves, the open
	 * dialogs and the start page see that pack alone. Creating a piece still offers every pack,
	 * defaulting to this one. Kept in a setting so it survives a restart; cleared if the folder
	 * has gone.
	 */
	function packScope() {
		const dir = String(Settings.get(ID + '_scope') || '').trim();
		return dir && fs.existsSync(dir) ? dir : '';
	}

	function setPackScope(dir) {
		settings[ID + '_scope'].set(dir || '');
		Settings.save();
	}

	/* The packs a list is drawn from: the chosen one, or all of them. */
	function scopedRoots() {
		const scope = packScope();
		return scope ? [scope] : searchRoots();
	}

	/* Where a pack select starts: on the pack being worked in, when there is one. */
	function defaultPack(packs) {
		const at = packs.indexOf(packScope());
		return String(at > 0 ? at : 0);
	}

	function allPieces() {
		const byKey = {};
		for (const packDir of scopedRoots()) {
			const halves = halvesIn(packDir);
			for (const key of Object.keys(halves)) {
				const half = halves[key];
				const entry = byKey[key] || (byKey[key] = {
					namespace: half.namespace, name: half.name, dataPack: null, assetPack: null, both: null,
				});
				if (half.data && half.assets && !entry.both) entry.both = packDir;
				if (half.data && !entry.dataPack) entry.dataPack = packDir;
				if (half.assets && !entry.assetPack) entry.assetPack = packDir;
			}
		}
		return Object.values(byKey).map(function (entry) {
			const dataPack = entry.both || entry.dataPack || entry.assetPack;
			const assetPack = entry.both || entry.assetPack || entry.dataPack;
			return pieceRecord(dataPack, assetPack, entry.namespace, entry.name);
		});
	}

	/* A pack folder as the list shows it: relative to the repository when it is inside it. */
	function packLabel(dir) {
		const root = repoRoot();
		if (root) {
			const relative = path.relative(root, dir);
			if (relative && !relative.startsWith('..') && !path.isAbsolute(relative)) {
				return relative.replace(/\\/g, '/');
			}
			if (!relative) return '.';
		}
		const game = minecraftDir();
		const relative = path.relative(game, dir);
		if (relative && !relative.startsWith('..') && !path.isAbsolute(relative)) {
			return '.minecraft/' + relative.replace(/\\/g, '/');
		}
		return dir;
	}

	/*
	 * What the manager needs to say about one pack folder. The old Packs... dialog listed paths
	 * and nothing else, which answers none of the questions an author actually has in front of it:
	 * is this a datapack or a resource pack, is the game going to load it at all, how much is in
	 * it, and is it mine to remove. All four are readable off the folder, so they are read.
	 *
	 * `parts` counts piece KEYS rather than files, so a pack holding both halves of one piece
	 * counts it once - and `data`/`assets` say how many of those keys each half covers, which is
	 * how a pack with models but no part files shows up as the half-finished thing it is.
	 */
	/* A pack.mcmeta's format as a label: "88", or "107-108" for a range, or null for none. */
	function packFormatOf(pack) {
		if (!pack) return null;
		if (typeof pack.pack_format === 'number') return String(pack.pack_format);
		const low = pack.min_format;
		const high = pack.max_format;
		const one = function (v) { return Array.isArray(v) ? v.join('.') : typeof v === 'number' ? String(v) : null; };
		if (one(low) === null && one(high) === null) return null;
		if (one(low) === null || one(high) === null || one(low) === one(high)) return one(low) || one(high);
		return one(low) + '-' + one(high);
	}

	function packInfo(dir) {
		const halves = halvesIn(dir);
		const keys = Object.keys(halves);
		let data = 0;
		let assets = 0;
		for (const key of keys) {
			if (halves[key].data) data++;
			if (halves[key].assets) assets++;
		}
		const meta = readJsonOr(path.join(dir, 'pack.mcmeta'), null);
		const pack = (meta && meta.pack) || null;
		return {
			dir: dir,
			label: packLabel(dir),
			parts: keys.length,
			data: data,
			assets: assets,
			hasData: fs.existsSync(path.join(dir, 'data')),
			hasAssets: fs.existsSync(path.join(dir, 'assets')),
			// Either shape the game has used: one pack_format, or the min_format..max_format range
			// the standalone zips the build writes carry.
			format: packFormatOf(pack),
			description: pack ? pack.description : null,
			// From armorpieces-credits.json, when the pack has one; all rights reserved otherwise.
			license: readCredits([dir]).pack.license || 'ARR',
			author: readCredits([dir]).pack.author || '',
			// Forgetting a folder only does anything if being in the author's list is the only
			// reason it shows up. A pack that is found anyway has to be deleted or left alone.
			mine: userPacks().indexOf(dir) !== -1 && autoRoots().indexOf(dir) === -1,
			/*
			 * Deleting is offered only where this plugin is the only way to do it. In a browser
			 * that is true of everything under the folder packs live in - there is no file manager
			 * to switch to, so a pack made here and not wanted here has no other way out. On the
			 * desktop it is true of nothing: packHome() is .minecraft, which is full of other
			 * people's packs, and offering to delete a datapack some other tool put in a world is
			 * both wrong and a click away from a real loss. There, Explorer is the right tool.
			 */
			deletable: !isApp && dir.indexOf(packHome() + '/') === 0,
		};
	}

	/* Datapack, resource pack, or one folder serving as both - by what is in it, not by its name. */
	function packKind(info) {
		if (info.hasData && info.hasAssets) return 'datapack + resource pack';
		if (info.hasData) return 'datapack';
		if (info.hasAssets) return 'resource pack';
		return 'empty';
	}

	// ---- where packs come from -------------------------------------------------------------------

	/*
	 * A SOURCE is somewhere parts can be installed from and published to. There is one today - a
	 * zip on the author's machine - and the manager is written against this list rather than
	 * against zips, because 0.4.0's online library is the second: browsing it and installing an
	 * entry is `install`, and offering your own pack to it is `publish`. Adding it should mean
	 * pushing an entry here and writing its two functions, not touching the dialog.
	 *
	 * `install` is handed a destination folder and calls back when something has landed in it.
	 * `publish` is handed a pack folder. Either may be absent: a read-only library would have no
	 * publish, and a source that is only somewhere to send things would have no install.
	 */
	const packSources = [];

	function registerPackSource(source) {
		packSources.push(source);
		return source;
	}

	registerPackSource({
		id: 'zip',
		label: 'a pack zip',
		installLabel: 'Import zip...',
		publishLabel: 'Export zip...',
		install: function (dest, done) {
			takeZip(function (zip) {
				try {
					const report = tool('import_pack.py', [zip, dest, '--force']);
					done(report.trim() || ('Unpacked into ' + dest));
				} catch (err) {
					console.error(err);
					Blockbench.showMessageBox({
						title: 'Import failed',
						message: String((err && err.stderr) || (err && err.message) || err),
					});
				}
			});
		},
		publish: function (dir, done) {
			// The desktop lets the author say where the zip goes. A browser has nowhere to be
			// asked about - a download is the only destination - so it does not ask.
			if (!isApp) return tryWritePackZip(dir, null, done);
			new Dialog({
				id: ID + '_publish_zip',
				title: 'Export Pack',
				form: {
					zip: {
						label: 'Zip file', type: 'save', extensions: ['zip'], filetype: 'Pack zip',
						value: defaultZipPath(dir),
						description: 'Blank writes <pack folder>.zip beside the folder.',
					},
				},
				onConfirm: function (result) {
					this.hide();
					tryWritePackZip(dir, (result.zip || '').trim(), done);
				},
			}).show();
		},
	});

	// ---- the library --------------------------------------------------------------------------

	/*
	 * The second source: a hosted list of packs. Each entry names one or more zips - a datapack
	 * half, a resource pack half, or one zip holding both - at URLs their author hosts, and
	 * installing an entry is fetching those and running import_pack.py over each, which is the
	 * same thing the zip source does with a file the author chose. Submitting a pack is a
	 * filled-in issue on the library's repository; a maintainer approves it, which is when it
	 * appears in the index. Nothing here decides what is in the library - the index does.
	 */
	let libraryCache = null;

	function libraryUrl() {
		return String(Settings.get(ID + '_library') || LIBRARY_INDEX).trim();
	}

	function libraryIndex(done, fail, fresh) {
		if (libraryCache && !fresh) return done(libraryCache);
		const url = libraryUrl();
		fetchBytes(url, function (bytes) {
			let index;
			try {
				index = JSON.parse(new TextDecoder().decode(bytes));
				if (!index || !Array.isArray(index.entries)) throw new Error('no entries list');
			} catch (err) {
				return fail(new Error(url + ' is not a library index: ' + err.message));
			}
			// A pack URL may be relative to the index, which is how one site hosts both.
			index.entries.forEach(function (entry) {
				entry.packs = (entry.packs || []).map(function (pack) {
					return Object.assign({}, pack, { url: new URL(pack.url, url).href });
				});
			});
			libraryCache = index;
			done(index);
		}, fail);
	}

	/*
	 * A download the page was refused. In a browser that is nearly always the host declining to
	 * serve a page on another origin, which the author of the entry can fix by hosting the zip
	 * somewhere that does; the visitor can fix it right now by downloading the file themselves
	 * and importing it, so that is what is offered.
	 */
	function cannotFetch(entry, pack, err) {
		const name = pack.url.split('/').pop() || 'the pack';
		const why = isApp
			? String((err && err.message) || err)
			: 'This page was not allowed to download it. Browsers can only fetch from hosts that ' +
				'permit it (GitHub raw files and jsDelivr do; GitHub release assets and Google Drive ' +
				'do not), and on other hosts the file has to come in by hand.';
		Blockbench.showMessageBox({
			title: 'Could not download ' + name,
			message: entry.name + ' - ' + why + '\n\nOpen the download, then bring the zip in with ' +
				'Import zip... in Packs....',
			buttons: ['Open the download', 'Cancel'],
			confirm: 0, cancel: 1,
		}, function (answer) {
			if (answer === 0) Blockbench.openLink(pack.url);
		});
	}

	/* Fetch every zip an entry lists and unpack each into one folder, in order. */
	function installEntry(entry, dest, done) {
		const packs = (entry.packs || []).slice();
		const reports = [];
		if (!packs.length) return done(entry.name + ' lists no packs to install.');
		(function next() {
			const pack = packs.shift();
			if (!pack) return done(entry.name + ': ' + reports.join('; '));
			fetchBytes(pack.url, function (bytes) {
				try {
					const scratch = path.join(tempDir(), 'library.zip');
					fs.writeFileSync(scratch, bytes);
					reports.push(tool('import_pack.py', [scratch, dest, '--force']).trim());
				} catch (err) {
					console.error(err);
					return Blockbench.showMessageBox({
						title: 'Install failed',
						message: String((err && err.stderr) || (err && err.message) || err),
					});
				}
				next();
			}, function (err) {
				console.error('[armorpieces] could not fetch ' + pack.url, err);
				cannotFetch(entry, pack, err);
			});
		})();
	}

	const LIBRARY_DIALOG_TEMPLATE = [
		'<div class="armorpieces_library">',
		'	<p class="ap_dim" v-if="loading">Reading the library...</p>',
		'	<p class="ap_dim ap_warn" v-else-if="error">{{ error }}</p>',
		'	<template v-else>',
		'		<div class="ap_add">',
		'			<input type="search" v-model="term" placeholder="Search packs..." autocomplete="off">',
		'			<span class="ap_dim">{{ shown.length }} of {{ entries.length }}</span>',
		'		</div>',
		'		<ul>',
		'			<li v-for="e in shown" :key="e.id">',
		'				<div class="ap_head">',
		'					<span class="ap_name">{{ e.name }}</span>',
		'					<span class="ap_tag" v-if="e.version">{{ e.version }}</span>',
		'					<span class="ap_tag" v-for="t in e.tags || []" :key="t">{{ t }}</span>',
		'				</div>',
		'				<div class="ap_body"><span class="ap_dim">{{ e.description }}</span></div>',
		'				<div class="ap_body">',
		'					<span class="ap_dim">by {{ e.author && e.author.name }}',
		'						<template v-if="e.packs.length > 1"> - {{ e.packs.length }} zips</template></span>',
		'					<a v-if="e.homepage" href="#" @click.prevent="open(e.homepage)">details</a>',
		'					<span class="ap_spacer"></span>',
		'					<button type="button" @click="pick(e)">Install</button>',
		'				</div>',
		'			</li>',
		'			<li v-if="!shown.length" class="ap_dim">Nothing matches.</li>',
		'		</ul>',
		'		<p class="ap_dim">Read from <a href="#" @click.prevent="open(home)">{{ url }}</a>.',
		'			Your own packs go in through Submit... in Packs....</p>',
		'	</template>',
		'</div>',
	].join('\n');

	/*
	 * Browse the library and pick an entry. The list is the index, filtered; what happens to the
	 * pick is the caller's, because the manager installs into a pack and the start page of the
	 * web build installs into a new one.
	 */
	function libraryDialog(onPick) {
		const dialog = new Dialog({
			id: ID + '_library',
			title: 'Armor Pieces Library',
			width: 640,
			singleButton: true,
			component: {
				data: function () {
					return { loading: true, error: '', entries: [], term: '', url: libraryUrl(), home: LIBRARY_HOME };
				},
				computed: {
					shown: function () {
						const term = this.term.trim().toLowerCase();
						if (!term) return this.entries;
						return this.entries.filter(function (e) {
							return [e.name, e.description, e.author && e.author.name, e.id]
								.concat(e.tags || []).join(' ').toLowerCase().indexOf(term) !== -1;
						});
					},
				},
				mounted: function () {
					const vue = this;
					libraryIndex(function (index) {
						vue.entries = index.entries;
						vue.loading = false;
					}, function (err) {
						vue.error = 'Could not read the library: ' + String((err && err.message) || err);
						vue.loading = false;
					});
				},
				methods: {
					open: function (url) { Blockbench.openLink(url); },
					pick: function (entry) {
						dialog.hide();
						onPick(entry);
					},
				},
				template: LIBRARY_DIALOG_TEMPLATE,
			},
		});
		dialog.show();
		return dialog;
	}

	/*
	 * The two places a pack can be offered, in the words the library's issue form uses - GitHub
	 * fills a dropdown in from a URL only when the text matches an option exactly.
	 */
	const SUBMIT_TO = {
		library: 'The library (hosted by me)',
		mod: 'The mod (for inclusion)',
	};

	/* The issue that is a submission, with everything the author typed already in it. */
	function submissionUrl(fields) {
		const query = {
			template: 'submission.yml',
			title: '[Pack] ' + fields.name,
			destination: SUBMIT_TO[fields.destination] || SUBMIT_TO.library,
			name: fields.name,
			author: fields.author,
			url: fields.url,
			homepage: fields.homepage,
			description: fields.description,
		};
		return LIBRARY_HOME + '/issues/new?' + Object.keys(query)
			.filter(function (key) { return query[key]; })
			.map(function (key) { return key + '=' + encodeURIComponent(query[key]); })
			.join('&');
	}

	/*
	 * Submit...: offer a pack to the library, or to the mod. Neither is something this plugin can
	 * do on its own - one is a listing a maintainer approves, the other is a change to the mod's
	 * own content - so both are an issue on the library's repository, opened here with the form
	 * filled in, and the zip written beside the pack so there is something to host or attach.
	 */
	function submitDialog(dir, done) {
		const info = packInfo(dir);
		new Dialog({
			id: ID + '_submit',
			title: 'Submit ' + info.label,
			width: 600,
			form: {
				about: {
					type: 'info',
					text: 'Submitting opens an issue on ' + LIBRARY_HOME.replace('https://', '') +
						' with this form in it, and writes a zip of the pack for you to host or attach. ' +
						'A maintainer reviews it; an approved pack appears in the library.',
				},
				destination: {
					label: 'Send it to', type: 'select', value: 'library',
					options: SUBMIT_TO,
					description: 'The library lists packs their authors host. The mod takes packs ' +
						'into Armor Pieces itself, under its license.',
				},
				name: { label: 'Pack name', type: 'text', value: info.label },
				author: { label: 'Your name', type: 'text', value: '' },
				description: {
					label: 'Description', type: 'textarea', value: '', height: 80,
					description: 'What is in it, for the list.',
				},
				url: {
					label: 'Download link', type: 'text', value: '',
					description: 'Where the zip will be, for the library. Host it somewhere a browser ' +
						'can fetch from - a file in a GitHub repository (raw.githubusercontent.com) or ' +
						'on jsDelivr works; a release asset or a Drive link has to be downloaded by hand.',
					condition: function (result) { return result.destination === 'library'; },
				},
				homepage: {
					label: 'Home page', type: 'text', value: '',
					description: 'Optional - a repository or a page about the pack.',
				},
			},
			onConfirm: function (result) {
				this.hide();
				const fields = {
					destination: result.destination,
					name: String(result.name || info.label).trim(),
					author: String(result.author || '').trim(),
					description: String(result.description || '').trim(),
					url: String(result.url || '').trim(),
					homepage: String(result.homepage || '').trim(),
				};
				tryWritePackZip(dir, null, function (report) {
					Blockbench.openLink(submissionUrl(fields));
					if (done) {
						done(report + ' - ' + (fields.destination === 'mod'
							? 'attach the zip to the issue that opened'
							: 'host the zip at the link you gave, then send the issue'));
					}
				});
			},
		}).show();
	}

	registerPackSource({
		id: 'library',
		label: 'the Armor Pieces library',
		installLabel: 'From the library...',
		publishLabel: 'Submit...',
		install: function (dest, done) {
			libraryDialog(function (entry) { installEntry(entry, dest, done); });
		},
		publish: submitDialog,
	});

	/*
	 * Anything the platform can offer that this file cannot write for itself. A browser can hand
	 * the author a real folder to work in through an API no desktop needs, so the web build puts
	 * that here and it appears in the manager as another way in. Nothing is assumed about what
	 * arrives beyond the shape a source has, which is what lets this list grow without this
	 * function knowing it did.
	 */
	if (typeof window !== 'undefined' && window.ArmorPiecesPlatform
		&& Array.isArray(window.ArmorPiecesPlatform.packSources)) {
		window.ArmorPiecesPlatform.packSources.forEach(registerPackSource);
	}

	function defaultZipPath(dir) {
		return dir.replace(/[\\\/]+$/, '') + '.zip';
	}

	// ---- the game -------------------------------------------------------------------------------

	/*
	 * What the toolchain has of the game. The figure wears real armor, the material preview has
	 * every palette and the cloth preview composites real banner sprites only where the game's
	 * textures have been extracted - which a clone built with gradle has had done for it, and a
	 * browser has not. Without them the tools run on the numbers vanilla_assets.py baked (the
	 * ramps, the lists) and the figure wears the studio set, and everything still opens.
	 *
	 * Use my game... points vanilla_assets.py at a copy the author already owns - the launcher's
	 * jar, the .minecraft folder, or any resource pack - and what it extracts stays on this
	 * machine: in the repository's asset cache on the desktop, in the same virtual filesystem the
	 * packs live in on the web. Nothing is uploaded anywhere. It is the same tool either way.
	 */
	function gameStatus() {
		return JSON.parse(tool('vanilla_assets.py', ['--status']));
	}

	/* Everything remembered from the tools that a new set of textures would change. */
	function forgetGameCaches() {
		ramps.material = {};
		ramps.static = {};
		for (const key of Object.keys(skinRamps)) delete skinRamps[key];
		for (const key of Object.keys(skinLights)) delete skinLights[key];
		itemCache = null;
		schemaCache = null;
		tablesCache = null;
		if (typeof Project !== 'undefined' && Project) Project[ID + '_fittings'] = null;
	}

	function installGame(args) {
		let report;
		try {
			report = tool('vanilla_assets.py', args).trim();
		} catch (err) {
			console.error(err);
			Blockbench.showMessageBox({
				title: 'Could not read the game',
				message: String((err && err.stderr) || (err && err.message) || err),
			});
			return null;
		}
		forgetGameCaches();
		Blockbench.showMessageBox({
			title: 'Game assets extracted',
			message: report + '\n\nReopen the piece or skin to see the figure in vanilla armor. ' +
				'Start from now offers vanilla\'s outlines, and every material that ships a texture ' +
				'previews in its own colours.',
		});
		return report;
	}

	function takeGame(done) {
		Blockbench.import({
			title: 'Your Minecraft client jar, or a resource pack',
			extensions: ['jar', 'zip'], type: 'Minecraft jar or resource pack', readtype: 'buffer',
		}, function (files) {
			const file = files && files[0];
			if (!file) return;
			const content = file.content;
			if (content) {
				const name = String(file.name || '').toLowerCase().endsWith('.jar') ? 'game.jar' : 'game.zip';
				const scratch = path.join(tempDir(), name);
				fs.writeFileSync(scratch, content instanceof ArrayBuffer ? new Uint8Array(content) : content);
				done(scratch, true);
			} else if (file.path) {
				done(file.path, false);
			}
		});
	}

	function useGameDialog() {
		let status = null;
		try {
			status = gameStatus();
		} catch (err) {
			console.error(err);
		}
		const has = !!(status && status.game);
		const lines = [
			has
				? 'The game\'s textures are here (Minecraft ' + status.version + '): the figure wears ' +
					'vanilla armor, the material preview has ' + status.palettes.length + ' palettes' +
					(status.patterns ? ', the cloth preview has the banner patterns' : '') +
					', and a new skin can start from vanilla\'s outlines.'
				: 'The game\'s textures are not here. The figure wears the studio set - the mod\'s ' +
					'plate skin in iron, on the same boxes - the material preview runs on the ramps ' +
					'baked from the game, and a new skin starts from the plate outline.',
			'',
			'Point the editor at your own copy of the game and it extracts what it needs - the ' +
			'player skin, the armor sheets, the trim palettes and the banner patterns - onto this ' +
			'machine and nowhere else. ' + (isApp
				? 'Pick the client jar (.minecraft/versions/<version>/<version>.jar), your .minecraft ' +
					'folder, or any resource pack.'
				: 'Pick the client jar (.minecraft/versions/<version>/<version>.jar) or any resource ' +
					'pack zip. It is kept in this browser\'s storage beside your packs; nothing is uploaded.'),
		];
		const buttons = isApp
			? ['Choose a jar or zip...', 'Choose a .minecraft folder...', 'Close']
			: ['Choose a jar or zip...', 'Close'];
		Blockbench.showMessageBox({
			title: 'Use my game', message: lines.join('\n'),
			buttons: buttons, confirm: 0, cancel: buttons.length - 1,
		}, function (answer) {
			if (answer === 0) {
				takeGame(function (file, scratch) {
					installGame(['--jar', file]);
					// The jar is tens of megabytes and only the extracted few hundred kilobytes are
					// wanted; in a browser leaving it would keep it in storage.
					if (scratch) {
						try { fs.rmSync(file); } catch (err) { /* scratch */ }
					}
				});
			} else if (isApp && answer === 1) {
				const dir = Blockbench.pickDirectory({ title: 'Your .minecraft folder', startpath: minecraftDir() });
				if (dir) installGame(['--minecraft', dir]);
			}
		});
	}

	/*
	 * Zip a pack and put it where the author can get at it. Both callers - the manager's per-pack
	 * button and the Export Pack... menu entry - end here, and so does either platform: the tool
	 * writes the zip into the filesystem it has, and giveZip does whatever getting it out of that
	 * filesystem means, which on the desktop is nothing and in a browser is a download.
	 */
	function writePackZip(dir, target) {
		const name = (path.basename(dir.replace(/[\\\/]+$/, '')) || 'pack') + '.zip';
		const out = target || (isApp ? defaultZipPath(dir) : path.join(tempDir(), name));
		const report = tool('export_pack.py', [dir, out]);
		giveZip(out, name);
		return report.trim() || ('Wrote ' + out);
	}

	function tryWritePackZip(dir, target, done) {
		try {
			const report = writePackZip(dir, target);
			if (done) done(report);
		} catch (err) {
			console.error(err);
			Blockbench.showMessageBox({
				title: 'Export failed',
				message: String((err && err.stderr) || (err && err.message) || err),
			});
		}
	}

	function pieceLabel(piece) {
		const where = piece.dataPack === piece.assetPack
			? packLabel(piece.dataPack)
			: packLabel(piece.dataPack) + ' + ' + packLabel(piece.assetPack);
		const half = (fs.existsSync(piece.data) ? '' : ' [no data]') +
			(fs.existsSync(piece.geometry) ? '' : ' [no model]');
		return piece.key + '  (' + where + ')' + half;
	}

	/*
	 * Which PNG to actually edit. In this repo the file inside the pack is an INSTALLED COPY - the
	 * master in tools/decoration_masters is the source of truth, and sync_decoration_masters.py
	 * copies it in. Painting the installed copy would put the edit in the place the next sync
	 * overwrites. So a piece with a master edits the master; a piece in someone else's pack, which
	 * has no master, edits the pack file directly. Only the mod's own namespace has masters here:
	 * a user's `circlet` is their file, not a way into the mod's.
	 */
	function masterFor(piece) {
		const root = repoRoot();
		if (root && piece.namespace === 'armorpieces') {
			const master = path.join(root, 'tools', 'decoration_masters', piece.name + '.png');
			if (fs.existsSync(master)) return { file: master, isMaster: true };
		}
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
			const entries = readJsonOr(langFile(piece.assetPack, piece.namespace), {});
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
				args = ['--fittings', scratch, '--pack', piece.dataPack, '--pack', piece.assetPack];
			} else if (fs.existsSync(piece.data)) {
				args = ['--fittings', piece.data, '--pack', piece.dataPack, '--pack', piece.assetPack];
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
			return JSON.parse(tool('preview_material.py',
				['--list-fittings', piece.dataPack, '--pack', piece.assetPack]));
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
	// The mod's recipe type that loads and does nothing. A recipe is switched off by writing the
	// file with this type and everything else kept, and on again by writing the real type back.
	const DISABLED_TYPE = 'armorpieces:disabled';
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

	/* The two choices an existing recipe file was written from, and whether it is switched on, or
	 * null if there is no such file or it is not shaped the way this plugin writes it (then it is
	 * somebody's hand-made recipe and is left alone). A disabled file keeps its pattern and key, so
	 * the two items still read back; a bare disabled file - `{"type": "armorpieces:disabled"}` by
	 * hand - reads as switched off with nothing to show. */
	function readTemplateRecipe(file) {
		if (!fs.existsSync(file)) return null;
		try {
			const recipe = JSON.parse(fs.readFileSync(file, 'utf8'));
			const craftable = recipe.type !== DISABLED_TYPE;
			if (craftable && recipe.type !== 'minecraft:crafting_shaped') return null;
			if (JSON.stringify(recipe.pattern) !== JSON.stringify(RING_PATTERN)) {
				return craftable ? null : { focus: '', ring: '', craftable: false };
			}
			const focus = ingredientId(recipe.key && recipe.key.F);
			const ring = ingredientId(recipe.key && recipe.key['#']);
			if (!focus || !ring) return craftable ? null : { focus: '', ring: '', craftable: false };
			return { focus: focus, ring: ring, craftable: craftable };
		} catch (err) {
			return null;
		}
	}

	function readRecipe(piece) {
		return readTemplateRecipe(recipeFileFor(piece));
	}

	function knownItem(id) {
		if (!ITEM_ID.test(id)) return false;
		// Only vanilla ids can be checked; another mod's item is taken on trust.
		if (!id.startsWith('minecraft:')) return true;
		return !!vanillaItems()[id];
	}

	/*
	 * Write one ring-around-a-centre template recipe. Returns what was done, for the Save message.
	 * A part and a skin hand their template out the same way and differ only in what the recipe
	 * results in, so `result` is the argument and everything else here is shared.
	 */
	function writeTemplateRecipe(file, result, focus, ring, craftable) {
		focus = (focus || '').trim();
		ring = (ring || '').trim() || 'minecraft:paper';
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
		// Only the fields the two choices decide are replaced. Anything else in an existing file - a
		// group, a notification flag - is somebody's authoring and stays. Switched off, the type is
		// the disabled one and the rest is written all the same, so the choices survive until it
		// is switched back on; the game ignores every field of a disabled recipe but its type.
		const recipe = Object.assign(readJsonOr(file, {}), {
			type: craftable ? 'minecraft:crafting_shaped' : DISABLED_TYPE,
			pattern: RING_PATTERN,
			key: { '#': ring, F: focus },
			result: result,
		});
		if (!recipe.category) recipe.category = 'equipment';
		writeJson(file, recipe);
		return (craftable ? 'recipe: ' : 'recipe off, kept: ') + focus + ' in ' + ring;
	}

	function writeRecipe(piece) {
		const s = state();
		const socket = anchorsOf(piece)[0] || s.anchor;
		return writeTemplateRecipe(recipeFileFor(piece), {
			id: 'armorpieces:' + socket + '_template',
			components: { 'armorpieces:decoration': piece.key },
		}, s.recipe_focus, s.recipe_ring, s.recipe_craftable !== false);
	}

	/*
	 * The autocomplete behind the two item fields. Filled once, on first use rather than when the
	 * panel is built, because the repository - and so the game jar - is not known until then.
	 */
	const itemListFilled = {};

	function fillItemLists(which) {
		which = which || panel;
		if (!which || !which.form || itemListFilled[which.id]) return;
		const items = vanillaItems();
		const ids = Object.keys(items);
		if (!ids.length) return;
		for (const field of ['recipe_focus', 'recipe_ring']) {
			const element = which.form.form_data[field];
			const input = element && element.input;
			if (!input) continue;
			const listId = which.form.uuid + '_' + field + '_list';
			input.setAttribute('list', listId);
			let list = document.getElementById(listId);
			if (!list) {
				list = Interface.createElement('datalist', { id: listId });
				input.parentElement.append(list);
			}
			list.innerHTML = '';
			for (const id of ids) list.append(Interface.createElement('option', { value: id }, items[id]));
		}
		itemListFilled[which.id] = true;
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
		// Which set the figure wears - the game's, or the studio set where the game's textures are
		// not here. bb_rig says; the note is taken off before Blockbench sees the project.
		const figure = content.armorpieces_figure || null;
		delete content.armorpieces_figure;
		// The rig is written as `free`, which is what it is. Loading it as the plugin's own format
		// is what turns the trimmed-down workspace on; the format shares every flag with `free`.
		content.meta.model_format = ID;
		Codecs.project.load(content, { path: file, content: content });

		Project[ID + '_piece'] = piece;
		Project[ID + '_figure'] = figure;
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
			Project[ID + '_state'].recipe_craftable = recipe.craftable;
		}
		Project.name = piece.name;
		// The rig is scratch; saving it would put a rig where the piece should go. Save Piece is the
		// only correct way out, so the project is left without a save path on purpose.
		Project.save_path = '';
		Project.export_path = '';

		// Format activation ran inside load(), before the piece was attached, so it saw an ordinary
		// project. Now that this is a piece, bring the workspace up.
		Project[ID + '_saved_index'] = 0;
		enterWorkspace();
		publishStatus('open', { model: true, sheets: 'all' });
		Blockbench.showQuickMessage(piece.name + ' on ' + anchor + figureNote(figure), 2500);
		return true;
	}

	/* ' - studio figure' when the game's textures are not here, so nobody mistakes the set. */
	function figureNote(figure) {
		return figure && figure.figure === 'studio' ? ' - ' + figure.label : '';
	}

	/*
	 * Open a piece for a caller that cannot click: the bridge. A piece already open in a tab is
	 * reused rather than opened twice, rebuilt on a new anchor, and refused while it has unsaved
	 * edits unless the caller says to discard them. The close of a rebuilt tab is deferred a
	 * tick, because a bridge eval that closes the current project has no project left for the
	 * bridge's own bookkeeping to finish on.
	 */
	function openFor(key, anchor, options) {
		options = options || {};
		const existing = ModelProject.all.find(function (p) {
			return p[ID + '_piece'] && p[ID + '_piece'].key === key;
		});
		if (existing) {
			if (existing !== Project) existing.select();
			const current = state().anchor;
			const unsaved = existing.undo && existing.undo.index !== (existing[ID + '_saved_index'] || 0);
			if ((!anchor || anchor === current) && !options.reload) {
				// Switching to the tab loses nothing, so unsaved edits are reported, not refused.
				enterWorkspace();
				publishStatus('select', { model: true, sheets: 'all' });
				return { piece: key, anchor: current, reused: true, unsaved_edits: unsaved ? existing.undo.index - (existing[ID + '_saved_index'] || 0) : 0 };
			}
			if (unsaved && !options.discard) {
				throw new Error(key + ' is open with unsaved edits, and rebuilding it on ' + (anchor || current) +
					' reloads it from disk: save it first (armorpieces_save), or pass discard: true to drop them');
			}
			existing.undo.history.length = 0;
			existing.undo.index = 0;
			const piece = currentPiece();
			const carry = options.discard ? null
				: { data: partData(), dirty: existing[ID + '_dirty'], name: existing[ID + '_name'] };
			const old = Project;
			if (!openPiece(piece, anchor || current, carry)) throw new Error('could not rebuild ' + key);
			const fresh = Project;
			setTimeout(function () {
				old.close(true).then(function () { if (fresh !== Project) fresh.select(); });
			}, 50);
			return { piece: key, anchor: anchor || current, reused: false };
		}
		const piece = allPieces().find(function (p) { return p.key === key; });
		if (!piece) {
			throw new Error('no piece ' + key + '; known: ' +
				allPieces().map(function (p) { return p.key; }).join(', '));
		}
		if (!openPiece(piece, anchor)) throw new Error('could not open ' + key + ' - see the message in Blockbench');
		return { piece: key, anchor: state().anchor, reused: false };
	}

	/* Close the open piece's tab, deferred a tick for the same reason as the rebuild above. */
	function closeFor(discard) {
		if (!isWorkspace()) throw new Error('no piece is open');
		const unsaved = Project.undo.index !== (Project[ID + '_saved_index'] || 0);
		if (unsaved && !discard) throw new Error('unsaved edits: save first, or close with discard: true');
		const closing = Project;
		const key = currentPiece().key;
		setTimeout(function () { closing.close(true); }, 50);
		return { closed: key };
	}

	/*
	 * Rebuild the rig for the piece from what is on disk. Used by the anchor selector and the
	 * Rebuild button. It is a reload, not a re-pose: unsaved geometry would be lost, so it refuses
	 * while there is anything to lose.
	 */
	function reopen(anchor) {
		const piece = currentPiece();
		if (!piece) return;
		// Unsaved means edited past the last save, not "has a history": a saved piece has one too.
		const unsaved = Project.undo && Project.undo.index !== (Project[ID + '_saved_index'] || 0);
		if (unsaved) {
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
				title: 'No pieces found',
				message: 'No part in any pack: not in the folders added under Tools > Armor Pieces > ' +
					'Packs..., not in the repository\'s resources or run/, and not in the game\'s ' +
					'resourcepacks/ or worlds\' datapacks/. Add the folder your pack is in, or make one ' +
					'with New Pack....',
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
			if (shown.key) writeLang(piece.assetPack, piece.namespace, shown.key, Project[ID + '_name']);
			Project[ID + '_name'] = null;
			notes.push('name');
		}
		if (Project[ID + '_credit']) {
			writeCredit(piece.dataPack, piece.key, Project[ID + '_credit']);
			Project[ID + '_credit'] = null;
			notes.push('credits');
		}

		// Geometry: write the live project to a scratch file and let bb_geo do the conversion, so
		// the export path here is the same one the command line uses.
		const scratch = path.join(tempDir(), 'save.bbmodel');
		fs.writeFileSync(scratch, Codecs.project.compile(), 'utf8');
		tool('bb_geo.py', ['export', scratch, '--out', piece.geometry]);

		// Texture: the master is a linked file, so Blockbench writes it back where it came from.
		const texture = Project[ID + '_texture'];
		const part = tex('part');
		let report = '';
		if (part && texture) {
			// save() writes back to the linked path; save(true) is "save as" and opens a native
			// file picker, which blocks the whole app. Every sheet is a real authored file linked
			// the same way: the master, the static layer, and each fitting mask.
			for (const sheet of sheets()) sheet.save();
			if (texture.isMaster) {
				// Installing is the sync script's job, and it is also what checks the master against
				// the geometry - the check that catches paint sliding off a face it was drawn for.
				report = tool('sync_decoration_masters.py', [piece.name]).trim();
				if (report) console.log('[armorpieces] ' + report);
			}
		}

		notes.push(writeRecipe(piece));
		// The summary line reads the name from the file it was just written to.
		syncForm();
		Project[ID + '_saved_index'] = Project.undo.index;
		// A save run from inside a bridge eval sits inside that eval's undo entry, which lands
		// after this returns; the wrapper around finishEdit moves the mark past it.
		if (Project.undo.current_save) Project[ID + '_save_in_edit'] = true;
		publishStatus('save', { model: false, sheets: [] });
		Blockbench.showQuickMessage('Saved ' + piece.name + ' to ' + piece.namespace + ' - ' + notes.join(', '), 3000);
		return { piece: piece.key, wrote: notes, report: report };
	}

	// ---- new piece ----------------------------------------------------------------------------

	// One bone with one small cube, sitting on the anchor. A new piece opens as something visible
	// and movable rather than an empty group, because an empty group in Blockbench looks broken.
	function starterGeometry() {
		// Inflated by a quarter so no face of it lies on an armor shell wall, whichever socket it
		// sits on: the shells are at whole and half units from the body, the socket offsets too.
		return {
			texture_width: 64,
			texture_height: 32,
			bones: [{
				name: 'main',
				pivot: [0, 0, 0],
				cubes: [{ origin: [-2, -2, -1], size: [4, 2, 2], uv: [0, 0], inflate: 0.25 }],
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

	/* The pack folders as a select's options, labelled the way the piece list labels them. */
	function packOptions(packs) {
		const options = {};
		packs.forEach(function (p, i) { options[i] = packLabel(p); });
		return options;
	}

	/*
	 * A new piece asks for two packs, the datapack for the part file and the resource pack for
	 * its model, texture and name, and they default to the same folder: in this repository and in
	 * a world used for both they are one folder, and a player making content for the launcher
	 * picks a world's datapack and a resource pack. A namespace other than the mod's is the
	 * default outside the repository, since the mod's namespace is the mod's.
	 */
	function newPiece() {
		const packs = searchRoots();
		if (!packs.length) {
			Blockbench.showMessageBox({
				title: 'No packs',
				message: 'No pack folder to put the piece in. Make one with Tools > Armor Pieces > ' +
					'New Pack..., or add an existing folder under Packs....',
			});
			return;
		}
		const root = repoRoot();
		const inRepo = root && packs[0].startsWith(root);
		const anchorOptions = {};
		for (const name of Object.keys(anchors())) {
			anchorOptions[name] = name + '  (' + anchors()[name].part + ')';
		}

		new Dialog({
			id: ID + '_new',
			title: 'New Armor Piece',
			form: {
				name: { label: 'Name', type: 'text', value: '', placeholder: 'gorget' },
				namespace: { label: 'Namespace', type: 'text', value: inRepo ? 'armorpieces' : 'mypack' },
				anchor: { label: 'Anchor', type: 'select', options: anchorOptions },
				data_pack: {
					label: 'Datapack', type: 'select', options: packOptions(packs), value: defaultPack(packs),
					description: 'Where the part file, its recipe and any fittings go.',
				},
				asset_pack: {
					label: 'Resource pack', type: 'select', options: packOptions(packs), value: defaultPack(packs),
					description: 'Where the model, the textures and the language file go. The same folder is fine.',
				},
			},
			onConfirm: function (result) {
				const name = (result.name || '').trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
				if (!name) {
					Blockbench.showQuickMessage('Name a piece first', 2000);
					return;
				}
				this.hide();

				const dataPack = packs[parseInt(result.data_pack, 10)];
				const assetPack = packs[parseInt(result.asset_pack, 10)];
				const namespace = (result.namespace || '').trim().toLowerCase().replace(/[^a-z0-9_.-]/g, '_') || 'mypack';
				let piece;
				try {
					piece = createPiece(dataPack, assetPack, namespace, name, result.anchor);
				} catch (err) {
					Blockbench.showMessageBox({ title: 'Already exists', message: err.message });
					return;
				}
				Blockbench.showQuickMessage('Created ' + namespace + ':' + name, 2500);
				openPiece(piece, result.anchor);
			},
		}).show();
	}

	/*
	 * The files a new piece starts from, written and nothing else: the dialog above and the
	 * bridge's armorpieces_new both end up here. Throws when the piece is already in the pack.
	 */
	function createPiece(dataPack, assetPack, namespace, name, anchor) {
		const piece = pieceRecord(dataPack, assetPack, namespace, name);
		if (fs.existsSync(piece.data) || fs.existsSync(piece.geometry)) {
			throw new Error(namespace + ':' + name + ' is already in that pack.');
		}
		if (!anchors()[anchor]) {
			throw new Error('unknown anchor ' + anchor + '; one of ' + Object.keys(anchors()).join(', '));
		}

		writeJson(piece.data, {
			asset_id: namespace + ':' + name,
			description: { translate: 'decoration.' + namespace + '.' + name },
			anchors: [anchor],
		});
		writeJson(piece.geometry, starterGeometry());

		// A blank master, so the piece has a texture to paint rather than sampling nothing. For
		// the mod's own parts the master lives in tools/decoration_masters and Save installs it
		// into the resources, so the blank goes there as well - otherwise the first Save would
		// find no master and skip the install and its checks.
		const blank = Buffer.from(blankPng(64, 32).split(',')[1], 'base64');
		fs.mkdirSync(path.dirname(piece.texture), { recursive: true });
		fs.writeFileSync(piece.texture, blank);
		const root = repoRoot();
		if (namespace === 'armorpieces' && root && assetPack.startsWith(root)) {
			const master = path.join(root, 'tools', 'decoration_masters', name + '.png');
			if (!fs.existsSync(master)) fs.writeFileSync(master, blank);
		}

		// The name a player reads, so the piece is not "decoration.ns.name" in a tooltip.
		// In the resource pack: the language file is assets, wherever the data file went.
		const key = 'decoration.' + namespace + '.' + name;
		if (!readJsonOr(langFile(assetPack, namespace), {})[key]) {
			writeLang(assetPack, namespace, key, titleCase(name));
		}
		return piece;
	}

	// ---- packs: the author's own folders ------------------------------------------------------

	/*
	 * The pack formats the game this mod is built for expects, read out of gradle.properties so a
	 * Minecraft bump stays one block in one file. The numbers under them are a last resort for a
	 * repository without the lines.
	 */
	function packFormats() {
		const formats = { resourcepack: 88, datapack: 107 };
		const root = repoRoot();
		if (!root) return formats;
		try {
			const text = fs.readFileSync(path.join(root, 'gradle.properties'), 'utf8');
			const resource = /^resourcepack_format\s*=\s*(\d+)/m.exec(text);
			const data = /^datapack_format\s*=\s*(\d+)/m.exec(text);
			if (resource) formats.resourcepack = parseInt(resource[1], 10);
			if (data) formats.datapack = parseInt(data[1], 10);
		} catch (err) {
			console.error(err);
		}
		return formats;
	}

	const PACKS_DIALOG_TEMPLATE = [
		'<div class="armorpieces_packs">',
		'	<p class="ap_dim">Every folder parts are read from and written to. The repository\'s own',
		'	and the game\'s are found; the rest are yours to add and forget.',
		'	<template v-if="scope">The piece list shows <b>{{ scopeLabel }}</b> alone -',
		'		<a href="#" @click.prevent="workIn(null)">show every pack</a>.</template>',
		'	<template v-else>The piece list shows every pack at once, first found winning by name;',
		'		<b>Work here</b> narrows it to one.</template></p>',
		'	<ul>',
		'		<li v-for="pack in packs" :key="pack.dir" :class="{ ap_scoped: pack.dir === scope }">',
		'			<div class="ap_head">',
		'				<span class="ap_name" :title="pack.dir">{{ pack.label }}</span>',
		'				<span class="ap_tag ap_here" v-if="pack.dir === scope">working here</span>',
		'				<span class="ap_tag">{{ pack.kind }}</span>',
		'				<span class="ap_tag" v-if="pack.format">format {{ pack.format }}</span>',
		'				<span class="ap_tag" :title="\'From armorpieces-credits.json; All rights reserved without one\'">{{ pack.license }}</span>',
		'				<span class="ap_tag ap_warn" v-else>no pack.mcmeta</span>',
		'			</div>',
		'			<div class="ap_body"><span class="ap_dim">{{ pack.summary }}</span></div>',
		'			<div class="ap_ops">',
		'				<button type="button" v-if="pack.dir !== scope" @click="workIn(pack)">Work here</button>',
		'				<button type="button" v-else @click="workIn(null)">Show all packs</button>',
		'				<button type="button" v-for="s in installers" :key="s.id"',
		'					@click="install(pack, s)">{{ s.installLabel }}</button>',
		'				<button type="button" v-for="s in publishers" :key="s.id"',
		'					@click="publish(pack, s)">{{ s.publishLabel }}</button>',
		'				<span class="ap_spacer"></span>',
		'				<button type="button" v-if="pack.mine" @click="forget(pack)">Forget</button>',
		'				<button type="button" v-else-if="pack.deletable" @click="remove(pack)">Delete</button>',
		'			</div>',
		'		</li>',
		'		<li v-if="!packs.length" class="ap_dim">No packs anywhere. Make one below.</li>',
		'	</ul>',
		'	<div class="ap_add">',
		'		<button type="button" @click="create">New Pack...</button>',
		'		<button type="button" v-if="canBrowse" @click="add">Add folder...</button>',
		'		<button type="button" v-for="s in installers" :key="s.id"',
		'			@click="installNew(s)">New pack from {{ s.label }}...</button>',
		'	</div>',
		'</div>',
	].join('\n');

	const PACKS_DIALOG_CSS = [
		'.armorpieces_packs ul { list-style: none; margin: 6px 0; padding: 0; max-height: 320px; overflow-y: auto; }',
		'.armorpieces_packs li { padding: 6px 8px; margin-bottom: 4px; background: var(--color-back); border-radius: 4px; }',
		'.armorpieces_packs .ap_head { display: flex; align-items: center; gap: 6px; min-width: 0; }',
		'.armorpieces_packs .ap_name { flex: 0 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--color-light); }',
		'.armorpieces_packs .ap_tag { flex: none; font-size: 0.78em; padding: 1px 6px; border-radius: 3px; background: var(--color-ui); color: var(--color-subtle_text); }',
		'.armorpieces_packs .ap_tag.ap_warn { color: var(--color-close); }',
		'.armorpieces_packs .ap_tag.ap_here { background: var(--color-accent); color: var(--color-light); }',
		'.armorpieces_packs li.ap_scoped { outline: 1px solid var(--color-accent); }',
		'.armorpieces_packs a { color: var(--color-accent); }',
		'.armorpieces_packs .ap_body { display: flex; align-items: center; gap: 6px; margin-top: 4px; }',
		'.armorpieces_packs .ap_ops { display: flex; align-items: center; gap: 6px; margin-top: 6px; flex-wrap: wrap; }',
		'.armorpieces_packs .ap_spacer { flex: 1; }',
		'.armorpieces_packs .ap_body button, .armorpieces_packs .ap_ops button { flex: none; }',
		'.armorpieces_packs .ap_add { display: flex; gap: 6px; flex-wrap: wrap; }',
		'.armorpieces_packs .ap_dim { color: var(--color-subtle_text); font-size: 0.9em; margin: 4px 0; }',
	].join('\n');

	// The library dialog is the manager's list with a search box over it, and shares its look.
	const LIBRARY_DIALOG_CSS = PACKS_DIALOG_CSS.replace(/\.armorpieces_packs/g, '.armorpieces_library') + '\n' +
		'.armorpieces_library .ap_add { align-items: center; }\n' +
		'.armorpieces_library input[type=search] { flex: 1; min-width: 10rem; }\n' +
		'.armorpieces_library a { color: var(--color-accent); }';

	/*
	 * Packs...: the pack manager. Every root discovery already looks in, said out loud - what kind
	 * of pack it is, whether the game will load it, how much of a piece each half has - with the
	 * operations that used to be scattered across three menu entries attached to the pack they act
	 * on. Installing and publishing are asked of the sources rather than hard-coded, so the
	 * library 0.4.0 adds appears here as more buttons and no new dialog.
	 */
	function packsDialog() {
		new Dialog({
			id: ID + '_packs',
			title: 'Armor Pieces Packs',
			width: 640,
			singleButton: true,
			component: {
				data: function () {
					return {
						packs: [],
						scope: packScope(),
						canBrowse: canBrowseFolders(),
						installers: packSources.filter(function (s) { return !!s.install; }),
						publishers: packSources.filter(function (s) { return !!s.publish; }),
					};
				},
				computed: {
					scopeLabel: function () { return this.scope ? packLabel(this.scope) : ''; },
				},
				mounted: function () { this.refresh(); },
				methods: {
					workIn: function (pack) {
						setPackScope(pack ? pack.dir : '');
						this.scope = packScope();
						Blockbench.showQuickMessage(this.scope
							? 'Working in ' + packLabel(this.scope) : 'Showing every pack', 2500);
					},
					refresh: function () {
						this.scope = packScope();
						this.packs = searchRoots().map(function (dir) {
							const info = packInfo(dir);
							info.kind = packKind(info);
							info.summary = info.parts
								? info.parts + (info.parts === 1 ? ' piece' : ' pieces') +
									' - ' + info.data + ' with a part file, ' + info.assets + ' with a model'
								: 'no pieces yet';
							return info;
						});
					},
					forget: function (pack) {
						setUserPacks(userPacks().filter(function (dir) { return dir !== pack.dir; }));
						this.refresh();
					},
					/*
					 * The only destructive thing in this dialog, so it says what it is about to
					 * lose and counts it. Offered only where forgetting would not work - a pack
					 * found by where it sits rather than by being listed - because otherwise the
					 * author would have two buttons for one intention and one of them would be
					 * the one that cannot be undone.
					 */
					remove: function (pack) {
						const vue = this;
						Blockbench.showMessageBox({
							title: 'Delete this pack?',
							message: pack.label + ' holds ' + pack.summary + '. Deleting it cannot be ' +
								'undone - export it first if you want to keep a copy.',
							buttons: ['Delete', 'Cancel'],
							confirm: 1, cancel: 1,
						}, function (answer) {
							if (answer !== 0) return;
							try {
								fs.rmSync(pack.dir, { recursive: true, force: true });
								setUserPacks(userPacks().filter(function (dir) { return dir !== pack.dir; }));
								Blockbench.showQuickMessage('Deleted ' + pack.label, 3000);
							} catch (err) {
								console.error(err);
								Blockbench.showMessageBox({
									title: 'Could not delete',
									message: String((err && err.message) || err),
								});
							}
							vue.refresh();
						});
					},
					add: function () {
						const vue = this;
						browseForPack(function (dir) {
							const list = userPacks();
							if (list.indexOf(dir) === -1) list.push(dir);
							setUserPacks(list);
							vue.refresh();
						});
					},
					create: function () {
						const vue = this;
						newPack(function () { vue.refresh(); });
					},
					install: function (pack, source) {
						const vue = this;
						source.install(pack.dir, function (report) {
							vue.refresh();
							Blockbench.showQuickMessage(report, 3000);
						});
					},
					/* Install into a folder that does not exist yet, which is how somebody else's
					 * pack arrives without being merged into one of yours. */
					installNew: function (source) {
						const vue = this;
						newPack(function (dir) {
							source.install(dir, function (report) {
								vue.refresh();
								Blockbench.showQuickMessage(report, 3000);
							});
						}, { title: 'New Pack from ' + source.label, mcmeta: false });
					},
					publish: function (pack, source) {
						source.publish(pack.dir, function (report) {
							Blockbench.showQuickMessage(report, 3000);
						});
					},
				},
				template: PACKS_DIALOG_TEMPLATE,
			},
		}).show();
	}

	/*
	 * New Pack...: a folder with a pack.mcmeta for one half - a datapack or a resource pack - at
	 * the format the game this mod is built for wants, so the author never has to know the
	 * numbers. Added to the author's list, so the next New Armor Piece can pick it.
	 */
	function newPack(done, options) {
		options = options || {};
		// A pack about to be filled from a zip brings its own pack.mcmeta, so asking what kind it
		// is and what it says would be asking the author to guess at somebody else's file.
		const wantMeta = options.mcmeta !== false;
		const formats = packFormats();
		const form = {
			name: { label: 'Folder name', type: 'text', value: '', placeholder: 'My Armor Pieces' },
		};
		if (wantMeta) {
			form.kind = {
				label: 'Kind', type: 'select', value: 'datapack',
				options: {
					datapack: 'Datapack  (parts, recipes, fittings; goes in a world\'s datapacks/)',
					resourcepack: 'Resource pack  (models, textures, names; goes in resourcepacks/)',
				},
			};
		}
		// Where to put it is a question only the desktop can answer: a browser has one place packs
		// can live, and a folder picker that does not exist there would be a dead field.
		if (isApp) {
			form.where = {
				label: 'Put it in', type: 'folder', value: packHome(),
				description: 'The folder the pack folder is created in. The game reads resource packs ' +
					'from .minecraft/resourcepacks and datapacks from .minecraft/saves/<world>/datapacks.',
			};
		}
		if (wantMeta) form.description = { label: 'Description', type: 'text', value: 'Armor Pieces parts' };
		new Dialog({
			id: ID + '_new_pack',
			title: options.title || 'New Pack',
			form: form,
			onConfirm: function (result) {
				const name = (result.name || '').trim();
				const where = isApp ? (result.where || '').trim() : packHome();
				if (!name || !where) {
					Blockbench.showQuickMessage(isApp ? 'Name the pack and say where it goes'
						: 'Name the pack', 2500);
					return false;
				}
				const dir = path.join(where, name);
				if (fs.existsSync(path.join(dir, 'pack.mcmeta'))) {
					Blockbench.showMessageBox({ title: 'Already a pack', message: dir + ' already has a pack.mcmeta.' });
					return false;
				}
				if (wantMeta) {
					const format = result.kind === 'resourcepack' ? formats.resourcepack : formats.datapack;
					writeJson(path.join(dir, 'pack.mcmeta'), {
						pack: { description: result.description || name, pack_format: format },
					});
					fs.mkdirSync(path.join(dir, result.kind === 'resourcepack' ? 'assets' : 'data'), { recursive: true });
				} else {
					fs.mkdirSync(dir, { recursive: true });
				}
				const list = userPacks();
				if (!list.includes(dir)) list.push(dir);
				setUserPacks(list);
				this.hide();
				if (wantMeta) Blockbench.showQuickMessage('Created ' + dir, 3000);
				if (done) done(dir);
			},
		}).show();
	}

	/*
	 * Export Pack...: a pack folder zipped for handing round, the way the build zips the mod's
	 * own halves. The zip is written by export_pack.py beside the folder, so what is in it is what
	 * the command line would make.
	 */
	function exportPack() {
		const packs = searchRoots();
		if (!packs.length) {
			Blockbench.showMessageBox({ title: 'No packs', message: 'Nothing to export. Add or make a pack first.' });
			return;
		}
		const form = { pack: { label: 'Pack', type: 'select', options: packOptions(packs), value: defaultPack(packs) } };
		if (isApp) {
			form.zip = {
				label: 'Zip file', type: 'save', extensions: ['zip'], filetype: 'Pack zip',
				value: path.join(packHome(), 'pack.zip'),
				description: 'Blank writes <pack folder>.zip beside the folder.',
			};
		}
		new Dialog({
			id: ID + '_export_pack',
			title: 'Export Pack',
			form: form,
			onConfirm: function (result) {
				const dir = packs[parseInt(result.pack, 10)];
				this.hide();
				tryWritePackZip(dir, isApp ? (result.zip || '').trim() : null, function (report) {
					Blockbench.showQuickMessage(report, 3000);
				});
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
			Blockbench.showQuickMessage((texture.id === 'part' ? 'Master' : texture.id)
				+ ' is greyscale - colour folded to value', 1500);
		} finally {
			greyscaleGuard = false;
		}
	}

	function onEditTexture(data) {
		if (!data || !data.texture) return;
		if (isSkinWorkspace()) return onSkinEditTexture(data);
		if (!isWorkspace()) return;
		const id = data.texture.id;
		if (!isSheetId(id)) return;
		if (isGreyId(id) && foldsMaster() && data.canvas) foldCanvasToGreyscale(data.canvas);
		refreshPreview(false);
	}

	/* Which cubes exist as an edit begins, on its undo record, for the layout to tell new from old. */
	function onInitEdit(data) {
		if (!isWorkspace() || !data || !data.save) return;
		data.save[ID + '_cubes'] = new Set(Cube.all.map(function (c) { return c.uuid; }));
	}

	function onFinishEdit(data) {
		if (isSkinWorkspace()) return onSkinFinishEdit(data);
		if (!isWorkspace()) return;
		const aspects = (data && data.aspects) || {};
		const textures = aspects.textures || [];
		let touched = false;
		for (const texture of textures) {
			if (isGreyId(texture.id) && foldsMaster()) enforceGreyscale(texture);
			if (isSheetId(texture.id)) touched = true;
		}
		if (touched) refreshPreview(true);
		// The edit is applied and laid out by now, so this is the moment the bridge's checker
		// wants: the model when the outliner changed, the sheets the edit painted.
		const model = !!(aspects.elements || aspects.outliner || aspects.group || aspects.groups || aspects.uv_mode);
		if (model || touched) publishStatus(data && data.message || 'edit', { model: model, sheets: textures });
	}

	/*
	 * Undo puts a texture back by reloading its image, which lands a moment later. Recomposite
	 * now for the common case and once more after the reload has had time to draw.
	 */
	function onUndoRedo() {
		if (isSkinWorkspace()) {
			publishSkin('undo');
			setTimeout(function () { refreshSkinPreview(); publishSkin('undo'); }, 200);
			return;
		}
		if (!isWorkspace()) return;
		syncSheetSize();
		refreshPreview(true);
		publishStatus('undo', { model: true, sheets: 'all' });
		setTimeout(function () {
			refreshPreview(true);
			publishStatus('undo', { model: false, sheets: 'all' });
		}, 200);
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
	 *
	 * A skin gets a palette of its own, because a skin has an ALPHABET: it is written in `0`-`f`,
	 * sixteen levels seventeen apart, and the ASCII painter and check_skin.py both read a texel
	 * back as one of those characters. So the swatches are those sixteen exactly, and a colour
	 * picked off the palette is a character an agent could have written. A part's master has no
	 * such alphabet - it bakes through a 256-entry ramp - and the nine stops below are stops on it.
	 */
	const GREYS = [0, 32, 64, 96, 127, 160, 192, 224, 255].map(function (v) { return hex(v, v, v); });
	const SKIN_GREYS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
		.map(function (level) { return hex(level * 17, level * 17, level * 17); });
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

	/* The palette this project wants, or null for the author's own. */
	function wantedPalette() {
		if (isSkinWorkspace()) return SKIN_GREYS;
		if (isWorkspace() && state().edit !== 'static') return GREYS;
		return null;
	}

	/* Either of the two the plugin puts in. Neither is anything an author would have chosen, and
	   the check has to cover both, or switching from a piece to a skin stashes the piece's greys
	   as if they were the author's and hands them back on the way out. */
	function isPluginPalette(list) {
		const joined = list.join();
		return joined === GREYS.join() || joined === SKIN_GREYS.join();
	}

	function restorePalette() {
		if (!ColorPanel.palette) return;
		const saved = userPalette || stashedPalette();
		userPalette = null;
		stashPalette(null);
		if (saved && isPluginPalette(ColorPanel.palette)) ColorPanel.palette.replace(saved);
	}

	function applyPalette() {
		if (!ColorPanel.palette) return;
		const wanted = wantedPalette();
		if (!wanted) {
			restorePalette();
			return;
		}
		if (userPalette === null && !isPluginPalette(ColorPanel.palette)) {
			userPalette = ColorPanel.palette.slice();
			stashPalette(userPalette);
		}
		if (ColorPanel.palette.join() !== wanted.join()) ColorPanel.palette.replace(wanted);
		const current = ColorPanel.get();
		// Mid grey: 0x7f on a part's continuous ramp, 0x88 on a skin, which is level `8` exactly.
		if (typeof current === 'string' && !/^#(..)\1\1$/i.test(current)) {
			ColorPanel.set(isSkinWorkspace() ? '#888888' : '#7f7f7f');
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
	 * A skin's figure has the same two switches and four more. The armor is the SUBJECT here rather
	 * than the reference, so its four shells come off one at a time: a boot drawn over the leggings
	 * and a helmet that swallows the face are the two mistakes a skin author cannot see any other
	 * way, and taking the shell above off is how you look. The armor cubes are unlocked in this rig
	 * - they are what is being painted - so the slot is read off the name alone.
	 */
	function applySkinVisibility() {
		if (!isSkinWorkspace()) return;
		const s = skinState();
		for (const cube of Cube.all) {
			const slot = ARMOR_NAME.exec(cube.name);
			cube.visibility = slot ? s['show_' + slot[1]] !== false : !!s.show_player;
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

	/* The same rule serves a skin, where what is unlocked is the four armor shells rather than a
	   part: show what is being worked on, and the chain of locked groups that has to stay above it. */
	const outlinerRule = {
		id: ID + '_part_only',
		test: function (node) {
			const on = isSkinWorkspace() ? skinState().armor_only
				: (isWorkspace() && state().part_only);
			if (!on) return true;
			if (!node.locked) return true;
			return node instanceof Group && hasUnlocked(node);
		},
	};

	/* The painting grid is drawn on every visible cube. The reference is not being painted. */
	function onPaintingGrid(data) {
		const element = data && data.element;
		if (!element || (!isWorkspace() && !isSkinWorkspace()) || !element.locked) return;
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
		// The cubes that existed when the edit began, stashed by the init_edit hook: a cube not in
		// it was created by this edit, whether or not the edit listed it - the MCP bridge's
		// place_cube lists nothing, and its cube would otherwise land on another's net.
		const existed = save[ID + '_cubes'];
		const placing = [];
		for (const cube of Cube.all) {
			if (cube.locked) continue;
			const born = existed && !existed.has(cube.uuid);
			// A cube with hand-placed faces cannot be authored in this format, so it is converted
			// whichever edit finds it; a box-UV cube is only reconsidered when the edit touched
			// or created it.
			if (cube.box_uv && !touched.has(cube) && !born) continue;
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

	// The message the Blockbench MCP plugin's risky_eval finishes its wrapper entry with.
	const BRIDGE_EVAL = 'Agent executed code';

	/*
	 * Whether an undo record's before-state is the state now. The snapshot holds plain data
	 * (element copies, the outliner tree, texture copies) plus a reference to the live aspects
	 * object, which is dropped before comparing.
	 */
	function unchangedSince(before, aspects) {
		const strip = function (save) {
			const copy = Object.assign({}, save);
			delete copy.aspects;
			// The plugin's own bookkeeping on the record (the cube set from init_edit) is not state.
			for (const key of Object.keys(copy)) if (key.indexOf(ID + '_') === 0) delete copy[key];
			return JSON.stringify(copy);
		};
		try {
			return strip(new UndoSystem.save(aspects)) === strip(before);
		} catch (err) {
			return false;
		}
	}

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

	// ---- painting by face ---------------------------------------------------------------------

	/*
	 * The bridge's painter: whole faces at a time, addressed by name, on one sheet, in one undo
	 * step. Both authoring sessions painted this way through a general shape tool - one rectangle
	 * per face or per row, from the face rectangles the check prints - so this does the
	 * arithmetic instead. A face is `<cube>.<face>`, the cube by its name or by the check's
	 * `bone[i]` label, `*` for every part cube or every face; a value is a grey, a hex colour, a
	 * [top, bottom] pair shaded row by row, or null to clear. On a greyscale sheet a colour is
	 * folded to its luminance, the same rule the brush follows.
	 */
	const FACE_NAMES = ['north', 'south', 'east', 'west', 'up', 'down'];

	function partCubes() {
		return Cube.all.filter(function (c) { return !c.locked; });
	}

	/* bone[i], the way check_part names a cube: its bone and its index among the bone's cubes. */
	function cubeLabel(cube) {
		const parent = cube.parent;
		if (!parent || parent === 'root' || !parent.children) return null;
		const index = parent.children.filter(function (ch) { return ch instanceof Cube; }).indexOf(cube);
		return parent.name + '[' + index + ']';
	}

	function resolveFaces(address) {
		const dot = address.lastIndexOf('.');
		if (dot < 0) throw new Error('face address "' + address + '" wants cube.face, e.g. plate.up, base[0].*, *.down');
		const cubePattern = address.slice(0, dot);
		const facePattern = address.slice(dot + 1);
		const faces = facePattern === '*' ? FACE_NAMES : [facePattern];
		if (!faces.every(function (f) { return FACE_NAMES.includes(f); })) {
			throw new Error('unknown face "' + facePattern + '"; one of ' + FACE_NAMES.join(', ') + ', or *');
		}
		const cubes = partCubes().filter(function (c) {
			return cubePattern === '*' || c.name === cubePattern || cubeLabel(c) === cubePattern;
		});
		if (!cubes.length) {
			throw new Error('no part cube "' + cubePattern + '"; the part has ' + partCubes().map(function (c) {
				return c.name + ' (' + cubeLabel(c) + ')';
			}).join(', '));
		}
		const out = [];
		for (const cube of cubes) for (const face of faces) out.push({ cube: cube, face: face });
		return out;
	}

	/* One colour: a grey 0-255, or #rrggbb, folded to grey on a greyscale sheet; null clears. */
	function parseColour(value, grey) {
		if (value === null) return null;
		if (typeof value === 'number' && isFinite(value)) {
			const v = Math.max(0, Math.min(255, Math.round(value)));
			return [v, v, v];
		}
		if (typeof value === 'string') {
			const m = /^#?([0-9a-f]{6})$/i.exec(value.trim());
			if (!m) throw new Error('bad colour "' + value + '": a grey 0-255 or #rrggbb');
			const rgb = [0, 2, 4].map(function (i) { return parseInt(m[1].slice(i, i + 2), 16); });
			if (grey && !(rgb[0] === rgb[1] && rgb[1] === rgb[2])) {
				const l = Math.round(0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]);
				return [l, l, l];
			}
			return rgb;
		}
		throw new Error('a value is a grey 0-255, a #rrggbb colour, a [top, bottom] pair, or null to clear');
	}

	/* A face value as [top, bottom] colours; a single value shades the face flat. */
	function parseValue(value, grey) {
		if (Array.isArray(value)) {
			if (value.length !== 2) throw new Error('a shaded value is a [top, bottom] pair');
			return [parseColour(value[0], grey), parseColour(value[1], grey)];
		}
		const one = parseColour(value, grey);
		return [one, one];
	}

	function paintFaces(sheetId, faces, pixels) {
		if (!isWorkspace()) throw new Error('no piece is open');
		const sheet = tex(sheetId || 'part');
		if (!sheet) {
			throw new Error('no sheet "' + sheetId + '"; the piece has ' + sheets().map(function (s) { return s.id; }).join(', ') +
				' (armorpieces_set_part creates the masks its fittings need, and the static layer)');
		}
		const grey = isGreyId(sheet.id);
		const jobs = [];
		for (const address of Object.keys(faces || {})) {
			const value = parseValue(faces[address], grey);
			for (const target of resolveFaces(address)) jobs.push({ target: target, value: value });
		}
		const dots = (pixels || []).map(function (p) {
			if (typeof p.x !== 'number' || typeof p.y !== 'number') throw new Error('a pixel is {x, y, value}');
			return { x: Math.floor(p.x), y: Math.floor(p.y), colour: parseColour(p.value === undefined ? null : p.value, grey) };
		});
		if (!jobs.length && !dots.length) throw new Error('nothing to paint: give faces, pixels, or both');

		const painted = [];
		Undo.initEdit({ textures: [sheet], bitmap: true });
		sheet.edit(function (canvas) {
			const ctx = canvas.getContext('2d');
			const fill = function (x, y, w, h, colour) {
				ctx.clearRect(x, y, w, h);
				if (!colour) return;
				ctx.fillStyle = 'rgb(' + colour.join(',') + ')';
				ctx.fillRect(x, y, w, h);
			};
			for (const job of jobs) {
				const cube = job.target.cube;
				const rect = faceRects(net(cube), cube.uv_offset || [0, 0])[job.target.face];
				const x = rect[0], y = rect[1], w = rect[2], h = rect[3];
				if (w <= 0 || h <= 0) continue;
				const top = job.value[0], bottom = job.value[1];
				if (!top || !bottom || h === 1 || (top[0] === bottom[0] && top[1] === bottom[1] && top[2] === bottom[2])) {
					fill(x, y, w, h, top);
				} else {
					for (let r = 0; r < h; r++) {
						const t = r / (h - 1);
						fill(x, y + r, w, 1, top.map(function (v, i) { return Math.round(v + (bottom[i] - v) * t); }));
					}
				}
				painted.push(cube.name + '.' + job.target.face + ' at ' + x + ',' + y + ' ' + w + 'x' + h);
			}
			for (const dot of dots) fill(dot.x, dot.y, 1, 1, dot.colour);
		}, { no_undo: true });
		Undo.finishEdit('Paint faces');
		return { sheet: sheet.id, faces: painted, pixels: dots.length };
	}

	// ---- pose ---------------------------------------------------------------------------------

	/*
	 * The walk and sprint cycles baked into the rig are shown without leaving edit or paint mode:
	 * mark one animation as playing, set the time, and ask the animator to display that frame.
	 * Blockbench resets the pose whenever it rebuilds bones or switches mode, so the same call is
	 * repeated from those hooks. In animate mode the timeline owns the pose and this stays out.
	 */
	function applyPose() {
		if ((!isWorkspace() && !isSkinWorkspace()) || Animator.open) return;
		const s = isSkinWorkspace() ? skinState() : state();
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
	let tablesCache = null;

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

	/* Every loot table a part could name, out of the game jar, chests first. */
	function lootTables() {
		if (!tablesCache) {
			try {
				tablesCache = JSON.parse(tool('vanilla_assets.py', ['--list-loot-tables']));
			} catch (err) {
				console.error(err);
				tablesCache = [];
			}
		}
		return tablesCache;
	}

	/* A row of the Loot group, from a data-file entry or blank. Chance starts low on purpose: a
	 * row with chance 1 puts the part in every chest of that table. */
	function lootRow(entry) {
		entry = entry || {};
		return {
			table: typeof entry.table === 'string' ? entry.table : '',
			weight: Number.isInteger(entry.weight) ? entry.weight : 1,
			chance: typeof entry.chance === 'number' ? entry.chance : 0.1,
		};
	}

	/* The data-file entry for a row: the three keys in the order check_authoring.py expects. */
	function lootFromRow(row) {
		return { table: row.table.trim(), weight: Number(row.weight), chance: Number(row.chance) };
	}

	function lootProblem(row) {
		const table = (row.table || '').trim();
		if (!/^[a-z0-9_.-]+:[a-z0-9_.\/-]+$/.test(table)) return 'A loot table id looks like minecraft:chests/ancient_city';
		const weight = Number(row.weight);
		if (!Number.isInteger(weight) || weight < 1) return 'A loot weight is a whole number, 1 or more';
		const chance = Number(row.chance);
		if (!(chance >= 0 && chance <= 1)) return 'A loot chance is between 0 and 1';
		return null;
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
		const loot = (data.loot || []).map(function (l) { return String(l.table || '').replace(/^minecraft:/, ''); });
		const name = Project[ID + '_name'] || displayName(piece, data).text;
		return name + '  ·  ' + anchorsOf(piece).join(', ')
			+ '  ·  ' + (fittings.length ? 'fittings: ' + fittings.join(', ') : 'no fittings')
			+ (effects.length ? '  ·  effects: ' + effects.join(', ') : '')
			+ (loot.length ? '  ·  found in: ' + loot.join(', ') : '')
			+ (state().recipe_craftable === false ? '  ·  not craftable' : '');
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
		'		<label class="name_space_left">Loot</label>',
		'		<div class="ap_column">',
		'			<div class="ap_loot" v-for="(l, i) in loot" :key="i">',
		'				<input type="text" class="dark_bordered ap_loot_table" v-model="l.table" list="armorpieces_loot_tables"',
		'					placeholder="minecraft:chests/ancient_city" title="The loot table the part is added to">',
		'				<label title="Splits the roll between the parts that share this table">w</label>',
		'				<input type="number" class="dark_bordered ap_loot_num" min="1" step="1" v-model.number="l.weight">',
		'				<label title="How often the part is offered at all; 1 is every chest">chance</label>',
		'				<input type="number" class="dark_bordered ap_loot_num" min="0" max="1" step="0.01" v-model.number="l.chance">',
		'				<i class="material-icons" title="Remove" @click="removeLoot(i)">clear</i>',
		'			</div>',
		'			<button type="button" @click="addLoot">Add a loot table...</button>',
		'			<datalist id="armorpieces_loot_tables">',
		'				<option v-for="t in tables" :key="t" :value="t"></option>',
		'			</datalist>',
		'			<p class="ap_dim">Where the part\'s template is found. The mod adds one roll per table, so a chest ',
		'			never holds two parts; the chance is the part\'s own, the weight only matters against ',
		'			other parts naming the same table.</p>',
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
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Credits</label>',
		'		<div class="ap_column">',
		'			<input type="text" class="dark_bordered" v-model="author" placeholder="author" title="Who made this piece">',
		'			<select class="dark_bordered" v-model="license" title="What others may do with it">',
		'				<option v-for="(label, id) in licenses" :key="id" :value="id">{{ label }}</option>',
		'			</select>',
		'			<p class="ap_dim">Written to armorpieces-credits.json in the pack, beside the pieces. A pack ',
		'			library and a composer read it; the game does not. All rights reserved keeps the piece ',
		'			yours - it is listed and downloaded as your pack and never copied into another.</p>',
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
		'.armorpieces_part .ap_loot { display: flex; align-items: center; gap: 6px; margin-bottom: 3px; }',
		'.armorpieces_part .ap_loot > label { width: auto; padding: 0; color: var(--color-subtle_text); }',
		'.armorpieces_part .ap_loot .ap_loot_table { flex: 1; min-width: 0; }',
		'.armorpieces_part .ap_loot .ap_loot_num { width: 64px; }',
		'.armorpieces_part .ap_loot .material-icons { cursor: pointer; opacity: 0.6; }',
		'.armorpieces_part .ap_loot .material-icons:hover { opacity: 1; }',
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
		const credit = Project[ID + '_credit'] || creditOf([piece.dataPack, piece.assetPack], piece.key);

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
						loot: (data.loot || []).map(lootRow),
						tables: lootTables(),
						author: credit.author,
						license: credit.license,
						licenses: LICENSE_OPTIONS,
					};
				},
				methods: {
					has: function (id) {
						return this.fittings.some(function (f) { return f.id === id; });
					},
					removeEffect: function (i) {
						this.effects.splice(i, 1);
					},
					addLoot: function () {
						this.loot.push(lootRow());
					},
					removeLoot: function (i) {
						this.loot.splice(i, 1);
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
				for (const row of vue.loot) {
					const problem = lootProblem(row);
					if (problem) {
						Blockbench.showQuickMessage(problem, 2500);
						return false;
					}
				}
				this.hide();
				applyPartEdit(piece, data, shown, vue.name, chosen,
					vue.fittings.map(function (f) { return f.id; }),
					vue.effects.map(function (row) { return effectFromRow(row, vue.fittings); }),
					vue.loot.map(lootFromRow),
					{ author: String(vue.author || '').trim(), license: vue.license });
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
			return JSON.parse(tool('preview_material.py',
				['--fitting-choices', piece.dataPack, '--pack', piece.assetPack]));
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
			ingredients: {
				label: 'Takes, in words', type: 'text', value: '', placeholder: 'Gems',
				description: 'The "Ingredients:" line of the fitting\'s template. Blank for the type\'s own: Trim Materials, Any Dye, A Banner.',
			},
			recipe_focus: {
				label: 'Recipe centre', type: 'text', value: '', placeholder: 'minecraft:amethyst_block',
				description: 'The item in the middle of the template recipe. Blank writes no recipe.',
			},
			recipe_ring: {
				label: 'Recipe ring', type: 'text', value: 'minecraft:paper',
				description: 'The four items around it.',
			},
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
				const ingredients = (result.ingredients || '').trim();
				if (ingredients) {
					definition.ingredients = { translate: 'fitting.' + namespace + '.' + name + '.ingredients' };
				}
				writeJson(file, definition);
				writeLang(piece.assetPack, namespace, 'fitting.' + namespace + '.' + name,
					(result.label || '').trim() || titleCase(name));
				if (ingredients) {
					writeLang(piece.assetPack, namespace, 'fitting.' + namespace + '.' + name + '.ingredients', ingredients);
				}
				// The fitting's own template: the bare fitting template carrying this fitting as
				// armorpieces:fitting, in the same ring shape as a part's template recipe.
				const focus = (result.recipe_focus || '').trim();
				const ring = (result.recipe_ring || '').trim() || 'minecraft:paper';
				if (focus) {
					writeJson(path.join(piece.pack, 'data', namespace, 'recipe', 'fitting_template_' + name + '.json'), {
						type: 'minecraft:crafting_shaped',
						category: 'equipment',
						pattern: RING_PATTERN,
						key: { '#': ring, F: focus },
						result: {
							id: 'armorpieces:fitting_template',
							components: { 'armorpieces:fitting': namespace + ':' + name },
						},
					});
				}
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

	function applyPartEdit(piece, data, shown, name, chosen, fittingIds, effects, loot, credit) {
		const s = state();
		let changed = false;

		// Credits: held until Save writes the pack's credits file, like the name.
		if (credit) {
			const was = creditOf([piece.dataPack, piece.assetPack], piece.key);
			if (credit.author !== was.author || credit.license !== was.license) {
				Project[ID + '_credit'] = credit;
				markDirty();
				changed = true;
			} else {
				Project[ID + '_credit'] = null;
			}
		}

		// Effects: compared with keys in a fixed order, so a row that merely re-spells what the
		// file said does not count as a change. Absent stays absent while the list is empty.
		if (effects && canonical(effects) !== canonical(data.effects || [])) {
			if (effects.length || 'effects' in data) data.effects = effects;
			markDirty();
			changed = true;
		}

		// Loot: the field is the list, and an empty list is no field - a part found nowhere is
		// written exactly as a part that never had the group.
		if (loot && JSON.stringify(loot) !== JSON.stringify(data.loot || [])) {
			if (loot.length) data.loot = loot;
			else delete data.loot;
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
			recipe_craftable: {
				label: 'Craftable', type: 'checkbox', style: 'toggle_switch', value: true,
				description: 'Off, Save writes the recipe as armorpieces:disabled - it loads, matches '
					+ 'nothing and is absent from the recipe book - with the two items kept, so it '
					+ 'can be switched back on. For a part that is found rather than made.',
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
				recipe_craftable: s.recipe_craftable !== false,
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
		s.recipe_craftable = result.recipe_craftable !== false;
		s.fitting = result.fitting || '';
		// The summary line says "not craftable" while the switch is off.
		if (changed.includes('recipe_craftable')) syncForm();
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
	 *
	 * A skin hides the same list, and the Textures panel is the one that matters: a skin shown on a
	 * material points its armor at two internal preview textures, and `internal` in Blockbench means
	 * "a bitmap rather than a linked file", not "hidden" - so the previews were listed beside the
	 * masters and were selectable, and paint aimed at one went into a texture that is never saved
	 * and is recomposited over on the next edit.
	 */
	const HIDDEN_PANELS = ['textures', 'layers', 'animations', 'keyframe', 'timeline',
		'variable_placeholders', 'bone', 'collections', 'animation_controllers'];

	function wrapCondition(owner) {
		const original = owner.condition;
		owner.condition = function () {
			if (isWorkspace() || isSkinWorkspace()) return false;
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
		writeCurrent(Project.uuid);
	}

	function leaveWorkspace() {
		// Called with the piece still selected, so applyPalette would keep the greys; restore
		// explicitly. Panels and the outliner re-evaluate on the next project's activation.
		restorePalette();
		writeCurrent(null);
	}

	/*
	 * The same two, for a skin. A skin project is `free` rather than the plugin's own format - the
	 * rig is vanilla's four shells and there is nothing to trim off a format for - so there is no
	 * onActivation to hang these on: openSkin calls the first, and the select/unselect events do
	 * the rest, which is what makes switching between a piece tab and a skin tab put the right
	 * panel and the right palette up.
	 */
	/*
	 * Re-resolve the open skin's list entry. A skin can gain its datapack half after it was opened
	 * - New Skin writes one, a pack is added under Packs..., a file is written outside - and the
	 * entry was resolved once, when the tab was made. Without this the panel goes on saying
	 * "masters only" for a skin that has both halves, and Save writes neither.
	 */
	function refreshSkinEntry() {
		if (!isSkinWorkspace()) return;
		const skin = currentSkin();
		const fresh = skinList().find(function (s) { return s.name === skin.name; });
		if (!fresh) return;
		const had = !!skin.half;
		Project[ID + '_skin'] = fresh;
		// Only when the half is NEW: re-reading it otherwise would drop the Skin dialog's edits.
		if (!had && fresh.half && !Project[ID + '_skin_dirty']) loadSkinHalf(Project, fresh);
	}

	function enterSkinWorkspace() {
		if (!isSkinWorkspace()) return;
		refreshSkinEntry();
		if (typeof updateInterfacePanels === 'function') updateInterfacePanels();
		if (Modes.vue) Modes.vue.$forceUpdate();
		Outliner.updateNodeDisplayRules();
		fillItemLists(skinPanel);
		syncSkinForm();
		applySkinPreview();
		applyPalette();
		applySkinVisibility();
		applyPose();
		writeCurrent(Project.uuid);
	}

	function leaveSkinWorkspace() {
		restorePalette();
		writeCurrent(null);
	}

	function onSelectProject() {
		if (isSkinWorkspace()) enterSkinWorkspace();
	}

	/* Fires with Blockbench.Project already cleared, so the project that is leaving is the
	   argument's rather than the global one. */
	function onUnselectProject(data) {
		const project = data && data.project;
		if (project && project[ID + '_skin']) leaveSkinWorkspace();
	}

	// ---- armor skins ---------------------------------------------------------------------------

	/*
	 * A skin is the armor's OWN texture - not a part hung on a socket and not a trim painted over
	 * one. It is a greyscale pair on vanilla's grid, `humanoid` and `humanoid_leggings`, coloured
	 * per armor material at load time from a ramp derived from that material's own texture
	 * (tools/bake_skin.py). Nothing is modelled: the geometry is vanilla's four armor shells, and
	 * the only thing an author decides is what is painted on them.
	 *
	 * So it gets a workspace of its own rather than a mode of the piece one. `bb_rig.py --skin`
	 * builds the same figure a part is judged on, wearing all four slots at their real inflate,
	 * with the ARMOR cubes unlocked and their two sheets linked to tools/skin_masters/<name>/.
	 * Everything the piece workspace does about bones, fittings and effects is absent here on
	 * purpose; what is shared is the loop - open, paint, look, check, save - the status the bridge
	 * checks after every edit, the "Armor Skin" panel beside the piece one, and the datapack half:
	 * a skin has a data file, a template recipe and loot rows exactly as a part does, written by
	 * the Skin dialog and on Save.
	 *
	 * The one thing the panel has that a piece's has not is the LIGHT slider, and it is there
	 * because of what the bake does. A skin is not painted onto bare armor: vanilla's own texture
	 * for the material - its panel edges, the rim along the top of a plate, the shadow under an
	 * overhang - is measured as a signed offset and added to the master's VALUE before the ramp is
	 * read (bake_skin.lightmap, SkinBake.lightmap, LIGHT_MIX = 0.35). Measured, that offset runs
	 * +/-45 on every material and both sheets: two and a half of the sixteen levels a skin is drawn
	 * in, in either direction. So a ladder four levels apart can be flattened, or locally inverted,
	 * by armor the author never drew - and nothing in the greyscale says so. The slider moves the
	 * mix, and the third view shows vanilla's contribution on its own, so the thing being drawn
	 * into can be looked at rather than guessed.
	 *
	 * The sheets are painted as ASCII rather than with a brush. A 64x32 sheet is thirty-two lines
	 * of sixteen greys and a dot for transparent, which is small enough to read back in full and to
	 * write in one call, and it is the form an agent can actually be accurate in - a rivet line is
	 * a row of characters, not eleven brush strokes.
	 */
	const SKIN_SHEETS = ['humanoid', 'humanoid_leggings'];
	const SKIN_LEVELS = '0123456789abcdef';
	const SKIN_CLEAR = '.';
	const SKIN_KEEP = ' ';
	const SKIN_SLOTS = ['helmet', 'chestplate', 'leggings', 'boots'];
	// The materials a skin is BAKED on, which are the armor materials - not MATERIALS above, which
	// is the trim palette list a part is previewed through. Same order as bake_skin.MATERIALS.
	const SKIN_MATERIALS = ['leather', 'chainmail', 'iron', 'gold', 'diamond', 'netherite',
		'turtle_scute', 'copper'];
	// bake_skin.py's own default, and so the mix a skin is really worn at. The slider starts here.
	const SKIN_LIGHT_MIX = 0.35;
	// 256-entry lookup tables from bake_skin.py, per material. A material's ramp never changes.
	const skinRamps = {};

	function defaultSkinState() {
		return {
			// What the armor shows: the greyscale master, the bake on a material, or vanilla's own
			// lighting for that material on its own.
			view: 'master',
			material: 'iron',
			light: SKIN_LIGHT_MIX,
			animation: 'idle',
			phase: 0,
			show_player: true,
			show_helmet: true,
			show_chestplate: true,
			show_leggings: true,
			show_boots: true,
			armor_only: true,
			recipe_focus: '',
			recipe_ring: 'minecraft:paper',
			recipe_craftable: true,
		};
	}

	function skinState() {
		if (!Project) return defaultSkinState();
		if (!Project[ID + '_skin_state']) Project[ID + '_skin_state'] = defaultSkinState();
		return Project[ID + '_skin_state'];
	}

	function skinsRoot() {
		const root = repoRoot();
		return root ? path.join(root, 'tools', 'skin_masters') : null;
	}

	/*
	 * A skin's datapack half, the way a piece has one. `data` is the `armor_skin` file the dynamic
	 * registry loads, `recipe` the template recipe that hands it out, `sheets` the directory the
	 * two masters are INSTALLED to - authoring stays under tools/skin_masters, because the rig is
	 * built from there - and `langKey` the line a player reads the name from.
	 */
	const SKIN_DATA_REL = ['armorpieces', 'armor_skin'];

	function skinRecord(dataPack, assetPack, namespace, name) {
		return {
			name: name,
			namespace: namespace,
			key: namespace + ':' + name,
			dataPack: dataPack,
			assetPack: assetPack,
			data: path.join(dataPack, 'data', namespace, ...SKIN_DATA_REL, name + '.json'),
			recipe: path.join(dataPack, 'data', namespace, 'recipe', 'skin_template_' + name + '.json'),
			sheets: path.join(assetPack, 'assets', namespace, 'textures', 'entity', 'skin', name),
			langKey: 'skin.' + namespace + '.' + name,
		};
	}

	/*
	 * The half each authored skin belongs to, by the master directory's name. A skin is matched by
	 * NAME rather than by a key, because the name is the only thing tools/skin_masters/<name>
	 * knows; a skin installed under another id (sync_skin_masters --as) is the one case this
	 * cannot see, and it reads as a skin with no half, which is what it looks like from here.
	 */
	function skinHalves() {
		const byName = {};
		const roots = scopedRoots();
		for (const packDir of roots) {
			for (const namespace of namespacesIn(packDir, 'data')) {
				for (const name of listJson(path.join(packDir, 'data', namespace, ...SKIN_DATA_REL))) {
					if (byName[name]) continue;
					// The sheets may be in another pack than the data file, as a piece's are.
					let assetPack = packDir;
					for (const candidate of roots) {
						const dir = path.join(candidate, 'assets', namespace, 'textures', 'entity', 'skin', name);
						if (fs.existsSync(path.join(dir, SKIN_SHEETS[0] + '.png'))) {
							assetPack = candidate;
							break;
						}
					}
					byName[name] = skinRecord(packDir, assetPack, namespace, name);
				}
			}
		}
		return byName;
	}

	function skinList() {
		const root = skinsRoot();
		if (!root) return [];
		const halves = skinHalves();
		return subdirs(root)
			.filter(function (dir) { return fs.existsSync(path.join(dir, SKIN_SHEETS[0] + '.png')); })
			.map(function (dir) {
				const name = path.basename(dir);
				return { name: name, dir: dir, half: halves[name] || null };
			});
	}

	/* The open skin's datapack half, or null while it is masters and nothing else. */
	function currentHalf() {
		const skin = currentSkin();
		return (skin && skin.half) || null;
	}

	/* Held on the project and written back whole on Save, exactly as a part's data file is. */
	function skinData() {
		return (Project && Project[ID + '_skin_data']) || null;
	}

	function markSkinDirty() {
		if (Project) Project[ID + '_skin_dirty'] = true;
	}

	/* The skin's name as a player reads it. The three shapes a description comes in are the part's. */
	function skinDisplayName(half, data) {
		const description = data && data.description;
		if (typeof description === 'string') return { text: description, editable: true, key: null };
		if (description && typeof description.translate === 'string') {
			const entries = readJsonOr(langFile(half.assetPack, half.namespace), {});
			const text = entries[description.translate];
			return {
				text: typeof text === 'string' ? text : titleCase(half.name),
				editable: true,
				key: description.translate,
			};
		}
		return { text: description ? JSON.stringify(description) : '', editable: false, key: null };
	}

	/* One line for the panel: what the datapack half says, or that there is not one. */
	function skinSummary() {
		const skin = currentSkin();
		if (!skin) return '';
		const half = currentHalf();
		if (!half) {
			return 'Masters only - no armor_skin file, so the game cannot wear it. Skin... writes one.';
		}
		const data = skinData();
		if (!data) return half.key + '  ·  ' + half.data + ' could not be read';
		const name = Project[ID + '_skin_name'] || skinDisplayName(half, data).text;
		const loot = (data.loot || []).map(function (l) {
			return String(l.table || '').replace(/^minecraft:/, '');
		});
		return name + '  ·  ' + half.key
			+ (loot.length ? '  ·  found in: ' + loot.join(', ') : '  ·  found nowhere')
			+ (skinState().recipe_craftable === false ? '  ·  not craftable' : '');
	}

	function currentSkin() {
		return (Project && Project[ID + '_skin']) || null;
	}

	function isSkinWorkspace() {
		return !!(Project && currentSkin());
	}

	function isSkinSheet(id) {
		return SKIN_SHEETS.indexOf(id) >= 0;
	}

	function skinSheets() {
		return Texture.all.filter(function (t) { return isSkinSheet(t.id); });
	}

	/* Which sheet a cube is painted from: the leggings shells have their own, everything else shares. */
	function skinSheetOf(cube) {
		return /_leggings$/.test(cube.name) ? 'humanoid_leggings' : 'humanoid';
	}

	function skinCubes() {
		return Cube.all.filter(function (c) { return !c.locked; });
	}

	/*
	 * Read the datapack half onto a skin project: the data file as the object it parsed to, held
	 * whole and written back whole the way a part's is, and the two recipe fields off the template
	 * recipe. Also the reload path's, so a skin open across a plugin reload picks up a half the
	 * build before it did not know how to find.
	 */
	function loadSkinHalf(project, entry) {
		project[ID + '_skin_data'] = entry.half ? readJsonOr(entry.half.data, null) : null;
		project[ID + '_skin_dirty'] = false;
		// A display name changed in the Skin dialog, held until Save writes the language line.
		project[ID + '_skin_name'] = null;
		const recipe = entry.half ? readTemplateRecipe(entry.half.recipe) : null;
		const s = project[ID + '_skin_state'];
		if (recipe && s) {
			s.recipe_focus = recipe.focus;
			s.recipe_ring = recipe.ring;
			s.recipe_craftable = recipe.craftable;
		}
	}

	function openSkin(name, options) {
		options = options || {};
		const existing = ModelProject.all.find(function (p) {
			return p[ID + '_skin'] && p[ID + '_skin'].name === name;
		});
		if (existing && !options.reload) {
			if (existing !== Project) existing.select();
			enterSkinWorkspace();
			publishSkin('select');
			return {
				skin: name, reused: true,
				unsaved_edits: existing.undo ? existing.undo.index - (existing[ID + '_saved_index'] || 0) : 0,
			};
		}
		const entry = skinList().find(function (s) { return s.name === name; });
		if (!entry) {
			throw new Error('no skin ' + name + ' under ' + skinsRoot() + '; known: ' +
				skinList().map(function (s) { return s.name; }).join(', ') +
				' (python tools/skin_sheets.py --new <name> starts one)');
		}
		if (existing) {
			const unsaved = existing.undo.index !== (existing[ID + '_saved_index'] || 0);
			if (unsaved && !options.discard) {
				throw new Error(name + ' is open with unsaved edits, and reloading it reads the ' +
					'sheets back off disk: save it first, or pass discard: true');
			}
			existing.undo.history.length = 0;
			existing.undo.index = 0;
			const old = existing;
			setTimeout(function () { old.close(true); }, 50);
		}

		const out = tempDir();
		tool('bb_rig.py', ['--skin', entry.dir, '--out-dir', out]);
		const file = path.join(out, 'skin_' + name + '.bbmodel');
		const content = JSON.parse(fs.readFileSync(file, 'utf8'));
		const figure = content.armorpieces_figure || null;
		delete content.armorpieces_figure;
		Codecs.project.load(content, { path: file, content: content });

		Project[ID + '_skin'] = entry;
		Project[ID + '_figure'] = figure;
		Project[ID + '_skin_material'] = '';
		Project[ID + '_skin_state'] = defaultSkinState();
		loadSkinHalf(Project, entry);
		Project[ID + '_saved_index'] = 0;
		Project.name = 'skin ' + name;
		// The rig is scratch, like a piece's: Save Skin puts the sheets back, saving the project
		// would put a rig where the masters live.
		Project.save_path = '';
		Project.export_path = '';
		// The project was loaded as `free`, so no format activation ran and nothing knows this is a
		// skin yet. Now that it is one, bring the workspace up - the same bargain openPiece makes.
		enterSkinWorkspace();
		publishSkin('open');
		Blockbench.showQuickMessage('Skin ' + name + figureNote(figure), 2500);
		return { skin: name, reused: false, dir: entry.dir };
	}

	function closeSkin(discard) {
		if (!isSkinWorkspace()) throw new Error('no skin is open');
		const unsaved = Project.undo.index !== (Project[ID + '_saved_index'] || 0);
		if (unsaved && !discard) throw new Error('unsaved edits: save first, or close with discard: true');
		const closing = Project;
		const name = currentSkin().name;
		setTimeout(function () { closing.close(true); }, 50);
		return { closed: name };
	}

	function saveSkin() {
		const skin = currentSkin();
		if (!skin) throw new Error('no skin is open');
		const written = [];
		// Both sheets are linked files under tools/skin_masters/<name>, so save() writes them back
		// where they came from - the same bargain a part's master makes.
		for (const sheet of skinSheets()) {
			sheet.save();
			written.push(path.join(skin.dir, sheet.id + '.png'));
		}

		// The datapack half, exactly as a piece's Save writes it: the whole data object as the Skin
		// dialog left it, so a field this editor has no control for is written back as it was read;
		// the language line the name lives on; and the template recipe from the panel's two fields.
		const half = currentHalf();
		const notes = [];
		if (half) {
			if (Project[ID + '_skin_dirty'] && skinData()) {
				writeJson(half.data, skinData());
				Project[ID + '_skin_dirty'] = false;
				notes.push('data');
			}
			if (Project[ID + '_skin_name']) {
				const shown = skinDisplayName(half, skinData());
				if (shown.key) writeLang(half.assetPack, half.namespace, shown.key, Project[ID + '_skin_name']);
				Project[ID + '_skin_name'] = null;
				notes.push('name');
			}
			if (Project[ID + '_skin_credit']) {
				writeCredit(half.dataPack, half.key, Project[ID + '_skin_credit']);
				Project[ID + '_skin_credit'] = null;
				notes.push('credits');
			}
			const s = skinState();
			notes.push(writeTemplateRecipe(half.recipe, {
				id: 'armorpieces:skin_template',
				components: { 'armorpieces:skin': half.key },
			}, s.recipe_focus, s.recipe_ring, s.recipe_craftable !== false));
		}

		// A skin is authored under tools/skin_masters and loaded from the resources, and its
		// template's icon is a swatch of the chest front off the sheet that ships - so a pair
		// written and left there is a skin the game cannot wear and the hotbar cannot draw. Save
		// therefore runs the same two scripts the command line does: the sync installs the pair and
		// is also what checks it, and the icon pass redraws every skin icon, its model and the
		// select that picks between them. That is the bargain a part's master already makes on save
		// (see sync_decoration_masters above); the difference is that a skin's icon draws itself, so
		// there is a second script behind it.
		//
		// A skin in somebody else's pack has no sync script - the mod's is a list of what the mod
		// ships, into the mod's own resources - so the pair is copied straight into the half's own
		// texture directory, which is the same two files at the same path under a different root.
		// Its icon needs nothing: the icon is a sprite source that lists every pack's skins.
		const root = repoRoot();
		const mine = half && half.namespace === 'armorpieces' && root && half.dataPack.startsWith(root);
		let report = '';
		if (!half || mine) {
			report = tool('sync_skin_masters.py', [skin.name]).trim();
			const icons = tool('gen_template_icons.py', ['--skins']).trim();
			report = [report, icons].filter(Boolean).join('\n');
			notes.push('installed');
		} else {
			fs.mkdirSync(half.sheets, { recursive: true });
			for (const sheetId of SKIN_SHEETS) {
				fs.copyFileSync(path.join(skin.dir, sheetId + '.png'),
					path.join(half.sheets, sheetId + '.png'));
			}
			// check_skin.py exits non-zero when the skin has problems, which is right for a command
			// line and wrong here: a half-drawn skin is exactly what a save in the middle of drawing
			// one looks like, and the report is news, not a reason to abandon the write. So the
			// exit code is ignored and the output taken either way. (The repo path above goes
			// through sync_skin_masters.py, which prints the same analysis without failing on it.)
			try {
				report = tool('check_skin.py', [skin.name, '--brief']).trim();
			} catch (err) {
				report = String((err && err.stdout) || err.message || '').trim();
			}
			notes.push('installed to ' + packLabel(half.assetPack));
		}
		if (report) console.log('[armorpieces] ' + report);

		Project[ID + '_saved_index'] = Project.undo.index;
		if (Project.undo.current_save) Project[ID + '_save_in_edit'] = true;
		// The summary line reads the name back off the file it was just written to.
		syncSkinForm();
		publishSkin('save');
		Blockbench.showQuickMessage('Saved skin ' + skin.name + ' - sheets, ' + notes.join(', '), 3000);
		return { skin: skin.name, wrote: written, notes: notes, report: report };
	}

	/* One sheet as rows of characters. See the section comment for the alphabet. */
	function skinAscii(sheetId) {
		const sheet = tex(sheetId);
		if (!sheet) throw new Error('no sheet "' + sheetId + '"; a skin has ' + SKIN_SHEETS.join(', '));
		const canvas = sheet.canvas;
		const data = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
		const rows = [];
		for (let y = 0; y < canvas.height; y++) {
			let row = '';
			for (let x = 0; x < canvas.width; x++) {
				const i = (y * canvas.width + x) * 4;
				if (!data[i + 3]) {
					row += SKIN_CLEAR;
					continue;
				}
				const value = data[i] === data[i + 1] && data[i + 1] === data[i + 2] ? data[i]
					: Math.round(data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114);
				row += SKIN_LEVELS[Math.max(0, Math.min(15, Math.round(value / 17)))];
			}
			rows.push(row);
		}
		return rows;
	}

	/*
	 * Stamp rows onto one sheet, in one undo step. A dot clears, a level character paints that
	 * grey, a space leaves the texel alone - so a stamp over one net does not have to redraw the
	 * sheet around it. Anything off the sheet is an error rather than a silent crop: a stamp that
	 * lands half outside is a mistake about where a net is, and swallowing it would hide it.
	 */
	/* The texels one stamp describes. Validated in full before anything is painted, so a typo in
	   the last row leaves the sheet as it was rather than half redrawn. */
	function skinJobs(sheetId, rows, at, opts) {
		if (!isSkinWorkspace()) throw new Error('no skin is open');
		const sheet = tex(sheetId);
		if (!sheet) throw new Error('no sheet "' + sheetId + '"; a skin has ' + SKIN_SHEETS.join(', '));
		if (!Array.isArray(rows) || !rows.length) throw new Error('rows is a list of strings');
		const ox = Math.floor((at && at[0]) || 0);
		const oy = Math.floor((at && at[1]) || 0);
		const width = sheet.canvas.width, height = sheet.canvas.height;

		// Validated in full before anything is painted, so a typo in the last row leaves the sheet
		// as it was rather than half redrawn.
		let jobs = [];
		for (let r = 0; r < rows.length; r++) {
			const row = String(rows[r]);
			for (let c = 0; c < row.length; c++) {
				const char = row[c];
				if (char === SKIN_KEEP) continue;
				const x = ox + c, y = oy + r;
				if (x < 0 || y < 0 || x >= width || y >= height) {
					throw new Error('row ' + r + ' column ' + c + ' lands at ' + x + ',' + y +
						', off a ' + width + 'x' + height + ' sheet');
				}
				if (char === SKIN_CLEAR) {
					jobs.push({ x: x, y: y, value: null });
					continue;
				}
				const level = SKIN_LEVELS.indexOf(char);
				if (level < 0) {
					throw new Error('unknown character "' + char + '" at row ' + r + ' column ' + c +
						': "." clears, " " keeps, "0"-"9" and "a"-"f" are the greys');
				}
				jobs.push({ x: x, y: y, value: level * 17 });
			}
		}

		/* shade_only: a skin pinned to a silhouette is drawn on vanilla's own outline, so a stamp
		   may change what a texel IS but never whether there is one. Paint aimed at a clear texel
		   is dropped rather than refused - the stamp is a rectangle, the armor is not. */
		let skipped = 0;
		if (opts && opts.shade_only) {
			const alpha = sheet.canvas.getContext('2d').getImageData(0, 0, width, height).data;
			const kept = [];
			for (const job of jobs) {
				if (job.value !== null && alpha[(job.y * width + job.x) * 4 + 3] > 0) kept.push(job);
				else skipped++;
			}
			jobs = kept;
		}
		return { sheet: sheet, id: sheetId, at: [ox, oy], rows: rows.length, jobs: jobs, skipped: skipped };
	}

	function applySkinJobs(sheet, jobs) {
		sheet.edit(function (canvas) {
			const ctx = canvas.getContext('2d');
			for (const job of jobs) {
				ctx.clearRect(job.x, job.y, 1, 1);
				if (job.value === null) continue;
				ctx.fillStyle = 'rgb(' + job.value + ',' + job.value + ',' + job.value + ')';
				ctx.fillRect(job.x, job.y, 1, 1);
			}
		}, { no_undo: true });
	}

	function paintSkin(sheetId, rows, at) {
		const stamp = skinJobs(sheetId, rows, at);
		Undo.initEdit({ textures: [stamp.sheet], bitmap: true });
		applySkinJobs(stamp.sheet, stamp.jobs);
		Undo.finishEdit('Paint skin');
		return { sheet: sheetId, at: stamp.at, rows: stamp.rows, texels: stamp.jobs.length };
	}

	/* Many stamps in ONE undo entry, and so in one bridge call. A skin is a face at a time by
	   nature, and a call per face is where a session's turns go: every one of them carries the
	   whole context again. Two or three calls draw a skin. */
	function paintSkinMany(stamps) {
		if (!Array.isArray(stamps) || !stamps.length) throw new Error('stamps is a list of stamps');
		const order = [], bySheet = {};
		let texels = 0, skipped = 0;
		for (let i = 0; i < stamps.length; i++) {
			const stamp = stamps[i];
			let got;
			try {
				got = skinJobs(stamp.sheet || SKIN_SHEETS[0], stamp.rows, stamp.at, stamp);
			} catch (e) {
				throw new Error('stamp ' + i + (stamp.where ? ' (' + stamp.where + ')' : '') +
					': ' + e.message);
			}
			if (!bySheet[got.id]) { bySheet[got.id] = { sheet: got.sheet, jobs: [] }; order.push(got.id); }
			for (const job of got.jobs) bySheet[got.id].jobs.push(job);
			texels += got.jobs.length;
			skipped += got.skipped || 0;
		}
		Undo.initEdit({ textures: order.map(function (id) { return bySheet[id].sheet; }), bitmap: true });
		for (const id of order) applySkinJobs(bySheet[id].sheet, bySheet[id].jobs);
		Undo.finishEdit('Paint skin');
		return { sheets: order, stamps: stamps.length, texels: texels, skipped: skipped };
	}

	/* The material's 256-entry table, from bake_skin.py. Asked for once per material per session.
	   `--light 0` keeps the lightmaps out of the answer: the table does not depend on the mix, and
	   the maps are two grids of two thousand numbers each. */
	function skinRamp(material) {
		if (!skinRamps[material]) {
			const data = JSON.parse(tool('bake_skin.py',
				['--ramps', '--material', material, '--light', '0']));
			if (!data[material]) throw new Error('no ramp for ' + material);
			skinRamps[material] = data[material];
		}
		return skinRamps[material];
	}

	/*
	 * Vanilla's own lighting for one material at one mix: a signed amount, in the master's own
	 * units, added to each texel's value before the ramp is read. Keyed by BOTH, because the mix is
	 * a control now rather than a constant - and asked of bake_skin.py rather than scaled here, so
	 * that the mix the slider sits at by default is the file the game loads, rounding included.
	 */
	function skinLight(material, mix) {
		mix = Math.round(Math.max(0, Math.min(1, Number(mix) || 0)) * 100) / 100;
		if (!mix) return null;
		const key = material + '@' + mix;
		if (!(key in skinLights)) {
			const data = JSON.parse(tool('bake_skin.py',
				['--ramps', '--material', material, '--light', String(mix)]));
			skinLights[key] = (data.lightmaps || {})[material] || null;
		}
		return skinLights[key];
	}

	function skinPreviewId(sheetId) {
		return 'preview_' + sheetId;
	}

	/*
	 * One sheet through one ramp, into a canvas: the bake, in the viewport.
	 *
	 * `lightOnly` draws vanilla's half of it instead of the skin - mid grey where the material adds
	 * nothing, and the offset it really adds either side of that, one for one in the master's own
	 * units. So a texel two shades brighter than mid is a texel vanilla will push two levels up,
	 * and the shape the drawing is going into is visible on the figure it is going onto. The alpha
	 * is still the master's, because that is what the model shows.
	 */
	function compositeSkin(target, sheet, lut, light, lightOnly) {
		target.width = sheet.canvas.width;
		target.height = sheet.canvas.height;
		const ctx = target.getContext('2d');
		const image = sheet.canvas.getContext('2d').getImageData(0, 0, target.width, target.height);
		const data = image.data;
		for (let i = 0; i < data.length; i += 4) {
			if (!data[i + 3]) continue;
			/* Vanilla's own lighting, mixed back over the pattern - see bake_skin.lightmap. */
			let offset = 0;
			if (light) {
				const texel = i / 4;
				const row = light[Math.floor(texel / target.width)];
				if (row) offset = row[texel % target.width] || 0;
			}
			if (lightOnly) {
				const shade = Math.max(0, Math.min(255, 128 + offset));
				data[i] = data[i + 1] = data[i + 2] = shade;
				continue;
			}
			let value = data[i] === data[i + 1] && data[i + 1] === data[i + 2] ? data[i]
				: Math.round(data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114);
			value += offset;
			const colour = lut[Math.max(0, Math.min(255, value))];
			data[i] = colour[0];
			data[i + 1] = colour[1];
			data[i + 2] = colour[2];
		}
		ctx.putImageData(image, 0, 0);
	}

	function pointArmorAt(bySheet) {
		for (const cube of skinCubes()) {
			const texture = bySheet[skinSheetOf(cube)];
			if (!texture) continue;
			for (const face of Object.keys(cube.faces)) cube.faces[face].texture = texture.uuid;
		}
		Canvas.updateAllFaces();
	}

	/*
	 * Show the skin as an armor material would render it, or as the greyscale it is authored in.
	 * The preview textures are internal and never saved; the brush and the ASCII painter always
	 * land on the masters, and the preview is recomposited from them after every edit.
	 */
	/* Point the armor at whatever the state asks for and build the previews it needs. */
	function applySkinPreview() {
		if (!isSkinWorkspace()) return { material: '', view: 'master' };
		const s = skinState();
		const byId = {};
		if (s.view === 'master' || !s.material) {
			for (const sheetId of SKIN_SHEETS) byId[sheetId] = tex(sheetId);
			Project[ID + '_skin_material'] = '';
			pointArmorAt(byId);
			return { material: '', view: 'master' };
		}
		const lut = skinRamp(s.material);
		const lights = skinLight(s.material, s.light) || {};
		const lightOnly = s.view === 'light';
		for (const sheetId of SKIN_SHEETS) {
			const sheet = tex(sheetId);
			if (!sheet) continue;
			let preview = tex(skinPreviewId(sheetId));
			if (!preview) {
				const scratch = document.createElement('canvas');
				compositeSkin(scratch, sheet, lut, lights[sheetId], lightOnly);
				preview = new Texture({
					name: skinPreviewId(sheetId), id: skinPreviewId(sheetId), internal: true,
					uv_width: sheet.uv_width, uv_height: sheet.uv_height,
				}).fromDataURL(scratch.toDataURL('image/png')).add(false);
			} else {
				compositeSkin(preview.canvas, sheet, lut, lights[sheetId], lightOnly);
				const own = preview.getOwnMaterial();
				if (own && own.map) own.map.needsUpdate = true;
			}
			byId[sheetId] = preview;
		}
		Project[ID + '_skin_material'] = s.material;
		pointArmorAt(byId);
		return { material: s.material, view: s.view, light: s.light };
	}

	/*
	 * The bridge's and the panel's one way in. A material with nothing else said shows the bake;
	 * 'none' goes back to the greyscale; `view` picks between the bake and vanilla's light alone,
	 * and `light` moves the mix. Whatever changes, the brush and the ASCII painter still land on
	 * the masters - the previews are only ever a thing you look at.
	 */
	function setSkinMaterial(material, options) {
		if (!isSkinWorkspace()) throw new Error('no skin is open');
		options = options || {};
		const s = skinState();
		material = material === undefined || material === null ? s.material : String(material).trim();
		if (!material || material === 'none') {
			s.view = 'master';
		} else {
			s.material = material;
			s.view = options.view || (s.view === 'master' ? 'material' : s.view);
		}
		if (options.light !== undefined && options.light !== null) {
			s.light = Math.max(0, Math.min(1, Number(options.light)));
		}
		const out = applySkinPreview();
		syncSkinForm();
		return out;
	}

	function refreshSkinPreview() {
		if (!isSkinWorkspace()) return;
		const s = skinState();
		if (s.view === 'master' || !s.material) return;
		let lut, lights;
		try {
			lut = skinRamp(s.material);
			lights = skinLight(s.material, s.light) || {};
		} catch (err) {
			return;
		}
		const lightOnly = s.view === 'light';
		for (const sheetId of SKIN_SHEETS) {
			const sheet = tex(sheetId);
			const preview = tex(skinPreviewId(sheetId));
			if (!sheet || !preview) continue;
			compositeSkin(preview.canvas, sheet, lut, lights[sheetId], lightOnly);
			const own = preview.getOwnMaterial();
			if (own && own.map) own.map.needsUpdate = true;
		}
	}

	/* The master a skin preview was composited from, or null for anything else. */
	function skinMasterOf(texture) {
		if (!texture) return null;
		for (const sheetId of SKIN_SHEETS) {
			if (texture.id === skinPreviewId(sheetId)) return tex(sheetId);
		}
		return null;
	}

	/* What the bridge checks after every edit: the two sheets as they are right now, and a meta
	 * that says they are a skin's rather than a piece's. check_skin.py --status reads this. */
	function publishSkin(reason) {
		if (!isSkinWorkspace()) return null;
		try {
			const dir = statusDir();
			const skin = currentSkin();
			const files = {};
			for (const sheetId of SKIN_SHEETS) {
				const texture = tex(sheetId);
				if (!texture) continue;
				const png = sheetPng(texture, function () { publishSkin('load'); });
				if (!png) continue;
				fs.writeFileSync(path.join(dir, sheetId + '.png'), png);
				files[sheetId] = sheetId + '.png';
			}
			Project[ID + '_seq'] = (Project[ID + '_seq'] || 0) + 1;
			fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({
				kind: 'skin',
				seq: Project[ID + '_seq'],
				time: Date.now(),
				reason: reason,
				project: Project.uuid,
				skin: skin.name,
				dir: skin.dir,
				sheets: files,
				material: Project[ID + '_skin_material'] || '',
				view: skinState().view,
				light: skinState().light,
				half: currentHalf() ? currentHalf().key : null,
				unsaved_edits: Project.undo.index - (Project[ID + '_saved_index'] || 0),
			}), 'utf8');
			writeCurrent(Project.uuid);
			return dir;
		} catch (err) {
			console.error('[armorpieces] skin status', err);
			return null;
		}
	}

	/* The skin half of the texture hooks, so the piece ones stay about pieces. */
	function onSkinEditTexture(data) {
		if (!isSkinSheet(data.texture.id)) return;
		if (Settings.get(ID + '_greyscale') && data.canvas) foldCanvasToGreyscale(data.canvas);
		refreshSkinPreview();
	}

	function onSkinFinishEdit(data) {
		const aspects = (data && data.aspects) || {};
		const textures = (aspects.textures || []).filter(function (t) { return isSkinSheet(t.id); });
		for (const texture of textures) {
			if (Settings.get(ID + '_greyscale')) enforceGreyscale(texture);
		}
		if (textures.length) refreshSkinPreview();
		publishSkin((data && data.message) || 'edit');
	}

	// ---- the Skin dialog ------------------------------------------------------------------------

	/*
	 * What an `armor_skin` file says that the sheets cannot: the name a player reads, and where the
	 * template turns up in the world. That is the whole of ArmorSkin beyond its asset id - there is
	 * deliberately no material list, because the ramp is derived rather than authored - so this
	 * dialog is the Part dialog's Name and Loot groups and nothing else, and it borrows that
	 * dialog's stylesheet rather than growing a second copy of it.
	 */
	const SKIN_DIALOG_TEMPLATE = [
		'<div class="armorpieces_part">',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Name</label>',
		'		<input type="text" class="dark_bordered" v-model="name" :disabled="!editable"',
		'			:title="editable ? \'\' : \'A text component the editor cannot edit\'">',
		'	</div>',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Loot</label>',
		'		<div class="ap_column">',
		'			<div class="ap_loot" v-for="(l, i) in loot" :key="i">',
		'				<input type="text" class="dark_bordered ap_loot_table" v-model="l.table" list="armorpieces_loot_tables"',
		'					placeholder="minecraft:chests/stronghold_crossing" title="The loot table the skin is added to">',
		'				<label title="Splits the roll between the skins and parts that share this table">w</label>',
		'				<input type="number" class="dark_bordered ap_loot_num" min="1" step="1" v-model.number="l.weight">',
		'				<label title="How often the skin is offered at all; 1 is every chest">chance</label>',
		'				<input type="number" class="dark_bordered ap_loot_num" min="0" max="1" step="0.01" v-model.number="l.chance">',
		'				<i class="material-icons" title="Remove" @click="removeLoot(i)">clear</i>',
		'			</div>',
		'			<button type="button" @click="addLoot">Add a loot table...</button>',
		'			<datalist id="armorpieces_loot_tables">',
		'				<option v-for="t in tables" :key="t" :value="t"></option>',
		'			</datalist>',
		'			<p class="ap_dim">A skin template is a whole look for a whole suit, so the weights want to be ',
		'			lower than a part\'s and the tables fewer.</p>',
		'		</div>',
		'	</div>',
		'	<div class="dialog_bar form_bar">',
		'		<label class="name_space_left">Credits</label>',
		'		<div class="ap_column">',
		'			<input type="text" class="dark_bordered" v-model="author" placeholder="author" title="Who drew this skin">',
		'			<select class="dark_bordered" v-model="license" title="What others may do with it">',
		'				<option v-for="(label, id) in licenses" :key="id" :value="id">{{ label }}</option>',
		'			</select>',
		'			<p class="ap_dim">Written to armorpieces-credits.json in the pack on Save.</p>',
		'		</div>',
		'	</div>',
		'</div>',
	].join('\n');

	function editSkin() {
		const half = currentHalf();
		if (!half) {
			Blockbench.showMessageBox({
				title: 'No datapack half',
				message: 'This skin is a master pair under tools/skin_masters and nothing else, so ' +
					'there is no armor_skin file to edit and the game cannot wear it. New... makes ' +
					'a skin with both halves; to give this one a half, make a new skin under the ' +
					'same name and it will find these masters.',
			});
			return;
		}
		const data = skinData();
		if (!data) {
			Blockbench.showQuickMessage('Could not read ' + half.data, 2500);
			return;
		}
		const shown = skinDisplayName(half, data);
		const credit = Project[ID + '_skin_credit'] || creditOf([half.dataPack, half.assetPack], half.key);
		new Dialog({
			id: ID + '_skin_edit',
			title: 'Skin ' + half.key,
			width: 560,
			component: {
				data: function () {
					return {
						name: Project[ID + '_skin_name'] || shown.text,
						editable: shown.editable,
						loot: (data.loot || []).map(lootRow),
						tables: lootTables(),
						author: credit.author,
						license: credit.license,
						licenses: LICENSE_OPTIONS,
					};
				},
				methods: {
					addLoot: function () { this.loot.push(lootRow()); },
					removeLoot: function (i) { this.loot.splice(i, 1); },
				},
				template: SKIN_DIALOG_TEMPLATE,
			},
			onConfirm: function () {
				const vue = this.content_vue;
				for (const row of vue.loot) {
					const problem = lootProblem(row);
					if (problem) {
						Blockbench.showQuickMessage(problem, 2500);
						return false;
					}
				}
				this.hide();
				applySkinEdit(half, data, shown, vue.name, vue.loot.map(lootFromRow),
					{ author: String(vue.author || '').trim(), license: vue.license });
			},
		}).show();
	}

	/* The dialog's answers onto the held data object. Nothing is written until Save. */
	function applySkinEdit(half, data, shown, name, loot, credit) {
		let changed = false;
		if (credit) {
			const was = creditOf([half.dataPack, half.assetPack], half.key);
			if (credit.author !== was.author || credit.license !== was.license) {
				Project[ID + '_skin_credit'] = credit;
				markSkinDirty();
				changed = true;
			} else {
				Project[ID + '_skin_credit'] = null;
			}
		}
		if (loot && JSON.stringify(loot) !== JSON.stringify(data.loot || [])) {
			if (loot.length) data.loot = loot;
			else delete data.loot;
			markSkinDirty();
			changed = true;
		}
		name = (name || '').trim();
		if (shown.editable && name && name !== shown.text) {
			if (shown.key) {
				Project[ID + '_skin_name'] = name;
			} else {
				data.description = name;
				markSkinDirty();
			}
			changed = true;
		} else if (shown.key && Project[ID + '_skin_name'] && name === shown.text) {
			Project[ID + '_skin_name'] = null;
		}
		syncSkinForm();
		if (changed) Blockbench.showQuickMessage('Skin changed - written on Save', 2000);
	}

	// ---- new skin ------------------------------------------------------------------------------

	/*
	 * Everything a skin is, written at once: the master pair the rig is built from, the
	 * `armor_skin` file the registry loads, the template recipe that hands it out, the language
	 * line, and the pair installed where the client reads it. That is the debt docs/plans/
	 * armor-skins.md books against this plugin - "painting works; writing does not" - and it is the
	 * same code path New Armor Piece and New Fitting already are, pointed at a third registry.
	 *
	 * The masters stay under tools/skin_masters even when the content does not, because the rig is
	 * built from there and the check reads from there; the pair is COPIED into the pack on Save.
	 * So authoring a skin still needs the repository, as it always has, while shipping one does not.
	 */
	function newSkin() {
		const root = repoRoot();
		if (!root) {
			Blockbench.showMessageBox({
				title: 'No repository',
				message: 'A skin is drawn on masters under tools/skin_masters, so the Armor Pieces ' +
					'repository has to be set in Settings before one can be started.',
			});
			return;
		}
		const packs = searchRoots();
		if (!packs.length) {
			Blockbench.showMessageBox({
				title: 'No packs',
				message: 'No pack folder to put the skin in. Make one with Tools > Armor Pieces > ' +
					'New Pack..., or add an existing folder under Packs....',
			});
			return;
		}
		const inRepo = packs[0].startsWith(root);
		// The mod's own plate outline is always here; vanilla's appear once the game's sheets have
		// been extracted (Use my game...). The tool says which, so this list never guesses.
		const seedOptions = { '': 'Blank sheets' };
		let outlines = [];
		try {
			outlines = JSON.parse(tool('skin_sheets.py', ['--outlines']));
		} catch (err) {
			console.error(err);
		}
		for (const outline of outlines) seedOptions[outline.value] = outline.label;
		const seedDefault = outlines.some(function (o) { return o.value === 'iron'; })
			? 'iron' : (outlines[0] ? outlines[0].value : '');

		new Dialog({
			id: ID + '_new_skin',
			title: 'New Armor Skin',
			form: {
				name: { label: 'Name', type: 'text', value: '', placeholder: 'brigandine' },
				namespace: { label: 'Namespace', type: 'text', value: inRepo ? 'armorpieces' : 'mypack' },
				seed: {
					label: 'Start from', type: 'select', options: seedOptions, value: seedDefault,
					description: 'A seeded skin starts as a flat grey on an existing silhouette - the ' +
						'mod\'s plate, or vanilla\'s where the game\'s sheets are here - so it is drawn ' +
						'where the armor really is and the check holds it to that outline. Blank ' +
						'sheets are the freehand start.',
				},
				data_pack: {
					label: 'Datapack', type: 'select', options: packOptions(packs), value: defaultPack(packs),
					description: 'Where the armor_skin file and its template recipe go.',
				},
				asset_pack: {
					label: 'Resource pack', type: 'select', options: packOptions(packs), value: defaultPack(packs),
					description: 'Where the two sheets and the language file go. The same folder is fine.',
				},
			},
			onConfirm: function (result) {
				const name = (result.name || '').trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
				if (!name) {
					Blockbench.showQuickMessage('Name a skin first', 2000);
					return;
				}
				this.hide();
				const dataPack = packs[parseInt(result.data_pack, 10)];
				const assetPack = packs[parseInt(result.asset_pack, 10)];
				const namespace = (result.namespace || '').trim().toLowerCase()
					.replace(/[^a-z0-9_.-]/g, '_') || 'mypack';
				try {
					createSkin(dataPack, assetPack, namespace, name, result.seed);
				} catch (err) {
					Blockbench.showMessageBox({ title: 'Could not create', message: String(err.message || err) });
					return;
				}
				Blockbench.showQuickMessage('Created ' + namespace + ':' + name, 2500);
				openSkin(name);
			},
		}).show();
	}

	/*
	 * The files a new skin starts from. Throws when the pack or the masters already hold it: the
	 * dialog above and the bridge both end up here, and neither should overwrite a drawing.
	 */
	function createSkin(dataPack, assetPack, namespace, name, seedMaterial) {
		const half = skinRecord(dataPack, assetPack, namespace, name);
		const masters = path.join(skinsRoot(), name);
		if (fs.existsSync(half.data)) throw new Error(half.key + ' is already in that pack.');
		if (fs.existsSync(path.join(masters, SKIN_SHEETS[0] + '.png'))) {
			throw new Error('tools/skin_masters/' + name + ' already holds a drawing. Open it instead.');
		}

		// The pair, by the same script the command line starts a skin with.
		if (seedMaterial) tool('skin_sheets.py', ['--seed', name, '--from', seedMaterial]);
		else tool('skin_sheets.py', ['--new', name]);

		writeJson(half.data, {
			asset_id: half.key,
			description: { translate: half.langKey },
		});
		// A skin found nowhere and craftable from nothing until the author says otherwise: the
		// recipe is written on Save from the panel's two fields, as a part's is.
		fs.mkdirSync(half.sheets, { recursive: true });
		for (const sheetId of SKIN_SHEETS) {
			fs.copyFileSync(path.join(masters, sheetId + '.png'), path.join(half.sheets, sheetId + '.png'));
		}
		if (!readJsonOr(langFile(assetPack, namespace), {})[half.langKey]) {
			writeLang(assetPack, namespace, half.langKey, titleCase(name));
		}
		return half;
	}

	// ---- the skin panel --------------------------------------------------------------------------

	let skinPanel = null;

	function skinOptions() {
		const options = {};
		for (const skin of skinList()) {
			options[skin.name] = skin.half ? skin.name + '  (' + skin.half.key + ')'
				: skin.name + '  (masters only)';
		}
		const current = currentSkin();
		if (current && !options[current.name]) options[current.name] = current.name;
		if (!Object.keys(options).length) options[''] = '-';
		return options;
	}

	function skinPanelForm() {
		const materialOptions = SKIN_MATERIALS.reduce(function (all, m) { all[m] = m; return all; }, {});
		const slots = {};
		for (const slot of SKIN_SLOTS) {
			slots['show_' + slot] = {
				label: titleCase(slot), type: 'checkbox', style: 'toggle_switch', value: true,
			};
		}
		return Object.assign({
			skin: { label: 'Skin', type: 'select', options: skinOptions },
			actions: {
				type: 'buttons', buttons: ['New...', 'Skin...', 'Save', 'Rebuild'],
				click: function (index) {
					if (index === 0) newSkin();
					else if (index === 1) editSkin();
					else if (index === 2) saveSkin();
					else reopenSkin();
				},
			},
			// What the datapack half says, in one line; syncSkinForm writes it into the element.
			summary: { type: 'info', text: '' },
			_1: '_',
			view: {
				label: 'Showing', type: 'inline_select',
				options: { master: 'Master (grey)', material: 'On a material', light: 'Vanilla\'s light' },
				value: 'master',
				description: 'The greyscale being painted, the bake as the game performs it, or ' +
					'vanilla\'s own lighting for that material on its own - mid grey where it ' +
					'changes nothing, and the amount it really adds either side of that.',
			},
			material: {
				label: 'Material', type: 'select', options: materialOptions, value: 'iron',
				condition: function (result) { return result.view !== 'master'; },
			},
			light: {
				label: 'Vanilla light', type: 'range', min: 0, max: 1, step: 0.05, value: SKIN_LIGHT_MIX,
				condition: function (result) { return result.view !== 'master'; },
				description: 'How much of the material\'s own texture is mixed back over the master ' +
					'before the ramp is read. 0.35 is what the game does; at that mix the offset ' +
					'runs +/-45, which is two and a half of the sixteen levels a skin is drawn in. ' +
					'Slide it to 0 to see the pattern alone, and to 1 to see what it is fighting.',
			},
			_2: '_',
			animation: { label: 'Pose', type: 'inline_select', options: animationOptions() },
			phase: {
				label: 'Phase', type: 'range', min: 0, max: 1, step: 0.01, value: 0,
				condition: function (result) { return result.animation !== 'idle'; },
			},
			_3: '_',
			show_player: { label: 'Show player', type: 'checkbox', style: 'toggle_switch', value: true },
		}, slots, {
			armor_only: { label: 'Outliner: armor only', type: 'checkbox', style: 'toggle_switch', value: true },
			_4: '_',
			// No `list` here for the same reason the piece panel has none: 5.1's own datalist never
			// reaches the page. fillItemLists attaches a working one.
			recipe_focus: {
				label: 'Recipe centre', type: 'text', value: '', placeholder: 'minecraft:iron_block',
				description: 'The item in the middle of the skin template\'s recipe. Written on Save.',
			},
			recipe_ring: {
				label: 'Recipe ring', type: 'text', value: 'minecraft:paper',
				description: 'The four items around it.',
			},
			recipe_craftable: {
				label: 'Craftable', type: 'checkbox', style: 'toggle_switch', value: true,
				description: 'Off, Save writes the recipe as armorpieces:disabled - it loads, matches '
					+ 'nothing and is absent from the recipe book - with the two items kept. For a '
					+ 'skin that is found rather than made.',
			},
		});
	}

	function syncSkinForm() {
		if (!skinPanel || !skinPanel.form || !isSkinWorkspace()) return;
		const skin = currentSkin();
		const s = skinState();
		syncingForm = true;
		try {
			const values = {
				skin: skin ? skin.name : '',
				view: s.view,
				material: s.material,
				light: s.light,
				animation: s.animation,
				phase: s.phase,
				show_player: s.show_player,
				armor_only: s.armor_only,
				recipe_focus: s.recipe_focus,
				recipe_ring: s.recipe_ring,
				recipe_craftable: s.recipe_craftable !== false,
			};
			for (const slot of SKIN_SLOTS) values['show_' + slot] = s['show_' + slot] !== false;
			const summary = skinPanel.form.form_data.summary;
			const box = summary && summary.bar && summary.bar.querySelector('.small_text');
			if (box) box.textContent = skinSummary();
			skinPanel.form.setValues(values);
		} finally {
			syncingForm = false;
		}
	}

	/* Rebuild the rig from the masters on disk, the way the piece panel's Rebuild does. */
	function reopenSkin() {
		const skin = currentSkin();
		if (!skin) return;
		try {
			openSkin(skin.name, { reload: true });
		} catch (err) {
			Blockbench.showMessageBox({ title: 'Could not rebuild', message: String(err.message || err) });
		}
	}

	function onSkinFormChange(event) {
		if (syncingForm || !isSkinWorkspace()) return;
		const result = event.result;
		const changed = event.changed_keys || [];
		const s = skinState();
		const skin = currentSkin();

		if (changed.includes('skin') && result.skin && result.skin !== skin.name) {
			try {
				openSkin(result.skin);
			} catch (err) {
				Blockbench.showMessageBox({ title: 'Could not open', message: String(err.message || err) });
				syncSkinForm();
			}
			return;
		}

		s.view = result.view;
		s.material = result.material;
		s.light = result.light;
		s.animation = result.animation;
		s.phase = result.phase;
		s.show_player = !!result.show_player;
		s.armor_only = !!result.armor_only;
		for (const slot of SKIN_SLOTS) s['show_' + slot] = !!result['show_' + slot];
		s.recipe_focus = result.recipe_focus || '';
		s.recipe_ring = result.recipe_ring || '';
		s.recipe_craftable = result.recipe_craftable !== false;
		// The summary line says "not craftable" while the switch is off.
		if (changed.includes('recipe_craftable')) syncSkinForm();

		if (changed.includes('view') || changed.includes('material') || changed.includes('light')) {
			try {
				applySkinPreview();
			} catch (err) {
				console.error(err);
				Blockbench.showQuickMessage('No ramp for ' + s.material +
					' - run tools/vanilla_assets.py', 3000);
				s.view = 'master';
				applySkinPreview();
				syncSkinForm();
			}
		}
		if (changed.includes('animation') || changed.includes('phase')) applyPose();
		if (changed.includes('show_player') || changed.some(function (key) {
			return SKIN_SLOTS.some(function (slot) { return key === 'show_' + slot; });
		})) applySkinVisibility();
		if (changed.includes('armor_only')) Outliner.updateNodeDisplayRules();
	}

	// ---- status for the bridge ----------------------------------------------------------------

	/*
	 * What the open piece is right now, on disk, for anything outside Blockbench that wants to
	 * check it - the MCP bridge's proxy (tools/mcp) runs check_part.py over it after every edit
	 * an agent makes, and `check_part.py --status` is the same by hand. Written synchronously
	 * inside the edit, so by the time a bridge call returns the files describe its result: the
	 * project compiled without its textures (bb_geo reads only the outliner), the sheets as PNGs
	 * straight from their canvases, and meta.json last, carrying a sequence number, so a reader
	 * that sees a new seq sees complete files. current.json beside the folders names the active
	 * piece's. Everything lives under the temp dir and is disposable.
	 */
	function statusRoot() {
		const dir = path.join(tempDir(), 'status');
		if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
		return dir;
	}

	function statusDir() {
		const dir = path.join(statusRoot(), Project.uuid);
		if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
		return dir;
	}

	function writeCurrent(uuid) {
		try {
			fs.writeFileSync(path.join(statusRoot(), 'current.json'),
				JSON.stringify({ uuid: uuid || null, time: Date.now() }), 'utf8');
			pruneStatus();
		} catch (err) {
			console.error('[armorpieces] status', err);
		}
	}

	/* The folders of tabs that are no longer open. */
	function pruneStatus() {
		const open = new Set(ModelProject.all.map(function (p) { return p.uuid; }));
		for (const name of fs.readdirSync(statusRoot())) {
			if (name === 'current.json' || open.has(name)) continue;
			fs.rmSync(path.join(statusRoot(), name), { recursive: true, force: true });
		}
	}

	function sheetFile(id) {
		if (id === 'part') return 'master.png';
		if (id === 'part_static') return 'static.png';
		return 'mask_' + id.slice('part_'.length) + '.png';
	}

	/*
	 * A sheet's pixels as PNG bytes. The canvas is what the brush paints and what Blockbench draws
	 * the loaded image into - but only once the image has loaded, and a piece just opened has not
	 * got there yet, so until then the image itself is used, and a sheet still loading is
	 * published again the moment it lands. Returns null for that last case.
	 */
	function sheetPng(texture, republish) {
		const fromCanvas = function (canvas) {
			const url = canvas.toDataURL('image/png');
			return Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
		};
		const img = texture.img;
		if (texture.width && texture.canvas.width === texture.width && texture.canvas.height === texture.height) {
			return fromCanvas(texture.canvas);
		}
		if (img && img.complete && img.naturalWidth) {
			const canvas = document.createElement('canvas');
			canvas.width = img.naturalWidth;
			canvas.height = img.naturalHeight;
			canvas.getContext('2d').drawImage(img, 0, 0);
			return fromCanvas(canvas);
		}
		if (img && !img[ID + '_republish']) {
			img[ID + '_republish'] = true;
			const owner = Project;
			img.addEventListener('load', function () {
				img[ID + '_republish'] = false;
				if (Project !== owner) return;
				if (republish) republish();
				else publishStatus('load', { model: false, sheets: [texture] });
			}, { once: true });
		}
		return null;
	}

	/* `what.model` writes the model; `what.sheets` is a list of textures, or 'all'. */
	function publishStatus(reason, what) {
		if (!isWorkspace()) return null;
		try {
			const dir = statusDir();
			if (what.model) {
				const doc = JSON.parse(Codecs.project.compile());
				for (const texture of doc.textures || []) delete texture.source;
				fs.writeFileSync(path.join(dir, 'part.bbmodel'), JSON.stringify(doc), 'utf8');
			}
			const list = what.sheets === 'all' ? sheets()
				: (what.sheets || []).filter(function (t) { return isSheetId(t.id); });
			for (const texture of list) {
				const png = sheetPng(texture);
				if (png) fs.writeFileSync(path.join(dir, sheetFile(texture.id)), png);
			}
			const piece = currentPiece();
			const s = state();
			const masks = {};
			for (const fitting of maskedFittings()) {
				masks[fitting.name] = tex(maskId(fitting.name)) ? sheetFile(maskId(fitting.name)) : null;
			}
			Project[ID + '_seq'] = (Project[ID + '_seq'] || 0) + 1;
			writeMeta(reason, dir, masks);
			return dir;
		} catch (err) {
			console.error('[armorpieces] status', err);
			return null;
		}
	}

	// Set while an edit's files are published before its undo entry has landed, so the wrapper
	// around finishEdit rewrites the meta once the entry is in and the unsaved count is right.
	let metaPending = null;

	function writeMeta(reason, dir, masks) {
		const piece = currentPiece();
		const s = state();
		if (!masks) {
			masks = {};
			for (const fitting of maskedFittings()) {
				masks[fitting.name] = tex(maskId(fitting.name)) ? sheetFile(maskId(fitting.name)) : null;
			}
		}
		const texture = Project[ID + '_texture'] || {};
		const meta = {
				seq: Project[ID + '_seq'] || 0,
				time: Date.now(),
				reason: reason,
				project: Project.uuid,
				piece: {
					key: piece.key, name: piece.name, namespace: piece.namespace,
					dataPack: piece.dataPack, assetPack: piece.assetPack,
					data: piece.data, geometry: piece.geometry,
					texture: texture.file || piece.texture, isMaster: !!texture.isMaster,
				},
				anchor: s.anchor,
				anchors: anchorsOf(piece),
				sheet: sheetSize(),
				editing: s.edit,
				fitting: s.fitting,
				recipe: { centre: s.recipe_focus || '', ring: s.recipe_ring || 'minecraft:paper',
					craftable: s.recipe_craftable !== false },
				sheets: { master: 'master.png', static: tex('part_static') ? 'static.png' : null, masks: masks },
				files: { model: 'part.bbmodel' },
				unsaved_edits: Project.undo.index - (Project[ID + '_saved_index'] || 0),
				part_dirty: !!Project[ID + '_dirty'],
		};
		fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify(meta), 'utf8');
		writeCurrent(Project.uuid);
		if (Project.undo.current_save) metaPending = { reason: reason, dir: dir, project: Project };
	}

	/* After the undo entry of a published edit has landed: the same meta, with the count right. */
	function settleMeta() {
		const pending = metaPending;
		metaPending = null;
		if (!pending || pending.project !== Project || !isWorkspace()) return;
		try {
			writeMeta(pending.reason, pending.dir, null);
		} catch (err) {
			console.error('[armorpieces] status', err);
		}
		metaPending = null;
	}

	// ---- registration -------------------------------------------------------------------------

	Plugin.register(ID, {
		title: 'Armor Pieces',
		author: 'mattjes',
		icon: 'shield',
		description: 'Browse, edit and save Armor Pieces on an animated vanilla player wearing real armor.',
		version: '0.3.0',
		variant: 'desktop',
		tags: ['Minecraft: Java Edition'],

		onload() {
			registered.push(new Setting(ID + '_root', {
				name: 'Armor Pieces repository',
				description: 'Required: a clone of github.com/mattjesmc/ArmorPieces (the folder holding ' +
					'tools/ and src/), with Python 3 and Pillow installed. It is the toolkit, not the ' +
					'workspace - your packs can live anywhere; add them under Tools > Armor Pieces > Packs....',
				category: 'edit',
				type: 'text',
				value: '',
			}));
			registered.push(new Setting(ID + '_packs', {
				name: 'Armor Pieces packs',
				description: 'The pack folders added under Tools > Armor Pieces > Packs..., as a JSON list. ' +
					'Edit them there rather than here.',
				category: 'edit',
				type: 'text',
				value: '[]',
			}));
			registered.push(new Setting(ID + '_scope', {
				name: 'Armor Pieces: pack being worked in',
				description: 'The one pack the piece list shows, or blank for every pack found. ' +
					'Set from Packs... rather than here.',
				category: 'edit',
				type: 'text',
				value: '',
			}));
			registered.push(new Setting(ID + '_library', {
				name: 'Armor Pieces library',
				description: 'The index.json of the pack library that Packs... installs from and ' +
					'Submit... offers packs to. The default is the library at ' + LIBRARY_SITE + '.',
				category: 'edit',
				type: 'text',
				value: LIBRARY_INDEX,
				onChange: function () { libraryCache = null; },
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
				// The unwrap is whole texels rounded UP, in the mod and every tool; Blockbench's
				// own choices are floored (this flag off: 0.9 deep becomes 0) or exact (on: a
				// 2.1-wide face straddles texels). Neither matches, so `size` is patched below.
				box_uv_float_size: false,
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
			format.box_uv_float_size = false;

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
			const openSkinAction = new Action(ID + '_open_skin', {
				name: 'Open Armor Skin...',
				description: 'Paint the armor texture itself on the player rig.',
				icon: 'texture',
				click: function () {
					const list = skinList();
					if (!list.length) {
						Blockbench.showMessageBox({
							title: 'No skins',
							message: 'A skin is a greyscale pair under tools/skin_masters/<name>. ' +
								'Start one with: python tools/skin_sheets.py --new <name>',
						});
						return;
					}
					const choices = {};
					for (const skin of list) choices[skin.name] = skin.name;
					new Dialog({
						id: ID + '_pick_skin',
						title: 'Open Armor Skin',
						form: { skin: { label: 'Skin', type: 'select', options: choices, value: list[0].name } },
						onConfirm: function (form) {
							this.hide();
							try {
								openSkin(form.skin);
							} catch (err) {
								Blockbench.showMessageBox({ title: 'Could not open', message: String(err.message || err) });
							}
						},
					}).show();
				},
			});
			const newSkinAction = new Action(ID + '_new_skin', {
				name: 'New Armor Skin...',
				description: 'Start a skin: its master pair, its data file, its recipe and its name.',
				icon: 'add_photo_alternate',
				click: newSkin,
			});
			const saveSkinAction = new Action(ID + '_save_skin', {
				name: 'Save Armor Skin',
				description: 'Write both sheets back to tools/skin_masters, install them, and write ' +
					'the datapack half.',
				icon: 'save',
				condition: function () { return isSkinWorkspace(); },
				click: function () { saveSkin(); },
			});
			const editSkinAction = new Action(ID + '_edit_skin', {
				name: 'Skin...',
				description: 'The name a player reads and where the template is found.',
				icon: 'edit',
				condition: function () { return isSkinWorkspace(); },
				click: editSkin,
			});
			const packs = new Action(ID + '_packs', {
				name: 'Packs...',
				description: 'The folders your own packs are in.',
				icon: 'folder_open',
				click: packsDialog,
			});
			const createPack = new Action(ID + '_new_pack', {
				name: 'New Pack...',
				description: 'Make a datapack or resource pack folder with its pack.mcmeta.',
				icon: 'create_new_folder',
				click: function () { newPack(null); },
			});
			const exportZip = new Action(ID + '_export_pack', {
				name: 'Export Pack...',
				description: 'Zip a pack folder for handing round.',
				icon: 'archive',
				click: exportPack,
			});
			const useGame = new Action(ID + '_use_game', {
				name: 'Use my game...',
				description: 'Point the editor at your copy of Minecraft, so the figure wears real armor.',
				icon: 'videogame_asset',
				click: useGameDialog,
			});

			// One submenu, not six loose entries in Tools. `children` is also what makes cleanup
			// tractable: there is exactly one menu node to remove on unload, and forgetting it is
			// how a reloaded plugin ends up listed twice.
			const menu = new Action(ID + '_menu', {
				name: 'Armor Pieces',
				description: 'Browse, edit and preview Armor Pieces.',
				icon: 'shield',
				children: [open, create, save, '_',
					openSkinAction, newSkinAction, editSkinAction, saveSkinAction, '_',
					packs, createPack, exportZip, '_', useGame],
			});
			registered.push(open, save, create, openSkinAction, newSkinAction, editSkinAction,
				saveSkinAction, packs, createPack, exportZip, useGame, menu);
			MenuBar.addAction(menu, 'tools');
			registered.push(Blockbench.addCSS(PACKS_DIALOG_CSS));
			registered.push(Blockbench.addCSS(LIBRARY_DIALOG_CSS));

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

			// The skin panel takes the same slot: a project is a piece or a skin, never both, so
			// the two conditions are exclusive and the sidebar holds whichever one applies.
			skinPanel = new Panel(ID + '_skin_panel', {
				name: 'Armor Skin',
				icon: 'texture',
				condition: function () { return isSkinWorkspace(); },
				default_position: {
					slot: 'right_bar',
					float_position: [0, 0],
					float_size: [320, 480],
					height: 460,
					sidebar_index: 0,
				},
				form: skinPanelForm(),
			});
			registered.push(skinPanel);
			skinPanel.form.on('change', onSkinFormChange);

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
				// A skin makes the same bargain and has two previews rather than one, so the
				// redirect is by which master a preview was composited from. Without it a stroke
				// lands on the preview: Blockbench's own getTextureToEdit hands back whatever
				// texture the face carries, and that one is never saved and is recomposited over
				// on the next edit - the paint is gone with no message that it went.
				if (input && isSkinWorkspace()) {
					const master = skinMasterOf(input);
					if (master) return master;
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
					let target = null;
					if (isWorkspace() && this.texture && this.texture.id === 'preview') target = editTarget();
					else if (isSkinWorkspace()) target = skinMasterOf(this.texture);
					if (target) {
						this.texture = target;
						this.layer = target.selected_layer || null;
						UVEditor.updateSelectionOutline();
						this.updateTextureCanvas();
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
					// The MCP bridge wraps every eval in an undo entry of its own, whether or not
					// the code changed anything. One that changed nothing - a read, a check - is
					// dropped here, so a piece read through the bridge is still a piece with no
					// unsaved edits, and Ctrl+Z still undoes the author's last stroke.
					if (message === BRIDGE_EVAL && (isWorkspace() || isSkinWorkspace()) &&
						unchangedSince(this.current_save, aspects || this.current_save.aspects)) {
						delete this.current_save;
						metaPending = null;
						if (Project) Project[ID + '_save_in_edit'] = false;
						return;
					}
				}
				const result = originalFinishEdit.call(this, message, aspects);
				if (Project && Project[ID + '_save_in_edit']) {
					Project[ID + '_save_in_edit'] = false;
					Project[ID + '_saved_index'] = Project.undo.index;
				}
				settleMeta();
				return result;
			};
			undo_hooks.push(function () { UndoSystem.prototype.finishEdit = originalFinishEdit; });

			/*
			 * Box UV in whole texels rounded up, matching the mod's bake and the tools' nets. Every
			 * place Blockbench lays a box out - the mesh, the UV editor, the template - asks
			 * `size(axis, true)` for the floored size; for a piece it gets the ceiling instead, so a
			 * 0.9-deep cube keeps its side faces and a 4.9-tall one shows all five rows it samples.
			 */
			const originalSize = Cube.prototype.size;
			Cube.prototype.size = function (axis, floored) {
				if ((floored === true || floored === 'box_uv') && Format === Formats[ID]) {
					const exact = originalSize.call(this, axis, false);
					const up = function (v) { return Math.ceil(v - 1e-7); };
					return axis === undefined ? exact.map(up) : up(exact);
				}
				return originalSize.call(this, axis, floored);
			};
			undo_hooks.push(function () { Cube.prototype.size = originalSize; });

			Outliner.node_display_rules.push(outlinerRule);
			undo_hooks.push(function () { Outliner.node_display_rules.remove(outlinerRule); });

			Cube.preview_controller.on('update_painting_grid', onPaintingGrid);
			undo_hooks.push(function () {
				Cube.preview_controller.removeListener('update_painting_grid', onPaintingGrid);
			});

			Blockbench.on('init_edit', onInitEdit);
			Blockbench.on('finish_edit', onFinishEdit);
			Blockbench.on('edit_texture', onEditTexture);
			Blockbench.on('select_mode', onSelectMode);
			Blockbench.on('update_view', onUpdateView);
			Blockbench.on('undo', onUndoRedo);
			Blockbench.on('redo', onUndoRedo);
			Blockbench.on('before_closing', restorePalette);
			// A skin project is `free`, so it has no format activation to hang the workspace on.
			Blockbench.on('select_project', onSelectProject);
			Blockbench.on('unselect_project', onUnselectProject);

			// A piece open across a reload of the plugin keeps its resolved fittings from before it,
			// which may be missing what the resolver now reports. Resolve them again on first use.
			for (const project of ModelProject.all) project[ID + '_fittings'] = null;
			// A skin open across one keeps the list entry it was opened from, and that entry carries
			// the datapack half - which an older build did not resolve at all. Look it up again.
			for (const project of ModelProject.all) {
				const skin = project[ID + '_skin'];
				if (!skin) continue;
				const fresh = skinList().find(function (s) { return s.name === skin.name; });
				if (!fresh) continue;
				project[ID + '_skin'] = fresh;
				if (!project[ID + '_skin_state']) project[ID + '_skin_state'] = defaultSkinState();
				// Unsaved edits to the data file would be lost, so only a project that has none.
				if (!project[ID + '_skin_dirty']) loadSkinHalf(project, fresh);
			}
			// A previous session may have ended with the greys still in. Put the author's palette
			// back before anything else can persist the greys again - and before the workspace
			// below puts them in on purpose, or this would take those straight back out.
			if (ColorPanel.palette && stashedPalette() && isPluginPalette(ColorPanel.palette)
				&& !wantedPalette()) {
				restorePalette();
			}

			// And the unload just before this reload told the bridge no piece was current.
			if (isWorkspace()) publishStatus('load', { model: true, sheets: 'all' });
			// A skin open across a reload has to bring its own workspace back for the same reason:
			// nothing else will, since its format is not this plugin's.
			if (isSkinWorkspace()) {
				enterSkinWorkspace();
				publishSkin('load');
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
				openFor: openFor,
				close: closeFor,
				create: function (dataPack, assetPack, namespace, name, anchor) {
					const piece = createPiece(dataPack, assetPack, namespace, name, anchor);
					if (!openPiece(piece, anchor)) throw new Error('created ' + piece.key + ' but could not open it');
					return { piece: piece.key, anchor: anchor, files: [piece.data, piece.geometry, piece.texture] };
				},
				packs: searchRoots,
				// Every pack with what is in it, and the one being worked in - '' for all of them.
				packList: function () {
					return searchRoots().map(function (dir) {
						const info = packInfo(dir);
						return { dir: dir, label: info.label, parts: info.parts, data: info.data, assets: info.assets };
					});
				},
				scope: packScope,
				setScope: function (dir) { setPackScope(dir || ''); return packScope(); },
				anchors: anchors,
				// The library: the index it reads, an install into a folder, the submission form.
				library: libraryIndex,
				libraryUrl: libraryUrl,
				installEntry: installEntry,
				submit: submitDialog,
				submissionUrl: submissionUrl,
				packSources: function () { return packSources.map(function (s) { return s.id; }); },
				// The game: what is here, the dialog, and an install from a path for a caller that
				// cannot click. `figure` is what the open rig's reference is wearing.
				gameStatus: gameStatus,
				useGame: useGameDialog,
				// Credits: the author and license an id resolves to in its pack, and setting them.
				credit: function (key) {
					const piece = allPieces().find(function (p) { return p.key === key; });
					if (!piece) throw new Error('no piece ' + key);
					return creditOf([piece.dataPack, piece.assetPack], key);
				},
				setCredit: function (key, author, license) {
					const piece = allPieces().find(function (p) { return p.key === key; });
					if (!piece) throw new Error('no piece ' + key);
					if (!LICENSE_OPTIONS[license]) throw new Error('unknown license ' + license);
					return writeCredit(piece.dataPack, key, { author: String(author || '').trim(), license: license });
				},
				installGame: function (file) { return installGame(['--jar', file]); },
				figure: function () {
					return (typeof Project !== 'undefined' && Project && Project[ID + '_figure']) || null;
				},
				paintFaces: paintFaces,
				// The sheets the part's fittings need, created where the panel would create them.
				ensureSheets: function () {
					if (!isWorkspace()) throw new Error('no piece is open');
					const made = [];
					for (const fitting of maskedFittings()) {
						if (!tex(maskId(fitting.name)) && createMaskLayer(fitting.name)) made.push(maskId(fitting.name));
					}
					publishStatus('sheets', { model: false, sheets: 'all' });
					return made;
				},
				ensureStatic: function () {
					if (!isWorkspace()) throw new Error('no piece is open');
					if (tex('part_static')) return false;
					createStaticLayer();
					publishStatus('sheets', { model: false, sheets: 'all' });
					return true;
				},
				setRecipe: function (centre, ring, craftable) {
					if (!isWorkspace()) throw new Error('no piece is open');
					const s = state();
					if (centre !== undefined && centre !== null) s.recipe_focus = String(centre).trim();
					if (ring !== undefined && ring !== null) s.recipe_ring = String(ring).trim() || 'minecraft:paper';
					if (craftable !== undefined && craftable !== null) s.recipe_craftable = !!craftable;
					syncForm();
					return { centre: s.recipe_focus, ring: s.recipe_ring, craftable: s.recipe_craftable !== false };
				},
				publish: function () { return publishStatus('api', { model: true, sheets: 'all' }); },
				// Armor skins: the armor's own texture, a workspace of its own. See the section
				// comment in this file, and tools/skin_sheets.py for the nets these sheets carry.
				skins: skinList,
				openSkin: openSkin,
				closeSkin: closeSkin,
				saveSkin: saveSkin,
				skinAscii: skinAscii,
				paintSkin: paintSkin,
				paintSkinMany: paintSkinMany,
				setSkinMaterial: setSkinMaterial,
				currentSkin: currentSkin,
				isSkinWorkspace: isSkinWorkspace,
				publishSkin: function () { return publishSkin('api'); },
				// The skin's datapack half, the way editPart/applyPartEdit are the piece's.
				skinState: skinState,
				skinData: skinData,
				skinHalf: currentHalf,
				editSkin: editSkin,
				newSkin: newSkin,
				createSkin: function (dataPack, assetPack, namespace, name, seed) {
					const half = createSkin(dataPack, assetPack, namespace, name, seed);
					openSkin(name);
					return { skin: half.key, files: [half.data, half.sheets] };
				},
				applySkinEdit: function (name, loot) {
					const half = currentHalf();
					if (!half) throw new Error('this skin has no datapack half');
					const data = skinData();
					applySkinEdit(half, data, skinDisplayName(half, data), name, loot);
				},
				setSkinRecipe: function (centre, ring, craftable) {
					if (!isSkinWorkspace()) throw new Error('no skin is open');
					const s = skinState();
					if (centre !== undefined && centre !== null) s.recipe_focus = String(centre).trim();
					if (ring !== undefined && ring !== null) s.recipe_ring = String(ring).trim() || 'minecraft:paper';
					if (craftable !== undefined && craftable !== null) s.recipe_craftable = !!craftable;
					syncSkinForm();
					return { centre: s.recipe_focus, ring: s.recipe_ring, craftable: s.recipe_craftable !== false };
				},
				refreshSkin: enterSkinWorkspace,
				statusDir: function () { return isWorkspace() ? statusDir() : null; },
				currentPiece: currentPiece,
				displayName: function () { return displayName(currentPiece(), partData()); },
				state: state,
				data: partData,
				fittings: function () { return fittingsOf(currentPiece()); },
				availableFittings: function () { return availableFittings(currentPiece()); },
				editPart: editPart,
				applyPartEdit: function (name, anchors, fittingIds, effects, loot) {
					const piece = currentPiece();
					const data = partData();
					applyPartEdit(piece, data, displayName(piece, data), name, anchors, fittingIds, effects, loot);
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
			Blockbench.removeListener('init_edit', onInitEdit);
			Blockbench.removeListener('finish_edit', onFinishEdit);
			Blockbench.removeListener('edit_texture', onEditTexture);
			Blockbench.removeListener('select_mode', onSelectMode);
			Blockbench.removeListener('update_view', onUpdateView);
			Blockbench.removeListener('undo', onUndoRedo);
			Blockbench.removeListener('redo', onUndoRedo);
			Blockbench.removeListener('before_closing', restorePalette);
			Blockbench.removeListener('select_project', onSelectProject);
			Blockbench.removeListener('unselect_project', onUnselectProject);
			leaveWorkspace();
			leaveSkinWorkspace();
			undo_hooks.reverse().forEach(function (fn) { fn(); });
			undo_hooks = [];
			// Deleting a BarItem does not take its menu entry with it, so the menu node has to go
			// explicitly - otherwise every reload leaves another copy behind in Tools.
			MenuBar.removeAction('tools.' + ID + '_menu');
			registered.forEach(function (item) { item.delete(); });
			registered = [];
			panel = null;
			skinPanel = null;
			anchorCache = null;
			delete window[ID + '_api'];
			if (typeof updateInterfacePanels === 'function') updateInterfacePanels();
			Outliner.updateNodeDisplayRules();
		},
	});
})();
