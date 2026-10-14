# Attribution and license scope

Copyright (C) 2026 NikonFirmwarePatch contributors.

The original tool source is licensed under **GPL-3.0-only**; see [LICENSE](LICENSE). This license does not grant rights to user-supplied Nikon firmware. Output licensing depends on its contents, including any generated code; the complete output firmware is not represented as a GPL-licensed distribution. See [GNU's explanation of program output](https://www.gnu.org/licenses/gpl-faq.en.html#WhatCaseIsOutputGPL).

## References and dependencies

- The Nikon package XOR indexing format was studied with reference to [Nikon Hacker's Package.cs](https://github.com/simeonpilgrim/nikon-firmware-tools/blob/main/Nikon-Patch/LocalUI/Package.cs). This repository includes neither that C# source nor its lookup tables. The implementation recovers equivalent parameters from the user-supplied package.
- [Capstone 5.0.7](https://github.com/capstone-engine/capstone/tree/5.0.7) is installed separately to inspect generated ARM64 instructions. Its code and runtime are not bundled here; its license is available in [LICENSE.TXT](https://github.com/capstone-engine/capstone/blob/5.0.7/LICENSE.TXT).

The compatibility profile contains hashes and layout parameters, not firmware contents. New patch instructions are generated from source; menu structures and text are read from the user's input.

The screenshots document the firmware interface running in an emulator. The tool's source-code license does not relicense the depicted firmware interface.
