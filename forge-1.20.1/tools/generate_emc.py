"""Generate data/undergarden/pe_custom_conversions/undergarden_emc.json
for ProjectE on Minecraft 1.20.1 (PE1.0.1).

Values come from `_handoff/UNDERGARDEN_EMC_SPEC.md` SS5 (values.before, 52 id), which
is the 1.21.1 SS3 table (64 id) minus the 7 id that don't exist on 1.20.1 (SS5.2 "1.21.1
にあって1.20.1に無い") minus the 5 music discs, which 1.20.1 does NOT need written by
hand: `minecraft:music_discs` already carries EMC 2048 in PE1.0.1's own defaults.json,
so writing them here would just duplicate a value ProjectE already supplies (SS5.2
"書かないが値は付く"). This cell has no `groups`: the infuser mechanism (and rogdorium,
its sole fuel/catalyst) does not exist on 1.20.1 (SS5.1).

`raw_cloggrum` / `raw_froststeel` intentionally have no entry, same reasoning as the
1.21.1 sibling: both sit in `forge:raw_materials`, which ProjectE's
RawOreBlacklistMapper forces to EMC 0 regardless of what a datapack writes. Per spec
SS2.2 the value lives on the ingot instead.

ProjectE 1.20.1's CustomConversionFile reads `values.before` as a MAP ({id: emc}), not
the array-of-objects form used by ProjectE 1.21.1 (PE1.1.0). No `replace` key and no
`groups` key on this cell (see PROJECTE_EMC_NOTES.md SS1.20.1 展開 table).

Usage: python tools/generate_emc.py
"""

import json
import os

OUT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "src",
    "data",
    "undergarden",
    "pe_custom_conversions",
    "undergarden_emc.json",
)

