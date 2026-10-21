# Validation scope / 验证范围

2026-10-21 · toolkit **v0.2.0** · public input: **official Nikon Z8 C 3.11**. The [machine-readable summary](validation-summary.json) binds the current source and recorded checks. Complete firmware, photographs, private device records and emulator/runtime inputs are not distributed.

## Current implementation and identity

The RAW feature is ported from the hardware-tested **HN8, 03.50.n8** implementation. It adds HE★, removes the card CFG dependency, follows ordinary Image quality through QUAL/f2 and the i menu, and uses the dual-card role and primary slot captured when each frame is submitted. ProRes patch bytes and their recipe are unchanged.

| Artifact | SHA-256 |
|---|---|
| Official C 3.11 input | `d67413c2ede6b9ce8887175f20700bd9fbad2a973a4820968c45503d15d80d96` |
| Tested HN8 complete package, 03.50.n8 | `c387206c102d611e46e0634aaac9527105ea534cc78a8dc1c6b93542eb8edeb3` |
| Public combined output, 04.04.p0 | `54a6876e336027acfa07c98c488b09bfe9a686dcef56158092cb32947223629d` |
| Public pre-capture code, 33,117 bytes | `d71bffd5f64105eeda35d627c5f628dd4c9da6a976c3ba2de09667ea5e49e224` |

The public output is **not byte-identical to HN8**. Public file/protocol identifiers, an auxiliary marker, diagnostic identity/label, default-off diagnostic footer and firmware identity differ. An offline comparison restores those choices, accounts for compiler-layout relocation at 24 branch sites and nine GUI callback pointers, then checks the code, MAIN payload and complete package byte-for-byte against HN8. All three match after that explicit normalization. This establishes the port's defined relationship to the reference; it does not turn the public package into a physically tested HN8 file.

## Public 04.04.p0 camera files 2026-10-21

**The public combined package identified above passed this limited camera-file validation.** The maintainer followed the reduced test plan, then returned both cards. All new images record `Ver.04.04`; both MOVs record `NIKON Z 8 Ver.04.04`. The SD update file still matches the package SHA-256 above. This identifies the supplied package and resulting files together with the maintainer's report; it is not a readback of flashed camera memory.

| Group | Unique exposures | CFexpress | SD | Metadata-marked history / current |
|---|---:|---|---|---:|
| C30, HE★, RAW+JPEG fine, split cards | 60 | 60 JPEG | 60 NEF | 30 / 30 |
| C15, HE, RAW-only, backup | 20 | 20 NEF | 20 NEF | 5 / 15 |
| Ordinary single, HE★, RAW+JPEG, backup retained | 1 | 1 NEF + 1 JPEG | 1 NEF + 1 JPEG | Single shot |

All **102 NEFs** (62 HE★ and 40 HE, including card copies) completed Adobe DNG Converter 18.1.1 conversion and full 5520×8280 mosaic reading with LibRaw. There are 81 distinct mosaics, matching the 81 exposures. All **21 dual-card NEF pairs** have identical RAW strips, decoded mosaics and previews; header differences are confined to documented card fields. The 60 split RAW/JPEG pairs agree on file number, shutter count and subsecond timestamp, and the independent checker verifies their shared metadata and copied thumbnail/VGA/FHD streams. Both JPEG copies of the ordinary single have identical image streams. All 62 JPEG main images decoded completely.

All NEFs carry an 8256×5504 main embedded preview. **Every RAW-strip end equals the file end: zero trailing bytes and no diagnostic footer**, including all 100 NEFs from the patched burst path and the two ordinary-shot copies. The checker also detects the known 512-byte footer in an earlier HN8 file as a positive control. Group file numbers and shutter counts are consecutive; no expected counterpart is missing, and no temporary `.NE_` or stop file was found. All 166 new source files, including videos, retained their initial SHA-256 after analysis.

