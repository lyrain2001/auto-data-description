import argparse
import pandas as pd
import os

try:
    from .profiler import *
except ImportError:
    from profiler import *


def process_file(input_path, sample_size):
    df = pd.read_csv(input_path)
    print(f"Processing {input_path}...")
    profiler = Profiler()
    return profiler.build_context(df, sample_size)

def main():
    parser = argparse.ArgumentParser(description='Generate context for multiple datasets')
    parser.add_argument('--input_dir', type=str, help='input directory path')
    parser.add_argument('--output', type=str, help='output file path')
    parser.add_argument('--sample_size', type=int, default=10, help='sample size')
    args = parser.parse_args()

    with open(args.output, 'w') as f:
        for file in os.listdir(args.input_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(args.input_dir, file)
                context = process_file(file_path, args.sample_size)
                f.write(f'"{os.path.splitext(file)[0]}", "{context}"\n')

if __name__ == "__main__":
    main()