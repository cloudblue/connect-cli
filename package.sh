#!/bin/bash

echo "Run pyinstaller..."

pyinstaller resources/ccli.spec

echo "Create tarball for $TRAVIS_OS_NAME -> $TRAVIS_CPU_ARCH..."

tar cvfz product-sync_$TRAVIS_TAG_$TRAVIS_OS_NAME_$TRAVIS_CPU_ARCH.tar.gz dist
rm -rf dist

echo "product-sync_$TRAVIS_TAG_$TRAVIS_OS_NAME_$TRAVIS_CPU_ARCH.tar.gz ready!"
