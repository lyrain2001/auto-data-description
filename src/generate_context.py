import argparse
import pandas as pd
import os

try:
    from .profiler import *
except ImportError:
    from profiler import *


def process_file(input_path, sample_size, use_profiler, title):
    df = pd.read_csv(input_path)
    print(f"Processing {input_path}...")
    profiler = Profiler()
    return profiler.build_context(df, use_profiler, sample_size, title)

def main():
    parser = argparse.ArgumentParser(description='Generate context for multiple datasets')
    parser.add_argument('--input_dir', type=str, help='input directory path')
    parser.add_argument('--output', type=str, help='output file path')
    parser.add_argument('--sample_size', type=int, default=10, help='sample size')
    parser.add_argument('--profiler', type=bool, default=False, help='use profiler')
    args = parser.parse_args()
    
    dataset_info = pd.read_csv('../../dataset/DatasetInfo_updated.csv')

    with open(args.output, 'w') as f:
        for file in os.listdir(args.input_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(args.input_dir, file)
                file_name = os.path.splitext(file)[0]
                title = dataset_info.loc[dataset_info['DatasetID'] == file_name, 'Title'].iloc[0]
                context = process_file(file_path, args.sample_size, args.profiler, title)
                f.write(f'"{file_name}", "{context}"\n')

if __name__ == "__main__":
    main()