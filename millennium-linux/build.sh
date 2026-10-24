#!/usr/bin/env bash
# Millennium Linux - ISO build script. Run on Debian 12 (real machine, VM or container).
# Ubuntu ships an old, incompatible live-build, so it is not supported.
set -euo pipefail
cd "$(dirname "$0")"

if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo: sudo ./build.sh"; exit 1; fi
. /etc/os-release
if [ "${ID:-}" != "debian" ]; then
  echo "This script needs Debian 12 (Ubuntu's live-build is too old). Use a Debian 12 VM or the GitHub Actions workflow."; exit 1
fi

apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso syslinux-utils \
  isolinux syslinux-common grub-pc-bin grub-efi-amd64-bin mtools dosfstools

# live-build wipes config/ when running "lb config", so keep our files in a safe place
rm -rf .overlay && mkdir .overlay && cp -a config/. .overlay/

lb clean --purge || true
lb config \
  --distribution bookworm \
  --architectures amd64 \
  --linux-flavours amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootloaders "syslinux,grub-efi" \
  --debian-installer none \
  --memtest none \
  --iso-application "Millennium Linux" \
  --iso-volume "MILLENNIUM" \
  --iso-publisher "Millennium Linux" \
  --bootappend-live "boot=live components quiet splash username=y2k hostname=millennium locales=pl_PL.UTF-8 keyboard-layouts=pl timezone=Europe/Warsaw"

cp -a .overlay/. config/
lb build 2>&1 | tee build.log

ls -lh ./*.iso
echo "Done. Write the .iso to a USB stick with Rufus (DD mode) or balenaEtcher."
