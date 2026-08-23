# mod-073-undergarden-emc 検証手順

EMC 値は `_handoff/UNDERGARDEN_EMC_SPEC.md` で確定済み（1.21.1 = 64 値 + infuser 変換4本 / 1.20.1 = 52 値）。
`pe_custom_conversions/undergarden_emc.json` は各セルの `tools/generate_emc.py` が生成する。
この手順で実機検証する。

## 前提: ホストスタック

- 1.21.1 NeoForge: `runclient-hosts.gradle`（gitignored）で ProjectE 1.21.1(PE1.1.0) + The Undergarden 1.21.1(0.9.6) を `localRuntime` で流し込み済み。The Undergarden の `neoforge.mods.toml` は neoforge/minecraft 以外の mod 依存を宣言していないので追加ホストは不要
- 1.20.1 Forge: `_research/v1201-hosts/server/mods/` に ProjectE 1.20.1(PE1.0.1) + The Undergarden 1.20.1(0.8.14) を配置済み。同様に追加ホストは不要（`META-INF/mods.toml` は forge/minecraft のみ依存）

---

## 1. 1.21.1 runClient

```bash
export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-21.0.10.7-hotspot"
RUNCLIENT_OWNER=undergarden-emc _tools/runclient_fresh.sh \
  "C:/Users/naoki/dev/projects/minecraft-mod-dev/mod-073-undergarden-emc"
```

`./gradlew runClient` を直接叩かない（二重起動防止のガードが効かなくなる）。`RUNCLIENT_OWNER` は必ず付ける（並行セッションの実機確認を潰さないため）。

### ワールドロード後に見るログ（parse エラーの有無）

`moze_intel.projecte.PECore` 由来の行だけを見る:

- `Considering file undergarden:pe_custom_conversions/undergarden_emc.json` — このアドオンの JSON が読まれたこと
- `Registered N EMC values` — N > 0 なら値付けが反映されている

`JsonParseException` が出た場合、ロガーで責任を切り分ける:
- ロガーが `moze_intel.projecte.PECore` → このアドオンの JSON の書式誤り。修正対象
- ロガーが `minecraft/RecipeManager`（The Undergarden 自身のレシピ JSON 由来） → 責任外。無視してよい

---

## 2. 1.20.1 Forge dedicated server

JDK17 で起動する（Forge 1.20.1 の要件。1.21.1 の JDK21 と混同しない）。

```bash
cd "C:/Users/naoki/dev/projects/minecraft-mod-dev/_research/v1201-hosts/server"
# user_jvm_args.txt の java 実体が JDK17 を指していることを事前に確認
./run.sh nogui
```

### 見るログ（`logs/latest.log`）

1.21.1 と同じ切り分け方針。ロガー `mo.pr.PECore`（1.20.1 は短縮表記）の行だけ見る:

- `Considering file undergarden:pe_custom_conversions/undergarden_emc.json`
- `Registered N EMC values`
- `EMC Exploit` WARN は正常な助言出力（バニラ nugget→ingot 等にも出る既知の仕様。無視してよい）
- `JsonParseException` は `mo.pr.PECore` 由来だけ見る。The Undergarden 自身の `minecraft/RecipeManager` 由来は責任外

出所: `kuronami-mods/knowledge/PROJECTE_EMC_NOTES.md`（1.20.1 展開節。Iron's Spellbooks/Forbidden & Arcanus/Malum の3 mod で同じ手順を実証済み）。

server は起動しない（このタスクのスコープ外。EMC jar 自体がまだプレースホルダのため意味が無い）。

---

## 3. parse エラー 0 だけでは足りない — EMC dump による機械照合

このアドオンは約80値＋groups 変換＋母岩(depthrock/dreadrock/shiverstone/tremblecrust)の重複入口を持つ。
parse が通っても、値の設計方針（`kuronami-mods/knowledge/PROJECTE_EMC_NOTES.md` の P2 均衡・最安ルート原則）に違反していないかは別途確認が要る。

### EMC dump の取り方（実測・ProjectE jar 解析で確認済み）

**1.21.1 (PE1.1.0)**: `config/ProjectE/mapping.toml` の

```toml
dumpToFile = false   # これを true にする
```

を `true` にしてサーバ/クライアントを1回起動すると、EMC マッピング計算完了時に **`config/ProjectE/mapping_dump.json`** へ全コンバージョン + 確定 EMC 値が書き出される（`moze_intel.projecte.emc.EMCMappingHandler` → `DumpToFileCollector`、jar 内 class 逆アセンブルで確認）。

