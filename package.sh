#!/bin/bash

set -e



echo "Run pyinstaller..."

pyinstaller resources/ccli.spec

echo "Create tarball for $TRAVIS_OS_NAME -> $TRAVIS_CPU_ARCH..."

if [ "$TRAVIS_OS_NAME" == "windows" ]; then
    tar.exe -a -c -f product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.zip dist
    ARCH_EXT="zip"
else
    tar cvfz product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.tar.gz dist
    ARCH_EXT="tar.gz"
fi


rm -rf dist

echo "product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.${ARCH_EXT} ready!"
