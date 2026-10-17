# NikonFirmwarePatch

[English](#english) · [简体中文](#简体中文)

## English

Build a local Nikon Z8 firmware update with the features you select:

- **ProRes quality:** HQ / Standard / LT / Proxy, with separate settings for shooting menu banks A/B/C/D.
- **HE RAW pre-capture:** save historical C15/C30 frames as HE NEF, up to one second and 30 frames, with direct camera playback and RAW+JPEG or RAW-only output.
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
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.02 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.02 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.02 --output build/combined

# RAW-only initial configuration (the same firmware also supports RAW+JPEG)
python patch.py "/path/to/Z_8_0311.bin" --features precapture --capture-mode raw-only --version 04.02 --output build/raw-only

# Or select the features interactively
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.02 --output build/chosen

# Independent verification of the combined build
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0402.bin" --features prores precapture
```

Without `--features` or `--interactive`, the legacy ProRes-only behavior is retained. `--version` accepts `NN.NN`; the example is not a required version. Choose a number higher than both the input and the firmware installed on your camera. The tool checks only the input version, not the camera. `--tag` is an optional lowercase letter and digit, default `p0`. A changed version number does not add compatibility or guarantee that the camera will accept an update. Downgrade/recovery is not guaranteed.

The output directory contains the update package, `manifest.json` and `SHA256SUMS.txt`. A pre-capture build also contains **`Z8PRE.CFG`**, enabling C15/C30 with a maximum of 30 historical frames. The default is `raw-jpeg`; `--capture-mode raw-only` selects RAW-only with a full-size embedded preview. **Replace old card configurations: this release requires the newly generated v2 `Z8PRE.CFG`.** Build updates from a fresh official package, not an earlier patched output. Later mode changes use `configure.py` and need no firmware reinstall. Inputs and existing output directories are never overwritten; an interrupted write may leave an incomplete directory without a success manifest.

### Before using RAW pre-capture

Read the full [preparation, shooting and limitations guide](docs/raw-precapture.md#english) before installing. In particular:

- Use photo mode, **FX, C15 or C30, JPEG fine L**, with pre-release capture enabled. Copy `Z8PRE.CFG` to the root of **one card only**. A missing/invalid configuration disables additional NEF saving; valid configurations on both cards also disable it.
- Half-press long enough to fill the history window, fully press briefly, then release. RAW+JPEG produces same-number `.NEF` and `.JPG`; RAW-only keeps only the selected history NEFs. **Frames after the full press remain JPEG-only in both modes.**
- **NEFs now enter the stock photo database for direct playback after writing.** Normal successful captures no longer need a power cycle to register.
- **Preview difference:** RAW+JPEG NEFs still embed only **1620×1080**; the camera displays their separate full-size JPEG. RAW-only NEFs embed **8256×5504** at the camera's NEF-preview quality. Both retain full-resolution RAW data.
- Wait for writing to finish. A 30-frame RAW-only trial took about 8 seconds; this is not an upper bound. Busy-card trials showed a temporary “!” pre-capture indicator while writes accumulated; allow the card to catch up.
- No lossless RAW, HE★, C60/C120, DX or post-release RAW. Failure fallbacks, missing metadata and software limits are explained in the guide.

### ProRes quality

The ProRes feature retains four quality choices, matching MOV identifiers and playback labels, quality-dependent recording-time estimates, and per-bank persistence. Its original patch bytes are unchanged. The shooting-screen icon does not identify the selected quality. Menu reset and bank-settings import/export remain unverified; bitrate varies with scene content.

These screenshots show the firmware UI in an emulator, not a camera recording test.

| Four options | Selected LT value |
|---|---|
| ![ProRes quality options](docs/images/prores-quality-options.png) | ![ProRes LT value](docs/images/prores-quality-value.png) |

### Verification and scope

The package has five modules and is 99,051,117 bytes. Input checks cover module identities, integrity, required code/data regions and patch-window fingerprints. Output verification independently checks the selected recipes, their shared loader edit, version fields and all bytes outside the declared windows. No force/bypass switch is provided. Selecting an already-applied or conflicting feature is rejected. Only the official 3.11 input is publicly supported; passing regional checks on another input is not a support or safety guarantee.

The registered RAW+JPEG implementation was hardware-tested with **59 pre-capture HE NEFs**, with paired playback visible without restarting. The current RAW-only full-preview implementation produced **223 pre-capture HE NEFs**: 59 in four planned C15/C30 trials and 164 in eight exploratory busy-card bursts. All fully decoded with Adobe DNG Converter 18.1.1; 139 frames with a readable timer matched their own embedded images. The other 84 frames had no visible timer and are not counted as image-correspondence checks. RAW+JPEG registration was not separately repeated on the latest preview revision; its unchanged path is covered by offline regression.

This is limited implementation testing, **not hardware certification of each newly generated public package or feature combination**. The public source changes file/protocol identifiers and the diagnostic identity; it does not distribute the tested private packages or inputs. Read the [validation scope](docs/validation.md).

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
- **HE RAW 预拍摄**：C15／C30 历史帧保存为 HE NEF，最长一秒、最多 30 张；支持机内直接回放及 RAW+JPEG／RAW-only。
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
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.02 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.02 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.02 --output build/combined

# RAW-only 初始配置（同一固件也支持 RAW+JPEG）
python patch.py "/path/to/Z_8_0311.bin" --features precapture --capture-mode raw-only --version 04.02 --output build/raw-only

# 或使用交互选择
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.02 --output build/chosen

# 独立核验组合包
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0402.bin" --features prores precapture
```

未指定 `--features` 或 `--interactive` 时，保留原先只添加 ProRes 的行为。`--version` 接受 `NN.NN`；示例不是规定版本。输出号必须高于输入号，安装时还须高于机身当前版本。脚本只能检查输入包，不读取机身版本。`--tag` 为一个小写字母加一位数字，默认 `p0`。改变版本号不代表支持其他固件布局，也不保证相机受理更新；不保证可以降级或恢复。

输出目录包含固件更新包、`manifest.json` 与 `SHA256SUMS.txt`。选择预拍摄后还生成 **`Z8PRE.CFG`**，默认启用 C15／C30、最多 30 张历史帧，模式为 `raw-jpeg`；`--capture-mode raw-only` 选择带全尺寸内嵌预览的 RAW-only。**本版需要新生成的 v2 `Z8PRE.CFG`，须替换卡上旧配置。** 更新时从全新的官方包构建，不叠加到旧补丁输出；之后可用 `configure.py` 切换模式，无需重装固件。脚本不会覆盖输入或已有输出目录；写盘中断可能留下没有成功 manifest 的不完整目录。

### RAW 预拍摄使用前必读

安装前请完整阅读[准备流程、拍摄步骤和限制](docs/raw-precapture.md#简体中文)。主要注意事项：

- 照片模式、**FX、C15 或 C30、JPEG fine L**，开启预拍摄。将 `Z8PRE.CFG` 放到**仅一张卡的根目录**。配置缺失／无效时不额外保存 NEF；两张卡都有有效配置时也不启用。
- 半按覆盖所选历史时长，短暂全按后松开。RAW+JPEG 生成同号 `.NEF`／`.JPG`；RAW-only 只保留选中历史帧的 NEF。**两种模式全按之后的连拍都仍是 JPEG-only。**
- **NEF 现在会登记到原厂照片库，写完后可直接回放。** 正常拍摄不再需要关开机补登记。
- **内嵌图有区别：** RAW+JPEG 的 NEF 仍只嵌 **1620×1080**，机内配对回放显示独立的全尺寸 JPEG；RAW-only 的 NEF 内嵌 **8256×5504**，采用相机 NEF 预览画质。两者 RAW 数据均为完整分辨率。
- 等写卡完成。30 张 RAW-only 的一次实测约 8 秒，不是耗时上限。写卡积压时探索性试验曾出现预拍“!”标志，需等待写卡追上。
- 没有无损、HE★、C60／C120、DX 或全按后的 RAW 连拍。异常回退、缺失元数据和软件限制见完整指南。

### ProRes 画质

保留四档画质、对应 MOV 编码标识与回放档名、按档位估算录制时间，以及菜单库分别保存设置。原有 ProRes 补丁字节保持不变。拍摄画面的图标不显示具体画质；重设视频菜单、设置文件导入／导出仍未验证；实际码率随场景变化。上方两张图是模拟器界面，不代表相机录制测试。

### 核验与支持边界

支持的更新包为五模块、99,051,117 字节。输入检查包括模块身份、封装完整性、依赖代码／数据和补丁窗口指纹；独立输出核验检查所选补丁、共同的装载范围、版本字段及所有窗口外字节。没有强制绕过选项；重复选择已应用或冲突的功能会被拒绝。公开支持仅限官方 3.11，其他输入即使通过局部指纹检查，也不代表兼容性或上机安全承诺。

原厂登记路线的 RAW+JPEG 已上机取得 **59 张预拍 HE NEF**，无需关开机即可看到配对回放。当前带全尺寸内嵌预览的 RAW-only 实现共取得 **223 张预拍 HE NEF**：四组计划 C15／C30 试验 59 张，八组边写卡边拍的探索性试验 164 张。全部由 Adobe DNG Converter 18.1.1 完整解码；计时器可见的 139 帧与自身内嵌图对应，另外 84 帧没有可见计时器，不计为图像对应验证。最新预览修订没有重新上机拍 RAW+JPEG，其未改变的路径由离线回归覆盖。

这些是有限的实现测试，**不等于公开脚本生成的每个新包或功能组合都已上机认证**。公开源码调整了文件／协议标识和诊断身份，不分发既有实测包或输入。具体见[验证范围](docs/validation.md)。

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
