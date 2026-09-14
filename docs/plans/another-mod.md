# Plan: Armor Pieces from another mod

What a second mod meets when it wants this one's decoration system under its own circumstances,
and what closes the gap. Written from a review taken on 2026-09-12 in the role of that modder,
against the working tree at the clone's `10eecfa`.

The one-line finding: **easy as an add-on, hard as a library.** A mod that adds pieces, effect
types or fitting types to Armor Pieces has a clean, documented, namespace-clean path and needs
almost no Java. A mod that wants the engine for its own content, its own items or its own
obtaining flow hits three walls before it writes a line: the licence forbids depending on it, there
is no artifact to depend on, and the mod cannot be told to keep quiet. None of the three is code.

---

## Measured today, 2026-09-12

What a consumer does, and what happens now. `works` means it works and is written down somewhere a
modder would look; `works, undocumented` means the code allows it and nothing says so.

| the consumer wants to | today |
| --- | --- |
| add pieces, fittings, skins, cloths, loot groups in its own namespace | **works.** Every lookup keeps the part's namespace (`DecorationGeometryManager.java:37`, `DecorationTextureManager.java:418`). Data only. |
| register an effect type | **works.** `DecorationEffects.register(Identifier, MapCodec)` (`:72`), with a from-another-mod tutorial in its Javadoc (`:16-59`) and in `docs/authoring.md:661`. |
| register a fitting type, with or without a renderer | **works.** `Fittings.register` (`:51`) and `FittingRenderers.register` (`:32`), same shape, same Javadoc. A `Fitting.Masked` needs no client code at all. |
| ask what an entity is wearing that does X | **works.** `DecorationEffectDispatcher.forEachWorn` / `anyWorn` (`:111`, `:123`), public on purpose. |
| decorate a stack in code, no smithing table | **works, undocumented.** `DecorationEntry` and `ArmorDecorations.with` are public records; `ModDataComponents.DECORATIONS` is a public field. The two guards (part fits the socket, base equips in the socket's slot) live only in the recipe (`SmithingDecorationRecipe.java:107-129`), so the consumer re-does them or calls `applyDecoration` (`:146`), which wants a trim-material stack. |
| use its own item as the template | **works, undocumented.** The recipe reads the component off whatever its `template` ingredient matched (`:111`); it never checks the item class. A consumer ships its own `armorpieces:smithing_decoration` recipe naming its item. |
| take a part off in its own UI | **fork.** Removal is a private method of `AdvancedSmithingMenu` (`:485`, `:538`). |
| draw a decorated stack in its own GUI or on its own humanoid | **works, undocumented.** `ArmorDecorationLayer.submitForSlot` (`:111`) is public; the layer attaches itself to any renderer whose model extends `HumanoidModel` (`ArmorPiecesClient.java:75`). |
| a socket the twelve do not have, or a non-humanoid body | **closed, by design.** `DecorationAnchor.java:14-19` says why. |
| effects on a curio or trinket slot | **fork.** Dispatch walks `HEAD/CHEST/LEGS/FEET` (`DecorationEffectDispatcher.java:48`); the per-stack path is private (`:143`). |
| an emissive or translucent part; its own colouring | **fork.** `FittingColour` is sealed; `DecorationPalette` is package-private; the render type is fixed (`ArmorDecorationLayer.java:195`). |
| its own wording on the tooltip and the templates | **works, undocumented.** Every string is a language key under `item.armorpieces.*` / `anchor.armorpieces.*`; a resource pack overrides them, as vanilla intends. |
| depend on the jar from `build.gradle` | **nothing to depend on.** `maven-publish` is applied (`build.gradle:3`) and no `publishing` block exists; no coordinates, no repository, no jar-in-jar guidance anywhere. |
| know what may change in the next version | **no answer.** No `@ApiStatus`, no api package, no stability or deprecation policy; the three documented front doors share packages with everything private-by-convention. |
| run the engine without the mod's content, tab, table or chat | **override every file.** Nothing in either initializer is conditional (`ArmorPieces.java:60-95`, `ArmorPiecesClient.java:30-85`). The two configs cover loot volume and first-person arms. The only lever is a datapack override per part (`anchors: []`) plus `armorpieces:disabled` per recipe, after which `PackAudit` reports each one as broken. |
| be allowed to do any of this | **the licence says no.** Clause 3 bans distribution "in whole or in part" and bans derivative works, with no carve-out for a mod that compiles against it and requires the player to install it. Linking to the download page is allowed (`LICENSE:33`); nothing says that is the way. |

Three things about that table decide the plan.

**The code is closer than the packaging.** Everything a consumer touches at runtime is tolerant,
namespace-clean and, for the three front doors, already written up. What is missing is declaration:
a sentence in the licence, a block in the build, a line drawn through the public surface, and a
switch that the split already designed.

**The walls that are code are design decisions, not oversights.** Closed sockets, humanoid-only
rendering and four-slot dispatch are each argued in the source. This plan leaves them closed and
says so, rather than half-opening them.

**Every "works, undocumented" row is one paragraph from "works".** They are the cheapest rows in the
table and together they are most of what a consumer needs.

---

## The two consumers

There are two mods in the review, and the plan has to know which row serves which.

**The one that adds to Armor Pieces.** A content mod, or a mod whose armor wants to accept pieces.
It ships pieces in its namespace, maybe an effect type or a fitting type, and it wants players to
find its content in the same tab, the same table and the same loot as everything else. This
consumer is nearly served today. It needs an artifact, a licence answer, and the README to say the
three front doors exist.

**The one that builds on Armor Pieces.** A mod with its own theme: its own template items, its own
obtaining flow, its own UI, and no wish to see Armor Pieces' knights and courtiers beside its
content. This consumer needs everything the first one needs, plus the engine to run silent, plus
the "works, undocumented" rows to become the documented way in.

The plan serves both. The second is what is missing.

---

## The contract

Three promises, and a consumer can hold the mod to each.

**An artifact you can name.** `maven.modrinth:armor-pieces:<version>` resolves from
`https://api.modrinth.com/maven` for every published version, with a sources jar beside it. The
README says so, with the four lines of Gradle. A dependent mod declares Armor Pieces as a required
dependency on its own Modrinth and CurseForge pages, the launcher installs it, and nothing is ever
bundled. That is the distribution channel the licence permits, and the plan makes it the only one
anyone needs.

**A boundary you can trust.** `docs/api.md` lists the public surface by class and member. What it
lists does not change within a minor version; what it lists and then drops is deprecated for one
minor version first, with a changelog line. Everything public and not listed is
`@ApiStatus.Internal`, and the annotation is what a consumer's IDE shows them. The gate proves the
list against the compiled jar.

**An engine you can run silent.** One server setting turns the mod's own content off: not offered,
not craftable, not dropped, not in the tab, still decoded and still drawn if already worn. That
setting is the one `additive-packs.md` designed and the one finishing the split needs anyway. A
consumer that sets it in its own config defaults ships a world with only its own pieces in it.

---

## The mechanism

### 1. The licence: one carve-out

Clause 3 stays. It gains a sentence a dependent mod can point at:

> Another mod may depend on this software: it may compile against it, declare it as a required
> dependency, and instruct its users to install it from an official download page. It may not
> bundle, embed or repackage any part of it.

The `fabric.mod.json` `license` field stays `All Rights Reserved`; the field is a label, not the
terms. The README's licence section and `modpage.yml`'s licence paragraph gain the same sentence,
so the pages a modder reads first give the same answer as the file.

This is the copyright holder's sentence to write, not the plan's. The wording above is the
recommendation; the decision is in [Open](#open).

### 2. The artifact: Modrinth's maven, and a publishing block as the proof

Modrinth serves every project's files as a maven repository with no setup:
`maven.modrinth:<slug>:<version>`, and the slug the mod pages are written for is `armor-pieces`
(`modpage.yml:2`).

**Measured 2026-09-13: that project does not exist.** `api.modrinth.com/v2/project/armor-pieces`
answers 404 and a search finds nothing by this author; the slug is free. The 0.3.0 release is a
GitHub release and nothing else, so today there is no maven anywhere, and `dist/modrinth.md` is a
page for a project nobody has created. Creating it is the copyright holder's act and is in
[Open](#open); until it exists the artifact story is a promise about a place, and the plan's steps
that depend on it (the README section, the sources upload) wait on it.

Three things make it a real story once the project exists.

- **The 0.4.0 release goes up as the project's first version**, with Fabric API declared as its
  required dependency there, the way `modpage.yml:276` already describes it. From that moment
  `maven.modrinth:armor-pieces:0.4.0` resolves.
- **The sources jar goes up as the version's second file.** `withSourcesJar()` already builds it
  (`build.gradle:34`) and it already carries the licence. The release checklist in
  `docs/plans/testing.md` gains the upload. Whether Modrinth's maven serves a second file by
  classifier is to be verified on that first upload, not assumed.
- **A `publishing` block publishes to `build/maven`**, nothing remote. It exists so the gate can
  prove the coordinates: the consumer example in [section 6](#6-the-consumer-example-the-falsifier)
  resolves `com.mattjesmc.armorpieces:armorpieces:<version>` from that directory offline. The
  Modrinth coordinates and the local ones differ in group and artifact, on purpose; the local one is
  a test fixture and the README never names it.

The README gains a section, `## From another mod`, between `## Adding a piece` and
`## Configuration`, holding the repository and dependency lines, the `depends` entry for
`fabric.mod.json` (`"armorpieces": ">=0.4.0"`), the sentence from the licence, and links to the
three front doors and to `docs/api.md`. `modpage.yml` carries it, since the README is generated.

### 3. The boundary: a listing, an annotation and a test

Not a package move. Moving twenty classes into `com.mattjesmc.armorpieces.api` costs every internal
caller and every test, changes nothing a consumer can see until the first artifact exists, and the
repo's packages are by subject, which is the right shape to keep. The line is drawn with two tools
that cost nothing at the call sites.

**`docs/api.md`** lists the surface. From the review, the list is short enough to read in one sitting:

| area | what is API |
| --- | --- |
| registries | `ArmorPiecesRegistries`: the five datapack keys and the two static registries |
| effects | `DecorationEffects.register`; `DecorationEffect` and its five hooks; `DecorationEffectContext`; `MaterialValue`; `DecorationEffectDispatcher.forEachWorn` / `anyWorn` |
| fittings | `Fittings.register`; `Fitting`, `Fitting.Masked`, `FittingValue`, `FittingColour`; `FittingRenderers.register`, `FittingRenderer`, `FittingRenderer.Context` |
| the stack | `ModDataComponents.DECORATIONS` / `DECORATION` / `FITTING` / `SKIN` / `CLOTH`; `ArmorDecorations`; `DecorationEntry`; `ArmorDecoration` (read side); `DecorationAnchor` |
| applying | `SmithingDecorationRecipe.applyDecoration`, and its new sibling `removeDecoration` (section 5) |
| drawing | `ArmorDecorationLayer.submitForSlot`; `DecorationGeometryManager.instance().get`; `DecorationTextureManager.instance().resolve` and `Mask` |
| data formats | the JSON of the five registries, the `smithing_*` recipe types, `armorpieces:template`, `armorpieces:set_decoration`, `armorpieces:disabled`, and the server config file |

Each row links to the Javadoc and states the one rule a consumer has to know (the guard
`applyDecoration` does, the same-instance rule `FittingRenderers.get` depends on, the four-slot
limit of the dispatcher).

**`@ApiStatus.Internal`** goes on every public class not in the list. `org.jetbrains:annotations` is
already on the compile classpath through Minecraft. The annotation is not access control; it is
what IntelliJ underlines when a consumer reaches past the line, which is the whole point.

**`ApiSurfaceTest`**, tier 1 of the gate, reads `docs/api.md`'s tables and reflects: every listed
class exists, is public, is not `@Internal`, and every listed member exists with the documented
parameter types. A class that is public and neither listed nor annotated fails the test too, so
the line cannot drift. The test is the promise made checkable.

**The versioning sentence** goes at the top of `docs/api.md` and in the changelog's head: within a
minor version the listing does not change; a listed member that is to go is deprecated one minor
version before it goes; the consumer's `depends` range is `>=0.4.0 <0.5.0` until 1.0.

### 4. The engine runs silent: the split's switch, made the library's

`additive-packs.md`'s [switch](additive-packs.md#the-switch) is the right mechanism and it is
already designed: `parts.mod_parts` and `parts.disabled` in the server config, re-read on every
reload, with the rule that disabled means not offered and never means not drawn. This plan adds
nothing to its design and takes a dependency on it: **the switch is what lets a consumer run the
engine without the content**, and finishing the split is what lets the mod ship the content as a
built-in pack the switch turns off.

What the plan adds around it, for the consumer specifically:

- **The switch applies to skins, cloths and fittings too** (the open question at
  `additive-packs.md` Open). Yes: the same predicate over the four registries. A consumer that
  turns the mod's parts off and still finds the mod's nine skins in the tab has not been served.
- **`PackAudit` respects it.** A disabled part is not "a part with no socket left"; it is not
  reported at all.
- **The creative tab walks the same predicate**, so with the switch on the tab holds only the
  consumer's pieces. The tab itself stays: a consumer that wants its own tab builds one the way
  `ModCreativeTabs` does, and `ModCreativeTabs.stacks(Predicate<Holder<ArmorDecoration>>)` becomes
  public so it does not have to copy the walk.

What the plan does **not** add: conditional registration. The items, the block, the menu, the
recipe serializers, the loot function and the commands register unconditionally and stay that way.
A registry entry that exists on one launch and not the next is a save-breaking act, and every one
of those is either invisible when unused (the serializers, the loot types), gated on operator
permission (the commands), or hidden by the switch (the templates, through the tab and the recipes).
The block is the one visible remainder: a consumer that does not want the advanced table in its
world overrides its recipe with `armorpieces:disabled`, which is the tool that already exists for
exactly that.

### 5. The undocumented rows become the way in

Each is a small change plus its paragraph in `docs/api.md`.

- **`SmithingDecorationRecipe.removeDecoration(ItemStack, DecorationAnchor)`**, public static
  beside `applyDecoration`, moved out of the menu's private `withoutPart`. The menu calls it. The
  same for a fitting: `removeFitting(ItemStack, DecorationAnchor, Holder<Fitting>)`.
- **`applyDecoration` gets an overload taking the material as a `Holder<TrimMaterial>`** rather
  than a stack that provides one, for the consumer whose obtaining flow has no item in hand. The
  two guards stay in both.
- **The fitting mask filename keeps a foreign namespace.** `ArmorDecorationLayer.java:180` takes
  the fitting id's path only, so `mymod:glow` and `armorpieces:glow` collide on `<part>_glow.png`.
  Rule: the mask name is the path when the fitting's namespace is the part's own, and
  `<ns>.<path>` otherwise. No shipped file changes name.
- **The table's fitting slot hint stops filtering on the mod's namespace**
  (`AdvancedSmithingScreen.java:530-536`): a hint is used when a texture exists at
  `<ns>:slot_hints/<path>_template`, whoever `<ns>` is.
- **`Fitting.ingredients()`'s default key is documented** as the mod's generic line, with the
  instruction to override it.
- **The four-slot limit and the closed sockets are documented as limits**, with the reason quoted
  from the source, so the consumer reads a decision rather than discovering a wall.

### 6. The consumer example: the falsifier

A plan about "another mod" is only checkable by another mod. `examples/consumer/` is one: a
complete second Fabric mod, id `armorpieces_example`, in its own Gradle build, that depends on Armor
Pieces by coordinates and does everything the README section says a consumer can do.

- an effect type, `armorpieces_example:blink_away`, the Javadoc's own example made real;
- a fitting type, `armorpieces_example:glow`, a `Fitting.Masked` with no renderer;
- one piece in its namespace naming both, with its own template item and its own
  `smithing_decoration` recipe for it;
- a command that decorates the held item through `applyDecoration` and strips it through
  `removeDecoration`, which is the code path the table never takes;
- a `config/armorpieces-server.json` default with `parts.mod_parts: false`, so its dev world holds
  only its own piece.

The gate builds it in tier 0 against `build/maven` (section 2), offline. Tier 2 boots it in the
headless server beside the mod and asserts the piece loads, the effect fires and the mod's own
content is absent. That last assertion is the one that proves the switch, and it is the one line
that turns "the engine can run silent" from a promise into a measurement.

The example is also the README section's source of truth: the Gradle lines the README shows are
the example's own, copied by `modpage build`, so they cannot go stale on their own.

---

## Order

1. **Licence sentence** (section 1). The user's; nothing else is worth publishing before it.
2. **`docs/api.md` and the annotations** (section 3), then `ApiSurfaceTest`. This is the first
   thing that changes Java and the first that can fail; it goes before any new API so the new API
   is born inside the line.
3. **The undocumented rows** (section 5): `removeDecoration`, the material overload, the mask
   name, the slot hint. Small, each with its test.
4. **The publishing block and the consumer example** (sections 2 and 6), tier 0 only.
5. **The switch** (section 4), which is the split's work and lands with it, then the example's
   tier 2 boot with the switch on.
6. **README section and `modpage.yml`**, then the sources jar on the 0.4.0 release.

Steps 1 to 4 fit 0.4.0 and are cheap. Step 5 is part of finishing the split, which wants its own
plan and may or may not make 0.4.0; if it does not, the example's tier 2 assertion waits with it and
the README says the switch is 0.5.0.

---

## What this does not do

- **It does not open a socket.** The twelve anchors stay a closed enum. A consumer that needs a
  thirteenth is asking for a different model, and `DecorationAnchor.java:14-19` says why that is
  not data.
- **It does not render on a non-humanoid.** The layer binds to `HumanoidModel`; a quadruped is a
  fork, and the plan says so in `docs/api.md` rather than pretending a resolver hook would make it
  cheap.
- **It does not dispatch to a trinket slot.** The per-stack path stays private. A foreign slot
  needs an equip lifecycle the dispatcher does not see, and half of that is worse than none. If a
  trinkets-style mod asks, that is its own plan.
- **It does not open the colouring.** `FittingColour` stays sealed and the palette stays
  package-private. An emissive part is a rendering feature, not an API one.
- **It does not move packages.** The line is a listing and an annotation, not a refactor.
- **It does not make registration conditional.** See section 4.
- **It does not publish to a maven of its own.** Modrinth's is enough, and the VPS is not a build
  server. If Modrinth's maven ever cannot serve the sources jar by classifier, that is the moment to
  revisit, not before.

---

## Open

- **The licence sentence.** Section 1's wording is a recommendation. The copyright holder writes
  it, and the plan does not publish an artifact story until it is in the file.
- **The Modrinth project.** It does not exist (section 2), and only the author can create it. The
  slug `armor-pieces` is free today. Without it the artifact promise has no address, and the
  fallback is a static maven directory on armorpieces.com, which the plan recommends against
  because the site is not a build server and Modrinth's maven costs nothing.
- **Which release.** Steps 1 to 4 in 0.4.0 is the recommendation; the switch rides the split.
- **Whether `docs/api.md` is hand-written or generated.** Hand-written is the recommendation: the
  list is twenty classes and the prose beside each is the value. `ApiSurfaceTest` keeps it honest
  in the direction that matters, which is the file claiming something the jar does not have.
- **Whether the consumer example is published.** As a repo directory it is a test fixture. As a
  Modrinth project it is a template other modders clone, which is worth more and costs a licence
  decision of its own (the example should be permissively licensed, unlike the mod, or it is not a
  template).
- **Whether the mod bundles its content as a built-in pack.** Not this plan's question, but this
  plan's section 4 assumes the answer `compatibility.md` §5.3 recommends.
