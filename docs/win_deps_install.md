# Install Git, Cairo, Pango and GDK-PixBuf on Windows

## Install Git, Cairo, Pango and GDK-PixBuf (GTK3+) using MSYS2


Install MSYS2 using the [MSYS2 installer](http://www.msys2.org/) for your system architecture.

Follow the instructions on the [MSYS2 website](https://github.com/msys2/msys2/wiki/MSYS2-installation) to update your MSYS2 shell.


Install GTK3+ and `git` for 32 bit architecture:

```sh
$ pacman -S mingw-w64-i686-gtk3
$ pacman -S git
```

Or for 64 bit architecure:

```sh
$ pacman -S mingw-w64-x86_64-gtk3
$ pacman -S git
```

Finally add following folders to your PATH environment variable:
* `C:\msys64\mingw64\bin` and `C:\msys64\usr\bin` in case of 64 bit architecture
* `C:\msys32\mingw32\bin` and `C:\msys32\usr\bin` in case of 32 bit architecture