| ProRes clip | Encoding | Frames | Duration | Video bitrate |
|---|---|---:|---:|---:|
| `DSC_7472.MOV` | HQ, `apch` | 171 | 5.7057 s | 910.893 Mb/s |
| `DSC_7473.MOV` | Proxy, `apco` | 174 | 5.8058 s | 187.971 Mb/s |

Both are **3840×2160, 30000/1001 fps, 10-bit 4:2:2**. Every frame's length, slice structure and luma/chroma quantization matrices match its declared grade; MOV labels and FFprobe agree. FFmpeg 8.1.2 decoded all video and audio without errors; decoded frame counts match the sample tables and timestamps are contiguous. Both audio tracks are 48 kHz stereo 24-bit PCM. First/middle/last video frames and selected RAW/preview pairs were visually reviewed without visible truncation or scene mismatch.

**Scope and storage:** cards were identified and mounted read-only. Original NEF/JPEG/MOV files stayed on the cards and were not copied to the computer or published. Temporary DNGs were removed after full-pixel checks; per-file derived images were also removed, retaining hashes, text records and two small review contact sheets locally. History counts use camera metadata, not an independent full-press recording. This round did not repeat exhaustive timer-ROI matching, prolonged stress, every UI operation or nearly-full-card tests. RawPy review images use independent rendering and are not an equal-brightness/color comparison with camera JPEGs. Earlier HN8 evidence remains distinct below.

**本轮公开 `04.04.p0` 实拍文件验证通过。** 81 个独立拍摄帧产生 102 个 NEF（62 个 HE★、40 个 HE）和 62 个 JPEG；NEF 全部完整解码，21 对双卡 NEF 的 RAW 条带与像素一致，60 对分卡 RAW／JPEG 的元数据和共享预览对应。所有 NEF 的 RAW 条带结束处就是文件末尾，确认没有诊断尾标。HQ／Proxy 两段 4K 29.97p、10-bit 4:2:2 录像分别 171／174 帧，逐帧矩阵、结构及视频／音频完整解码均通过。没有停止文件或临时 NEF 残留，检查前后全部新文件哈希一致。

原始文件只在卡上读取，没有复制到电脑或发布；临时 DNG 和逐文件解码缩略图已清理，仅保留小型报告、哈希及两张复核拼图。预拍计数依据机内元数据，本轮不追加完整逐帧计时器匹配结论，不覆盖近满卡或长期压力测试；既有限制仍适用。

## HN8 camera evidence

The latest HN8 session used HE★ and recorded 108 unique C15/C30 frames:

| Run | Camera settings and output | Historical / current frames |
|---|---|---:|
| R1 | SD primary, RAW+JPEG fine, RAW-primary/JPEG-secondary: NEF on SD, JPEG on CFexpress | 30 / 28 |
| R2 | Backup, RAW+JPEG: both file types on both cards | 5 / 15 |
| R3 | CFexpress primary, RAW, RAW-primary/JPEG-secondary: NEF on both cards | 15 / 15 |

These produced **158 C15/C30 NEF files including dual-card copies**, plus one ordinary single-shot NEF, and 99 JPEG files. All **159 HE★ NEFs** completed Adobe DNG Converter 18.1.1 decoding. Fifty duplicate NEF pairs have identical RAW strips and decoded mosaics; card-specific header fields differ as expected. The files contain full-size 8256×5504 previews.

The card role changed during R1's queued writing (about 21.2 seconds), and the primary slot changed during R3's queued writing (about 14.2 seconds). Submitted frames retained the settings at submission. Camera quality-display checks U1–U9 were reported as normal, with four screen photographs supporting the observations.

**Frame-comparison limitation:** the original fixed timer ROI criterion failed on 49 comparisons because the RAW and JPEG timer positions differed by about 54 pixels. It remains a failed original criterion. A corrected exploratory ROI matched 58/58 R1, 19/20 R2 and 30/30 R3 frames. The remaining R2 ambiguity also appeared in the corresponding copy on the other card: adjacent readings shared milliseconds but differed by one second. Visual review of the actual seconds and milliseconds confirmed the RAW/JPEG correspondence. This repair is documented as exploratory/visual review, not a retroactive pass of the original criterion.

