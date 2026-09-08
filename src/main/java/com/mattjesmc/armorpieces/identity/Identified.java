package com.mattjesmc.armorpieces.identity;

import java.util.List;
import java.util.Optional;
import net.minecraft.resources.Identifier;

/**
 * A registry value that knows what it used to be called, and what it durably IS.
 *
 * <p>Implemented by the three datapack-defined content types a save can name - a part, a skin and a
 * cloth. Both of its answers exist for one reason: an item saved on Tuesday must still find its piece
 * on Friday, after the pack that ships it has been reorganised, renamed, split in two or replaced by
 * a different author's version.
 *
 * <p>The two are deliberately different mechanisms, and neither replaces the other:
 *
 * <ul>
 *   <li>{@link #formerIds()} is DECLARED. The piece says which ids it used to answer to, so a move
 *       an author makes on purpose costs one line in a file and works on saves written years before
 *       the line existed. It is the only one of the two that can rescue the 0.3.0 -&gt; 0.4.0 split,
 *       because a 0.3.0 save carries no uid to look anything up by.</li>
 *   <li>{@link #uid()} is AUTOMATIC. A lineage identifier minted once - by the content library for
 *       library content, by {@code tools/mint_uids.py} for the mod's own - and never changed after,
 *       so a move an author forgets to declare still resolves. It costs a field on disk and buys
 *       every FUTURE move for free.</li>
 * </ul>
 *
 * <p>Both are optional. A hand-written pack that has neither behaves exactly as one did before this
 * interface existed, which is the promise the mod makes about a part being three JSON files and a
 * PNG.
 *
 * <p>A uid is not a content hash. The content library gives every version of a piece a sha256 of its
 * file set, and that is the wrong identifier for this job: fix one pixel and it changes. What a save
 * needs is the identity of the THING, which survives its art being redrawn - so the uid is a lineage,
 * carried forward across every version of the piece, and opaque to this mod.
 *
 * @see Rebind the index these two are read through
 */
public interface Identified {
    /** Ids this value used to be registered under, in no particular order. Usually empty. */
    List<Identifier> formerIds();

    /** This value's lineage identifier, if it has been minted one. Opaque; never parsed. */
    Optional<String> uid();
}
