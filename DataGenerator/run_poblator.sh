#!/bin/bash
cd "$(dirname "$0")"
export $(cat ../.env | xargs)
python3 DataPoblator.py
