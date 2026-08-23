"""Generate data/undergarden/pe_custom_conversions/undergarden_emc.json (NeoForge 1.21.1).

Values come from `_handoff/UNDERGARDEN_EMC_SPEC.md` SS3 (values.before, 65 id) and SS4
(groups.infuser, 4 conversions). Every number below is copied from that spec, not
invented here -- this script only encodes the ProjectE 1.21.1 JSON shape.

`raw_cloggrum` / `raw_froststeel` intentionally have no entry: both sit in
`c:raw_materials`, which ProjectE's RawMaterialsBlacklistMapper forces to EMC 0
(setValueBefore/After) regardless of what a datapack writes. Per spec SS2.2, the value
is placed on the ingot instead -- the same shape ProjectE itself uses for vanilla
metals (`c:ingots/iron` = 256 in `values.before`, nothing on iron ore or raw iron).

ProjectE NSS schema (1.21.1): values.before = list of {type,emc_value,id}; groups use
{type:"projecte:item", id/tag:...}. Tags are `{"type":"projecte:item","tag":"c:..."}`,
never `{"type":"projecte:tag",...}` (see PROJECTE_EMC_NOTES.md trap). This mod uses no
tags, only plain item ids.
"""

import json
import os

OUT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "src",
    "main",
    "resources",
    "data",
    "undergarden",
    "pe_custom_conversions",
    "undergarden_emc.json",
)

# Hand-set EMC values, spec SS3. Comment on each id = spec's "根拠" column, condensed.
BEFORE = {
    # SS3.1 S terrain (14)
    "depthrock": (1, "dimension's base stone; vanilla cobblestone anchor"),
    "shiverstone": (2, "cold-layer base stone; cobbled_deepslate anchor"),
    "tremblecrust": (4, "deepest base stone; tuff/basalt anchor"),
    "dreadrock": (
        8,
        "one layer below tremblecrust, sole rogdorium host; layer order 1->2->4->8",
    ),
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
    "deepturf": (1, "vanilla short_grass anchor"),
    "ashen_deepturf": (1, "same as deepturf"),
    "frozen_deepturf": (1, "same as deepturf"),
    # SS3.2 P gatherables (13)
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
    "gronglet": (32, "grongle fruit; crimson/warped_fungus anchor; infuser input"),
    "utherium_growth": (
        32,
        "utherium vein decor, zero crafting use; fungus band, not ore band",
    ),
    "gloomgourd": (144, "c:pumpkins/normal anchor; yields seeds, carvable"),
    "carved_gloomgourd": (144, "worldgen-carved state; carving itself has no EMC cost"),
    # SS3.3 P mushrooms (17)
    "blood_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "indigo_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "ink_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "puff_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "veil_mushroom": (32, "vanilla red/brown_mushroom anchor"),
    "blood_mushroom_stem": (
        32,
        "giant mushroom stem, building material; matches minecraft:logs(32)",
    ),
    "indigo_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "ink_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "puff_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "veil_mushroom_stem": (32, "matches minecraft:logs(32)"),
    "blood_mushroom_cap": (
        64,
        "non-silk drops up to 2 mushrooms(32); 2x32=64 floor blocks break profit",
    ),
    "indigo_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "ink_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "puff_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "veil_mushroom_cap": (64, "non-silk drops up to 2 mushrooms(32); 2x32=64 floor"),
    "engorged_blood_mushroom_cap": (
        256,
        "non-silk drops 2-6 blood_globule + 0-2 blood_mushroom; 6x32+2x32=256 floor",
    ),
    "blood_globule": (
        32,
        "engorged cap's dedicated drop; zero recipe use, decor-drop band",
    ),
    # SS3.4 D everyday drops (8)
    "goo_ball": (
        32,
        "c:slime_balls member; vanilla slime_ball anchor (keeps sticky_piston parity)",
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
        "c:bones member but bone(144) too low; tusk->4 bone_meal needs 4x48=192 to protect bone_meal(48)",
    ),
    # SS3.5 M metals/gems (7)
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
        "common corrupted-mob drop; 9 shards = utheric_cluster(2304), lands above gold(2048)",
    ),
    "regalium_crystal": (
        2048,
        "non-tool 'glowing metal' for beacon/decor/trim only; role parity with gold_ingot(2048)",
    ),
    "rogdorium": (
        4608,
        "dreadrock-only deepest ore, consumed once per infuser catalyst use; 4x froststeel, 512x9 nugget(512)",
    ),
    "forgotten_nugget": (
        1024,
        "sole source is the forgotten_guardian mini-boss; 9 = forgotten_ingot(9216), above diamond(8192)",
    ),
    "rogdoric_ancient_root": (
        1024,
        "in minecraft:logs(32) tag but non-silk break drops 1-2 rogdorium_nugget(512); 2x512=1024 floor overrides the tag's 32",
    ),
    # SS3.6 other (6)
    "forgotten_upgrade_smithing_template": (
        7497,
        "role/duplication cost matches minecraft:netherite_upgrade_smithing_template; reuse ProjectE's own value",
    ),
    "music_disc_mammoth": (
        2048,
        "ProjectE's disc band; c:music_discs has no 1.21.1 value, so restored by hand",
    ),
    "music_disc_limax_maximus": (
        2048,
        "ProjectE's disc band; c:music_discs has no 1.21.1 value, so restored by hand",
    ),
    "music_disc_relict": (
        2048,
        "ProjectE's disc band; c:music_discs has no 1.21.1 value, so restored by hand",
    ),
    "music_disc_gloomper_anthem": (
        2048,
        "ProjectE's disc band; c:music_discs has no 1.21.1 value, so restored by hand",
    ),
    "music_disc_gloomper_secret": (
        2048,
        "ProjectE's disc band; c:music_discs has no 1.21.1 value, so restored by hand",
    ),
}

