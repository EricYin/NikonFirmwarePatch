# Z8PRESTP.BIN：读取、原因码与恢复（公开版 v0.2.0）

[中文说明](#这个文件是什么) · [English summary](#english-summary)

**发现停止文件后，先停止继续连拍，等待写入结束，保留文件及相关素材。不要直接删除停止文件后继续长连拍。** 本文依据 v0.2.0 的实际源码核对，原因码说明的是代码走到哪条异常路径，不能单凭它判断卡满、卡速或硬件故障。

## 这个文件是什么

补丁在某些 NEF 写入错误或时间预算超限时，会尝试在对应卡的根目录创建 `Z8PRESTP.BIN`。正常写出的记录是 **32 字节**。

- 对命中补丁的 **C15／C30 RAW 或 RAW＋JPEG 帧**，写入任务发现该文件就跳过该卡的新增 NEF，尝试走原厂 JPEG 写入。选“仅 RAW”也可能得到替代 JPEG，其质量可能采用 NEF 预览档位；卡仍有错误时，JPEG 也不保证写成功。
- 这不是关闭预拍摄、画质菜单或整机 RAW 的开关；普通单拍等原厂 RAW 路径不由这个检查禁用。预拍缓存、HE★ 分配与菜单仍可能生效，不能据此保证卡故障或积压不会影响继续拍摄。
- **双卡不是完全独立的。** 在受支持的双卡帧路径上，主卡已有停止文件时，补丁会释放该帧保留的 RAW 缓冲，随后副卡也会退回 JPEG，尽管副卡没有停止文件。仅副卡停止时，主卡可能已正常写出 NEF。主卡／副卡是该帧提交时的设置，不固定等于 CFexpress／SD。两张卡都要检查。
- **重启不清除它。** 固件仅检查同名文件是否存在，不读取或验证其内容：空文件、短文件或内容异常的同名文件也可能阻止后续 NEF。
- 已有同名文件不会被覆盖，因此保留下来的通常是较早的一次异常，不一定对应最后一帧。修改文件里的原因码不能解除停止或改变时间预算。
- 创建、写入和关闭这个小文件本身也可能失败；代码没有确认 32 字节是否全部成功落盘。因此文件缺失不能证明没有发生错误，格式异常也不能证明不是本版写出的。

请保留停止文件原件、`.NE_`、对应 NEF／JPEG 及两卡目录清单。将可读素材备份到**有足够空间的另一存储介质**，例如外置盘；不要求复制到本机数据卷。空间不足时先保留卡、停止继续使用，不要为腾空间删除待核查素材。

## 读取命令

以下命令只读文件，先检查长度和完整的 16 字节标识区，再解读字段。正常输出中的数字使用十进制。

### macOS / Linux

```bash
python3 -c 'import struct,sys;d=open(sys.argv[1],"rb").read();print("size",len(d),"magic",d[:9].decode("ascii","replace"));sys.exit("INVALID FORMAT: keep the original file; do not delete it") if len(d)!=32 or d[:16]!=b"Z8PRESTOP"+bytes(7) else None;s,n,t=struct.unpack_from("<IIQ",d,16);print("status",s,"shot",n,"clock_us",t)' "/path/to/Z8PRESTP.BIN"
```

把引号内的路径换成实际路径，保留引号。也可以删除最后的路径参数，把文件拖到命令末尾；检查路径已被正确引用或转义后再执行。

### Windows PowerShell

```powershell
& {
    $b = [IO.File]::ReadAllBytes("E:\Z8PRESTP.BIN")
    if ($b.Length -ne 32) { throw "INVALID SIZE $($b.Length): keep the original file; do not delete it" }
    $magic = [Text.Encoding]::ASCII.GetString($b, 0, 9)
    $reservedNonzero = @($b[9..15] | Where-Object { $_ -ne 0 }).Count
    if ($magic -cne "Z8PRESTOP" -or $reservedNonzero -ne 0) { throw "INVALID MAGIC: keep the original file; do not delete it" }
    "size $($b.Length) magic $magic status $([BitConverter]::ToUInt32($b,16)) shot $([BitConverter]::ToUInt32($b,20)) clock_us $([BitConverter]::ToUInt64($b,24))"
}
```

把 `E:\Z8PRESTP.BIN` 换成实际位置。若报长度或标识异常，停止按正常格式解释，保留原件和错误输出。不要补零、编辑或重建这个文件来让命令通过。

正常格式的示例值（不是本次故障的诊断结论）：

```text
size 32 magic Z8PRESTOP
status 3 shot 169896 clock_us 36217878
```

PowerShell 将这些字段显示在同一行。

## 字段含义

所有整数按小端存放。记录没有独立的固件版本字段，也没有 CRC；长度和标识正确只表示符合布局，不能单独证明来源版本或内容未损坏。

| 偏移／长度 | 字段 | 含义 |
|---|---|---|
| `0x00`／9 字节 | magic | ASCII `Z8PRESTOP` |
| `0x09`／7 字节 | 保留区 | 本版写为全零 |
| `0x10`／4 字节 | status | 无符号原因码，见下表 |
| `0x14`／4 字节 | shot | 该帧的快门计数，对应 `ShutterCount`；**不是照片文件名中的流水号**。NEF 没写成时，要结合对应 JPEG、另一张卡及前后帧定位 |
| `0x18`／8 字节 | clock_us | 创建记录时读取的相机内部微秒时间戳；**不是这张 NEF 的写入耗时，也不是日期时间**。仅在同一连续计时会话中辅助比较先后，不能跨重启直接相减 |

## 原因码与检查方向

| status | 代码含义 | 如何理解卡上文件 |
|---|---|---|
| **3** | 检测到时间预算超限，默认预算为 **1,500,000 微秒** | 原厂 NEF 写入路径是在调用返回后检查：原厂返回成功、最终 NEF 文件名存在，然后发现耗时 ≥ 1.5 秒；该路径不因超时撤销 NEF，但仍须完整解码确认内容。后备 `.NE_` 路径则可能在头／预览写完后、或 RAW 尚未写完时发现超时，留下不完整的 `.NE_`。 |
| **4** | 原厂 NEF 写入返回错误、段表等内部检查失败，或后备写法的创建／写入／关闭失败 | 原厂路径会撤销或尝试撤销 NEF 登记；不能据此保证实际残留文件都已清除。后备路径可能留下 `.NE_`。JPEG 会按相应路径写入或回退，但不保证成功；检查两卡的 NEF、JPEG 和临时文件。 |
| **5** | 后备路径的写入和关闭已返回成功，但从 `.NE_` 改名为 `.NEF` 失败 | `.NE_` 可能包含完整内容。保留原件；如需尝试解码，先在备份介质上复制一份再改扩展名，不直接修改证据原件。 |
| **6** | 原厂返回写入成功，但随后按目标 NEF 路径检查，未确认文件存在 | 这是“返回值与存在性检查不一致”，不单独证明文件丢失的具体原因。必须核查相关目录和两张卡；部分路径仍会按成功返回值取消 JPEG，**不能保证存在替代 JPEG**。 |
| 其他 | 本版正常的停止文件调用点不写出这些值 | 不强行解释；保留原文件、读取输出、固件版本及相关素材反馈。 |

**不能用“有没有 `.NE_`”单独确定 status 3 走了哪条路径。** `.NE_` 可能属于此前其他帧；残留或文件缺失也受写入错误影响。必须结合 `shot`、文件名、目录、另一张卡与文件完整性检查。

**1.5 秒不是能强制中断 I/O 的硬截止时间。** 原厂路径只在整个 NEF 写入调用返回后计时；后备路径在若干写入返回点检查，而且最后一个 RAW 分块完成后不会因刚超过预算再改为 status 3。阻塞调用可能持续更久，停止文件也不保证相机不会冻结。

“33 MB ÷ 1.5 秒 ≈ 22 MB/s”只能作数量级参考，不是卡速诊断或最低速度认证。实际文件大小、调用开销、瞬时停顿和所走路径都会影响计时。卡空闲不足、文件系统／介质错误、接触问题或瞬时写入停顿是排查方向，不是原因码已经证明的结论；NEF 登记失败也可能来自锁或数据库等条件，不能直接等同于卡满。

## 自查与恢复

1. 停止继续连拍，等待写入结束。按正常流程关机、取卡；不要为了“无需重启”而在写入中拔卡。
2. 备份可读素材及停止文件，列出两张卡中的 `.NE_` 和相关 NEF／JPEG。按 `shot` 找到对应曝光及前后帧，确认最终 NEF 是否存在、能否完整解码；看见缩略图不等于 RAW 已完整解码。
3. 先处理明显的空间或介质问题。近满卡保护在 v0.2.0 仍未修复；不要仅凭剩余张数或卡的标称速度判断已经安全。
4. 准备重试时，在电脑上**只删除已备份的 `Z8PRESTP.BIN`**；`.NE_` 和相关素材保留。如果两张卡都有停止文件，应分别核查，不要只清一张便推断两卡已恢复。
5. 安全弹出存储卡，再按所需 RAW 设置拍一个短组，等待写完并检查文件。代码没有要求必须重启才能复位的内存锁存状态；删除文件后，后续符合条件的新帧会重新尝试 NEF，**不保证下一帧一定成功，也不会补回此前已退成 JPEG 的 RAW**。再次出现停止文件时保留新记录，停止反复清除重试。

若暂不继续 RAW 测试，可在普通画质菜单选择 JPEG-only。不要修改停止文件的 status 或编辑旧 CFG 来尝试恢复。更换为空闲充足、已验证过的卡后仍需短测；不将某种卡型或速度等级视为不会再触发的保证。

## 反馈时请提供

1. 停止文件**原件**、读取输出或格式错误信息；明确固件版本、工具包版本及构建 manifest／固件 SHA-256（如有）。
2. 文件位于哪张卡，SD／CFexpress、卡型号、容量、速度等级、事发前的大约空闲空间；两张卡是否都有停止文件。
3. `.NE_` 及对应 NEF／JPEG 的路径、大小和完整解码结果；最好提供两卡相关目录清单。不要把 `shot` 当文件号。
4. C15／C30、预拍和后拍时长、画质及 JPEG 档位／★、HE／HE★、单卡／双卡，**主卡槽和副卡槽功能**；事发时是否改过这些设置。
5. 事前拍了几组、每组全按多久、写卡积压／错误提示，以及是否重启、删过停止文件或恢复后再次触发。

不需要公开上传整张卡的个人照片；先提供小文件与文字，必要的影像样本另行约定。

## 核查依据

本文核对的是 [v0.2.0 固件补丁源码](https://github.com/XinmiaoZhao/NikonFirmwarePatch/blob/v0.2.0/z8precapture/firmware.c)：`stop_file()`／`stopped()` 定义格式与存在性行为，`raw_route()`、`stock_nef()` 定义原因码，`flow()`／`take()`／`dual_second()` 定义回退与双卡缓冲生命周期。默认预算来自 `DEFAULT_BUDGET`。既有公开机器码的限定执行记录也覆盖主卡停止导致两卡 JPEG、副卡停止而主卡保留 NEF 的场景；这不替代触发者的真实故障文件核查。

适用的预编译补丁为 33,117 字节，SHA-256 `d71bffd5f64105eeda35d627c5f628dd4c9da6a976c3ba2de09667ea5e49e224`。本文修订不修改该机器码或已发布附件，不能视为修复了触发原因。未知版本的同名文件应单独核对。

## English summary

`Z8PRESTP.BIN` is a sticky, per-card **existence marker** checked by the patched C15/C30 NEF writer. A normal record is 32 bytes: `Z8PRESTOP` followed by seven zero bytes, then little-endian `uint32 status`, `uint32 shot` and `uint64 clock_us` at offsets 16, 20 and 24. The commands above validate length and the full prefix before decoding. An empty or malformed file can still stop NEFs, and can result from an incomplete attempt to write the marker. Existing markers are not overwritten. The record contains no firmware version or CRC; its timestamp is not the write duration.

The writer attempts JPEG fallback, including for RAW-only, but successful JPEG output is not guaranteed. **A stop on the frame's primary card can make both cards fall back to JPEG**, because the shared RAW buffer is released. A stop only on the secondary card can leave the primary NEF intact. This marker does not disable all ordinary RAW shooting or act as a global pre-capture/menu switch. Rebooting does not remove it.

Status **3** means a detected budget overrun (default 1.5 s): the stock path returned success and found the final filename, while the temporary-file fallback can stop with incomplete RAW data. Status **4** covers write/internal-validation failures; **5** is fallback rename failure after successful write/close; **6** is a success return followed by a failed existence check. None identifies card speed, free space or a hardware cause by itself. A `.NE_` file alone does not identify the route or affected frame. Budget checks are cooperative and cannot interrupt a blocked stock I/O call.

Stop shooting, wait for writes, preserve both cards' files, and back up readable data to a separate device with sufficient space. Keep the marker and any `.NE_` files. After investigating the cause, remove only the backed-up marker, safely reinsert the card and test a short burst. New eligible frames may then attempt NEF writing; this does not restore previously lost RAWs or guarantee the next write succeeds. Do not repeatedly clear the marker to continue long bursts. Report the original marker, output, exact firmware identity, both cards' primary/secondary roles, capacity/free space, shooting settings and relevant file lists. Nearly-full-card handling remains unvalidated and unfixed.
