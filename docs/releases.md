# 发布包与独立验证

工具包版本 `v0.1.0` 与固件版本号相互独立。用户仍可选择 ProRes、预拍摄或两者，以及 `NN.NN` 版本号和一个小写字母加一位数字的 tag。默认功能仍为 ProRes；“默认预编译”指选择预拍摄后取得该功能代码的方式。

## 下载和使用

普通用户下载 [Release 的完整 toolkit ZIP](https://github.com/XinmiaoZhao/NikonFirmwarePatch/releases/tag/v0.1.0)，在独立目录解压，按 [README](../README.md)安装 Python 依赖。工具包包含全部工具源码、许可证、验证配方和 `resources/precapture.bin`；不包含编译器、Python 运行库、官方完整固件或修改后的完整固件。

GitHub 自动生成的 Source code 归档和 Git 克隆不包含机器码。源码用户可显式使用 `--code-source source --compiler clang`，或者从**同一版本**完整工具包取得机器码，放在对应源码的 `resources/precapture.bin`。不要混用不同版本的代码和配方；加载时始终检查固定长度及哈希。

Release 的 `SHA256SUMS.txt` 提供 ZIP 的校验值。macOS 可运行 `shasum -a 256 -c SHA256SUMS.txt`，Linux 可运行 `sha256sum -c SHA256SUMS.txt`；Windows PowerShell 可用 `Get-FileHash .\NikonFirmwarePatch-v0.1.0-toolkit.zip -Algorithm SHA256` 与清单比较。校验信息应从可信的项目发布页面取得；同一不可信来源提供的文件和哈希不能证明来源真实。

默认预编译构建不运行 Clang，也不联网下载补丁。缺失或损坏的机器码会报错，并在写输出前停止；不会自动改为源码编译。源码方式仍要求生成已审阅的机器码及入口地址，不提供放宽检查的选项。ProRes 修改继续由 Python 生成并逐块匹配固定配方。

## 如何验证可自定义的固件

1. 构建器和独立验证器分别检查官方输入 SHA-256：`d67413c2ede6b9ce8887175f20700bd9fbad2a973a4820968c45503d15d80d96`，文件大小为 99,051,117 字节。
2. 对所选功能，根据公开配方核对各修改位置的原字节和新字节哈希。组合包只允许已声明的共享装载修改。
3. 验证版本指令、内部字符串、尾部标识和模块名，并检查版本递增。构建时将用户要求的版本及 tag 传给独立验证器，不能只证明输出“自洽”。
4. 独立解开输出封装，重算模块 CRC、整包 CRC 和封装摘要；检查修改范围外的所有字节及其他模块不变。
5. 写入后读回本地输出并确认其哈希，再生成 manifest。整包哈希标识这次产物，不能代替前面的正确性核验。

例如，对自定义版本 `17.42.x7` 的组合包：

```sh
python patch.py "/path/to/Z_8_0311.bin" --features prores precapture --version 17.42 --tag x7 --output build/custom
python verify.py "/path/to/Z_8_0311.bin" "build/custom/Z_8_1742.bin" --features prores precapture --version 17.42 --tag x7
```

`verify.py` 不导入构建器、编码器或打包器，不以候选固件自己的 manifest 作为“正确答案”。它读取发布的配方，直接检查输入和输出。单独运行时若省略选项，会检测功能并检查版本一致性，但不声称检查了用户原本想选的功能或版本。

固定整包参考哈希仅覆盖固定的输入、功能、版本和 tag。其他自定义组合通过上述规则验证，无需公布每一种可能的整包哈希，更无需分发完整固件。验证通过表示符合已审阅构建规则，不扩大真实上机测试的范围。当前只在 macOS 完成完整固件构建回归，不能据此宣称 Windows／Linux 已经过相同实测。

## 发布者与开发者复现

源码编译使用 `resources/precapture.json` 记录的编译参数及入口地址。当前机器码为 30,301 字节，SHA-256 为 `479f4e37db3968a9e796fc97d865246793ebbac83b28f10a95711535c45cb715`，与前一版已审阅实现相同；改变的是分发、构建和验证方式。

完成并提交源码后，在干净的对应提交上生成工具包：

```sh
python tools/build_release.py --tag v0.1.0 --compiler clang --output /path/to/new-release-assets
python tools/check_release.py /path/to/new-release-assets/NikonFirmwarePatch-v0.1.0-toolkit.zip --commit COMMIT_SHA
python tests/validate_distribution.py --archive /path/to/new-release-assets/NikonFirmwarePatch-v0.1.0-toolkit.zip --archive-only --report /path/to/new-archive-report.json
```

发布构建器要求记录中的编译器版本，并再次核对机器码哈希。它只读取明确允许的、已提交源码及自编译代码，不读取任何完整固件。ZIP 包含对应提交的完整源码、构建和验证脚本、许可证，以及带文件哈希与源码提交的 `release-manifest.json`。生成时使用固定时间和文件模式。

独立包检查器检查精确成员清单、文件类型、大小、源码字节、机器码哈希和 manifest。多出完整固件路径、缺文件、重复成员、损坏内容或不匹配的来源提交都会被拒绝。检查 Git 内容仍使用原有 `tools/check_repository.py`；机器码和 ZIP 保持 Git 忽略，只作为 Release 附件发布，不能用强制纳入绕过仓库规则。

发布前运行功能回归和源码／预编译等价性测试，检查 Release 归档；上传后下载附件再核对。正式发布的资产与源码 tag 一同保留，有修正时创建新版本。源码、编译材料和许可证随同补丁提供；Nikon 固件的许可不因此改变。