# Infuser conversions, spec SS4. The catalyst slot is consumed once per craft
# (InfuserBlockEntity#infuse), so it is priced as part of the input cost.
GROUPS = {
    "infuser": {
        "comment": (
            "The Undergarden infuser is a custom recipe type, so ProjectE cannot derive "
            "these. The catalyst slot is consumed once per craft (InfuserBlockEntity#infuse), "
            "so it is part of the cost."
        ),
        "conversions": [
            {
                "output": {
                    "type": "projecte:item",
                    "id": "undergarden:utherium_crystal",
                },
                "count": 1,
                "ingredients": [
                    {"type": "projecte:item", "id": "undergarden:utheric_cluster"},
                    {"type": "projecte:item", "id": "undergarden:rogdorium"},
                ],
            },
            {
                "output": {
                    "type": "projecte:item",
                    "id": "undergarden:rogdoric_gronglet",
                },
                "count": 1,
                "ingredients": [
                    {"type": "projecte:item", "id": "undergarden:gronglet"},
                    {"type": "projecte:item", "id": "undergarden:rogdorium"},
                ],
            },
            {
                "output": {"type": "projecte:item", "id": "undergarden:denizen_totem"},
                "count": 1,
                "ingredients": [
                    {"type": "projecte:item", "id": "undergarden:ancient_root"},
                    {"type": "projecte:item", "id": "undergarden:rogdorium"},
                ],
            },
            {
                "output": {
                    "type": "projecte:item",
                    "id": "undergarden:utheric_gronglet",
                },
                "count": 1,
                "ingredients": [
                    {"type": "projecte:item", "id": "undergarden:gronglet"},
                    {"type": "projecte:item", "id": "undergarden:utherium_crystal"},
                ],
            },
        ],
    }
}


def main() -> None:
    doc = {
        "replace": False,
        "comment": (
            "The Undergarden EMC integration for ProjectE (KURONAMI). Values per "
            "_handoff/UNDERGARDEN_EMC_SPEC.md. Ore blocks and raw_cloggrum/raw_froststeel "
            "intentionally have no EMC: ProjectE's OreBlacklistMapper / "
            "RawMaterialsBlacklistMapper force them to 0 (c:ores / c:raw_materials). "
            "Gear (tools/armor/trims) intentionally has no EMC."
        ),
        "values": {
            "before": [
                {"type": "projecte:item", "emc_value": v, "id": f"undergarden:{k}"}
                for k, (v, _comment) in BEFORE.items()
            ]
        },
        "groups": GROUPS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")
    n_groups = sum(len(g["conversions"]) for g in GROUPS.values())
    print(
        f"values.before={len(BEFORE)} groups.conversions={n_groups} -> {os.path.normpath(OUT)}"
    )


if __name__ == "__main__":
    main()
