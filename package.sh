#!/bin/bash

set -e



echo "Run pyinstaller..."

pyinstaller resources/ccli.spec

echo "Create tarball for $OS_NAME -> $CPU_ARCH..."

if [ "$OS_NAME" == "windows" ]; then
    powershell.exe -nologo -noprofile -command "& { compress-archive -path '.\dist' -destinationpath '.\connect-cli_${PKG_TAG}_${OS_NAME}_${CPU_ARCH}.zip' }"
    ARCH_EXT="zip"
else
    tar cvfz connect-cli_${PKG_TAG}_${OS_NAME}_${CPU_ARCH}.tar.gz dist
    ARCH_EXT="tar.gz"
fi


rm -rf dist

echo "connect-cli_${PKG_TAG}_${OS_NAME}_${CPU_ARCH}.${ARCH_EXT} ready!"
