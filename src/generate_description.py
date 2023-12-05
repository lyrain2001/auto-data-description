import argparse
try:
    from .description import *
except ImportError: 
    from description import *

class DescriptionGenerator:
    def __init__(self, openai_key, task_name):
        self.openai_key = openai_key
        self.task_name = task_name

    def read_contexts(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        return [line.strip().split(' ', 1) for line in lines if line.strip()]

    def generate_and_write_descriptions(self):
        profiler_filename = f'../samples/{self.task_name}_sample_profiler.txt'
        sample_filename = f'../samples/{self.task_name}_sample.txt'

        profiler_contexts = self.read_contexts(profiler_filename)
        sample_contexts = self.read_contexts(sample_filename)

        with open(f'../results/{self.task_name}_result_profiler.txt', 'w') as profiler_file, \
            open(f'../results/{self.task_name}_result_sample.txt', 'w') as sample_file, \
            open(f'../results/{self.task_name}_result_template.txt', 'w') as template_file:

            for profiler_context in profiler_contexts:
                print("Generating description with profiler for", profiler_context[0])
                auto_desc = AutoDescription(self.openai_key, profiler_context[1])
                description_profiler, description_template = auto_desc.generate_description_profiler(profiler_context[1])
                profiler_file.write(f'{profiler_context[0]}\t{description_profiler}\n')
                template_file.write(f'{profiler_context[0]}\t{description_template}\n')

            for sample_context in sample_contexts:
                print("Generating description with only samples for", sample_context[0])
                auto_desc = AutoDescription(self.openai_key, sample_context[1])
                description_sample = auto_desc.generate_description_samples(sample_context[1])
                sample_file.write(f'{sample_context[0]}\t{description_sample}\n')

def main():
    parser = argparse.ArgumentParser(description="Generate descriptions for datasets")
    parser.add_argument('--task_name', type=str, default='task1', help='Task name (i.e. task1)')

    args = parser.parse_args()
    OPENAI_API_KEY = "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"

    generator = DescriptionGenerator(OPENAI_API_KEY, args.task_name)
    generator.generate_and_write_descriptions()

if __name__ == "__main__":
    main()
