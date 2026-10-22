# C15/C30 RAW capture / RAW 连拍与预拍

[English](#english) · [简体中文](#简体中文)

## English

v0.2.0 is based on HN8. In C15/C30 it uses ordinary **Image quality** for RAW / RAW+JPEG / JPEG, JPEG grade and ★, and **RAW recording** for HE / HE★. Both pre-release history and full-press/post-release frames follow the selected format. QUAL/f2 and the i menu edit the ordinary quality; the shooting-screen and i-menu quality indicators show it. The pre-release window still comes from the camera menu.

### Known risk: nearly full cards

**Do not keep shooting as either destination card approaches full.** The remaining-shot count and card-space reservation still use the stock HSFC JPEG file plan. They do not fully account for the added NEFs. A card may have room for the planned JPEG but insufficient space for the NEF, causing failed writes, missing files or incomplete files. Near-full-card handling has not been validated or fixed in this release, including in backup and split-card modes.

Use cards with ample free space, check each destination card separately, and change cards before capacity becomes marginal. There is no validated minimum-free-space threshold. The displayed remaining count and r/buffer value are not guarantees of RAW capacity or safe completion. Allow pending writes to finish before power-off or card removal. Successful normal-space tests do not cover this limit.

### Prepare and select settings

1. Read the [README risk statement and build instructions](../README.md). Use the complete matching v0.2.0 toolkit and your own official Nikon Z8 C 3.11 input. Choose a firmware version higher than the one installed on your camera; the tool cannot read the camera’s version. Verify the output with the expected features, version and tag.
2. Back up your cards and leave ample free space. Installation follows the camera’s normal firmware-update procedure; this toolkit does not write cards or operate the camera.
3. Select photo mode, **FX / full-size L**, and **C15 or C30**. In **Image quality settings → Image quality**, select RAW, RAW+JPEG or JPEG fine/normal/basic, with or without ★. Select **High efficiency** or **High efficiency★** under RAW recording. Lossless RAW, DX RAW and C60/C120 RAW are not added; selecting lossless does not make this C15/C30 path lossless.
4. Set the camera’s pre-release duration and post-release limit. No `Z8PRE.CFG` is needed. Old public or research configuration files are ignored, so removing one does not disable this implementation. `configure.py` and its old configuration options are no longer supplied.
5. Start with a short burst of a static scene, preferably RAW+JPEG, and inspect both card files and complete RAW decoding before relying on a new setup. Do not change format or compression in the middle of a burst or queued writes; those transitions are not a validated workflow.

A full selected history window produces up to 5/15 history frames at C15 with 0.3/1 s, or 9/30 at C30. Shorter half-presses, missing buffers or pending writes may yield fewer. The 30-frame ceiling is for history, not the entire burst. With pre-release off, current frames still use the ordinary quality setting.

### Dual-card routing

The supported two-card path follows the tested stock single-shot rules. Primary slot and secondary-slot role are stored with each submitted frame. Changing them while a previous burst is still writing affects subsequent submissions, not the already queued frames.

| Secondary-slot role | RAW | RAW+JPEG |
|---|---|---|
| Overflow / one destination | NEF on the destination selected by the stock camera | NEF + JPEG on that destination |
| Backup | NEF on each card | NEF + JPEG on each card |
| RAW primary – JPEG secondary | NEF on each card, as in the tested stock RAW-only behavior | NEF on primary, JPEG on secondary |
| JPEG primary – JPEG secondary | NEF on each card for the supported stock one-JPEG frame plan | NEF + JPEG on each card for that plan |

JPEG-only output remains on the stock file path with the selected ordinary JPEG grade. Separately sized secondary JPEG entries and other unsupported file plans can fall back to stock JPEG behavior; do not assume every dual-card combination is covered. The routing table does not certify automatic rollover, card removal during writes, a nearly full card, or recovery when a card fails. Each card must have sufficient space for its actual files.

### File behavior and limits

- Successful NEFs use the stock photo database and writer, with direct playback after writing. RAW and RAW+JPEG NEFs normally contain an **8256×5504** embedded preview. RAW+JPEG basic reuses its main JPEG; the other paired grades encode a separate NEF preview at the camera’s preview quality.
- HE and HE★ are both compressed RAW formats. The actual frame allocation and decode selector determine the recorded compression. The patch does not encode lossless RAW. HLG/HEIF, DX, C60/C120 RAW and unsupported special processing remain outside this feature.
- The immediate playback RAW label may omit **L** even though the NEF records Large; restarting refreshes it. This display issue is unchanged. The remaining-shot count and r/buffer value also remain the stock HSFC estimates.
- Holding compressed RAW frames and extra previews increases memory use. HE★ uses more buffer and card space than HE. The ready-margin change allows the tested HE★ pre-release settings, but does not guarantee an unlimited burst or sustained card-writing at C15/C30 cadence. “!” can coincide with unavailable history; let writing catch up before expecting a full window again.
- Some optional factory metadata, including lens-correction blocks, a grayscale subimage and some XMP correction data, is still missing. Adobe DNG Converter is covered by the recorded checks; complete equivalence in every converter, in-camera deletion/protection/transfer, AF tracking and automatic capture is not established.

### Failures and stopping RAW capture

Registration or write failures can leave JPEG-only output, missing/incomplete files, a temporary `.NE_`, a reduced 1620×1080 NEF preview, or **`Z8PRESTP.BIN`**. RAW-only fallback JPEGs can use NEF-preview quality. Check the complete file set and decoding; lack of an on-screen error is not sufficient.

**Read the [stop-file decoding and recovery guide](stop-file.md#english-summary) before deleting `Z8PRESTP.BIN`.** The patched writer checks its existence, not its contents: an empty or malformed file can also stop additional NEFs, and restarting does not remove it. Existing markers are not overwritten. On a supported two-card frame, a marker on the primary card releases the shared RAW buffer, so the secondary can also fall back to JPEG without its own marker. If only the secondary is stopped or fails, the primary NEF may already have been written. JPEG fallback is attempted but is not guaranteed to succeed; the marker does not globally disable ordinary RAW shooting or menu/UI changes.

Stop shooting, let pending writes finish, preserve both cards' files, and back up readable data to a separate device with sufficient space. Investigate before removing a marker and testing a short burst. Deletion allows new NEF attempts; it does not guarantee the next write or recover earlier RAWs. The time budget is cooperative: it cannot interrupt an already blocked stock I/O call or guarantee freedom from freezes. Reason codes alone do not establish card speed, free-space or hardware causes.

To avoid additional RAW capture, select **JPEG-only** in the ordinary Image quality menu, or leave C15/C30. Removing a CFG file has no effect in v0.2.0. This does not uninstall the patch or remove ProRes, and a firmware downgrade/recovery route is not guaranteed. Public builds do not append diagnostic footers; deleting a CFG file cannot toggle them.

Read the [validation record](validation.md) for HN8 camera observations, the public build’s exact scope, prior incident follow-up and the retained limitations.

## 简体中文

v0.2.0 以 HN8 为基础。C15／C30 使用普通“**画质**”控制 RAW／RAW+JPEG／JPEG、JPEG 档位和 ★，使用“**RAW 记录**”选择 HE／HE★。预拍历史帧及全按后正式帧均生效。QUAL／f2 和 i 菜单修改普通画质，取景画质标识与 i 菜单画质格也显示该值；预拍时长仍由机内菜单控制。

### 已知风险：存储卡接近写满

**主卡或副卡接近写满时，不要继续拍摄。** 剩余张数和空间预留仍按原厂 HSFC 的 JPEG 文件计划估算，没有为新增 NEF 完整计入空间。卡可能还能放下原计划的 JPEG，却不足以写完 NEF，从而出现写入失败、文件缺失或不完整。本版尚未验证或修复这一场景，双卡备份和分卡模式同样受影响。

使用空闲空间充足的卡，分别确认每张目标卡的余量，提前换卡，不等到接近满卡才处理。目前没有经过验证的最小剩余空间阈值；屏幕剩余张数及 r／缓冲数值不能保证 RAW 容量或安全写完。关机或取卡前等待全部写入结束。正常余量下的测试通过不覆盖这一限制。

### 准备与设置

1. 阅读 [README 风险声明及构建流程](../README.md)。使用匹配的完整 v0.2.0 工具包和自行取得的官方 Nikon Z8 C 3.11 输入，选择高于机身当前版本的输出号，并按预期功能、版本与 tag 独立验证。工具不能读取机身版本。
2. 备份存储卡，保留充足空间。相机安装按通常的固件更新流程进行；工具不会自动写卡或操作相机。
3. 选择照片模式、**FX／全尺寸 L、C15 或 C30**。在“画质设置 → 画质”选择 RAW、RAW+JPEG 或 JPEG fine／normal／basic 及 ★；“RAW 记录”选择**高效率或高效率★**。没有新增无损 RAW、DX RAW 或 C60／C120 RAW；选择无损并不会让此 C15／C30 路径变成无损。
4. 在机内设置预拍时长及后拍上限。**无需 `Z8PRE.CFG`**。旧公开版及研究版配置文件均被忽略，删除它们也不会停用本实现；不再提供 `configure.py` 及旧配置参数。
5. 先拍静态场景的短组，建议 RAW+JPEG，在电脑检查两张卡的文件和完整 RAW 解码，再使用新设置。拍摄或积压写入中途改变格式、压缩方式不是已验证流程。

缓存完整时，C15 预拍 0.3／1 秒最多为 5／15 帧，C30 对应 9／30 帧；半按不足、缓存不足或写入积压可能更少。30 帧是历史上限，不是整次连拍上限。关闭预拍时，正式帧仍按普通画质输出。

### 双卡规则

受支持的双卡路径按已测原厂单张规则写入。副卡槽功能和主卡槽在每帧提交时记下；前一组仍在写入时改这些设置，只影响后续提交，不改变已排队帧。

| 副卡槽功能 | RAW | RAW+JPEG |
|---|---|---|
| 额外空间／单一目标卡 | NEF 写到原厂选择的目标卡 | NEF + JPEG 写到该卡 |
| 备份 | 两张卡各写 NEF | 两张卡各写 NEF + JPEG |
| RAW 主卡－JPEG 副卡 | 两张卡各写 NEF，与已测原厂 RAW-only 行为一致 | 主卡 NEF，副卡 JPEG |
| JPEG 主卡－JPEG 副卡 | 对受支持的原厂单 JPEG 帧计划，两张卡各写 NEF | 对该计划，两张卡各写 NEF + JPEG |

JPEG-only 沿用原厂文件路径，但采用普通菜单的 JPEG 档位。副卡独立尺寸 JPEG 等未支持的文件计划可能回退原厂 JPEG 行为，不能视为所有双卡组合均已支持。上表不代表自动溢出切卡、写入中拔卡、近满卡或卡故障恢复已通过；每张卡都必须能容纳实际要写的文件。

### 文件表现与限制

- 正常 NEF 使用原厂照片库和写入器，写完可直接回放。RAW 与 RAW+JPEG 的 NEF 通常内嵌 **8256×5504** 预览；RAW+JPEG basic 复用主 JPEG，其余配对档位单独编码 NEF 预览。
- HE 和 HE★ 都是压缩 RAW。记录格式来自该帧实际分配及解码选择；本补丁不编码无损 RAW。HLG／HEIF、DX、C60／C120 RAW 及未支持的特殊处理不在功能范围。
- 刚拍完回放时 RAW 标签可能缺 **L**，但文件记录 Large，重启后显示恢复；这个问题未改。剩余张数和 r／缓冲值也仍沿用原厂 HSFC 估算。
- 保留 RAW 压缩帧及额外预览会增加内存占用，HE★ 比 HE 占用更多缓冲与卡空间。就绪门槛调整支持了已测 HE★ 预拍设置，但不保证无限连拍或持续按 C15／C30 帧率写卡。“!”可能伴随历史帧不可用，应先让写入追上，再等待预拍缓存填满。
- 仍缺少镜头校正块、灰度子图及部分 XMP 校正等可选原厂元数据。现有检查覆盖 Adobe DNG Converter；不能推及所有软件完整等效，机内删除／保护／传输、跟踪对焦和自动捕获也未充分验证。

### 异常与停止 RAW 拍摄

登记或写入失败可能留下 JPEG-only、缺失／不完整文件、临时 `.NE_`、缩小的 1620×1080 NEF 预览或 **`Z8PRESTP.BIN`**。RAW-only 回退 JPEG 可能使用 NEF 预览画质。要核对完整文件集合与解码结果，不能只看是否有报错。

**删除 `Z8PRESTP.BIN` 前，请先看[读取、原因码与恢复说明](stop-file.md)。** 补丁写入任务只检查同名文件存在，不读取内容：空文件、短文件也可能阻止后续 NEF，重启不清除，已有文件不会被覆盖。受支持的双卡帧上，主卡已有停止文件会释放共享 RAW 缓冲，副卡即使没有停止文件也可能退成 JPEG；仅副卡停止或失败时，主卡 NEF 可能已写好。JPEG 回退不保证成功；它也不是关闭普通单拍 RAW 或菜单／显示改动的总开关。

出现异常后停止拍摄，等写入结束，保留两卡相关文件，将可读素材备份到有足够空间的另一存储介质。排查后再删除已备份的停止文件，做短组重试；删除只允许后续重新尝试 NEF，不保证下一帧写入成功，也不补回此前的 RAW。时间预算不能中断已阻塞的原厂 I/O，也不保证不会冻结。原因码不能单独证明卡速不足、卡满或硬件故障。

若要停止额外 RAW 拍摄，在普通“画质”中选择 **JPEG-only**，或退出 C15／C30。v0.2.0 删除 CFG 没有效果；这也不卸载补丁、不移除 ProRes，不保证可以降级或恢复。公开构建默认不附加诊断尾标，删除 CFG 不能切换尾标开关。

HN8 实机记录、公开迁移验证、既有故障反馈及验证范围见[验证记录](validation.md)。
