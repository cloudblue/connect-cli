#!/bin/bash

set -e



echo "Run pyinstaller..."

pyinstaller resources/ccli.spec

echo "Create tarball for $TRAVIS_OS_NAME -> $TRAVIS_CPU_ARCH..."

if [ "$TRAVIS_OS_NAME" == "windows" ]; then
    tar.exe -a -c -f product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.zip dist
else
    tar cvfz product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.tar.gz dist
fi


rm -rf dist

echo "product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.tar.gz ready!"
