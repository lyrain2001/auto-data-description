#!/bin/bash

# Define the directory containing the datasets and output file path
DATASETS_DIR="../../dataset/task1data"
OUTPUT_FILE="../samples/task1_sample.txt"

# Path to your Python script
PYTHON_SCRIPT="../src/generate_context.py"

# Sample size
SAMPLE_SIZE=10

# Profiler
PROFILER=False

# Run the Python script
python $PYTHON_SCRIPT --input_dir $DATASETS_DIR --output $OUTPUT_FILE --sample_size $SAMPLE_SIZE