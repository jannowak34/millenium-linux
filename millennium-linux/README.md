# Millennium Linux 2000.1

A Y2K-styled live/installable Linux for the Toshiba Satellite C855 (Pentium B960, 8 GB RAM):
Debian 12 + XFCE, bondi-blue gel theme, glossy window buttons, chrome taskbar with a "Start" button.

## Build the ISO
Needs Debian 12 (a VM is fine; Ubuntu and WSL are not supported), ~15 GB free disk, internet.
No Linux machine? Push this folder to a GitHub repo and run the "Build ISO" workflow (Actions tab); the ISO lands under Releases.

    sudo ./build.sh

The ISO appears in this folder. Write it to a USB stick with Rufus (DD mode) or balenaEtcher.

## Use
- Live login is automatic: user `y2k`, password `live`.
- Double-click "Install Millennium Linux" on the desktop to install (Calamares). Install onto an SSD if you can.
- Language/keyboard/timezone default to Polish / Europe/Warsaw (edit `--bootappend-live` in build.sh).

## Regenerate the artwork
    python3 gen_assets.py     # needs python3-pil and python3-numpy

## Layout
- `config/package-lists/` - what gets installed
- `config/includes.chroot/` - files copied into the system (theme, panel, wallpaper, tweaks)
- `config/hooks/normal/` - branding and service trimming