## Actual public code and files

The actual default public bytes, with diagnostic footers disabled, were tested independently of the HN8 normalization. The final `04.04.p0` combined MAIN repeated the native functional/control and stock-writer suites. Its generated NEFs were compared byte-for-byte with the earlier decoded files:

- **16 ProRes, 68 feature and 49 distribution checks passed.** Prebuilt and explicit-source complete firmware agree for all three feature selections at both `04.04.p0` and `17.42.x7`. Default builds run with an empty executable search path. Checks reject unsupported inputs, invalid identities, altered hooks/callbacks/code/loaders, unrelated edits and missing/corrupted prebuilt assets. No CFG is generated; retired configuration options are rejected.
- **110 bounded native cases passed:** 83 functional cases and 27 controls, including 26 deliberately defective builds rejected and one forced-failure fallback. Coverage includes the 13 Image quality selections, HE★ resource/layout choices, frame ordering, previews, dual-card routing and submission-time settings, GUI quality callbacks, and absence of CFG/filesystem reads in the capture path.
- **12 stock-writer cases passed**, with three additional defective width/height, total-length and cache-cleaning builds rejected. Original ARM64 routines execute within recorded boundaries; heap, filesystem/database, clock/DMA and JPEG-engine interfaces have explicit models. Supplied JPEG/HE streams do not prove real encoder timing or sustained throughput.
- **20 generated NEFs passed structural checks. Nineteen contain valid HE streams** and completed Adobe decoding; their mosaics equal the archived input mosaics. The twentieth is a deliberately synthetic HE★ layout fixture made with padded HE data: it tests fields and allocation, and is not counted as a decodable HE★ stream. Four corrupt file/metadata controls were rejected. Public files contain no diagnostic footer.

A source-only checkout can reproduce public build/verification tests with a user-supplied official package, but cannot reproduce private archived-frame or camera tests. Full firmware integration ran on macOS; complete Windows/Linux builds have not been independently tested.

## QEMU observations

Current QEMU startup, display and two-card file checks are recorded separately in the [validation summary](validation-summary.json). They use pinned Z8QemuBoard `main-u5` (`5a9b9a63adcfc158870b611b4be39818fff468c0`) and launcher tools `c24e33460ab311b8b120b19ba25f532ccef1b391`, with explicit synthetic ROM, sensor and MCU inputs and regular-file virtual cards.

All three public feature selections at `04.04.p0`, compared with the official C 3.11 positive control, reached the native photo menu and responded to down/up MCU inputs. Corresponding menu images were byte-identical across all four runs; visual review confirmed the selected rows. Each run completed without an unmodeled-MMIO abort and stopped its owned emulator process. This is a MAIN-entry boot/menu check, not a hardware boot guarantee.

The combined package also completed an ordinary single RAW shot with both virtual cards present, role 2 and CFexpress primary. Each card held exactly the expected NEF, database and camera-identification files. Both 35,110,512-byte NEFs matched the corresponding HN8 reference except variable ShotInfo and the declared version strings; all other bytes, including preview and RAW strips, matched. The successful retry used the same firmware, board and input settings as the retained first failed attempt.

The display and two-card capture runs used the earlier public `04.11.p0` identity. An independent comparison verifies that the final `04.04.p0` outputs differ only in version-immediate instructions, version strings, module identity and required integrity fields; all patch code and other bytes are identical. Startup/menu checks were repeated on all three actual `04.04.p0` outputs. The display run checks C15/C30 ordinary quality, a type-only QUAL change, C60's stock fallback, and the final i-menu quality/star values. It had no unmodeled access, CPU-register redirection or debugger RAM patches. The final i-menu image was visually checked.

