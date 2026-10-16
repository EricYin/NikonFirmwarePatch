# Validation scope / 验证范围

2026-10-17. This document separates implementation testing from support for a newly generated firmware package. The public input support scope remains official Nikon Z8 C 3.11.

## Hardware observations

The pre-capture implementation was tested in five bursts: C15 0.3 s (5 NEFs), C15 1 s (15), C30 0.3 s twice (9 each), and C30 1 s (30). All 68 NEFs passed structure checks and complete Adobe DNG Converter 18.1.1 decoding. Their file-number sets matched the camera's pre-capture JPEG sets. No temporary NEF or stop file remained. Ordinary single-shot NEFs also decoded normally.

The readable timer groups matched their corresponding JPEGs; one nine-frame group's timer display was off, so visual timer correspondence was not assessable for that group. The same setting was repeated successfully. This limitation is retained rather than counting that group as a successful timer test.

The 30-frame group finished writing in about 15 seconds including JPEGs. Normal power-off/power-on refreshed the photo database and made the RAW icon visible in playback. Retriggering while the card was busy, long post-release bursts, all card types, and all converter applications were not tested.

Existing ProRes hardware checks covered the four profiles, clip identifiers, complete decoding and per-bank persistence. These observations do not certify every new build or every combination of settings.

## Public-source offline checks

- The three choices—ProRes only, pre-capture only and both—build from the exact official 3.11 fixture and pass independent package verification. The shared text-loader edit is composed once. Unselected bytes and other modules are preserved.
- The original ProRes regression suite is retained. Feature tests cover conflicts, occupied patch space, repeated application, wrong feature claims, existing-output protection, invalid configuration limits, guards under optimized Python and unrelated changes hidden behind repaired checksums.
- Bounded execution of the public pre-capture machine code uses five archived real-frame inputs and explicit filesystem, heap, clock and DMA models. All 47 cases passed, including refusal paths, failures and deliberately defective negative controls. This is CPU execution with modeled services, not a physical camera or proprietary codec simulation.
- The generated 15 NEFs (three configurations × five frames) passed independent structure and metadata checks and complete decoding. Every RAW sample matched the existing decode of its input payload. Two deliberately damaged-file controls were rejected. The optional diagnostic filename padding was verified to be zero.
- An additional compatible-input regression confirmed preservation outside the selected patch and identical NEF output for the same archived inputs. This does not expand the publicly supported input beyond official 3.11.

The official-input combined build also reached the firmware-version menu in QEMU with an empty firmware error table; the loaded code, three hooks and allocation table matched the built image. One additional compatible-input boot recorded startup error 64, with an error table identical to a prior reference-model run. A fresh reference-firmware control and an unchanged repeat of the compatible-input build completed without that error. The warning is retained and is not counted as a clean boot or proof that the patch caused or fixed the model's timing behavior.

The source-bound [validation summary](validation-summary.json) records these checks without distributing the input firmware or capture data.

The public source uses its own configuration/file identifiers and clears optional diagnostic filename padding. The default configuration omits the diagnostic footer. Publicly generated packages have not each been installed on a camera. None of these checks proves freedom from freezes, data loss, dropped frames or hardware damage.

The firmware, photos, full device metadata, emulator images and native testing inputs are not distributed. Repository tests require a user-supplied official package; the archived-frame execution cannot be reproduced from this source checkout alone. Compatibility profiles contain hashes, not embedded firmware.

## 中文

预拍摄实现经过五组上机：C15 0.3 秒 5 张、C15 1 秒 15 张、C30 0.3 秒两次各 9 张、C30 1 秒 30 张，共 68 张 HE NEF。全部通过结构核对和 Adobe DNG Converter 18.1.1 完整解码，文件编号集合与相机标记的预拍 JPEG 对应，无临时 NEF 或停止文件残留，普通单拍 NEF 也正常。

可读计时器组逐帧对应；其中一组九帧因计时器黑屏无法判断这一项，随后同设置重拍通过。该组不计为计时器验证成功。30 张那组连同 JPEG 约 15 秒写完；写完后正常关开机重新加载，回放显示 RAW 标识。忙碌时再次触发、长时间后拍、全部卡型和全部解码软件尚未覆盖。

公开源码已验证三种功能组合、独立封装和改动范围、原 ProRes 回归及各类冲突／失败保护。公开预拍机器码的 47 项限定执行通过；五帧存档输入在三种配置下生成的 15 张 NEF 全部完整解码，RAW 样本与输入负载既有解码一致，逐帧元数据和预览核对通过，两个损坏文件负控被拒。可选诊断尾标的文件名填充区清零通过。另以兼容输入进行了窗口外字节保持和同输入 NEF 一致性的回归，但不扩大官方 3.11 之外的公开支持范围。

官方输入的组合包还通过 QEMU 启动，进入固件版本菜单且固件错误表为空；代码、三处钩子和分配表的装载内容与构建一致。另一次兼容输入启动出现错误 64，错误表与此前参考模型的一次记录完全相同；本轮原参考固件对照，以及固件和输入均未改变的兼容输入复跑，均未出现该错误。保留这次告警，不将其计为无错误启动，也不据此断言补丁导致或解决了模型时序问题。[验证摘要](validation-summary.json)绑定公开源码，并记录验证范围。

限定执行中的文件系统、堆、时钟与 DMA 是显式模型，不能当作硬件或压缩编码器仿真。公开版调整了配置／文件标识并清零诊断尾标，默认不添加该尾标；并非每个公开脚本新生成的包都已上机。测试不保证不会冻结、丢帧、损坏数据或相机。

仓库不分发固件、照片、完整设备元数据、模拟器映像和原指令测试输入。仓库内测试需自行提供官方固件；只克隆源码不能重现存档帧执行。兼容性 profile 保存指纹，不嵌入固件。
