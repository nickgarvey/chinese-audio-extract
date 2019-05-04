#!/bin/bash
set -ex

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/cred.json"
python3.7 chinese-audio-extract.py
