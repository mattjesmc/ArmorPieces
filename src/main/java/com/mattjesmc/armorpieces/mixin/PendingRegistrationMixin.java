package com.mattjesmc.armorpieces.mixin;

import com.google.gson.JsonElement;
import com.mattjesmc.armorpieces.pack.PackFile;
import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Decoder;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.packs.resources.Resource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Tells {@link PackFile} which file is being read, for the length of one element's decode.
 *
 * <p>This is the only point in the game where an element's id and the pack its bytes came from are
 * both in hand, and it is two frames above every codec that can find something wrong. Without it a
 * salvaged field can only warn about itself - "an anchor named `nose` was dropped" - which tells a
 * pack author nothing they can open and edit. With it every warning raised anywhere underneath names
 * the file: "armorpieces_coral:coral_crown, from pack coral".
 *
 * <p>Targeted by name rather than by class literal: the record is {@code protected} inside
 * {@code RegistryLoadTask}, so it cannot be named from another package at all.
 *
 * <p>Both loads are covered. {@code loadFromResource} is a datapack being read on a server;
 * {@code loadFromNetwork} is a registry arriving from one, where there is no pack to name but the id
 * is still worth having.
 *
 * <p>It changes nothing: two thread-local writes around a call that was going to happen anyway, on
 * the load path only, and {@code done()} on RETURN - which is every exit, because both methods answer
 * with an {@code Either} rather than by throwing.
 */
@Mixin(targets = "net.minecraft.resources.RegistryLoadTask$PendingRegistration")
public class PendingRegistrationMixin {
    @Inject(method = "loadFromResource", at = @At("HEAD"))
    private static <T> void armorpieces$readingFile(
        final Decoder<T> decoder,
        final RegistryOps<JsonElement> ops,
        final ResourceKey<T> key,
        final Resource resource,
        final CallbackInfoReturnable<Either<T, Exception>> info
    ) {
        PackFile.reading(key, resource.sourcePackId());
    }

    @Inject(method = "loadFromResource", at = @At("RETURN"))
    private static <T> void armorpieces$readFile(
        final Decoder<T> decoder,
        final RegistryOps<JsonElement> ops,
        final ResourceKey<T> key,
        final Resource resource,
        final CallbackInfoReturnable<Either<T, Exception>> info
    ) {
        PackFile.done();
    }

    @Inject(method = "loadFromNetwork", at = @At("HEAD"))
    private static <T> void armorpieces$readingSynced(
        final Decoder<T> decoder,
        final RegistryOps<Tag> ops,
        final ResourceKey<T> key,
        final Tag value,
        final CallbackInfoReturnable<Either<T, Exception>> info
    ) {
        PackFile.reading(key, null);
    }

    @Inject(method = "loadFromNetwork", at = @At("RETURN"))
    private static <T> void armorpieces$readSynced(
        final Decoder<T> decoder,
        final RegistryOps<Tag> ops,
        final ResourceKey<T> key,
        final Tag value,
        final CallbackInfoReturnable<Either<T, Exception>> info
    ) {
        PackFile.done();
    }
}
