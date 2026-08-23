package com.kuronami.undergardenemc;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

/**
 * The Undergarden ProjectE EMC — a data-only integration. EMC values live in
 * {@code data/undergarden/pe_custom_conversions/} and are loaded by ProjectE
 * via datapack reload; this class only provides the {@code @Mod} entry point so
 * the project fits the standard NeoForge build / runClient pipeline.
 */
@Mod(UndergardenEMC.MODID)
public final class UndergardenEMC {
    public static final String MODID = "undergarden_emc";
    public static final String VERSION = "0.1.0";
    private static final Logger LOGGER = LogUtils.getLogger();

    public UndergardenEMC(IEventBus modBus) {
        LOGGER.info("The Undergarden ProjectE EMC v{} loading — EMC via data/undergarden/pe_custom_conversions", VERSION);
    }
}
