# Validation scope / 验证范围

2026-10-17. Public input support remains **official Nikon Z8 C 3.11**. Implementation tests, public-source regression and physical installation of a newly generated package are different claims.

## Hardware observations

| Implementation and setting | Recorded result | Scope |
|---|---|---|
| Registered RAW+JPEG, C15 0.3/1 s and C30 0.3/1 s | 59 historical NEFs, all structurally checked and fully decoded; same-number JPEG sets matched | User observed paired RAW+JPEG playback without a power cycle or card swap |
| Current RAW-only full-size preview, the same four planned settings | 59 historical NEFs: 5 + 15 + 9 + 30 | No separate JPEG for those historical numbers; full-size embedded preview |
| Current RAW-only, eight exploratory C30 bursts while writing | 164 additional historical NEFs | Recorded frames all saved and decoded; “!” pre-capture indication appeared temporarily during backlog |

The current RAW-only run therefore contains **223 historical NEFs**, plus three ordinary single-shot NEFs. All 223 passed complete Adobe DNG Converter 18.1.1 decoding. Each contained an 8256×5504 JPEG of about 3.15–3.32 MB, with JPEG marker structure, quantization tables, Huffman tables and sampling matching the camera-made NEF reference. Total file sizes were 21.26–21.46 MB. The user reported full-size in-camera preview; no photograph of the information page or separate zoom/page-turn/rescan assessment was supplied.

Groups 1–7 contain **139 timer-visible frames**, all matched to their own embedded full-size images. The other **84** frames have no visible timer; their records and distinct RAW mosaics were checked, but image-to-timer correspondence is not claimed. These totals are recomputed from the per-file/per-group records: 5 + 15 + 9 + 30 + 30 + 28 + 22 = 139; the eight exploratory groups total 164. Preliminary narrative totals of 144 and 166 were arithmetic errors, not additional verified frames.

The 38 post-release JPEGs retained the original fine quantization tables. The new preview-quality hook only changes selected RAW-only history frames. The latest revision did not repeat the earlier RAW+JPEG hardware bursts; its RAW+JPEG writer/registration behavior is retained and covered by offline regression. **RAW+JPEG NEFs still embed only 1620×1080.** Full-size embedded preview applies to the supported RAW-only configuration.

Busy-card testing does not establish unrestricted continuous capture. The “!” indicator coincided with pending writes and later cleared; its exact meaning/threshold has not been established with an original-firmware control. Some bursts contained fewer than 30 frames, consistent with shorter available history, and no recorded frame was missing from the file set. Deletion, protection, near-full cards, all card types, dual-card settings and all converter applications remain untested or incomplete.

Existing ProRes hardware observations covered all four profiles, clip identifiers, complete decoding and per-bank persistence. They do not certify every new build or setting combination.

## Public-source regression

- All three feature selections—ProRes only, pre-capture only and both—build from official 3.11 and pass independent package verification. Shared text-loader composition occurs once; unselected bytes and other modules are preserved. The original ProRes recipe and its 16-check regression remain unchanged.
- Feature tests cover occupied/conflicting windows, new writer/database/preview dependencies, repeat application, incorrect feature claims, repaired checksums hiding unrelated edits, Python optimization, configuration modes and output protection. The interactive combined build matches the explicit combined build. RAW+JPEG and RAW-only produce identical firmware bytes and different configuration files.
- **107 bounded machine-code cases passed**, including both public default configurations in C15/C30, rejection of the previous public configuration format, registration/cancellation order, failure fallbacks and 11 deliberately faulty control builds. The actual built image supplies the code and patched call sites. Original preview-parameter and quantization routines execute; filesystem, database, heap, clock and DMA services have explicit models.
- **10 original-writer cases passed.** The original still-image writer executes the patch's segment/attribute parameter block. File bytes, sizes, dimensions, write events and cancellation behavior are checked. Three defective builds are rejected at this layer for width, length and cache-cleaning violations.
- **55 generated NEFs passed independent structure/source checks; 25 were fully decoded** with Adobe DNG Converter 18.1.1. Every decoded RAW sample equals the existing decode of its archived real-frame payload. Both public output modes, diagnostic and non-diagnostic output, and fallbacks are covered. Two damaged-file controls were rejected; diagnostic filename padding is zero. Full-size JPEG streams in these CPU tests are supplied test inputs, not a simulation of hardware JPEG encoding.
- A compatible-input regression preserves all unrelated modifications. Normalizing only public file/protocol identifiers and diagnostic identity reconstructs the exact machine code, payload and complete package of the hardware-tested implementation. **The actual public output is not byte-identical to that reference.** This regression does not extend public support beyond official C 3.11.
- The official-input combined build booted and completed an ordinary RAW still capture in the established QEMU camera model. Its full-size NEF preview retained the stock quantization tables. The run used explicit model inputs, no CPU register redirection and no debugger RAM patches. **It does not exercise end-to-end C15/C30 pre-capture or establish physical-camera behavior.** Earlier model startup-error observations remain part of the prior validation history; a successful current run does not establish model or firmware reliability.

