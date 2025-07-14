#!/usr/bin/env bash
set -e

# Extract version from pyproject.toml
VERSION=$(grep -Po '(?<=^version = ")[^"]+' pyproject.toml)
echo "Detected version in pyproject.toml: $VERSION"

# Update docs/conf.py if needed
CURRENT_CONF_VERSION=$(grep -Po '(?<=^release = ")[^"]+' docs/conf.py || echo "none")
if [ "$CURRENT_CONF_VERSION" != "$VERSION" ]; then
  echo "Updating docs/conf.py version from $CURRENT_CONF_VERSION to $VERSION"
  sed -i "s/^release = .*/release = \"$VERSION\"/" docs/conf.py
else
  echo "docs/conf.py already has the correct version."
fi

# Build docs
cd docs
make html