QEMU loads decrypted MAIN at `0x40160000`. It does not cover firmware installation, the boot ROM/full power-on chain, real persistent settings/calibration, physical card timing, or end-to-end C15/C30 capture. Bounded native tests, ordinary QEMU single shots and hardware bursts are different evidence. The first two-card attempt stopped at the model's previously recorded timing-dependent write to `0x150c000c` from `0x40c1fce4`; that failed run is retained and is not called a pass.

## Known risks and limits

**Avoid nearly full cards.** Remaining-shot count, DCF estimate and free-space reservation still use the stock HSFC JPEG file plan. They do not reserve the added NEF space. A JPEG may fit when its NEF does not, risking write failure, missing or incomplete files. This situation has not been validated or fixed; there is no measured minimum-free-space threshold. Keep ample space on every destination card. The displayed remaining count is not a RAW-capacity guarantee.

The r/buffer estimate remains the stock HSFC estimate. Immediate playback can omit the RAW **L** label until restart although the files record Large. Unlimited sustained bursts, all cards and dual-card transitions, special secondary-size JPEG combinations, card removal during writes, deletion/protection/transfer, AF tracking and auto capture remain outside complete validation. C60/C120 RAW, DX and HLG/HEIF are not added.

The earlier public combined `04.11.p0` candidate was copied to the maintainer's SD card and read back. The maintainer confirmed it had not been installed before changing the public example to `04.04.p0`. After the final-version checks completed, the `04.04.p0` combined package was written to the SD card, read back against the package hash above, and safely ejected. **Copying to a card is not camera installation or a camera test.** The subsequent public-package camera-file results are recorded above, separately from the earlier HN8 session. These checks do not establish freedom from freezes, dropped frames, data loss or camera damage.

## 中文说明

本版以已上机的 HN8（`03.50.n8`）迁移而来，公开版使用独立标识、默认关闭诊断尾标，示例组合包为 `04.04.p0`。恢复所列标识、尾标和版本选择，并核对布局变化对应的 24 处跳转与 9 处回调指针后，代码、MAIN 和整包都能逐字节还原 HN8；**实际公开包本身与 HN8 并不相同**。ProRes 原有修改字节保持不变。

HN8 最近一轮实拍的 108 个 C15／C30 独立帧，在两张卡上产生 158 个 NEF 文件，另有普通单拍 1 个 NEF；159 个 HE★ NEF 全部完整 Adobe 解码通过。50 对双卡副本的 RAW 条带与解码像素相同。备份、RAW／JPEG 分卡，以及积压写入时修改副卡槽功能或主卡槽的测试，均保留了每帧提交时的设置。显示 U1–U9 的机身观察正常，附有四张拍屏。

原定计时器 ROI 因 RAW／JPEG 位置约偏移 54 像素而有 49 项失败，原失败仍保留；修正 ROI 的探索性比对分别为 58/58、19/20、30/30。R2 剩余歧义在另一张卡的副本也存在，原因是相邻秒的毫秒相同；随后逐秒和毫秒目视确认帧内对应。不能把后来的修正记成原判据通过。

实际公开机器码另完成 110 项限定原指令用例（83 功能、26 缺陷负控、1 强制失败恢复）、12 项原厂写入用例及 3 个写入负控。20 个生成 NEF 通过结构检查，其中 19 个有效 HE 码流完整解码且像素等于存档输入；另 1 个是填充 HE 数据的 HE★ 布局夹具，不算 HE★ 解码成功。四个文件／元数据负控被拒。公开构建的 ProRes／功能／分发检查分别 16／68／49 项，三种功能、两组版本的预编译／源码输出一致。

