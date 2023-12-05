#!/bin/bash

DATASETS_DIR="../../dataset/task2data"
OUTPUT_FILE="../samples/task2_sample_profiler.txt"

PYTHON_SCRIPT="../src/generate_context.py"

SAMPLE_SIZE=10

python $PYTHON_SCRIPT --input_dir $DATASETS_DIR --output $OUTPUT_FILE --sample_size $SAMPLE_SIZE --profiler true

OUTPUT_FILE="../samples/task2_sample.txt"
python $PYTHON_SCRIPT --input_dir $DATASETS_DIR --output $OUTPUT_FILE --sample_size $SAMPLE_SIZE