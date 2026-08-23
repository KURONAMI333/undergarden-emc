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

## 1.5 1.21.1 dedicated server（headless・runClient を潰せない時の代替経路）

他セッションの dev client（runClient）が生きていて `_tools/runclient_fresh.sh` を撃てない場合、
dedicated server で同じ parse 経路を検証できる（ProjectE の `pe_custom_conversions` はサーバ側 datapack として読まれるため）。
実測・再現確認済み（2026-08-24）。置き場は `_research/v1201-hosts/server` と同じ並びの `_research/v1211-hosts/server`。

### セットアップ（初回のみ）

```bash
export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-21.0.10.7-hotspot"
cd "C:/Users/naoki/dev/projects/minecraft-mod-dev/_research/v1211-hosts"
curl -sL -o neoforge-21.1.227-installer.jar \
  https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.227/neoforge-21.1.227-installer.jar
cd server
"$JAVA_HOME/bin/java" -jar ../neoforge-21.1.227-installer.jar --installServer
printf "eula=true\n" > eula.txt
mkdir -p mods
cp "C:/Users/naoki/curseforge/minecraft/Instances/2605_nf21_Magi/mods/ProjectE-1.21.1-PE1.1.0.jar" mods/
cp "C:/Users/naoki/dev/workspace/undergarden_hosts/The_Undergarden-1.21.1-0.9.6.jar" mods/
cp "<mod-073-undergarden-emc>/build/libs/undergarden_emc-0.1.0.jar" mods/
```

`server.properties` に **RCON を有効化する**（stop コマンド到達性の唯一の確実な経路。§2 の stdin/FIFO は 1.20.1 で全滅した）:

```
level-name=world
online-mode=false
enable-rcon=true
rcon.port=25575
rcon.password=<任意>
```

### 起動と操作（毎回）

```bash
export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-21.0.10.7-hotspot"
cd "C:/Users/naoki/dev/projects/minecraft-mod-dev/_research/v1211-hosts/server"
nohup "$JAVA_HOME/bin/java" @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.227/win_args.txt nogui > run.out 2>&1 &
```

`win_args.txt` を直接指定する（1.20.1 の unix_args.txt 問題と同型の Windows/Git Bash 地雷を避ける。1.21.1 の NeoForge installer は `run.bat`/`run.sh` の両方を最初から生成するので、1.20.1 のような `run.sh` 単独失敗は起きない。念のため win_args.txt を直接使う形に統一する）。

**起動した Windows PID を必ず確認する**（`jps -l` で `cpw.mods.bootstraplauncher.BootstrapLauncher` が新規に出る。`bash` の `$!` は MSYS PID で Windows PID と一致しないので使わない）。

### 重要: 1.21.1 の EMC マッピングは起動直後には走らない

1.20.1（PE1.0.1）と違い、**1.21.1（PE1.1.0）は `OnDatapackSyncEvent` でしか EMC マッピングを計算しない**
（`moze_intel.projecte.PECore.dataPackSync`、逆アセンブル実測）。この event はプレイヤーの join 時か `/reload` でしか飛ばない。
**headless dedicated server はプレイヤーが繋がないので、`Done` まで起動しただけでは EMC マッピングは一度も走らない**
（`Registered N EMC values` も `Considering file` も出ない）。

RCON で `reload` を1回撃つ:

```bash
python3 - <<'PYEOF'
import socket, struct
HOST, PORT, PASSWORD = "127.0.0.1", 25575, "<設定したパスワード>"
def pkt(sock, rid, ptype, payload):
    data = struct.pack("<ii", rid, ptype) + payload.encode("utf8") + b"\x00\x00"
    sock.send(struct.pack("<i", len(data)) + data)
def read(sock):
    length = struct.unpack("<i", sock.recv(4))[0]
    data = b""
    while len(data) < length:
        data += sock.recv(length - len(data))
    return struct.unpack("<ii", data[:8]), data[8:-2].decode("utf8", "replace")
s = socket.create_connection((HOST, PORT), timeout=10)
pkt(s, 1, 3, PASSWORD); read(s)
pkt(s, 2, 2, "reload"); print(read(s)[1])
s.close()
PYEOF
```

### ワールドロード後に見るログ（1.21.1 の実際のログレベル）

**`Considering file` は DEBUG レベルでしか出ない**（`logs/latest.log` には出ず、`logs/debug.log` にのみ出る）。
`Registered N EMC values.` は `Server thread/INFO` で `logs/latest.log`（console 出力）にも出る。
ロガー表記は latest.log では短縮形 `mo.pr.PECore`、debug.log ではフル `moze_intel.projecte.PECore`（同一ロガー）。

- `logs/debug.log`: `grep "Considering file undergarden:pe_custom_conversions" logs/debug.log`
- `logs/latest.log`（または console 出力）: `grep "Registered .* EMC values" logs/latest.log`
- `JsonParseException` / `JsonSyntaxException` / `Unknown registry key` の0件確認は `logs/debug.log` 全体をロガー別に見る（`minecraft/RecipeManager` 由来は責任外、`PECore` 由来だけが対象）

### サーバーの正常終了

**RCON で `stop` を送る**。1.20.1 で試した stdin EOF / named pipe は届かなかったが、RCON は確実に届く:

```bash
# 上と同じ python スニペットの reload を stop に変えるだけ
```

`stop` 到達を `jps -l` で確認する（プロセスが消えていること）。**taskkill は使わない**（RCON が確立していれば不要）。

### 既知の制約: `dumpToFile=true` は 1.21.1（PE1.1.0）でクラッシュする

`config/ProjectE/mapping.toml` の `dumpToFile` を `true` にして `/reload` すると、
`mo.pr.PECore` が **ERROR** で `Failed to convert custom conversion to json: Value must not be zero: 0; ...`
（および `Element with unknown name: 0`）を大量に吐き、`mapping_dump.json` が**一切生成されない**。

**本アドオンが原因ではない**: 本アドオンの jar を `mods/` から抜いた状態（ProjectE + Undergarden のみ）でも
同じエラーが再現する（2026-08-24 実測）。`Ore-Blacklist-Mapper` / `Raw-Ore-Blacklist-Mapper` を無効化しても
`Value must not be zero` は消えない（`Element with unknown name` は減るが0にはならない）。
**ProjectE 1.1.0 の `DumpToFileCollector` 側の既知バグとして扱う**（EMC=0 の custom conversion を含む環境では
dump 書き出しがコード全体を通して失敗する）。

したがって **1.21.1 セルでは §3 の dump による機械照合ができない**。parse エラー0件の確認と
`Registered N` の総数比較（addon 込み/抜きの差分）までが実測できる範囲。
将来 ProjectE がこのバグを直したら §3 の手順をそのまま使える（JSON 構造自体は 1.20.1 と同名の
`mapping_dump.json`＝ハイフン無しで想定通りのはず。未検証）。

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
   **このリストは 1.21.1 専用（dreadrock 系2件を含む10件）。1.20.1 セルでは dreadrock 系の id 自体が存在しないため実在8件のみで照合する**
   （`_handoff/UNDERGARDEN_EMC_SPEC.md` §1.4。このリストをそのまま 1.20.1 の検証にコピーしない）。

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
