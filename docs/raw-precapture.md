# HE RAW pre-capture / HE RAW 预拍摄

[English](#english) · [简体中文](#简体中文)

## English

**Experimental; use at your own risk.** Read the [risk notice](../README.md#english) before installation. Back up photographs and settings first. No successful test rules out data loss or camera damage.

### Preparation

1. Supply the official Z8 C 3.11 update package, build with `--features precapture` or `--features prores precapture`, and run `verify.py` against the exact input. Keep the manifest and checksums. Read Nikon's [official update instructions and precautions](https://downloadcenter.nikonimglib.com/en/download/fw/606.html); installation remains a manual decision. Use adequate battery power, do not interrupt an update, and do not assume that a higher custom version can later be downgraded.
2. Use a backed-up card with plenty of free space. Initial hardware testing used SD; equivalent timings with other cards are not established. For initial use, insert just the intended recording card, avoiding untested dual-card arrangements.
3. Copy the generated update package to the card root and perform the update manually through the camera's firmware menu, following the official procedure. Confirm that the displayed version matches your build. The project does not supply or install firmware for you.
4. Copy the build's **`Z8PRE.CFG`** to that card's root. It is a generated 64-byte binary configuration; do not create it with a text editor. Put it on only one card. The default enables C15 and C30 and sets the history-frame ceiling to 30; it does not force every burst to have 30 frames. Reformatting the card removes the configuration and disables the additional NEF output until it is copied back.
5. Choose photo mode, FX image area and JPEG fine L for high-speed frame capture. Start with C15 and a 0.3-second pre-release window. In Custom Settings, locate **Pre-Release Capture Options** by name (numbering may vary), set the pre-release duration, and use a short post-release duration for initial trials. See Nikon's [release modes](https://onlinemanual.nikonimglib.com/z8/en/release_mode_33.html) and [pre-release settings](https://onlinemanual.nikonimglib.com/z8/en/csmd_pre-release_capture_options_233.html).
6. The first hardware checks used manual focus and a static scene with a visible timer. Begin with similarly simple conditions. AF tracking, automatic-capture workflows and every exposure/processing combination have not been covered.

These restrictions concern the added pre-capture function, not the ordinary shooting modes. There is no new RAW-only or compression-quality menu. The card configuration controls the extra HE NEFs; the ordinary RAW-recording menu does not change their compression type.

### Shooting and expected files

1. Half-press for at least the selected history duration; at least one second is a practical initial procedure. A shorter half-press may leave fewer historical frames available.
2. Fully press briefly and release. The camera writes its JPEGs and additionally saves selected historical frames as same-number NEFs in the same directory. Keep both files for checking.
3. Wait until card access has finished, then allow an additional 15 seconds during initial trials before playback, normal power-off or card removal. Do not remove power or the card while it is writing. This extra wait is a precaution, not a hard completion guarantee.
4. Before another burst, ensure the previous one is finished. Repeated triggers while writing and long held-down post-release bursts have not been hardware-validated.
5. To refresh the camera's photo database, turn it off normally after writing has finished and turn it back on. The tested camera then showed the RAW icon with the JPEG/NEF pair. Immediate playback before that reload may show only JPEG; NEF files are already on the card.

With a filled buffer and the default configuration:

| Mode | Pre-release duration | Expected historical NEFs | Hardware coverage |
|---|---:|---:|---|
| C15 | 0.3 s | 5 | Tested |
| C15 | 0.5 s | 8 | Original frame-count table; not separately hardware-tested |
| C15 | 1 s | 15 | Tested |
| C30 | 0.3 s | 9 | Tested |
| C30 | 0.5 s | 15 | Original frame-count table; not separately hardware-tested |
| C30 | 1 s | 30 | Tested |

These counts exclude frames captured after the full press: **those are JPEG-only**. Configuring a smaller ceiling saves only the most recent N history frames. A one-second C30 trial produced 30 NEFs and took approximately 15 seconds to finish all files including JPEGs. Per-NEF writing in the limited trial was roughly 0.25–0.32 seconds. Slow cards, different scenes and other camera settings can change this substantially. This is not continuous 30-fps RAW recording.

### Limits and failures

- Only C15/C30, FX and HE NEF are implemented. No DX, C60/C120, RAW-only, lossless RAW or HE★. JPEG generation and saving remain necessary because the NEF obtains its own frame's metadata and previews from that path.
- No immediate registration in the camera photo database. Deletion, transfer and other database-dependent operations on newly created pairs have not been comprehensively tested; back up the card files directly before experimenting.
- Validation used Adobe DNG Converter 18.1.1. NX Studio, Lightroom and other converters have not been directly tested. The generated NEFs omit some optional metadata, including lens-correction blocks present in factory NEFs; lens distortion/vignetting correction and complete software equivalence are unverified.
- Thirty retained frames occupy substantial memory (approximately 519 MB for their compressed-frame allocations). Rapid retriggering or prolonged post-release bursts may exhaust buffers or change capture behavior. No guarantee of no dropped frames, freezes or resets is made.
- Additional saving has a 1.5-second cooperative budget per NEF, checked between I/O calls. It cannot interrupt a single blocked filesystem call and is not a guarantee against a hang.
- A successful file is renamed from `.NE_` to `.NEF`. A write/close/rename failure or budget overrun may leave `.NE_` and **`Z8PRESTP.BIN`**. The stop file disables subsequent extra NEF writes; restarting the camera does not remove it. Some precondition failures simply skip a NEF, so also check the expected file count.
- If files are missing, a stop file or `.NE_` appears, an error is displayed, or the camera freezes/restarts, stop testing. Preserve all files and logs. After card access has ended, back up the card and disable the feature; investigate before removing a stop file or trying again. Do not repeatedly trigger a failing configuration.

To disable extra NEF saving, remove `Z8PRE.CFG` from the card while the camera is off and the card is safely accessible. This does not uninstall the firmware or disable ProRes if that feature was included. It does not make firmware rollback guaranteed.

### Optional configuration

The build already supplies the recommended 30-frame, C15+C30 configuration. To make a smaller ceiling or C15-only file locally:

```sh
python configure.py --frames 5 --c15-only --output build/config-small
# Optional diagnostic timing footer; normally omitted
python configure.py --frames 30 --diagnostic-footer --output build/config-diagnostic
```

Manually copy the generated `Z8PRE.CFG` to one card root. The default excludes the diagnostic footer. The public source clears its optional filename padding; do not edit binary configuration flags by hand.

## 简体中文

**测试版本，风险自负。** 安装前阅读[风险说明](../README.md#简体中文)，先备份照片和设置。已有测试成功不能排除数据丢失或相机损坏。

### 准备流程

1. 使用官方 Z8 C 3.11 更新包，选择 `--features precapture` 或 `--features prores precapture` 构建，再用 `verify.py` 对照同一个原始输入核验，保留 manifest 和校验值。阅读 Nikon 的[官方更新步骤与注意事项](https://downloadcenter.nikonimglib.com/en/download/fw/606.html)，自行决定是否安装；保证电量充足，不中断更新，不假定自定义高版本号可以降级恢复。
2. 备份存储卡并留足空间。本次上机使用 SD 卡，其他卡的耗时未验证。初次使用建议只插入用于记录的一张卡，避免未经测试的双卡组合。
3. 手动将生成的更新包放到卡根目录，按照官方流程在机身固件菜单中更新，确认显示版本与本次构建相同。本项目不会替用户安装。
4. 将构建输出的 **`Z8PRE.CFG`** 复制到同一张卡根目录。它是生成的 64 字节二进制配置，不可用文本编辑器手写。只在一张卡放置。默认允许 C15、C30，最多保存 30 张历史帧；并非每次都强制拍 30 张。格式化会删除配置，额外 NEF 保存随之停用，需重新复制配置。
5. 设置照片模式、FX、适用于高速画面捕捉的 JPEG fine L。首次从 C15、预拍 0.3 秒开始。在自定义设置中按名称找到**预拍摄选项**（编号可能变化），选择预拍时长，初次测试采用较短的后拍时长。官方说明：[释放模式](https://onlinemanual.nikonimglib.com/z8/en/release_mode_33.html)、[预拍摄选项](https://onlinemanual.nikonimglib.com/z8/en/csmd_pre-release_capture_options_233.html)。
6. 首轮实测采用手动对焦、静态场景和可读计时器，建议先用同样简单的条件。自动对焦跟踪、自动捕获及所有曝光／处理设置组合尚未覆盖。

以下限制针对新增预拍功能，不是普通拍摄模式的功能列表。本版没有新增 RAW-only 或压缩质量菜单。额外 NEF 由卡上配置控制，固定使用 HE；普通“RAW 录制”菜单不会把预拍 NEF 改成无损或 HE★。

### 拍摄流程与预期结果

1. 半按快门，至少覆盖所选预拍时长；首次可统一半按至少一秒。半按不足时，实际历史帧可能少于表中数量。
2. 短暂全按快门后松开。相机保存原有 JPEG，并为选中的历史帧在同一目录另存同号 NEF。保留两种文件以便核对。
3. 等卡灯熄灭、写卡完成，初次测试再多等 15 秒后才回放、正常关机或取卡。写卡中不得拔卡或断电。额外等待是预防措施，不是完成时间的硬性保证。
4. 确认上一组完全写完，再进行下一组。卡灯亮着时再次全按、长时间按住快门后拍，尚未上机验证。
5. 如需刷新机内照片库，在写完后正常关机再开机。实测重新加载后，回放中能看到 JPEG／NEF 配对的 RAW 标识。**刚拍完不会自动登记 NEF，立即回放可能只显示 JPEG；此时 NEF 已在卡上。**

缓存已填满、使用默认配置时：

| 模式 | 预拍时长 | 预期历史 NEF 数 | 实测范围 |
|---|---:|---:|---|
| C15 | 0.3 秒 | 5 | 已实测 |
| C15 | 0.5 秒 | 8 | 原厂计数表支持，未单独实测 |
| C15 | 1 秒 | 15 | 已实测 |
| C30 | 0.3 秒 | 9 | 已实测 |
| C30 | 0.5 秒 | 15 | 原厂计数表支持，未单独实测 |
| C30 | 1 秒 | 30 | 已实测 |

表中不包括全按后的帧：**预拍之后的连拍依然只有 JPEG**。如果配置较小的 N，上限只取最近 N 张历史帧。C30 一秒的一次实拍保存 30 张 NEF，连同 JPEG 约 15 秒全部写完；本轮每张 NEF 写入约 0.25–0.32 秒。卡速、场景、设置不同都可能显著改变耗时；这不是持续每秒写入 30 张 RAW 的功能。

### 当前限制与异常处理

- 仅实现 C15／C30、FX、HE NEF；没有 DX、C60／C120、RAW-only、无损压缩或 HE★。仍需生成并保存 JPEG，因为 NEF 的逐帧元数据和预览取自该帧 JPEG 流程。
- 不会即时进入机内照片库。对新生成文件配对的删除、传输等依赖数据库的操作未全面验证；尝试前先直接备份卡内文件。
- 使用 Adobe DNG Converter 18.1.1 验证解码；NX Studio、Lightroom 等未直接测试。NEF 缺少原生文件中的部分可选元数据，包括镜头校正块；畸变／暗角校正及各软件完整等效性未验证。
- 保留 30 帧占用较大内存，压缩帧分配约 519 MB。写卡中再次触发、长时间后拍可能耗尽缓冲或影响拍摄行为；不保证不会丢帧、冻结或重启。
- 每张 NEF 的协作式写入预算为 1.5 秒，只能在文件操作之间检查，不能中断一个已经阻塞的文件调用，不是防死机保证。
- 正常文件由 `.NE_` 改名为 `.NEF`。写入／关闭／改名失败或超预算时，可能留下 `.NE_` 和 **`Z8PRESTP.BIN`**。停止文件会阻止后续额外 NEF 写入，关开机不会清除它。有些前置条件不满足只会跳过 NEF，所以也要检查文件数量。
- 如果缺片、出现停止文件或 `.NE_`、错误提示、冻结或重启，立即停止测试并保留文件。待卡访问结束后备份、关闭此功能，排查后再决定是否移除停止文件和重试，不要反复触发失败组合。

临时关闭方法：关机并安全取卡后移除 `Z8PRE.CFG`，即可停用额外 NEF 保存。这不会卸载固件，也不会关闭已经包含的 ProRes 功能，更不代表保证可回退固件。

### 可选配置

构建已附带建议的 C15+C30、最多 30 帧配置。需要更小上限或仅 C15 时，在本地生成：

```sh
python configure.py --frames 5 --c15-only --output build/config-small
# 可选诊断计时尾标，默认不添加
python configure.py --frames 30 --diagnostic-footer --output build/config-diagnostic
```

然后手动将新生成的 `Z8PRE.CFG` 复制到仅一张卡根目录。公开源码会清零可选尾标的文件名填充区；不要手工修改二进制配置位。
