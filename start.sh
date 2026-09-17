#!/bin/bash
# プロジェクトディレクトリに移動
cd "$(dirname "$0")"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
# 仮想環境のPythonを使って実行
./venv/bin/python main.py