# Hand-set EMC values, spec SS5.2 (= SS3 minus the 7 id absent on 1.20.1, minus the 5
# music discs auto-valued via #minecraft:music_discs). Comment on each id = spec's
# "根拠" column, condensed. Values are identical to the 1.21.1 sibling.
BEFORE = {
    # SS3.1 S terrain (13; dreadrock dropped, SS5.2)
    "depthrock": (1, "dimension's base stone; vanilla cobblestone anchor"),
    "shiverstone": (2, "cold-layer base stone; cobbled_deepslate anchor"),
    "tremblecrust": (4, "deepest base stone; tuff/basalt anchor"),
    "smog_vent": (
        1,
        "decorative rock, non-silk drops depthrock; same value blocks break profit",
    ),
    "sediment": (1, "smelts to glass; vanilla sand anchor"),
    "deepsoil": (1, "vanilla dirt anchor"),
    "deepsoil_farmland": (1, "tilled deepsoil, nothing else changes"),
    "deepturf_block": (
        1,
        "grass_block equivalent; non-silk drops deepsoil(1), same value",
    ),
    "ashen_deepturf_block": (1, "same as deepturf_block"),
    "frozen_deepturf_block": (1, "same as deepturf_block"),
    "deepturf": (1, "vanilla grass (short_grass on 1.21.1) anchor"),
    "ashen_deepturf": (1, "same as deepturf"),
    "frozen_deepturf": (1, "same as deepturf"),
    # SS3.2 P gatherables (11; utherium_growth dropped, SS5.2)
    "glitterkelp": (1, "vanilla kelp anchor; keeps derived dried_kelp value at 1"),
    "hanging_grongle_leaves": (
        1,
        "only leaf not covered by minecraft:leaves tag; matched by hand",
    ),
    "blisterberry": (16, "vanilla sweet_berries anchor"),
    "rotten_blisterberry": (16, "same bush's alternate drop, same value"),
    "underbeans": (16, "vanilla glow_berries anchor"),
    "ditchbulb": (16, "cave cluster; glow_berries anchor"),
    "droopvine_item": (16, "cave_vines equivalent; glow_berries anchor"),
    "seeping_ink": (16, "shears-only self-drop decor; vanilla ink_sac anchor"),
    "mushroom_veil": (16, "hanging decor plant; small_flowers anchor"),
    "gronglet": (32, "grongle fruit; crimson/warped_fungus anchor"),
    "gloomgourd": (144, "minecraft:pumpkin anchor; yields seeds, carvable"),
    # `carved_gloomgourd` deliberately has no entry, mirroring vanilla
    # `minecraft:carved_pumpkin`: no recipe produces it, so ProjectE derives no value for
    # it either. Carving costs 144 (the gourd) and returns 4 gloomgourd_seeds derived at
    # 144/4 = 36 each, so the operation breaks even. Pricing the carved block would make
    # every carve a free +144. `gloom_o_lantern` / `shard_o_lantern` therefore carry no
    # EMC, exactly as vanilla `jack_o_lantern` does not.
    # SS3.3 P mushrooms (14; puff_mushroom/_stem/_cap dropped, SS5.2 -- 1.21.1-only)
    "blood_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "indigo_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "ink_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "veil_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "blood_mushroom_stem": (
        32,
        "giant mushroom stem, building material; matches minecraft:logs(32)",
    ),
    "indigo_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "ink_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "veil_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "blood_mushroom_cap": (
        64,
        "non-silk drops up to 2 mushrooms(32); 2x32=64 floor blocks break profit",
    ),
    "indigo_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "ink_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "veil_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "engorged_blood_mushroom_cap": (
        256,
        "non-silk drops 2-6 blood_globule + 0-2 blood_mushroom; 6x32+2x32=256 floor",
    ),
    "blood_globule": (
        32,
        "engorged cap's dedicated drop; zero recipe use, decor-drop band",
    ),
    # SS3.4 D everyday drops (8; unchanged)
    "goo_ball": (
        32,
        "forge:slimeballs member; vanilla slime_ball anchor (keeps sticky_piston parity)",
    ),
    "goo": (128, "non-silk drops 1-4 goo_ball(32); 4x32=128 floor"),
    "mogmoss": (
        48,
        "sheared mog fur, rug-crafting parallels wool; minecraft:wool anchor",
    ),
    "blue_mogmoss": (48, "smog_mog variant, same value"),
    "raw_dweller_meat": (64, "vanilla beef anchor"),
    "raw_gloomper_leg": (64, "vanilla porkchop/mutton anchor"),
    "raw_gwibling": (64, "minecraft:fishes; cod/salmon anchor"),
    "brute_tusk": (
        192,
        "forge:bones member but bone(144) too low; tusk->4 bone_meal needs 4x48=192 to protect bone_meal(48)",
    ),
    # SS3.5 M metals/gems (5; rogdorium, rogdoric_ancient_root dropped, SS5.2)
    "cloggrum_ingot": (
        288,
        "early-game metal, just above iron(256) since cloggrum tools outlast iron; 32x9 nugget(32)",
    ),
    "froststeel_ingot": (
        1152,
        "mid-game metal, 4.5x iron, below diamond(8192); 128x9 nugget(128)",
    ),
    "utheric_shard": (
        256,
        "common corrupted-mob drop; 9 shards = utherium_crystal(2304) on 1.20.1's own conversion chain",
    ),
    "regalium_crystal": (
        2048,
        "non-tool 'glowing metal' for beacon/decor/trim only; role parity with gold_ingot(2048)",
    ),
    "forgotten_nugget": (
        1024,
        "sole source is the forgotten_guardian mini-boss; 9 = forgotten_ingot(9216), above diamond(8192)",
    ),
    # SS3.6 other (1; music discs dropped -- auto-valued via #minecraft:music_discs, SS5.2)
    "forgotten_upgrade_smithing_template": (
        7497,
        "role/duplication cost matches minecraft:netherite_upgrade_smithing_template; reuse ProjectE's own value",
    ),
}


def main() -> None:
    doc = {
        "comment": (
            "The Undergarden EMC integration for ProjectE (KURONAMI). Values per "
            "_handoff/UNDERGARDEN_EMC_SPEC.md SS5. Ore blocks and "
            "raw_cloggrum/raw_froststeel intentionally have no EMC: ProjectE's "
            "OreBlacklistMapper / RawOreBlacklistMapper force them to 0 (forge:ores / "
            "forge:raw_materials). Gear (tools/armor/trims) intentionally has no EMC. "
            "No infuser on 1.20.1, so no groups here."
        ),
        "values": {
            "before": {f"undergarden:{k}": v for k, (v, _comment) in BEFORE.items()},
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"values.before={len(BEFORE)} -> {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