The [source-bound validation summary](validation-summary.json) records the completed release checks. Public source uses its own file/protocol identifiers, v2 card configuration and diagnostic identity. The optional diagnostic footer is off by default. Earlier v1 configurations are rejected and must be regenerated for this release.

No new public package was installed on a physical camera during this release preparation. None of these checks proves freedom from freezes, dropped frames, data loss or hardware damage. Firmware, original photos, complete device metadata, emulator images and archived native-test inputs are not distributed. Repository tests require a user-supplied official package; a source-only checkout cannot reproduce the archived-frame and hardware checks.

## 中文

本次公开支持的构建输入仍仅限**官方 Z8 C 3.11**。原厂照片库登记的 RAW+JPEG 实现已上机四组，C15／C30 各 0.3 秒和 1 秒，共 **59 张历史 HE NEF**，全部结构核对和完整解码通过；用户确认不关机、不换卡即可看到 RAW+JPEG 配对回放。

当前带全尺寸内嵌预览的 RAW-only 实现，上机四组计划试验 59 张，加八组边写卡边拍的探索性试验 164 张，共 **223 张历史 NEF**，另有三张普通单拍 NEF。223 张全部由 Adobe DNG Converter 18.1.1 完整解码；每张内嵌 8256×5504 JPEG，约 3.15–3.32 MB，标记结构、量化表、哈夫曼表和采样与相机自产 NEF 参照一致；NEF 总体积 21.26–21.46 MB。用户报告机内显示完整尺寸，但没有提供信息页照片或单独报告放大、翻页和关开机重扫。

按逐文件／逐组记录重算，1–7 组有计时器的 **139 帧**全部与自身内嵌图对应，另外 **84 帧**没有可见计时器，只检查记录一致性和 RAW 马赛克互异，不计为图像对应通过。139 = 5 + 15 + 9 + 30 + 30 + 28 + 22；八组探索性 NEF 合计 164。初步文字摘要中的 144 和 166 是汇总算术错误，不是额外验证过的帧。

38 张后拍 JPEG 保持 fine 量化表。最新预览修订没有重新上机拍 RAW+JPEG，其保留的写入／登记路径由离线回归覆盖。**RAW+JPEG 的 NEF 内嵌图仍为 1620×1080；当前只有所提供的 RAW-only 配置内嵌全尺寸图。**

写卡积压时曾出现“!”预拍标志，之后消失；没有原厂同节奏对照，确切含义和阈值尚不清楚。有些组可用历史不足 30 帧，文件集合与记录下来的帧相符，不能据此保证无限连续预拍。机内删除、保护、近满卡、全部卡型／双卡配置及所有解码软件尚未充分测试。原有 ProRes 四档、编码标识、完整解码和菜单库持久化实测结论继续保留，也不等于所有新组合均已上机。

公开源码本轮完成：三种功能选择的构建和独立整包核验、原有 **16 项 ProRes 回归**、功能冲突与配置／覆盖保护、交互构建，以及两种模式使用相同固件、不同配置的核对。新机器码 **107 项限定执行通过**，含两种默认配置在 C15／C30 的执行、旧配置拒绝、登记和撤销、异常回退及 11 个缺陷构建；原厂写入函数 **10 项通过**，另外三个宽高／长度／缓存清理缺陷被拒。**55 张生成 NEF 独立结构核对通过，25 张完整解码**，每个 RAW 样本都与存档输入既有解码一致；两个损坏文件负控被拒，诊断文件名填充清零通过。CPU 测试中整幅 JPEG 是提供的测试输入，不是硬件 JPEG 编码仿真。

兼容输入回归确认保留无关改动；只还原公开文件／协议标识和诊断身份，就能逐字节重建上机参照的机器码、payload 与整包。**实际公开输出因标识不同，并不与参照包逐字节相同**，也不扩大官方 3.11 之外的支持范围。

官方输入的组合包在既有 QEMU 模型中完成启动和普通 RAW 单拍，NEF 整幅预览保持原厂量化表；运行使用明确的模型输入，没有 CPU 寄存器重定向或调试器 RAM 补丁。**这不是 C15／C30 端到端预拍仿真，也不是硬件结论。** 以往模型启动错误仍保留在历史验证记录中，当前成功运行不证明长期可靠性。

[验证摘要](validation-summary.json)绑定公开源码和已完成检查。公开版使用独立文件／协议标识、v2 配置和诊断身份，默认不添加诊断尾标；旧 v1 配置会被拒绝，必须重新生成。此次发布准备没有给实体相机安装新包。仓库不分发固件、原始照片、完整设备元数据、模拟器映像或存档测试输入；只克隆源码无法重现全部帧和硬件核查。任何测试都不保证不会丢帧、冻结、损坏数据或相机。