**1.20.1 (PE1.0.1)**: `config/ProjectE/mapping.toml` の `[general]` セクションの

```toml
dumpEverythingToFile = false   # これを true にする
```

を `true` にすると **`config/ProjectE/mappingdump.json`** に同様の内容が書かれる（ファイル名がハイフン無しで 1.21.1 と異なる点に注意）。

両方とも常時 true のままにしない（生成コストがあるため既定 false）。ダンプを取ったら false に戻す。

### dump を取る前に確認する対応条件: blacklist mapper が有効であること

本アドオンは「鉱石ブロックと raw 素材は ProjectE 自身が 0 にする」ことを前提に、値を ingot 側だけに置いている
（`_handoff/UNDERGARDEN_EMC_SPEC.md` §2.2）。この前提は設定で外せる。

`config/ProjectE/mapping.toml` の `[mappers]` セクションで、次の2つが `enabled = true` であることを見る:

- `Ore Blacklist Mapper`（`c:ores` / 1.20.1 は `forge:ores` を 0 にする）
- `Raw Material Blacklist Mapper`（1.20.1 は `Raw Ore Blacklist Mapper`。`c:raw_materials` / `forge:raw_materials` を 0 にする）

既定はどちらも有効（`MappingConfig` が `IEMCMapper.isAvailable()` を既定値にしており、両マッパーとも true。
ProjectE jar の逆アセンブルで実測）。**無効化された環境は本アドオンの対応外**で、
`raw_cloggrum` / `raw_froststeel` と各鉱石ブロックに値が付き、下の照合1〜3が落ちる。
照合が落ちたときは、まずここを見てからアドオン側を疑う。

### dump を使って照合する3点

1. **ORE_BLOCK（鉱石ブロック10件）に EMC が付いていないこと**
   対象 id: `undergarden:depthrock_cloggrum_ore` / `depthrock_regalium_ore` / `depthrock_utherium_ore` / `dreadrock_rogdorium_ore` / `dreadrock_utherium_ore` / `shiverstone_cloggrum_ore` / `shiverstone_froststeel_ore` / `shiverstone_regalium_ore` / `shiverstone_utherium_ore` / `tremblecrust_utherium_ore`
   dump JSON をこれらの id で grep し、`values`（または values セクション）に出現しないこと、または出現していても他コンバージョンから導出された値が無いことを確認する。

2. **VANILLA_DROP 系（7件: `depthrock_coal_ore`/`depthrock_diamond_ore`/`depthrock_gold_ore`/`depthrock_iron_ore`/`shiverstone_coal_ore`/`shiverstone_diamond_ore`/`shiverstone_iron_ore`）に触れておらず、バニラ coal/iron/gold/diamond の EMC が動いていないこと**
   ProjectE 単体（The Undergarden 抜き）で一度 dump を取り、`minecraft:coal` / `minecraft:iron_ingot` / `minecraft:gold_ingot` / `minecraft:diamond` の EMC 値を控える。The Undergarden + このアドオン込みで dump を取り直し、同じ4値が変化していないことを突合する。

3. **母岩の異なる鉱石が同じ落とし物に収束し、最安ルートでの引き下げが起きていないこと**
   例: `raw_cloggrum` は `depthrock_cloggrum_ore` と `shiverstone_cloggrum_ore` の双方からドロップする（母岩違い・同一ドロップ）。dump JSON で `raw_cloggrum` の確定 EMC 値と、それを産む conversion 群を確認し、複数の母岩経由の経路があっても値が単一で確定していること（ProジェクトE は最安ルートを採用するため、母岩側に値を付けていなければここは自動的に安全なはずだが、`values.before` の PRIM 側の値付け1箇所だけになっているかを dump で直接確認する）。

4. **値が付かないことが正常な id が、実際に付いていないこと**
   `undergarden:carved_gloomgourd` / `gloom_o_lantern` / `shard_o_lantern` に EMC が無いこと
   （vanilla の `carved_pumpkin` / `jack_o_lantern` と同じ状態。仕様 §6-10）。
   ここに値が出ていたら、彫刻1回ごとに +144 EMC の経路が開いている。
   あわせて仕様 §6-8 の 0 落ち7 id（`depthrock_pebble` / `coarse_deepsoil` / depthrock 系スラブ4種 / `sediment_glass_pane`）が
   0 で出るのは正常。バグとして扱わない。

未確定点: dump JSON のトップレベル構造（`values` オブジェクトのキー形式が NSS 文字列か item id かなど）は jar 逆アセンブルからは確定できていない。実際に1回 dump を取ってから grep パターンを決める。
