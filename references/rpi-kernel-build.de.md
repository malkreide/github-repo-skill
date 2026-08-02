# Den Raspberry-Pi-Linux-Kernel bauen

Lies diese Datei, sobald ein `raspberry-pi`-Repo einen Kernel-Build, ein
Out-of-Tree-Kernelmodul oder ein Device-Tree-Overlay enthält — also immer dann,
wenn das README Build-Anweisungen tragen muss oder die CI Header- und
Toolchain-Voraussetzungen erfüllen soll.

Kondensiert aus der offiziellen Raspberry-Pi-Dokumentation
([Linux kernel](https://www.raspberrypi.com/documentation/computers/linux_kernel.html)).
Anders als die übrigen Referenzen dieses Bundles stammen die Punkte hier *nicht*
aus real aufgetretenen Fehlern im Portfolio — sie geben das Vorgehen des
Herstellers wieder, mit den versions- und modusabhängigen Schritten separat
hervorgehoben.

Der Raspberry-Pi-Kernel liegt auf
[`raspberrypi/linux`](https://github.com/raspberrypi/linux) und hinkt dem
Upstream-Kernel bewusst hinterher: Raspberry Pi integriert *Long-Term*-Releases
von Linux, testet jedes auf einem `next`-Branch und merged es erst danach nach
`main`.

---

## Zuerst das Ziel bestimmen

Vier Werte ergeben sich aus dem Modell, und jeder spätere Befehl hängt daran.
Ein falscher Wert liefert einen Kernel, der baut und nicht bootet.

| Architektur | Modell | `KERNEL` | defconfig |
|---|---|---|---|
| 64 Bit | 3 · CM3 · 3+ · CM3+ · Zero 2 W · 4 · 400 · CM4 · CM4S | `kernel8` | `bcm2711_defconfig` |
| 64 Bit | 5 · 500/500+ · CM5 | `kernel_2712` | `bcm2712_defconfig` |
| 32 Bit | 1 · CM1 · Zero · Zero W | `kernel` | `bcmrpi_defconfig` |
| 32 Bit | 2 · 3 · CM3 · 3+ · CM3+ · Zero 2 W | `kernel7` | `bcm2709_defconfig` |
| 32 Bit | 4 · 400 · CM4 · CM4S | `kernel7l` | `bcm2711_defconfig` |

**Das 32-Bit-Raspberry-Pi-OS auf 4er-Geräten fährt ein 32-Bit-Userland auf einem
64-Bit-Kernel.** Ein 32-Bit-*Userland* belegt also keinen 32-Bit-Kernel. Wer
wirklich einen bauen und booten will: `ARCH=arm` beim Build und `arm_64bit=0` in
der `config.txt`.

## Quellcode holen

```bash
sudo apt install git
git clone --depth=1 https://github.com/raspberrypi/linux
```

`--depth=1` holt den aktuellen aktiven Branch — denselben, aus dem die
Raspberry-Pi-OS-Images gebaut werden — ohne Historie. Weglassen lädt das ganze
Repository. Für einen anderen Branch ohne Historie:

```bash
git clone --depth=1 --branch <branch> https://github.com/raspberrypi/linux
```

---

## Nativ bauen (auf dem Pi)

```bash
sudo apt install bc bison flex libssl-dev make

cd linux
KERNEL=kernel8                       # aus der Tabelle oben
make bcm2711_defconfig               # aus der Tabelle oben

make -j6 Image.gz modules dtbs       # 64 Bit
make -j6 zImage modules dtbs         # 32 Bit
```

`nproc` nennt die Kernanzahl; die Dokumentation empfiehlt für `-j` etwa das
1,5-Fache davon.

## Cross-kompilieren

```bash
sudo apt install bc bison flex libssl-dev make libc6-dev libncurses5-dev
sudo apt install crossbuild-essential-arm64      # Ziel 64 Bit
sudo apt install crossbuild-essential-armhf      # Ziel 32 Bit

cd linux
KERNEL=kernel8
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- bcm2711_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- Image modules dtbs
```

32 Bit verwendet `ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-` und das
`zImage`-Target.

`ARCH` und `CROSS_COMPILE` gehören an **jeden** Aufruf — `defconfig`,
`menuconfig`, Build und `modules_install` gleichermassen. Ein einziger Aufruf
ohne sie konfiguriert oder baut für den Host statt für das Ziel.

### Der 64-Bit-Image-Name unterscheidet sich zwischen den beiden Modi

Der dokumentierte native Weg baut und installiert `Image.gz`, der
Cross-Compile-Weg `Image`. Kopiert wird das Artefakt, das tatsächlich gebaut
wurde — `arch/arm64/boot/Image.gz` oder `arch/arm64/boot/Image` —, nicht das aus
dem jeweils anderen Abschnitt.

### `sudo` wirft die Cross-Toolchain aus dem `PATH`

`modules_install` braucht Root-Rechte, und ein blosses `sudo make` verliert die
Toolchain. Daher die `env`-Klammer im Cross-Compile-Weg:

```bash
sudo env PATH=$PATH make -j12 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  INSTALL_MOD_PATH=mnt/root modules_install
```

---

## `LOCALVERSION` — vor dem Build setzen, nicht danach

Ohne sie überschreibt ein eigener Kernel die Module des Systemkernels in
`/lib/modules`, und `uname -r` verrät nicht, welcher Kernel läuft. In `.config`:

```
CONFIG_LOCALVERSION="-v7l-MY_CUSTOM_KERNEL"
```

Dieselbe Einstellung findet sich im `menuconfig` unter *General setup → Local
version - append to kernel release*.

## Konfigurieren: `menuconfig`

```bash
sudo apt install libncurses5-dev
make menuconfig                                                  # nativ
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig      # cross, 64 Bit
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig      # cross, 32 Bit
```

Pfeiltasten navigieren, Enter öffnet ein Untermenü (`--->`), Leertaste schaltet
eine binäre Option um, `H` zeigt Hilfe, zweimal Escape geht eine Ebene hoch oder
beendet. Änderungen landen in `.config` — Konfigurationen lassen sich also durch
Kopieren dieser Datei sichern und zurückholen.

---

## Installieren

Zuerst die Module, dann Kernel-Image, Device-Tree-Blobs und Overlays. **Vor dem
Überschreiben eine Sicherung des laufenden Kernels anlegen** — sie ist der
einzige Rückweg, wenn der neue nicht bootet.

**Nativ, 64 Bit:**

```bash
sudo make -j6 modules_install
sudo cp /boot/firmware/$KERNEL.img /boot/firmware/$KERNEL-backup.img
sudo cp arch/arm64/boot/Image.gz /boot/firmware/$KERNEL.img
sudo cp arch/arm64/boot/dts/broadcom/*.dtb /boot/firmware/
sudo cp arch/arm64/boot/dts/overlays/*.dtb* /boot/firmware/overlays/
sudo cp arch/arm64/boot/dts/overlays/README /boot/firmware/overlays/
sudo reboot
```

**Nativ, 32 Bit:** derselbe Ablauf, aber `arch/arm/boot/zImage` als Image — und
der Quellpfad der `.dtb`-Dateien hängt an der Kernelversion:

| Kernelversion | `.dtb`-Pfad, 32 Bit |
|---|---|
| bis 6.4 | `arch/arm/boot/dts/*.dtb` |
| ab 6.5 | `arch/arm/boot/dts/broadcom/*.dtb` |

Bei 64 Bit lag der Pfad immer unter `broadcom/`; verschoben hat sich nur der
32-Bit-Pfad.

**Cross-kompiliert:** dieselben Kopien, nur in ein eingehängtes Boot-Medium statt
nach `/boot/firmware`. `lsblk` vor und nach dem Anschliessen des Mediums
ausführen — das neu erschienene Gerät ist es. Mit `sdb1` als FAT32-Boot- und
`sdb2` als Root-Partition:

```bash
mkdir -p mnt/boot mnt/root
sudo mount /dev/sdb1 mnt/boot
sudo mount /dev/sdb2 mnt/root
# ... modules_install mit INSTALL_MOD_PATH=mnt/root, dann cp nach mnt/boot ...
sudo umount mnt/boot
sudo umount mnt/root
```

### Einen bootfähigen Systemkernel behalten

Statt `kernel.img` zu überschreiben, unter eigenem Namen installieren und in der
`config.txt` auswählen:

```
kernel=kernel-myconfig.img
```

Zusammen mit einer eigenen `LOCALVERSION` bleiben der vom System verwaltete
Kernel und seine Module unangetastet, und der Rückweg ist eine Zeile.

---

## Patches

Vor jedem Anwenden die Version aus dem Baum lesen — Patchsets sind
versionsspezifisch, und manche verlangen einen bestimmten Commit:

```bash
head Makefile -n 4        # VERSION / PATCHLEVEL / SUBLEVEL, z. B. 6.1.38
uname -r                  # was gerade läuft
```

Einzeldatei-Patches laufen über `patch`, Verzeichnisse im Mailbox-Format über
Git — das dafür `user.name` und `user.email` konfiguriert braucht:

```bash
cat patch-6.1.38-rt13-rc1.patch | patch -p1     # Einzeldatei
git am -3 /pfad/zu/patches/*                    # Mailbox-Format
```

## Kernel-Header

Out-of-Tree-Module kompilieren gegen die Header. Ein vollständiger Clone enthält
sie bereits, sonst:

```bash
sudo apt install linux-headers-rpi-v8            # 64 Bit
sudo apt install linux-headers-rpi-{v6,v7,v7l}   # 32 Bit
```

**Das apt-Paket hinkt neuen Kernel-Releases um Wochen hinterher.** Für einen
frisch erschienenen Kernel den Baum klonen, statt auf das Paket zu warten. Die
Installation zeigt keinen Fortschritt und dauert mehrere Minuten.

## Änderungen zurückgeben

| Änderung | Wohin |
|---|---|
| Raspberry-Pi-spezifischer Code oder Bugfix | Pull Request an `raspberrypi/linux` |
| Generischer Treiber oder generischer Kernel-Bugfix | zuerst Upstream-Linux, von dort erreicht er Raspberry Pi |

Die Upstream-Linux-Entwicklung läuft über **Mailinglisten, nicht über GitHub** —
die Änderung wird als E-Mail-Patch eingereicht, nach *Submitting patches: the
essential guide to getting your code into the kernel* und dem Linux Kernel
Coding Style. Von dort erreicht sie den Raspberry-Pi-Kernel mit dem nächsten
Long-Term-Release.

---

## Was das für ein mit diesem Skill gebautes Repo bedeutet

- **Build-Anweisungen müssen `ARCH`, defconfig und Target nennen.** Ein blosses
  `make` ist über die Modelle hinweg nicht reproduzierbar — und die Modelltabelle
  oben ist genau der Teil, den Lesende sich nicht herleiten können.
- **Ein Kernelmodul bindet sich an eine Kernelversion.** Diese Version in beiden
  READMEs nennen; Header und laufender Kernel müssen zusammenpassen.
- **Keinen vollständigen Kernel-Build in die `ci.yml` hängen.** Er braucht die
  Cross-Toolchain und läuft weit länger als die Lint-Jobs, für die der
  mitgelieferte Workflow gebaut ist. In der CI das Modul gegen installierte
  Header bauen und den Kernel-Build stattdessen im README dokumentieren.
