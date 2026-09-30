# rustdesk-hevc

Builds upstream [RustDesk](https://github.com/rustdesk/rustdesk) for Linux x86_64 with
hwcodec's `hevc_vaapi` encoder re-enabled (upstream comments it out), so AMD/Intel GPUs can
encode H.265 via VA-API.

- `.github/workflows/build.yml` checks daily for a new RustDesk release, patches hwcodec,
  builds the `.deb`, and publishes it as release `<tag>-hevc`. Run it manually from the
  Actions tab to build a specific tag.
- `patch_hwcodec.py` does the one-block patch and fails loudly if upstream code moves.
- `rustdesk-hevc-update` installs the newest release on the host (`--force` to reinstall).
