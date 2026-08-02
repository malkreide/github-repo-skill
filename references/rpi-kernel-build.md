# Building the Raspberry Pi Linux kernel

Read this file when a `raspberry-pi` repo ships a kernel build, an out-of-tree
kernel module, or a Device Tree overlay — that is, whenever the README has to
carry build instructions or the CI has to satisfy header and toolchain
prerequisites.

Condensed from the official Raspberry Pi documentation
([Linux kernel](https://www.raspberrypi.com/documentation/computers/linux_kernel.html)).
Unlike the other reference files in this bundle, the rules here are *not*
derived from failures observed across the portfolio — they restate the upstream
procedure, with the version- and mode-dependent steps called out separately.

The Raspberry Pi kernel lives at
[`raspberrypi/linux`](https://github.com/raspberrypi/linux) and lags upstream by
design: Raspberry Pi integrates *long-term* Linux releases, tests each one on a
`next` branch, and only then merges it into `main`.

---

## Pick the target first

Four values follow from the model, and every later command depends on them.
Getting one wrong produces a kernel that builds and does not boot.

| Arch | Model | `KERNEL` | defconfig |
|---|---|---|---|
| 64-bit | 3 · CM3 · 3+ · CM3+ · Zero 2 W · 4 · 400 · CM4 · CM4S | `kernel8` | `bcm2711_defconfig` |
| 64-bit | 5 · 500/500+ · CM5 | `kernel_2712` | `bcm2712_defconfig` |
| 32-bit | 1 · CM1 · Zero · Zero W | `kernel` | `bcmrpi_defconfig` |
| 32-bit | 2 · 3 · CM3 · 3+ · CM3+ · Zero 2 W | `kernel7` | `bcm2709_defconfig` |
| 32-bit | 4 · 400 · CM4 · CM4S | `kernel7l` | `bcm2711_defconfig` |

**32-bit Raspberry Pi OS on 4-series devices runs a 32-bit userland on a 64-bit
kernel.** A 32-bit *userland* is therefore not evidence of a 32-bit kernel. To
actually build and boot one: `ARCH=arm` at build time, and `arm_64bit=0` in
`config.txt`.

## Get the source

```bash
sudo apt install git
git clone --depth=1 https://github.com/raspberrypi/linux
```

`--depth=1` fetches the current active branch — the one Raspberry Pi OS images
are built from — without history. Omit it for the full repository. For a
different branch without history:

```bash
git clone --depth=1 --branch <branch> https://github.com/raspberrypi/linux
```

---

## Native build (on the Pi)

```bash
sudo apt install bc bison flex libssl-dev make

cd linux
KERNEL=kernel8                       # from the table above
make bcm2711_defconfig               # from the table above

make -j6 Image.gz modules dtbs       # 64-bit
make -j6 zImage modules dtbs         # 32-bit
```

`nproc` reports the core count; the documentation recommends `-j` at roughly
1.5× that number.

## Cross-compile

```bash
sudo apt install bc bison flex libssl-dev make libc6-dev libncurses5-dev
sudo apt install crossbuild-essential-arm64      # 64-bit target
sudo apt install crossbuild-essential-armhf      # 32-bit target

cd linux
KERNEL=kernel8
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- bcm2711_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image modules dtbs
```

32-bit uses `ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-` and the `zImage`
target.

`ARCH` and `CROSS_COMPILE` belong on **every** invocation — `defconfig`,
`menuconfig`, the build, and `modules_install` alike. A single call without them
configures or builds for the host instead of the target.

### The 64-bit image name differs between the two modes

The documented native path builds and installs `Image.gz`; the cross-compile
path builds and installs `Image`. Copy the artefact you actually built —
`arch/arm64/boot/Image.gz` or `arch/arm64/boot/Image` — rather than the one the
other section names.

### `sudo` drops the cross toolchain from `PATH`

`modules_install` needs root, and plain `sudo make` loses the toolchain. Hence
the `env` wrapper in the cross-compile path:

```bash
sudo env PATH=$PATH make -j12 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  INSTALL_MOD_PATH=mnt/root modules_install
```

---

## `LOCALVERSION` — do this before the build, not after

Without it, a custom kernel overwrites the stock modules in `/lib/modules` and
`uname -r` gives no hint which kernel is running. In `.config`:

```
CONFIG_LOCALVERSION="-v7l-MY_CUSTOM_KERNEL"
```

Same setting in `menuconfig` under *General setup → Local version - append to
kernel release*.

## Configure: `menuconfig`

```bash
sudo apt install libncurses5-dev
make menuconfig                                                  # native
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig      # cross, 64-bit
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig      # cross, 32-bit
```

Arrow keys navigate, Enter opens a submenu (`--->`), space toggles a binary
option, `H` shows help, Escape twice goes up or exits. Changes are written to
`.config`, so configurations can be saved and restored by copying that file.

---

## Install

Install the modules first, then the kernel image, Device Tree blobs, and
overlays. **Back up the running kernel before overwriting it** — the copy is the
only way back if the new one does not boot.

**Native, 64-bit:**

```bash
sudo make -j6 modules_install
sudo cp /boot/firmware/$KERNEL.img /boot/firmware/$KERNEL-backup.img
sudo cp arch/arm64/boot/Image.gz /boot/firmware/$KERNEL.img
sudo cp arch/arm64/boot/dts/broadcom/*.dtb /boot/firmware/
sudo cp arch/arm64/boot/dts/overlays/*.dtb* /boot/firmware/overlays/
sudo cp arch/arm64/boot/dts/overlays/README /boot/firmware/overlays/
sudo reboot
```

**Native, 32-bit:** same shape, but `arch/arm/boot/zImage` as the image, and the
`.dtb` source path depends on the kernel version:

| Kernel version | 32-bit `.dtb` path |
|---|---|
| up to 6.4 | `arch/arm/boot/dts/*.dtb` |
| 6.5 and above | `arch/arm/boot/dts/broadcom/*.dtb` |

64-bit was always under `broadcom/`; only the 32-bit path moved.

**Cross-compile:** the same copies, into a mounted boot medium instead of
`/boot/firmware`. Run `lsblk` before and after connecting the medium — the newly
appeared device is it. With `sdb1` as the FAT32 boot partition and `sdb2` as the
root partition:

```bash
mkdir -p mnt/boot mnt/root
sudo mount /dev/sdb1 mnt/boot
sudo mount /dev/sdb2 mnt/root
# ... modules_install with INSTALL_MOD_PATH=mnt/root, then cp into mnt/boot ...
sudo umount mnt/boot
sudo umount mnt/root
```

### Keep a stock kernel bootable

Instead of overwriting `kernel.img`, install under a distinct name and select it
in `config.txt`:

```
kernel=kernel-myconfig.img
```

Combined with a custom `LOCALVERSION`, the system-managed kernel and its modules
stay untouched, and reverting is a one-line edit.

---

## Patches

Read the version out of the tree before applying anything — patchsets are
version-specific, and some require a specific commit:

```bash
head Makefile -n 4        # VERSION / PATCHLEVEL / SUBLEVEL, e.g. 6.1.38
uname -r                  # what is currently running
```

Single-file patches use `patch`; mailbox-format directories use Git, which needs
`user.name` and `user.email` configured:

```bash
cat patch-6.1.38-rt13-rc1.patch | patch -p1     # single file
git am -3 /path/to/patches/*                    # mailbox format
```

## Kernel headers

Out-of-tree modules compile against the headers. A full clone already contains
them; otherwise:

```bash
sudo apt install linux-headers-rpi-v8            # 64-bit
sudo apt install linux-headers-rpi-{v6,v7,v7l}   # 32-bit
```

**The apt package trails new kernel releases by weeks.** For a freshly released
kernel, clone the tree instead of waiting for the package. Installation shows no
progress indicator and takes several minutes.

## Contributing changes back

| Change | Where it goes |
|---|---|
| Raspberry Pi-specific code or bug fix | pull request to `raspberrypi/linux` |
| Generic driver or generic kernel bug fix | upstream Linux first, then it reaches Raspberry Pi |

Upstream Linux development happens on **mailing lists, not GitHub** — submit the
change as an emailed patch following *Submitting patches: the essential guide to
getting your code into the kernel* and the Linux kernel coding style. From
there, a change reaches the Raspberry Pi kernel via the next long-term release.

---

## Consequences for a repo built with this skill

- **Build instructions must name `ARCH`, the defconfig, and the target.** A bare
  `make` is not reproducible across models — and the model table above is the
  part a reader cannot reconstruct.
- **Kernel modules pin a kernel version.** State the version the module was
  built against in both READMEs; headers and running kernel have to match.
- **Do not wire a full kernel build into `ci.yml`.** It needs the cross
  toolchain and runs far longer than the linting jobs the bundled workflow is
  built for. Build the module against installed headers in CI, and document the
  kernel build in the README instead.
