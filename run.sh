#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [ "$#" -ne 2 ]; then
    echo -e "${RED}Usage:${NC} ./run.sh <input_nominal.smv> <faults.xml>"
    exit 1
fi

INPUT_SMV="$1"
FAULTS_XML="$2"

OUTPUT_DIR="output"
OUTPUT_FILE="${OUTPUT_DIR}/ExtendedModel.smv"

mkdir -p "$OUTPUT_DIR"

if [ ! -f "$INPUT_SMV" ]; then
    echo -e "${RED}Error:${NC} '$INPUT_SMV' not found."
    exit 1
fi

if [ ! -f "$FAULTS_XML" ]; then
    echo -e "${RED}Error:${NC} '$FAULTS_XML' not found."
    exit 1
fi

echo -e "${NC}Generating extended model...${NC}"
python3 main.py "$INPUT_SMV" "$FAULTS_XML" "$OUTPUT_FILE"

echo -e "${GREEN}Done! Output saved in ${OUTPUT_FILE}"