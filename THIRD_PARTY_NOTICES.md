# Third-party notices

The root MIT license covers original project code and documentation. It does not replace upstream licenses, grant rights to trademarks, or relicense third-party material embedded in patches and evaluated profiles. External runtimes, Docker images, and model services retain their own terms and are not redistributed in this Git repository.

## SWE-Milestone

The integration patch in `patches/swe-milestone-oauth.patch` contains upstream source context and modifications. Upstream: https://github.com/DeepCommit-ai/SWE-Milestone, pinned commit `17a8f1593e172e26b36cea15e2b30fb9536c93f5`. The separately acquired SWE-Milestone dataset is MIT-licensed according to its pinned dataset card; it is not vendored here.

```text
MIT License

Copyright (c) 2025 SWE-Milestone Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## ripgrep

Source patches in `reports/patches/` contain context from ripgrep. Upstream: https://github.com/BurntSushi/ripgrep. The initial task series uses the 14.1.1-to-15.0.0 benchmark source. ripgrep offers MIT or Unlicense; redistribution here uses its MIT option. The following notice is from the 14.1.1 tag.

```text
The MIT License (MIT)

Copyright (c) 2015 Andrew Gallant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

## Ponytail

The pinned 5.3.2 profile assets are distributed under MIT, Copyright (c) 2026 DietrichGebert. The full notice is retained at [`profiles/ponytail/assets/LICENSE`](profiles/ponytail/assets/LICENSE). Origin and hashes are recorded in [`profiles/ponytail/manifest.json`](profiles/ponytail/manifest.json).

## Caveman

The pinned Caveman v4.0.1 assets are distributed under Apache-2.0. The full license is retained at [`profiles/caveman/assets/LICENSE`](profiles/caveman/assets/LICENSE), with the historical MIT notice at [`profiles/caveman/assets/LICENSE-MIT`](profiles/caveman/assets/LICENSE-MIT). This is not a claim that all pinned assets may be selected under MIT. Upstream licensing: https://github.com/JuliusBrussee/caveman/blob/d262ab3882952a59312ff3537cd86d894523c5ab/LICENSING.md.

Applicable attribution from the pinned upstream NOTICE:

```text
Caveman
Copyright 2026 Julius Brussee

Before Caveman 3.0.0, the parts of this repository outside the Engine-linked
runtime were licensed under the MIT License (see LICENSING.md). Contributions
made to those parts before 3.0.0 were received under the MIT License and remain
available under it. Its copyright and permission notice is retained in
LICENSE-MIT.
```

The Caveman engine, browser implementation, embedded fonts, and CLI implementation are not included in this profile asset closure. Notices specific to those omitted components are not reproduced here. Local integration/profile code is maintained by this project; the pinned upstream asset bytes and their licenses are preserved.

## External tools

Serena, Codex CLI, SonarQube, Rust tooling, Node, Python, and plotting/setup dependencies are acquired separately. Version manifests identify them; the root license does not cover their distributions or service access. A downstream Docker/runtime distribution requires its own complete dependency-license inventory.
