#!/bin/bash

DATASETS_DIR="../../dataset/task1data"
OUTPUT_FILE="../samples/task1_sample.txt"

PYTHON_SCRIPT="../src/generate_context.py"

SAMPLE_SIZE=10

python $PYTHON_SCRIPT --input_dir $DATASETS_DIR --output $OUTPUT_FILE --sample_size $SAMPLE_SIZE