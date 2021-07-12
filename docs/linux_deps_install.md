# Install Python, Cairo, Pango and GDK-PixBuf on linux

## Debian/Ubuntu

```sh
$ sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info git
```

## Fedora

```sh
$ sudo yum install redhat-rpm-config python-devel python-pip python-setuptools python-wheel python-cffi libffi-devel cairo pango gdk-pixbuf2 git
```

## Gentoo

```sh
$ emerge pip setuptools wheel cairo pango gdk-pixbuf cffi dev-vcs/git
```

## Archlinux

```sh
$ sudo pacman -S python-pip python-setuptools python-wheel cairo pango gdk-pixbuf2 libffi pkg-config git
```

## Alpine

For Alpine Linux 3.6 or newer:

```sh
$ apk --update --upgrade add gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev git
```
