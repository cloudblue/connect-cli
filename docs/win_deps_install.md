# Install Python, Cairo, Pango and GDK-PixBuf on Windows

## Install Python

Get the latest Python installer for your system architecture from the [Python download page](https://www.python.org/downloads/windows/).

Follow the installation instructions for windows that are available at [https://docs.python.org/3/using/windows.html](https://docs.python.org/3/using/windows.html).


## Install Cairo, Pango and GDK-PixBuf (GTK3+) using MSYS2


Install MSYS2 using the [MSYS2 installer](http://www.msys2.org/) for your system architecture.

Follow the instructions on the [MSYS2 website](https://github.com/msys2/msys2/wiki/MSYS2-installation) to update your MSYS2 shell.


Install GTK3+ for 32 bit architecture:

```sh
$ pacman -S mingw-w64-i686-gtk3
```

Or for 64 bit architecure:

```sh
$ pacman -S mingw-w64-x86_64-gtk3
```

Finally add the `C:\msys2\mingw64\bin`or `C:\msys2\mingw32\bin` folder to your PATH environment variable.

