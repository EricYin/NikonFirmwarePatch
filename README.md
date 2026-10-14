# NikonFirmwarePatch

[English](#english) · [简体中文](#简体中文)

## English

Adds **ProRes 422 HQ / Standard / LT / Proxy** quality selection to compatible Nikon Z8 firmware, with separate quality settings for shooting menu banks A/B/C/D.

Currently supports the **Z8 3.11 firmware layout and compatible derivatives**. Every input must pass the compatibility checks. Other camera models and firmware layouts are not supported.

### Features

- Four quality options in the video menu, selecting the corresponding recording profile.
- Matching MOV codec identifiers, encoder names and playback labels.
- Quality-dependent recording-time estimates and per-bank settings.
- Custom output version numbers and an independent output verifier.

The tool changes only the declared ProRes patch windows, version fields and checksums. All other firmware bytes are preserved. Firmware must be supplied by the user; this repository contains source code, compatibility fingerprints and emulator screenshots. The tool builds local files and does not automatically copy them to a card or update a camera.

<a id="screenshots"></a>

### Emulator screenshots / 模拟器截图

These captures show the firmware UI running in an emulator. They illustrate menu selection, not camera recording or encoding performance.

截图来自模拟器中的固件界面，仅展示菜单选择，不代表相机实拍或编码性能测试。

| Four quality options / 四档画质 | Selected LT value / 主菜单显示 LT |
|---|---|
| ![Four ProRes quality options](docs/images/prores-quality-options.png) | ![ProRes LT selected in the video menu](docs/images/prores-quality-value.png) |

### Setup

Requires Python 3.10 or newer. Building uses Capstone; compatibility checks and independent verification use the Python standard library.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the following commands from the repository root. Replace `/path/to/input.bin` with the path to a **complete firmware update package**, keeping quotes around paths containing spaces.

```sh
# Read-only compatibility and integrity check
python patch.py "/path/to/input.bin" --check

# Build into a new directory
python patch.py "/path/to/input.bin" --version 03.23 --output build/prores-0323

# Independently verify the output against the input
python verify.py "/path/to/input.bin" "build/prores-0323/Z_8_0323.bin"
```

The output directory contains `Z_8_0323.bin`, `manifest.json` and `SHA256SUMS.txt`. The manifest records input/output hashes, modules, source hashes and edit ranges. Existing output directories are rejected; the input file is never overwritten. A failed build does not produce a success manifest, though an interrupted write may leave an incomplete output directory.

`--version` accepts `NN.NN`, such as `03.23` or `04.07`, and updates all version fields and the output filename. The output version must be higher than the input version; before installing, also choose a number higher than the version currently installed on the camera. The tool does not read the camera's version. Changing the displayed version does not add support for a different firmware layout.

`--tag` optionally sets the internal revision suffix: one lowercase letter and one digit, default `u0`.

### Compatibility and validation

The supported update package has five modules and is 99,051,117 bytes long. Checks cover module identities, package integrity, required code/data regions and the original bytes in every patch window. Already patched or conflicting inputs are rejected. There is no option to bypass these checks.

Hardware validation has covered all four ProRes profiles, clip identification and complete decoding. Separate LT/Proxy settings in banks A/C survived battery removal. Bank copying has also been checked with bounded CPU execution and menu emulation.

The shooting-screen ProRes icon does not show the selected quality. Resetting the video menu to HQ and importing/exporting bank settings have not been verified. Recording bitrate varies with scene content; offline verification is not a camera test of each newly built package.

### Development tests

Provide an original Z8 3.11 package. Tests use temporary local directories and do not access a camera.

```sh
python tests/validate.py \
  --stock "/path/to/stock/Z_8_0311.bin" \
  --report build-validation.json
```

Tests cover the reference ProRes output, custom versions, preservation of bytes outside the patch, damaged or conflicting inputs, repeated patching, existing-output protection, checks under `python -O`, and rejection of unrelated byte changes even after all package checksums have been repaired.

Before committing, run `python tools/check_repository.py --staged`. Enable the included hook with `git config core.hooksPath .githooks`.

### License

The tool's original source code is licensed under [GPL-3.0-only](LICENSE). This does not relicense Nikon firmware or grant permission to distribute it. See [NOTICE.md](NOTICE.md) for attribution and license scope. This project is not affiliated with Nikon.

## 简体中文

为兼容的 Nikon Z8 固件增加 **ProRes 422 HQ / Standard / LT / Proxy 四档画质选择**，并让 A/B/C/D 拍摄菜单库分别保存档位。

当前支持 **Z8 3.11 固件布局及兼容派生包**。所有输入均须通过兼容性检查；尚不支持其他机型或固件布局。

### 功能

- 在视频菜单中选择四档画质，录制时使用对应编码档位。
- 同步 MOV 编码标识、编码器名称和回放档名。
- 按档位估算剩余录制时间，支持各拍摄菜单库分别保存设置。
- 自定义输出版本号，并提供独立输出校验器。

工具只改变规定的 ProRes 补丁窗口、版本字段和校验值，其他固件字节均保持不变。固件由用户自行提供；本仓库包含源码、兼容性指纹及模拟器截图。工具只构建本地文件，不会自动复制到卡或升级相机。

界面示例见上方的[模拟器截图](#screenshots)。

### 安装

需要 Python 3.10 或更新版本。构建使用 Capstone；兼容性检查和独立校验只需 Python 标准库。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

以下命令在仓库根目录执行。将 `/path/to/input.bin` 换成自己的**完整固件更新包**路径；路径含空格时保留引号。

```sh
# 只读检查输入兼容性与完整性
python patch.py "/path/to/input.bin" --check

# 构建到一个尚不存在的目录
python patch.py "/path/to/input.bin" --version 03.23 --output build/prores-0323

# 相对于原输入独立核验输出
python verify.py "/path/to/input.bin" "build/prores-0323/Z_8_0323.bin"
```

输出目录含 `Z_8_0323.bin`、`manifest.json` 和 `SHA256SUMS.txt`。Manifest 记录输入／输出哈希、模块、源码哈希及改动范围。已有输出目录会被拒绝，输入文件不会被覆盖。构建失败不会生成成功 manifest，写盘中断时可能留下未完成的输出目录。

`--version` 接受 `NN.NN`，如 `03.23` 或 `04.07`，并同步修改所有版本字段和输出文件名。输出号须高于输入号；安装前还应选择高于机身当前版本的号。工具不读取机身版本。修改显示版本号不代表兼容其他固件布局。

`--tag` 可选，用于设置内部修订后缀：一个小写字母加一位数字，默认为 `u0`。

### 兼容性与验证范围

支持的更新包包含五个模块，大小为 99,051,117 字节。检查包括模块身份、封装完整性、依赖的代码／数据区域，以及每个补丁窗口的原字节。已打过补丁或存在冲突的输入会被拒绝，没有绕过检查的选项。

真机已验证四档 ProRes 录制、片段识别及完整解码；A/C 库分别设置 LT/Proxy 后，扣电池仍能保留。菜单库复制还经过限定范围的 CPU 原指令执行和菜单仿真验证。

拍摄画面的 ProRes 图标不会显示当前画质档位。重设视频菜单是否回到 HQ，以及设置文件导入／导出尚未验证。录制码率随场景变化；离线核验通过不等于每个新构建包都已上机测试。

### 开发测试

提供原厂 Z8 3.11 固件包即可运行。测试只使用本地临时目录，不访问相机。

```sh
python tests/validate.py \
  --stock "/path/to/stock/Z_8_0311.bin" \
  --report build-validation.json
```

测试覆盖 ProRes 输出基准、自定义版本、补丁以外字节保持、损坏或冲突输入、重复打补丁、已有输出保护、`python -O` 下的检查，以及修复全部封装校验后仍存在额外改动的拒绝测试。

提交前运行 `python tools/check_repository.py --staged`；可用 `git config core.hooksPath .githooks` 启用随仓库提供的检查钩子。

### 许可证

工具原创代码采用 [GPL-3.0-only](LICENSE)。该许可不会改变 Nikon 固件的许可，也不授予固件分发权。来源和许可范围见 [NOTICE.md](NOTICE.md)。本项目与 Nikon 无隶属关系。