QEMU、合成内存执行、已有实拍及新公开固件必须分别理解。QEMU 从解密 MAIN 入口运行，不能证明刷写流程、完整上电链或所有实机状态。三种功能包及官方正控均进入原生菜单并响应上下按键，对应截图逐字节一致且已目视检查。组合包双卡普通 RAW 单拍也通过，两卡 NEF 除可变 ShotInfo 和版本字段外与 HN8 参照一致。首次双卡 QEMU 在模型已知访问处中断，失败保留；相同固件和模型输入的重试成功。先前 `04.11.p0` 候选包已写卡读回，但用户确认尚未安装；最终公开示例改为 `04.04.p0`，另重跑三种功能启动与组合包原指令用例。独立字节审计确认两个版本只差版本标识、对应立即数与封装校验，功能代码不变。`04.04.p0` 的所需检查全部完成后才重新写卡，读回哈希与上表一致并安全弹出。**写卡本身不等于已上机测试**；写卡后另完成的公开版实拍文件检查见本页前节。

**近满卡风险尚未修复或验证。** 原厂 HSFC 的剩余张数、DCF 估计与空间预留仍按 JPEG 计划计算，没有覆盖新增 NEF；可能 JPEG 放得下而 NEF 放不下，造成写入失败、漏文件或不完整文件。参与写入的每张卡都要保留充足空闲，不把剩余张数当成 RAW 容量保证；目前没有测得安全余量阈值。r／缓冲估计、即时 RAW 的 L 标签及其他限制见上文与[使用指南](raw-precapture.md)。

## Historical evidence

The prior v0.1.0 summary is preserved verbatim in [validation-v0.1.0.json](validation-v0.1.0.json); its earlier implementation snapshot remains in [validation-implementation-v3.json](validation-implementation-v3.json). The [previous full report](https://github.com/XinmiaoZhao/NikonFirmwarePatch/blob/8995eac3e734b506fef0807f11475795c46b4ae1/docs/validation.md) preserves the older 329-NEF hardware session and v3 configuration behavior. Those are historical results, not current CFG instructions. The following incident history concerns v0.1.0 / 04.03.p0.

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

The four runs used the same pinned board, tools, synthetic ROM/sensor/MCU inputs and fresh file-backed virtual NVMe card. Down selected **Extended menu banks** and up selected **Shooting menu bank**; corresponding screenshots were byte-identical across all four runs and visually checked. No unmodeled-MMIO abort occurred. Each owned emulator process was stopped. Full package and MAIN hashes, model identities and screen hashes are recorded under `boot_investigation_20261019` in the [validation summary](validation-v0.1.0.json).

**These QEMU runs alone did not resolve or exclude the reported hardware failures.** The emulator loads the decrypted MAIN at `0x40160000`; it does not test flashing, the boot ROM, real persistent settings/calibration, power behavior or the full camera startup chain. The virtual card was initially blank, with no `Z8PRE.CFG`; C15/C30 capture and live card removal/reinsertion were not tested. At the time of these QEMU runs, the reporter's files had not yet been received. The later file comparison and physical observation are recorded above; the affected camera's update/boot logs and flashed-memory readback remain unavailable. These runs did not establish a recovery procedure. The subsequent reporter follow-up and removal of the incident-specific notice are recorded above.

本轮重新下载实际公开的 v0.1.0 工具包，按默认预编译方式生成三个 `04.03.p0` 功能包，整包哈希均与既有发布记录一致。原厂正控和三个修改 MAIN 在同一固定 QEMU 条件下都进入原生拍摄菜单并响应上下按键，对应截图逐字节一致，目视确认选中行正确。**没有复现这一入口和模型条件下的不开机，不等于排除实机故障。** 本轮不覆盖升级／刷写、完整上电链、真实保留设置／校准或真实卡状态；空白虚拟卡无配置文件，没有测试 C15／C30 或运行中换卡。这些 QEMU 运行时尚未收到反馈者文件；后续文件比对和实机观察见上节。故障相机的刷写／启动过程和已刷内容读回仍缺失，这些模拟运行本身没有确定根因或恢复方法。后续测试者反馈及专项提示撤下经过见上节。
