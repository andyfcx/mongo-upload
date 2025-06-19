#!/bin/bash
set -e

echo "Installing mongo_upload..."

if ! command -v poetry &> /dev/null; then
    echo "Poetry not installed, please install it first: https://python-poetry.org/docs/"
    exit 1
fi

poetry install
poetry build

pip install dist/*.whl

echo "✅ Install complete, you can use mongo_upload any where"
