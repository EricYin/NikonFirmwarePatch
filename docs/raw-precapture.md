# HE RAW pre-capture / HE RAW 预拍摄

[English](#english) · [简体中文](#简体中文)

## English

**Experimental; use at your own risk.** Read the [risk notice](../README.md#english), back up photographs and settings, and assess the risk before installing. Tests do not rule out data loss or camera damage. Public support is limited to official Nikon Z8 C 3.11 as the build input.

### Choose the historical-frame output

The firmware now registers NEFs in the stock photo database and writes them through the stock still-image writer. After writing finishes, normal successful captures can be played back directly; a power cycle is no longer required to register them.

| Configuration | Selected historical-frame files | JPEG embedded inside each NEF | Camera playback |
|---|---|---|---|
| `raw-jpeg` (default) | Same-number `.NEF` + `.JPG` | **1620×1080**, reduced preview | Registered RAW+JPEG pair; displays the separate full-size JPEG |
| `raw-only` | `.NEF` only; the matching JPEG reservation is cancelled after the NEF is written | **8256×5504**, full-size preview at the camera's NEF-preview quality, plus 1620×1080 | Registered NEF; full-size embedded preview |
| Configuration absent or invalid | Original JPEG behavior | No additional NEF | Original JPEG playback |

**RAW+JPEG does not yet have the full-size embedded NEF preview.** A standalone NEF viewer may therefore show a smaller preview, even though the RAW pixel data remains full resolution. Only the supported `raw-only` configuration embeds the full-size preview. It uses the camera's NEF-preview quantization, approximately JPEG basic / IJG quality 75, keeping the tested NEFs around 21.3 MB rather than embedding the much larger fine JPEG. The standalone JPEG in `raw-jpeg` retains fine quality.

These choices apply only to the selected frames **before the full press**. Frames captured after the full press remain **JPEG-only in both modes**, including `raw-only`. A smaller configured ceiling leaves older, unselected history frames as JPEGs as well. This is not continuous RAW shooting at 15/30 fps.

### Build and prepare

1. Supply a fresh official C 3.11 package and build with `--features precapture` or `--features prores precapture`. Set `--capture-mode raw-jpeg` (default) or `--capture-mode raw-only`. Verify against that same original input and retain the manifest/checksums. To replace an earlier public pre-capture build, **build again from the official input, not from the already-patched output**. Choose an output version higher than the camera's installed version; the script cannot read the camera's version or guarantee downgrade/recovery.
2. Read Nikon's [official update instructions and precautions](https://downloadcenter.nikonimglib.com/en/download/fw/606.html). Installation is manual. Use adequate battery power and do not interrupt the update. The tool neither writes a card nor operates a camera.
3. Back up a card and leave ample free space. Hardware trials used SD; timings on other cards are not established. For initial use, insert only the intended recording card. Copy the locally generated update package to its root, update through the camera's firmware menu following Nikon's procedure, and confirm your chosen version.
4. Copy the **newly generated `Z8PRE.CFG`** to the root of **one card only**. This is a 64-byte binary file, not editable text. The new configuration format is v2: **regenerate and replace an older `Z8PRE.CFG`**. A v1 configuration is rejected by this firmware and produces no extra NEFs. A missing/invalid configuration, valid configurations on both cards, or a stop file prevents additional NEF saving. Formatting deletes the configuration; copy it back if you want to re-enable the feature.
5. Use photo mode, **FX, C15 or C30, JPEG fine L**, and enable pre-release capture. This JPEG processing setting is also required in `raw-only`; the configuration controls whether the historical JPEG file is kept. No new camera menu selects RAW-only. The ordinary RAW-recording menu does not switch the extra NEFs from HE to lossless or HE★.
6. Start with C15, 0.3 s of pre-release capture and a short post-release duration. Find **Pre-Release Capture Options** by name; numbering may vary. See Nikon's [release modes](https://onlinemanual.nikonimglib.com/z8/en/release_mode_33.html) and [pre-release settings](https://onlinemanual.nikonimglib.com/z8/en/csmd_pre-release_capture_options_233.html). Begin with a static scene, manual focus and a visible timer; AF tracking, automatic capture and every exposure/processing combination have not been tested.

```sh
# One firmware supports both configurations; this selects the initially supplied file
python patch.py "/path/to/Z_8_0311.bin" --features precapture --capture-mode raw-only --version 04.02 --output build/raw-only
python verify.py "/path/to/Z_8_0311.bin" "build/raw-only/Z_8_0402.bin" --features precapture

# Change the configuration later, without rebuilding or reinstalling the firmware
python configure.py --capture-mode raw-jpeg --output build/config-paired
python configure.py --capture-mode raw-only --output build/config-raw-only
# Optional smaller ceiling / C15-only
python configure.py --capture-mode raw-only --frames 5 --c15-only --output build/config-small
# Optional timing/diagnostic footer; normally omitted
python configure.py --capture-mode raw-only --diagnostic-footer --output build/config-diagnostic
```

Copy just the chosen `Z8PRE.CFG` to the recording card while the camera is off and the card is safely accessible. Both default modes enable C15/C30 and retain up to 30 history frames. The mode changes the configuration, not the firmware patch bytes. The optional footer is omitted by default; do not hand-edit flags.

### Shoot, wait, check

1. Half-press long enough to fill the selected history window; initially, use at least one second. A shorter half-press can yield fewer frames.
2. Fully press briefly, then release. The camera saves selected historical frames according to the table above and saves post-release frames as JPEGs.
3. Wait for card writing to finish before playback, normal power-off or card removal. Do not remove power or the card while writing. Check the registered NEF or RAW+JPEG pair directly in playback; a restart is not part of the normal workflow.
4. Initially let each burst finish before triggering another. In eight exploratory busy-card bursts, all recorded history frames were saved and decoded, but the pre-capture icon temporarily showed **“!”** while writes accumulated. The association with backlog is observed; its exact meaning and threshold are not established. Wait for writing to catch up and the normal pre-capture indication to return. These trials do not guarantee unrestricted retriggering.
5. On a computer, check the expected file set and full RAW decoding. In `raw-only`, the selected history numbers should have no separate JPEG; later JPEG-only numbers are expected. In `raw-jpeg`, keep both members, remembering that the NEF's own preview is reduced.

With a filled buffer and a 30-frame ceiling:

| Mode | Pre-release duration | Historical NEFs | Hardware coverage |
|---|---:|---:|---|
| C15 | 0.3 s | 5 | Tested |
| C15 | 0.5 s | 8 | Original count table; not separately tested |
| C15 | 1 s | 15 | Tested |
| C30 | 0.3 s | 9 | Tested |
| C30 | 0.5 s | 15 | Original count table; not separately tested |
| C30 | 1 s | 30 | Tested |

In the limited trials, 30 RAW-only NEFs took roughly 7.6–8.0 s to write, about 0.26 s per NEF; the registered RAW+JPEG trial took about 13.2 s for its 30-frame group. These are measured examples, not completion deadlines or throughput guarantees. Scene, card, processing settings and queued earlier bursts affect the wait. A later frame in the busy-card trial waited up to 23.8 s before its NEF finished.

### Limits and failure handling

- C15/C30, FX and HE NEF only. No DX, C60/C120, lossless RAW, HE★ or post-release RAW. RAW+JPEG full-size embedded previews are not implemented.
- Database registration and direct playback have been tested. In-camera deletion, protection, transfer, near-full-card behavior and all dual-card combinations have not been fully tested. Back up card originals before experimenting with these operations.
- Adobe DNG Converter 18.1.1 fully decoded the tested files. NX Studio, Lightroom and other converters have not been directly tested. Optional factory metadata is still missing, including lens-correction blocks, a grayscale subimage and some XMP correction data; full software and lens-correction equivalence is unverified.
- Thirty retained compressed-frame allocations use approximately 519 MB. Busy-card retriggers and long post-release bursts can exhaust buffers or alter capture behavior. Limited successful trials do not rule out dropped frames, freezes or resets.
- The per-NEF budget is 1.5 s. The stock-writer path checks the elapsed time after the write returns; the fallback checks between I/O calls. Neither can interrupt a blocked call or guarantee against a hang.
- If registration fails, the implementation can fall back to JPEG plus a separately written NEF, using `.NE_` then rename. That fallback NEF may require a later database rescan. Other failures can produce JPEG-only output, a partial/missing NEF or **`Z8PRESTP.BIN`**. The stop file disables subsequent extra NEF writes and survives restart. Some precondition failures only skip NEF output, so check counts even without a stop file.
- If the RAW-only preview-quality step cannot be confirmed, the NEF falls back to its reduced 1620×1080 preview. If a RAW-only failure subsequently saves the processed JPEG, it can have the lower NEF-preview quality while its metadata still says FINE. This is a failure/recovery path, not normal output.
- On missing files, `.NE_`, a stop file, errors, freezes or resets, stop testing and preserve the files. After card access ends, back up the card and disable the feature. Investigate before deleting a stop file or retrying.

To return to original JPEG pre-capture, remove `Z8PRE.CFG` while the camera is off and the card is safely accessible. This does not uninstall the firmware, disable an included ProRes feature, or guarantee rollback. See the [validation scope](validation.md) for the distinction between implementation tests and newly built packages.

## 简体中文

**测试版本，风险自负。** 安装前阅读[风险说明](../README.md#简体中文)，备份照片和设置，自行衡量上机风险。测试通过不能排除数据丢失或相机损坏。公开支持的构建输入仅限官方 Nikon Z8 C 3.11。

### 选择历史帧的保存方式

本版会把 NEF 登记到原厂照片库，并通过原厂静态图像写入函数保存。正常拍摄写完后可以直接回放，无需通过关开机补登记。

| 配置 | 选中的历史帧文件 | NEF 内嵌 JPEG | 机内回放 |
|---|---|---|---|
| `raw-jpeg`（默认） | 同号 `.NEF` + `.JPG` | **1620×1080，缩小的预览** | 登记为 RAW+JPEG 配对，显示独立的全尺寸 JPEG |
| `raw-only` | 只有 `.NEF`；成功写完后撤销同号 JPEG 的预留 | **8256×5504，全尺寸预览**，采用相机 NEF 预览的画质档；另有 1620×1080 | 登记为 NEF，显示全尺寸内嵌预览 |
| 缺少配置或配置无效 | 原有 JPEG 行为 | 不新增 NEF | 原有 JPEG 回放 |

**RAW+JPEG 模式的 NEF 目前仍没有全尺寸内嵌图。** 电脑单看 NEF 时可能只显示较小预览，但 RAW 原始像素数据仍为完整分辨率。只有当前提供的 `raw-only` 配置内嵌全尺寸图，使用相机 NEF 预览的量化档，约为 JPEG basic／IJG 质量 75；实测 NEF 约 21.3 MB，避免嵌入体积很大的 fine 主图。`raw-jpeg` 中独立保存的 JPEG 仍为 fine。

以上选择只影响**全按之前选中的历史帧**。两种模式全按之后的连拍都仍是 **JPEG-only**，包括 `raw-only`。配置较小的帧数上限时，更早、未被选中的历史帧也仍保存为 JPEG。这不是持续每秒拍摄 15／30 张 RAW 的功能。

### 构建与准备

1. 从一份全新的官方 C 3.11 更新包构建，选择 `--features precapture` 或 `--features prores precapture`，用 `--capture-mode raw-jpeg`（默认）或 `--capture-mode raw-only` 选择初始配置。对照同一份原始输入运行核验并保留 manifest／校验值。替换之前的公开预拍版本时，**重新从官方输入构建，不要叠加到已经打过预拍补丁的输出上**。输出版本号须高于机身现有版本；脚本不读取机身版本，不保证降级或恢复。
2. 阅读 Nikon 的[官方更新步骤和注意事项](https://downloadcenter.nikonimglib.com/en/download/fw/606.html)。手动决定并执行安装，保证电量充足，不中断更新。工具不会写卡或操作相机。
3. 备份存储卡并留足空间。上机试验使用 SD，其他卡的耗时未验证。初次使用只插入用于记录的一张卡，把本地生成的更新包放到卡根目录，按官方流程从机身固件菜单更新并核对版本。
4. 将**本次新生成的 `Z8PRE.CFG`** 放到**仅一张卡的根目录**。它是 64 字节二进制文件，不是文本。本版配置格式为 v2：**旧的 `Z8PRE.CFG` 必须重新生成并替换**；v1 配置会被拒绝，不产生额外 NEF。缺少／无效配置、两张卡都有有效配置或存在停止文件时，都不会额外保存 NEF。格式化会删除配置，重新启用需复制回来。
5. 设置照片模式、**FX、C15 或 C30、JPEG fine L**，开启预拍摄。`raw-only` 也需要该 JPEG 处理设置；配置决定是否保留历史帧的 JPEG 文件。机内没有新增 RAW-only 菜单。普通“RAW 录制”菜单不会把这些 HE NEF 改成无损或 HE★。
6. 首次从 C15、0.3 秒预拍和较短后拍时长开始，按名称找到**预拍摄选项**（编号可能变化）。官方说明：[释放模式](https://onlinemanual.nikonimglib.com/z8/en/release_mode_33.html)、[预拍摄选项](https://onlinemanual.nikonimglib.com/z8/en/csmd_pre-release_capture_options_233.html)。先采用静态场景、手动对焦和可见计时器；自动对焦跟踪、自动捕获及全部曝光／处理组合尚未覆盖。

```sh
# 同一固件支持两种配置；此处选择随包提供的初始配置
python patch.py "/path/to/Z_8_0311.bin" --features precapture --capture-mode raw-only --version 04.02 --output build/raw-only
python verify.py "/path/to/Z_8_0311.bin" "build/raw-only/Z_8_0402.bin" --features precapture

# 后续只换配置，无需重建或重新安装固件
python configure.py --capture-mode raw-jpeg --output build/config-paired
python configure.py --capture-mode raw-only --output build/config-raw-only
# 可选：较小上限、仅启用 C15
python configure.py --capture-mode raw-only --frames 5 --c15-only --output build/config-small
# 可选诊断计时尾标，默认不添加
python configure.py --capture-mode raw-only --diagnostic-footer --output build/config-diagnostic
```

关机并安全取卡后，把所选的 `Z8PRE.CFG` 放到记录卡根目录。两种模式默认都启用 C15／C30、最多保留 30 张历史帧。模式改变的是配置，不是固件补丁字节。默认不添加诊断尾标，不要手工修改配置位。

### 拍摄、等待与核对

1. 半按快门，至少覆盖所选预拍时长；首次可半按至少一秒。半按不足时实际历史帧会减少。
2. 短暂全按后松开。相机按上表保存选中的历史帧，全按之后的帧仍保存 JPEG。
3. 等待写卡完成再回放、正常关机或取卡，写卡中不拔卡或断电。直接在回放中核对 NEF 或 RAW+JPEG 配对；正常流程不再要求关开机。
4. 初次使用先让上一组写完再拍。八组边写卡边拍的探索性试验中，所有记录到的历史帧都已保存并解码，但写入积压时预拍图标曾出现 **“!”**。已观察到它与积压同时出现；确切含义和阈值尚未确定。等待写卡追上、正常预拍标志恢复再继续；有限试验不保证可以无限连续触发。
5. 在电脑上检查文件集合并完整解码 RAW。`raw-only` 选中的历史帧编号应没有独立 JPEG，之后的 JPEG-only 编号属于正常后拍。`raw-jpeg` 保留两个成员，注意 NEF 自身内嵌的是缩小预览。

缓存填满、帧数上限为 30 时：

| 模式 | 预拍时长 | 历史 NEF 数 | 实测覆盖 |
|---|---:|---:|---|
| C15 | 0.3 秒 | 5 | 已实测 |
| C15 | 0.5 秒 | 8 | 原厂计数表支持，未单独实测 |
| C15 | 1 秒 | 15 | 已实测 |
| C30 | 0.3 秒 | 9 | 已实测 |
| C30 | 0.5 秒 | 15 | 原厂计数表支持，未单独实测 |
| C30 | 1 秒 | 30 | 已实测 |

有限实测中，30 张 RAW-only NEF 约 7.6–8.0 秒写完，每张约 0.26 秒；登记路线的 RAW+JPEG 30 帧组约 13.2 秒。这些是测量实例，不是完成期限或吞吐保证；场景、卡、处理设置和前面未写完的组都会影响等待。边写卡边拍时，一张较晚帧到 NEF 写完曾等待 23.8 秒。

### 限制与异常处理

- 仅 C15／C30、FX、HE NEF；没有 DX、C60／C120、无损、HE★ 或全按后的 RAW 连拍。RAW+JPEG 的全尺寸 NEF 内嵌图尚未实现。
- 照片库登记和直接回放已测试。机内删除、保护、传输、接近满卡以及全部双卡组合尚未充分测试，尝试前先备份原件。
- 已用 Adobe DNG Converter 18.1.1 完整解码。NX Studio、Lightroom 等未直接测试；仍缺少部分原厂可选元数据，包括镜头校正块、灰度子图和部分 XMP 校正数据，各软件与镜头校正的完整等效性未验证。
- 30 帧压缩帧分配约占 519 MB。写卡中再次触发和长时间后拍可能耗尽缓冲或改变拍摄行为；有限成功记录不能排除丢帧、冻结或重启。
- 每张 NEF 预算 1.5 秒。原厂写入路径在调用返回后检查耗时；回退路径在 I/O 调用之间检查。两者都不能中断已阻塞的调用，不是防死机保证。
- 登记失败时可能退回“JPEG＋另写 NEF”，使用 `.NE_` 再改名；这种回退 NEF 可能需要之后重新扫描照片库。其他失败可能产生 JPEG-only、缺失／不完整 NEF 或 **`Z8PRESTP.BIN`**。停止文件阻止后续额外 NEF 写入，关开机不会清除；有些前提不符只会跳过 NEF，仍须检查数量。
- RAW-only 的预览质量步骤无法确认时，NEF 退回 1620×1080 预览。若 RAW-only 出错后补存了已经处理的 JPEG，该 JPEG 可能是较低的 NEF 预览画质，元数据却仍写 FINE；这是异常回退行为，不是正常输出。
- 缺片、出现 `.NE_`／停止文件、报错、冻结或重启时停止测试，保留文件。待卡访问结束后备份并停用功能，排查后再决定是否删除停止文件和重试。

要恢复原有 JPEG 预拍，关机并安全取卡后移除 `Z8PRE.CFG`。这不会卸载固件、关闭已包含的 ProRes 功能，也不保证固件可回退。实现测试与新生成包的验证边界见[验证范围](validation.md)。
