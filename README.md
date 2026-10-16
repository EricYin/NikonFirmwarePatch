# NikonFirmwarePatch

[English](#english) · [简体中文](#简体中文)

## English

Build a local Nikon Z8 firmware update with the features you select:

- **ProRes quality:** HQ / Standard / LT / Proxy, with separate settings for shooting menu banks A/B/C/D.
- **HE RAW pre-capture:** save historical C15/C30 frames as HE NEF alongside their JPEGs, up to one second and 30 frames.
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
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.01 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.01 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.01 --output build/combined

# Or select the features interactively
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.01 --output build/chosen

# Independent verification of the combined build
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0401.bin" --features prores precapture
```

Without `--features` or `--interactive`, the legacy ProRes-only behavior is retained. `--version` accepts `NN.NN`; the example is not a required version. Choose a number higher than both the input and the firmware installed on your camera. The tool checks only the input version, not the camera. `--tag` is an optional lowercase letter and digit, default `p0`. A changed version number does not add compatibility or guarantee that the camera will accept an update. Downgrade/recovery is not guaranteed.

The output directory contains the update package, `manifest.json` and `SHA256SUMS.txt`. A pre-capture build also contains **`Z8PRE.CFG`**, enabling C15/C30 with a maximum of 30 historical frames. Keep this configuration with the corresponding build. Inputs and existing output directories are never overwritten; an interrupted write may leave an incomplete directory without a success manifest.

### Before using RAW pre-capture

Read the full [preparation, shooting and limitations guide](docs/raw-precapture.md#english) before installing. In particular:

- Use photo mode, **FX, C15 or C30, JPEG fine L**, with pre-release capture enabled. Copy `Z8PRE.CFG` to the root of **one card only**. A missing/invalid configuration disables additional NEF saving; valid configurations on both cards also disable it.
- Half-press long enough to fill the selected history window, fully press briefly, then release. The historical frames receive same-number `.NEF` and `.JPG` files. **Frames after the full press remain JPEG-only.**
- Wait for writing to finish. The 30-frame hardware trial took about 15 seconds including JPEGs; this is not an upper bound or a throughput guarantee. Do not retrigger while writing during initial use.
- **NEFs are not registered immediately in the camera's photo database.** After writing finishes, normal power-off/power-on reloads the files; the tested camera then showed the RAW icon in playback. The NEFs already exist on the card before that reload.
- No RAW-only choice, no lossless RAW, no HE★, no C60/C120 or DX support in this patch. Missing metadata and software-compatibility limits are listed in the guide.

### ProRes quality

The ProRes feature retains four quality choices, matching MOV identifiers and playback labels, quality-dependent recording-time estimates, and per-bank persistence. Its original patch bytes are unchanged. The shooting-screen icon does not identify the selected quality. Menu reset and bank-settings import/export remain unverified; bitrate varies with scene content.

These screenshots show the firmware UI in an emulator, not a camera recording test.

| Four options | Selected LT value |
|---|---|
| ![ProRes quality options](docs/images/prores-quality-options.png) | ![ProRes LT value](docs/images/prores-quality-value.png) |

### Verification and scope

The package has five modules and is 99,051,117 bytes. Input checks cover module identities, integrity, required code/data regions and patch-window fingerprints. Output verification independently checks the selected recipes, their shared loader edit, version fields and all bytes outside the declared windows. No force/bypass switch is provided. Selecting an already-applied or conflicting feature is rejected. Only the official 3.11 input is publicly supported; passing regional checks on another input is not a support or safety guarantee.

Hardware testing of the feature implementation produced **68 pre-capture HE NEFs** across C15 0.3/1 s and C30 0.3/1 s, including a 30-frame burst. All fully decoded with Adobe DNG Converter 18.1.1. This is limited testing of the implementation, **not a hardware certification of every package produced by this public builder or of the new feature combinations**. The public source also uses a new configuration namespace and clears diagnostic filename padding. Read the [validation scope](docs/validation.md).

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
- **HE RAW 预拍摄**：C15／C30 的历史帧另存为与 JPEG 同号的 HE NEF，最长一秒、最多 30 张。
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
python patch.py "/path/to/Z_8_0311.bin" --features prores --version 04.01 --output build/prores
python patch.py "/path/to/Z_8_0311.bin" --features precapture --version 04.01 --output build/precapture
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 04.01 --output build/combined

# 或使用交互选择
python patch.py "/path/to/Z_8_0311.bin" --interactive --version 04.01 --output build/chosen

# 独立核验组合包
python verify.py "/path/to/Z_8_0311.bin" "build/combined/Z_8_0401.bin" --features prores precapture
```

未指定 `--features` 或 `--interactive` 时，保留原先只添加 ProRes 的行为。`--version` 接受 `NN.NN`；示例不是规定版本。输出号必须高于输入号，安装时还须高于机身当前版本。脚本只能检查输入包，不读取机身版本。`--tag` 为一个小写字母加一位数字，默认 `p0`。改变版本号不代表支持其他固件布局，也不保证相机受理更新；不保证可以降级或恢复。

输出目录包含固件更新包、`manifest.json` 与 `SHA256SUMS.txt`。选择预拍摄后还生成 **`Z8PRE.CFG`**，默认启用 C15／C30、最多 30 张历史帧，应与对应构建一起使用。脚本不会覆盖输入或已有输出目录；写盘中断可能留下没有成功 manifest 的不完整目录。

### RAW 预拍摄使用前必读

安装前请完整阅读[准备流程、拍摄步骤和限制](docs/raw-precapture.md#简体中文)。主要注意事项：

- 照片模式、**FX、C15 或 C30、JPEG fine L**，开启预拍摄。将 `Z8PRE.CFG` 放到**仅一张卡的根目录**。配置缺失／无效时不额外保存 NEF；两张卡都有有效配置时也不启用。
- 半按快门使预拍缓存覆盖所选时长，然后短暂全按并松开。历史帧生成同号 `.NEF` 和 `.JPG`；**全按之后的连拍帧依然只有 JPEG**。
- 等待写卡完成。实拍 30 张的一组连同 JPEG 约用 15 秒写完，不是耗时上限或持续吞吐保证。首次使用不要在写卡过程中再次触发。
- **NEF 不会立即登记到相机照片库。** 完成写卡后正常关机再开机，重新加载后实测可在回放中看到 RAW 标识；重新加载前 NEF 已存在于卡上。
- 没有 RAW-only 选项，没有无损压缩或 HE★，不支持 C60／C120 和 DX。缺失元数据和软件兼容限制见详细指南。

### ProRes 画质

保留四档画质、对应 MOV 编码标识与回放档名、按档位估算录制时间，以及菜单库分别保存设置。原有 ProRes 补丁字节保持不变。拍摄画面的图标不显示具体画质；重设视频菜单、设置文件导入／导出仍未验证；实际码率随场景变化。上方两张图是模拟器界面，不代表相机录制测试。

### 核验与支持边界

支持的更新包为五模块、99,051,117 字节。输入检查包括模块身份、封装完整性、依赖代码／数据和补丁窗口指纹；独立输出核验检查所选补丁、共同的装载范围、版本字段及所有窗口外字节。没有强制绕过选项；重复选择已应用或冲突的功能会被拒绝。公开支持仅限官方 3.11，其他输入即使通过局部指纹检查，也不代表兼容性或上机安全承诺。

功能实现已进行有限上机测试：C15 0.3／1 秒、C30 0.3／1 秒共取得 **68 张预拍 HE NEF**，包括一组 30 张，均由 Adobe DNG Converter 18.1.1 完整解码。这**不等于公开脚本生成的每个新包或新功能组合都已上机验证**。公开源码另调整了配置命名，并清零诊断尾标的文件名填充区。具体见[验证范围](docs/validation.md)。

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
