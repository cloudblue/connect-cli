#!/bin/bash

echo "Run pyinstaller..."

pyinstaller resources/ccli.spec

echo "Create tarball for $TRAVIS_OS_NAME -> $TRAVIS_CPU_ARCH..."

tar cvfz product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.tar.gz dist
rm -rf dist

echo "product-sync_${TRAVIS_TAG}_${TRAVIS_OS_NAME}_${TRAVIS_CPU_ARCH}.tar.gz ready!"
