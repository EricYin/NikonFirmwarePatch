# NikonFirmwarePatch

[English](#english) · [简体中文](#简体中文)

## English

Build a local Nikon Z8 firmware update with the features you select:

- **ProRes quality:** HQ / Standard / LT / Proxy, with separate settings for shooting menu banks A/B/C/D.
- **C15/C30 HE RAW capture:** select RAW / RAW+JPEG / JPEG in the ordinary Image quality menu, for both pre-release history and full-press/post-release frames. Both NEF modes include a full-size embedded preview and direct playback.
- **Both features in one build.**

**Experimental firmware — install at your own risk.** A successful build or test does not guarantee safe operation. Installation or use may cause lost images, corrupted cards, camera malfunction or permanent camera damage. You must assess and accept these risks before installing. To the extent permitted by applicable law, the repository, its authors and contributors provide no warranty and accept no liability for data loss, camera damage or other losses caused by building, installing or using the output. Do not use it for irreplaceable work. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

The publicly supported input is **official Nikon Z8 C 3.11**. Download it yourself from [Nikon](https://downloadcenter.nikonimglib.com/en/download/fw/606.html), subject to Nikon's terms. This repository distributes **no firmware, RAW files or prebuilt patch binaries**. It contains source, compatibility fingerprints and the existing menu screenshots. Output firmware is generated locally. The tool does not copy files to a card or operate a camera.

### Build

Requires Python 3.10+ and the pinned Python dependency. RAW pre-capture also requires Clang with the AArch64 target. The reviewed compiler is **Apple clang 21.0.0 (clang-2100.1.1.101)**. Another compiler is accepted only if it generates the identical reviewed patch bytes; otherwise the build stops. Use `--compiler /path/to/clang` to select it. ProRes-only does not require Clang.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Read-only compatibility check for the selected features
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --check

# Choose one of these builds; each output directory must be new
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.03 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.03 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.03 --output build/combined

# Or select the features interactively
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.03 --output build/chosen

# Independent verification of the combined build
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0403.bin" --features prores precapture
```

Without `--features` or `--interactive`, the legacy ProRes-only behavior is retained. `--version` accepts `NN.NN`; the example is not a required version. Choose a number higher than both the input and the firmware installed on your camera. The tool checks only the input version, not the camera. `--tag` is an optional lowercase letter and digit, default `p0`. A changed version number does not add compatibility or guarantee that the camera will accept an update. Downgrade/recovery is not guaranteed.

The output directory contains the update package, `manifest.json` and `SHA256SUMS.txt`. A pre-capture build also supplies **`Z8PRE.CFG`**, enabling ordinary-menu control for C15/C30. **Regenerate and replace old files: this release requires v3 configuration.** RAW/JPEG choices now come from the camera, so the former `--capture-mode`, `--frames` and `--c15-only` switches are removed. Build upgrades from a fresh official package, not an earlier pre-capture output. Inputs and existing output directories are never overwritten.

### Before using RAW pre-capture

Read the full [preparation, shooting and limitations guide](docs/raw-precapture.md#english) before installing. In particular:

- Use photo mode, **FX / full-size L, C15 or C30**, and put the new `Z8PRE.CFG` on **one card only**. Choose RAW, RAW+JPEG or one of six JPEG qualities in **MENU → Photo shooting menu → Image quality settings → Image quality**.
- **Both pre-release and full-press/post-release frames follow that choice**, including when pre-release capture is off. The history window remains up to one second / 30 frames; this is not a 30-frame limit on the full burst.
- **RAW and RAW+JPEG NEFs both embed 8256×5504 previews.** JPEG fine/normal/basic, with or without ★, are effective. RAW remains HE only; the RAW recording menu does not enable lossless or HE★ here.
- Successful NEFs enter the stock database for direct playback. The immediate RAW label may omit **L** until a restart, although the files record Large. **i-menu/dial shortcuts and the shooting display still show HSFC quality**, which may disagree with the ordinary menu this feature uses.
- Wait for writing to catch up. The “!” indicator can coincide with unavailable pre-capture history; one stress trigger saved current frames with no history. This does not provide unlimited sustained RAW capture. C60/C120, DX, HLG/HEIF and unsupported dual-card arrangements remain outside the added function.

### ProRes quality

The ProRes feature retains four quality choices, matching MOV identifiers and playback labels, quality-dependent recording-time estimates, and per-bank persistence. Its original patch bytes are unchanged. The shooting-screen icon does not identify the selected quality. Menu reset and bank-settings import/export remain unverified; bitrate varies with scene content.

These screenshots show the firmware UI in an emulator, not a camera recording test.

| Four options | Selected LT value |
|---|---|
| ![ProRes quality options](docs/images/prores-quality-options.png) | ![ProRes LT value](docs/images/prores-quality-value.png) |

### Verification and scope

The package has five modules and is 99,051,117 bytes. Input checks cover module identities, integrity, required code/data regions and patch-window fingerprints. Output verification independently checks the selected recipes, their shared loader edit, version fields and all bytes outside the declared windows. No force/bypass switch is provided. Selecting an already-applied or conflicting feature is rejected. Only the official 3.11 input is publicly supported; passing regional checks on another input is not a support or safety guarantee.

Hardware records for the current implementation contain **328 C15/C30 HE NEFs: 256 historical and 72 full-press/post-release frames**, plus an ordinary single-shot regression. All 328 passed file checks and complete Adobe DNG Converter 18.1.1 decoding, including full-size embedded previews. Menu tests covered RAW, RAW+JPEG fine/basic/fine★ and JPEG normal★; all six JPEG grades and the menu-setting composition also have bounded machine-code coverage.

Frame correspondence was checked by automated image comparison, supplemented by visual review where repeated timer readings made the score ambiguous. The reviewed readings matched their own RAW/JPEG frames; no frame mismatch was identified. This is limited implementation testing, **not hardware certification of each newly generated public package or feature combination**. See the [validation scope](docs/validation.md).

```sh
python tests/validate.py --stock "/path/to/Z_8_0311.bin" --report build/prores-tests.json
python tests/validate_features.py --stock "/path/to/Z_8_0311.bin" --report build/feature-tests.json
python tools/check_repository.py --staged
```

Tests use local temporary directories, without a camera. Enable the repository hook with `git config core.hooksPath .githooks`.

### Outlook and license

A future Log3G10 firmware option may be explored. It is not implemented, offered or promised by this release.

Original tool code is [GPL-3.0-only](LICENSE); Nikon firmware is not relicensed. Attribution and licensing scope are in [NOTICE.md](NOTICE.md). This project is not affiliated with Nikon.

### Acknowledgements

Thanks to [RdWing/z8-qemu](https://github.com/RdWing/z8-qemu) for its Z8 emulation work, [WonderLantern/z9-qemu](https://github.com/WonderLantern/z9-qemu) for the upstream camera model and tools, [WonderLantern/z7-qemu](https://github.com/WonderLantern/z7-qemu) for emulator and protocol references, and [QEMU](https://www.qemu.org/) for the emulation infrastructure. These projects helped the offline development and validation work; their code and binaries are not distributed here. See [NOTICE.md](NOTICE.md).

## 简体中文

从用户自行提供的 Nikon Z8 固件构建所选功能：

- **ProRes 画质选择**：HQ／Standard／LT／Proxy，A/B/C/D 拍摄菜单库分别保存档位。
- **C15／C30 HE RAW 连拍与预拍**：在普通“画质”菜单选择 RAW／RAW+JPEG／JPEG，预拍历史帧及全按后正式帧都生效；两种 NEF 模式均带全尺寸内嵌预览并支持直接回放。
- **可同时选择两项功能，构建一个更新包。**

**这是测试版固件，上机风险由使用者自行衡量和承担。** 构建、校验或既有测试通过不保证安全。安装或使用可能导致照片丢失、存储卡损坏、相机故障乃至永久损坏。在适用法律允许的范围内，本仓库及其作者、贡献者不作任何担保，不对构建、安装或使用本项目产物造成的数据损失、相机损失或其他损失承担责任。请勿用于不可重拍的重要工作。详见 [LICENSE](LICENSE) 和 [NOTICE.md](NOTICE.md)。

公开支持范围仅为**官方 Nikon Z8 C 3.11 固件**。请自行从 [Nikon 下载中心](https://downloadcenter.nikonimglib.com/en/download/fw/606.html)获取并遵守其条款。仓库**不提供固件本身、原始照片或预编译补丁二进制**，只提供源码、兼容性指纹及原有菜单截图。固件在本地生成；脚本不会自动写卡或操作相机。

### 构建

需要 Python 3.10+ 和固定的 Python 依赖。预拍摄功能还需支持 AArch64 的 Clang；当前审阅的编译器是 **Apple clang 21.0.0 (clang-2100.1.1.101)**。其他编译器只有生成完全相同的已审阅补丁字节才会被接受，否则停止构建。可用 `--compiler /path/to/clang` 指定。仅构建 ProRes 不需要 Clang。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# 对所选功能只读检查
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --check

# 三选一；输出目录必须尚不存在
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.03 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.03 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.03 --output build/combined

# 或使用交互选择
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.03 --output build/chosen

# 独立核验组合包
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0403.bin" --features prores precapture
```

未指定 `--features` 或 `--interactive` 时，保留原先只添加 ProRes 的行为。`--version` 接受 `NN.NN`；示例不是规定版本。输出号必须高于输入号，安装时还须高于机身当前版本。脚本只能检查输入包，不读取机身版本。`--tag` 为一个小写字母加一位数字，默认 `p0`。改变版本号不代表支持其他固件布局，也不保证相机受理更新；不保证可以降级或恢复。

输出目录包含更新包、`manifest.json` 和 `SHA256SUMS.txt`。选择预拍摄功能后还生成 **`Z8PRE.CFG`**，启用 C15／C30 的普通菜单控制。**本版需要 v3 配置，旧文件须重新生成并替换。** RAW／JPEG 改由机内选择，原 `--capture-mode`、`--frames` 和 `--c15-only` 参数已移除。升级时从全新的官方包构建，不叠加到旧预拍输出；脚本不覆盖输入或已有输出目录。

### RAW 预拍摄使用前必读

安装前请完整阅读[准备流程、拍摄步骤和限制](docs/raw-precapture.md#简体中文)。主要注意事项：

- 照片模式、**FX／全尺寸 L、C15 或 C30**，新 `Z8PRE.CFG` 只放在**一张卡的根目录**。通过 **MENU → 照片拍摄菜单 → 画质设置 → 画质** 选择 RAW、RAW+JPEG 或 JPEG 六档。
- **预拍历史帧、全按当帧和之后的正式帧都采用该选择**，关闭预拍也生效。历史窗口仍最长一秒／30 张，不代表整次拍摄最多 30 张。
- **RAW 和 RAW+JPEG 的 NEF 都内嵌 8256×5504 预览。** JPEG fine／normal／basic 及各自 ★ 均生效；RAW 只支持 HE，普通“RAW 记录”设置不会启用无损或 HE★。
- 正常 NEF 登记到原厂照片库，写完可直接回放。刚拍完 RAW 标签可能没有 **L**，重启后恢复，但文件已记录 Large。**i 菜单／拨盘快捷设置和取景显示仍对应 HSFC 画质**，可能与实际采用的普通菜单不一致。
- 等写卡追上后再继续。“!”可能伴随历史缓存不可用；压力试验曾有一次只保存正式帧、没有预拍历史。这不保证无限持续 RAW 拍摄。C60／C120、DX、HLG／HEIF 及未支持的双卡安排不在新增功能范围内。

### ProRes 画质

保留四档画质、对应 MOV 编码标识与回放档名、按档位估算录制时间，以及菜单库分别保存设置。原有 ProRes 补丁字节保持不变。拍摄画面的图标不显示具体画质；重设视频菜单、设置文件导入／导出仍未验证；实际码率随场景变化。上方两张图是模拟器界面，不代表相机录制测试。

### 核验与支持边界

支持的更新包为五模块、99,051,117 字节。输入检查包括模块身份、封装完整性、依赖代码／数据和补丁窗口指纹；独立输出核验检查所选补丁、共同的装载范围、版本字段及所有窗口外字节。没有强制绕过选项；重复选择已应用或冲突的功能会被拒绝。公开支持仅限官方 3.11，其他输入即使通过局部指纹检查，也不代表兼容性或上机安全承诺。

当前实现的上机记录包含 **328 张 C15／C30 HE NEF：256 张历史帧、72 张全按当帧及后拍帧**，另有普通单拍回归。328 张全部文件检查和 Adobe DNG Converter 18.1.1 完整解码通过，均带全尺寸内嵌预览。菜单上机覆盖 RAW、RAW+JPEG fine／basic／fine★ 及 JPEG normal★；六档 JPEG 和菜单三项组合另有原指令限定执行覆盖。

画面对应通过自动图像比对检查，并对计时器重复读数造成的评分歧义进行了目视复核；复核读数与本帧 RAW／JPEG 一致，未发现帧错配。这是有限的实现测试，**不是每个公开新包或功能组合的上机认证**。详细边界见[验证范围](docs/validation.md)。

```sh
python tests/validate.py --stock "/path/to/Z_8_0311.bin" --report build/prores-tests.json
python tests/validate_features.py --stock "/path/to/Z_8_0311.bin" --report build/feature-tests.json
python tools/check_repository.py --staged
```

测试只使用本地临时目录，不访问相机。可用 `git config core.hooksPath .githooks` 启用提交检查。

### 展望与许可

后续可能研究 Log3G10 固件选项；本次不实现、不提供，也不承诺交付时间。

工具原创代码采用 [GPL-3.0-only](LICENSE)，不改变 Nikon 固件的许可。来源和许可范围见 [NOTICE.md](NOTICE.md)。本项目与 Nikon 无隶属关系。

### 致谢

感谢 [RdWing/z8-qemu](https://github.com/RdWing/z8-qemu) 的 Z8 仿真工作、[WonderLantern/z9-qemu](https://github.com/WonderLantern/z9-qemu) 的上游相机模型与工具、[WonderLantern/z7-qemu](https://github.com/WonderLantern/z7-qemu) 的模拟器与协议参考，以及 [QEMU](https://www.qemu.org/) 的仿真基础设施。它们为本项目的离线开发和验证提供了帮助；本仓库不分发这些项目的源码或二进制。详见 [NOTICE.md](NOTICE.md)。
