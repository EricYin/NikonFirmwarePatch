# Validation scope / 验证范围

2026-10-18. Public input support remains **official Nikon Z8 C 3.11**. Recorded implementation tests, public-source regression and installation of a newly generated package are distinct evidence.

## Issue #3 follow-up 2026-10-20

The original [issue #3](https://github.com/XinmiaoZhao/NikonFirmwarePatch/issues/3) reported failure to boot on one Z8 and loss of RAW pre-capture after card changes on another. On 2026-10-20, the reporter [updated and closed the issue](https://github.com/XinmiaoZhao/NikonFirmwarePatch/issues/3#issuecomment-6288128394): they reported testing C 4.03 modified firmware on 10 Z8 cameras without black screens, freezes or failure to boot. They said the earlier black-screen incident had not been reproduced, and attributed the RAW pre-capture problem to an operating mistake rather than a confirmed firmware defect.

Based on that follow-up, I have removed the incident-specific pause-installation notice. The original report, file comparison and investigation below remain available. This is the reporter’s hardware feedback; the comment does not provide per-camera package hashes or test logs. It does not establish the cause of the earlier black screen or general hardware safety. The usual experimental-firmware risk statement remains applicable; no firmware change was made for this update.

原 [issue #3](https://github.com/XinmiaoZhao/NikonFirmwarePatch/issues/3) 报告一台 Z8 刷写后无法开机，另一台换卡后 RAW 预拍摄无法恢复。测试者于 2026-10-20 [补充反馈并关闭 issue](https://github.com/XinmiaoZhao/NikonFirmwarePatch/issues/3#issuecomment-6288128394)：10 台 Z8 使用 C 4.03 修改固件测试，均未出现黑屏、死机或无法开机；此前黑屏个例未能复现，RAW 预拍摄失效则被测试者确认为操作不当，并非已确认的固件缺陷。

我已据此撤下专项暂停刷写提示，原故障报告、文件比对及下文的调查记录继续保留。这是测试者提供的实机反馈，评论未附逐台固件哈希或测试日志；不能据此确定早先黑屏的原因或保证普遍安全。常规实验固件风险说明继续适用，本次没有修改固件。

## Maintainer hardware observation 2026-10-19

Following the initial incident report and QEMU checks, I tested the staged public **04.03.p0 ProRes + pre-capture** build on my Z8. I observed:

- Normal startup; the reported failure-to-boot symptom was not observed in this test.
- No abnormality during card changes, including card insertion/removal with the camera powered on.
- Pre-capture could be enabled with a card containing `Z8PRE.CFG` inserted.

The reporter-supplied firmware/configuration, the locally rebuilt reference, and the files read back from my card before this test are byte-identical:

| File | Bytes | SHA-256 |
|---|---:|---|
| `Z_8_0403.bin` | 99,051,117 | `7047c831e0517e5e5352ae3721e21a0b1ad1f9aa12ddca52eb81cf927e81af9c` |
| `Z8PRE.CFG` | 64 | `a8067db1a7e8350c07e1e76bda32aaeb3dde22fb327e829fddc1c9f262704f1f` |

The supplied manifest records source compilation; the reference used the default precompiled path. Their final files match exactly, and independent verification of the supplied firmware passed. This comparison identifies the received files; it is not a readback of the affected camera's flashed memory.

**Test scope:** these observations cover this test on my camera, using the firmware and configuration identified by the pre-test comparison and card readback. This update includes no new capture-file checks, RAW decoding, device logs, repeat count, or record of write activity at removal. The test does not establish safety for removal during active writes, every card/slot/dual-card arrangement, or long-term reliability. Existing image-decoding counts below are unchanged. I have retained the original failure report. This test alone did not establish its cause; the reporter’s later follow-up and issue closure are recorded above.

在先前故障报告与 QEMU 对照之后，我用已写卡核对的公开 **04.03.p0 ProRes＋预拍摄组合包**在自己的 Z8 上进行了测试，相机正常开机；换卡以及开机状态下插拔卡均未见异常，插着有 CFG 的卡时可以启用预拍摄。收到的反馈者固件／配置、本地参考及测试前卡上读回文件逐字节一致，具体身份见上表；对方采用源码编译，本地采用预编译路径，最终字节相同。

以上是我这次在自己相机上的观察。本次更新没有新增照片检查、RAW 解码、设备日志、重复次数或拔卡时写入状态记录，因此不能外推到写入中拔卡、全部卡型／卡槽／双卡组合或长期可靠性；下文旧实拍的文件检查数量保持不变。我也没有对故障相机的已刷内容做读回。我保留了原故障报告；仅凭这次测试未遇到异常，不能确定原故障的原因。测试者后续反馈及 issue 关闭经过见上节。

## Boot investigation 2026-10-19

The exact public `v0.1.0` toolkit was downloaded again and verified against SHA-256 `4f2dde963e888987c1ad6f03f151de6b335780d378206f4320d9ecc864cf4a53`. With the official C 3.11 input, all three feature selections were built in default precompiled mode with an empty executable search path, using output identity `04.03.p0`. Independent package verification passed and the output hashes matched the release's existing records.

| MAIN image | Result in the fixed QEMU model |
|---|---|
| Official C 3.11 control | Reached the native photo menu; down/up inputs responded |
| ProRes only, 04.03.p0 | Reached the native photo menu; down/up inputs responded |
| RAW pre-capture only, 04.03.p0 | Reached the native photo menu; down/up inputs responded |
| Combined, 04.03.p0 | Reached the native photo menu; down/up inputs responded |

The four runs used the same pinned board, tools, synthetic ROM/sensor/MCU inputs and fresh file-backed virtual NVMe card. Down selected **Extended menu banks** and up selected **Shooting menu bank**; corresponding screenshots were byte-identical across all four runs and visually checked. No unmodeled-MMIO abort occurred. Each owned emulator process was stopped. Full package and MAIN hashes, model identities and screen hashes are recorded under `boot_investigation_20261019` in the [validation summary](validation-summary.json).

**These QEMU runs alone did not resolve or exclude the reported hardware failures.** The emulator loads the decrypted MAIN at `0x40160000`; it does not test flashing, the boot ROM, real persistent settings/calibration, power behavior or the full camera startup chain. The virtual card was initially blank, with no `Z8PRE.CFG`; C15/C30 capture and live card removal/reinsertion were not tested. At the time of these QEMU runs, the reporter's files had not yet been received. The later file comparison and physical observation are recorded above; the affected camera's update/boot logs and flashed-memory readback remain unavailable. These runs did not establish a recovery procedure. The subsequent reporter follow-up and removal of the incident-specific notice are recorded above.

本轮重新下载实际公开的 v0.1.0 工具包，按默认预编译方式生成三个 `04.03.p0` 功能包，整包哈希均与既有发布记录一致。原厂正控和三个修改 MAIN 在同一固定 QEMU 条件下都进入原生拍摄菜单并响应上下按键，对应截图逐字节一致，目视确认选中行正确。**没有复现这一入口和模型条件下的不开机，不等于排除实机故障。** 本轮不覆盖升级／刷写、完整上电链、真实保留设置／校准或真实卡状态；空白虚拟卡无配置文件，没有测试 C15／C30 或运行中换卡。这些 QEMU 运行时尚未收到反馈者文件；后续文件比对和实机观察见上节。故障相机的刷写／启动过程和已刷内容读回仍缺失，这些模拟运行本身没有确定根因或恢复方法。后续测试者反馈及专项提示撤下经过见上节。

## Precompiled distribution update

The release changes code delivery and offline validation, without changing the reviewed ARM64 patch or its feature recipes. The 30,301-byte pre-capture module retains SHA-256 `479f4e37db3968a9e796fc97d865246793ebbac83b28f10a95711535c45cb715`. The original implementation evidence below is retained from source commit `d155b8b183e359140ac36147297f33707b9374e5`; its hash-bound summary is preserved in [implementation validation](validation-implementation-v3.json). Native execution, image decoding and camera tests were not repeated for this packaging change.

Current distribution regression compares prebuilt and explicit-source full outputs for all three feature selections, at both `04.03.p0` and custom `17.42.x7`. Default builds run with an empty executable search path to catch accidental compiler use. The official `04.03.p0` combined output remains identical to the preceding public build. Separate checks cover wrong requested version/tag/features, modified input with a repaired envelope, changed hooks/code/shared loader, unrelated edits, version opcodes, trailer/module names, missing/truncated/corrupted prebuilt code, and an explicit source build without any prebuilt asset. The ProRes and feature/configuration regression suites are also rerun.

The public builder and independent verifier now require the exact official input hash. Prior compatible-input model work below remains historical implementation evidence; it is not a supported way to use the current public CLI. Both delivery modes verify the requested options and every allowed edit, not a candidate's own self-reported digest. Release packaging has a fixed member allowlist and an independent source/archive checker; it excludes complete firmware and original photos. Detailed results and host scope are in the [current validation summary](validation-summary.json). Full integration was tested on macOS; Windows/Linux full firmware builds have not been independently run.

本次更新只改变分发、构建和离线验证，预拍摄机器码及功能配方保持相同。此前 `d155b8b` 的原指令执行、像素／文件检查和相机观察作为既有实现证据保留，原始摘要单独存档；没有为了打包变化重复全部仿真和图像解码。当前回归比较三种功能组合、两组版本／tag 的源码与预编译完整输出，并覆盖错误声明、合法封装下的非法修改、缺失或损坏机器码、源码独立构建及既有功能检查。默认构建测试清空 PATH，确保未暗中调用编译器。当前公开 CLI 严格拒绝非官方输入；下文的兼容修改输入试验只属于历史实现证据。此次发布没有安装相机或写卡，也没有新增上机认证。

## Hardware observations

The current implementation was tested on a camera with the ordinary Image quality menu controlling C15/C30. File type, JPEG grade and ★ selection matched the menu in these groups:

| Setting | Recorded output | Historical / current NEF frames |
|---|---|---:|
| C15, 0.3 s history, RAW + JPEG fine | 7 NEF/JPEG pairs | 5 / 2 |
| C30, 0.3 s history, RAW | 12 NEFs, no matching JPEGs | 9 / 3 |
| C15, 0.3 s history, JPEG normal★ | 7 JPEGs, no NEFs | — |
| C15, history off, RAW + JPEG basic | 1 NEF/JPEG pair | 0 / 1 |
| C30, 1 s history, RAW + JPEG fine★, 14-trigger stress sequence | 308 NEF/JPEG pairs | 242 / 66 |

There are **328 C15/C30 NEFs: 256 historical and 72 full-press/post-release frames**. Together with one ordinary single-shot NEF/JPEG pair, the acquisition contains **329 NEFs and 324 JPEGs**. These totals come from the per-file records.

All 328 C15/C30 NEFs passed structure, metadata, recorded-format and complete Adobe DNG Converter 18.1.1 decoding checks. Every file carried an **8256×5504 full-size preview**, with JPEG marker structure, quantization, Huffman tables and sampling matching the camera-made reference. The files were about 20.6–21.4 MB; embedded full-size previews were about 3.17–3.23 MB. RAW+JPEG basic reused the main JPEG stream as expected; the other tested paired grades had separately encoded NEF previews. The ordinary single-shot regression also decoded normally.

**Frame correspondence was confirmed using automated image comparison and visual review.** Repeated timer readings created scoring ambiguity in a small subset of stress frames; the visual review compared the actual seconds and milliseconds and confirmed matching readings in each frame's RAW/JPEG pair. No frame mismatch was identified. The original measurements and review images are retained with the local evidence.

The file sets were continuous within the recorded bursts, with no stop file or temporary NEF residue. The user reported normal playback. The immediate RAW label can omit **L**, although every checked NEF records Large; a subsequent restart restores the label. This display issue is not yet fixed. The full menu controls output; i-menu/dial shortcuts and the shooting display still refer to HSFC quality.

The stress sequence demonstrates limited busy-card use, not unlimited sustained capture. One trigger had zero history frames and three current frames. The “!” indicator coincided with pending writes and later cleared; an exact code-level threshold or original-firmware comparison has not been established. The 308 pairs took about 155 s to write in that trial. Near-full cards, all card types, dual-card modes, deletion/protection/transfer, AF tracking and automatic capture have not been fully validated.

Existing ProRes hardware observations covered its four quality choices, clip identifiers, complete decoding and menu-bank persistence. They do not certify every newly generated combination.

## Public-source regression

- All three feature selections—ProRes only, capture only and both—build from official 3.11 and pass independent container/module and byte-range verification. The shared loader edit is composed once; other input bytes and modules are preserved. The original ProRes recipe and its **16-check regression** remain unchanged.
- **42 feature/configuration checks** cover conflicting or occupied patch windows, the new current-frame/menu/preview dependencies, repeat application, incorrect feature claims, repaired checksums hiding unrelated edits, optimized Python, configuration generation and overwrite protection. Obsolete fixed-output CLI options are rejected. The interactive combined build matches the explicit build and configuration exactly.
- **119 bounded machine-code cases** execute the actual public build's patched call sites. They cover historical/current frames, all 13 valid menu choices, six JPEG grades, preview allocation/layout and encoding parameters, original statistics, failure fallbacks, both C15/C30 default configurations and rejection of old public configurations. The menu-composition case compares **75 combinations** against the original menu composer: 20 supported combinations agree; 55 unsupported combinations are declined.
- **17 control builds** were exercised: 16 deliberately faulty builds were rejected for the intended reason, and one forced-failure build verified recovery. Controls include reading only JPEG grade instead of composing all three settings, preview overlap, wrong preview kind, incorrect retention, missing cache cleaning and leaked resources.
- **13 original-writer cases** execute the original still-image writer on the generated segment/attribute blocks. Three defective builds are rejected at this layer for width, length and cache-cleaning violations.
- **15 generated NEFs passed independent structure/source checks and complete Adobe decoding**, covering RAW+JPEG fine/basic and RAW, with three historical and two current frames in each set. Every RAW sample matches the existing decode of its archived real-frame input. Four damaged-file/metadata controls were rejected. Default non-diagnostic output matches the verified diagnostic file before its footer; diagnostic filename padding is zero.
- A compatible-input run passes the same functional cases and produces byte-identical NEFs for the same archived inputs. Normalizing only public file/protocol identifiers, record magic and diagnostic identity reconstructs the exact machine code, payload and complete package of the hardware-tested reference. **The actual public package differs from that reference**, and this regression does not extend public support beyond official C 3.11.
- The official-input combined build booted and saved an ordinary RAW still in the established QEMU camera model. Embedded JPEGs and RAW strips matched the original-firmware control; outside the model's variable ShotInfo block, differences were confined to version text. The run used explicit model inputs, no CPU register redirection and no debugger RAM patches. **This is not end-to-end C15/C30 emulation or a physical-camera test.**

The CPU tests execute original menu, allocation, layout, JPEG parameter/rate-control and writer routines. Filesystem/database/heap/clock/DMA and JPEG-engine boundaries have explicit models; JPEG streams are supplied test inputs. These tests verify code behavior and arguments, not hardware JPEG timing or unlimited throughput.

The [source-bound summary](validation-summary.json) records the completed release checks. Public identifiers and v3 card configuration differ from the recorded camera implementation. Old public v1/v2 configurations must be regenerated; diagnostic footers are off by default. Original development and model-warning records remain local; a successful current run is not a reliability guarantee.

No new public package was installed on a physical camera during this release preparation. Firmware, photos, complete device metadata, emulator images and native-test inputs are not distributed. Repository tests require a user-supplied official package; a source-only checkout cannot reproduce the archived-frame or hardware checks. Tests do not establish freedom from freezes, dropped frames, data loss or camera damage.

## 中文

本次公开支持的构建输入仍仅限**官方 Z8 C 3.11**。当前实现的上机记录确认：C15／C30 按普通“画质”菜单选择文件类型、JPEG 档位和 ★，预拍及全按后正式帧都生效。

| 设置 | 结果 | 历史／正式 NEF 帧 |
|---|---|---:|
| C15，预拍 0.3 秒，RAW＋JPEG fine | 7 对 NEF／JPEG | 5／2 |
| C30，预拍 0.3 秒，RAW | 12 张 NEF，没有同号 JPEG | 9／3 |
| C15，预拍 0.3 秒，JPEG normal★ | 7 张 JPEG，没有 NEF | — |
| C15，预拍关，RAW＋JPEG basic | 1 对 NEF／JPEG | 0／1 |
| C30，预拍 1 秒，RAW＋JPEG fine★，连续触发 14 次 | 308 对 NEF／JPEG | 242／66 |

C15／C30 合计 **328 张 NEF：256 张历史帧、72 张全按当帧及后拍帧**。另有一对普通单拍回归，因此整次新增 **329 张 NEF 和 324 张 JPEG**，数字按逐文件记录汇总。

328 张 C15／C30 NEF 的结构、元数据、记录格式及 Adobe DNG Converter 18.1.1 完整解码都正常。全部内嵌 **8256×5504**，JPEG 标记结构、量化表、哈夫曼表和采样与相机自产参照一致。NEF 约 20.6–21.4 MB，整幅内嵌预览约 3.17–3.23 MB。RAW+JPEG basic 如预期复用主图；其余已测配对档另编 NEF 预览。普通单拍回归也完整解码正常。

**画面对应经自动图像比对和目视复核确认。** 压力序列少数帧因计时器重复读数产生评分歧义，复核直接核对秒位和毫秒位，本帧 RAW／JPEG 读数一致，未发现帧错配。原始测量与复核图保留在本地证据中。

已记录的各次连拍文件号连续，没有停止文件或临时 NEF 残留；用户报告回放正常。刚拍完 RAW 标签可能不显示 **L**，但所有文件已记录 Large，之后关开机显示恢复。这个显示问题尚未修复；i 菜单／拨盘快捷方式及取景显示也仍指向 HSFC 画质，实际输出应以完整普通菜单为准。

压力试验是有限的边写卡边拍覆盖，不代表无限持续连拍。有一次触发没有历史帧，只有三张正式帧；“!”与写入积压同时出现，随后消失，但精确代码阈值及原厂对照尚未建立。308 对文件在本次约 155 秒写完。近满卡、全部卡型／双卡模式、删除／保护／传输、自动对焦跟踪与自动捕获尚未充分验证。原有 ProRes 四档、编码标识、完整解码和菜单库保存实测结论保留，也不等于每个新组合都已上机。

公开源码本轮完成三种功能选择的构建、独立整包／改动范围核验和原有 **16 项 ProRes 回归**；**42 项功能／配置检查**覆盖冲突、重复应用、模式声明、优化运行、旧参数拒绝和覆盖保护，交互组合构建与显式构建完全一致。

实际公开机器码 **119 项限定执行通过**，包括预拍／正式帧、13 个有效菜单选项、六档 JPEG、预览空间／参数、原有统计和异常回退。菜单组合用例对照原厂组合函数检查 75 种组合，20 种受支持组合一致，55 种不受支持组合不接管。共运行 17 个控制构建，其中 16 个缺陷构建按预期被拒，一个强制失败构建验证恢复路径。原厂写入函数 **13 项通过**，另有三个宽高／总长／缓存清理负控按预期被拒。

**15 张生成 NEF 全部独立检查和完整解码通过**，覆盖 RAW+JPEG fine／basic 与 RAW，每种包含三张历史帧和两张正式帧；全部 RAW 样本与存档输入既有解码相同。四个损坏文件／元数据负控被拒；默认无尾标文件与已验证诊断文件的尾标前内容完全一致，诊断文件名填充清零。兼容修改输入的功能回归及同输入 NEF 字节一致性也通过；仅还原公开文件／协议标识、记录魔数和诊断身份，即可逐字节重建上机参照整包。**实际公开包与参照并不逐字节相同**，支持范围仍仅官方 3.11。

官方输入组合包在既有 QEMU 模型完成普通 RAW 单拍，内嵌 JPEG 和 RAW 条带与原厂对照相同；模型中会变化的 ShotInfo 之外只差版本文字。使用明确的模型输入，没有 CPU 寄存器重定向或调试器 RAM 补丁；**不是 C15／C30 端到端仿真或实体相机测试**。CPU 测试的 JPEG 引擎及若干服务是边界模型，码流由测试提供，不证明真实硬件的编码耗时或持续吞吐。

[验证摘要](validation-summary.json)绑定源码和本轮结果。公开版使用独立标识及 v3 配置，旧 v1／v2 配置必须重新生成，默认不加诊断尾标。原始开发与模型告警记录保留在本地，成功运行不等于长期可靠。此前 v0.1.0 发布准备阶段没有给实体相机安装新公开包；我的后续实机测试见本页上节。仓库不分发固件、照片、完整设备元数据、模拟器映像或存档输入；只克隆源码无法重现全部帧与硬件核查，也不保证不会冻结、丢帧、损坏数据或相机。
