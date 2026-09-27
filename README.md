# add-BSP-microPython

公式MicroPythonで直接サポートされていないNordic系モジュール／基板向けのBSPを追加していくリポジトリです。

## 方針

- MicroPython本体は `micropython/` submoduleとして追従
- nRF52系はMicroPython native nrf portを使用
- nRF91系は将来的にZephyr portを使用
- BSP固有ファイルは `boards/` 側で管理し、upstream MicroPythonを直接改変しない
- ローカルとGitHub Actionsで同じ `scripts/build.py` を使用

## 対応ターゲット

| ID | Module | SoC | Backend | Status |
| --- | --- | --- | --- | --- |
| `isp1807` | Insight SiP ISP1807-LR | nRF52840 | MicroPython nrf | Initial BSP |

## Build

```bash
git clone --recurse-submodules https://github.com/NekomuraHana/add-BSP-microPython.git
cd add-BSP-microPython
python3 scripts/build.py isp1807
```

既にclone済みの場合は:

```bash
git submodule update --init
python3 scripts/build.py isp1807
```

生成物はMicroPython側のbuild directoryに出力されます。

```text
micropython/ports/nrf/build-ISP1807_LR-s140/
├─ firmware.hex
├─ firmware.bin
└─ firmware.elf
```
