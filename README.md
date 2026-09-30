# rustdesk-hevc

**RustDesk for Linux with H.265 (HEVC) hardware encoding on AMD and Intel GPUs.**

> Unofficial build. Not affiliated with or endorsed by RustDesk. It is upstream
> RustDesk with a one-line change (see [What's different](#whats-different)).

Stock RustDesk on Linux only uses your GPU to encode **H.264**. Its H.265 encoder for
VA-API is commented out upstream. H.265 needs roughly 30-50% less bandwidth for the same
picture quality, which helps a lot on a slow or metered connection. This project rebuilds
each RustDesk release with that encoder switched back on.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/TheRealEminem/rustdesk-hevc/main/rustdesk-hevc-update | bash
```

It downloads the latest `.deb` from [Releases](../../releases), installs it with `apt`
(asks for your sudo password), and restarts the RustDesk service. **Any active RustDesk
session will drop and need to reconnect.** Prefer to do it by hand? Download the `.deb`
from Releases and run `sudo apt-get install --reinstall ./rustdesk-*-hevc.deb`.

Your existing RustDesk ID, password and settings are kept.

## Will it work on my machine?

You need **all** of these on the machine being controlled (the "host"):

| Requirement | How to check |
|---|---|
| Linux, x86_64, Debian/Ubuntu family (built on Ubuntu 22.04, needs glibc 2.35+) | `dpkg --print-architecture` shows `amd64` |
| An **AMD** (Mesa `radeonsi`) or **Intel** GPU that can encode HEVC through VA-API | `vainfo` lists `VAProfileHEVCMain : VAEntrypointEncSlice` |
| X11 session (the login screen also works when the service is running) | `echo $XDG_SESSION_TYPE` |

The other side (the "client" you connect *from*) must be able to decode H.265. Recent
Macs, Windows PCs with a modern GPU, and current phones all can.

**Not covered:**
- **NVIDIA** GPUs: stock RustDesk already does H.265 through NVENC. You don't need this.
- **No GPU / cloud servers / Raspberry Pi:** there is no hardware encoder for this to use.
- **ARM:** not built.

**Tested on:** AMD Radeon Pro WX 5100 (Polaris), Mesa 25.2, Ubuntu 24.04 base, X11,
connected from a Mac. Intel is expected to work but has not been tested here. Reports welcome.

## Check that it's working

Connect to the machine, then look at the newest server log on the host:

```bash
grep -hE 'used preference|new encoder' ~/.local/share/logs/RustDesk/server/rustdesk_rCURRENT.log | tail
```

You want to see `encoder: H265` and `name: "hevc_vaapi"`. If it shows `h264_vaapi`,
open the client's toolbar, go to **Display -> Codec**, and pick **H265**.

**Picture looks blurry?** RustDesk lowers its quality when it thinks bandwidth is tight.
On the client, choose Display -> Image quality -> **Optimize image quality**.

## Updates

- A GitHub Action checks for a new upstream RustDesk release **every day** and builds a
  matching `-hevc` release when there is one. Compiling takes about an hour.
- Installing is **manual on purpose**: run the install command above again, or
  `rustdesk-hevc-update --force` to reinstall the same version.
- Don't use RustDesk's own "update available" prompt on a machine with this build. It
  installs the stock version and HEVC goes away. Run the updater instead.

## What's different

RustDesk's GPU encoding code (the [hwcodec](https://github.com/rustdesk-org/hwcodec)
library) contains this, with the note *"remove because poor quality on one of my
computer"*:

```rust
// codecs.push(CodecInfo {
//     name: "hevc_vaapi".to_owned(),
//     format: H265, ...
```

[`patch_hwcodec.py`](patch_hwcodec.py) uncomments that block, and the workflow in
[`.github/workflows/build.yml`](.github/workflows/build.yml) builds RustDesk against the
patched copy using the same toolchain versions as upstream's own release workflow. Nothing
else is changed. If upstream moves that code, the patch stops with an error and no release
is published, rather than shipping a build without HEVC.

## License and source

RustDesk is licensed under the [AGPL-3.0](https://github.com/rustdesk/rustdesk/blob/master/LICENSE),
and so are these binaries. The complete source for any release is the upstream tag of the
same version number plus the one-block change in `patch_hwcodec.py`.

## Limitations

- Builds are tested by me on the one machine above, and the automated build cannot test
  GPU encoding (GitHub's servers have no GPU).
- The quality reason upstream disabled this encoder is real for some hardware. If H.265
  looks worse than H.264 on your GPU, switch the client's codec back to H264.
