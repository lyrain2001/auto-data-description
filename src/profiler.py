import tiktoken
import datamart_profiler
from datetime import datetime

class Profiler:
    def __init__(self, sample_size=1000):
        self.sample_size = sample_size
        self.context = ""
        self.contextArr = []
        
    def get_context(self):
        return self.context

    def build_context(self, df, use_profiler, sample_size, title):
            if sample_size is None:
                sample_size = self.sample_size
            try:
                print("Profiling...")
                if use_profiler:
                    contextArr = self.profiler(df)
                    self.contextArr = contextArr
                if sample_size <= len(df):
                    df_sample = df.sample(sample_size)
                else:
                    df_sample = df
                sample = df_sample.to_csv(index=False)

                context=self.form_context(self.contextArr, sample, use_profiler, title)
                num_tokens = self.num_tokens_from_string(context)

                # Decrease the sample size iteratively until the number of tokens is less than or equal to 4000
                while num_tokens > 4000:
                    sample_size -= 1

                    if sample_size <= len(df):
                        df_sample = df.sample(sample_size)
                    else:
                        df_sample = df
                    sample = df_sample.to_csv(index=False)

                    context = self.form_context(self.contextArr, sample, use_profiler, title)
                    num_tokens = self.num_tokens_from_string(context)
            except Exception as e:
                print(f"An exception occurred: {e}")
                context = ""
            self.context = context
            return context


    @staticmethod
    def profiler(data_frame):
        metadata = datamart_profiler.process_dataset(data_frame)
        print("Profiling done, generating stats...")
        contextDict = {}

        contextArr=[]
        for i in range(len(metadata['columns'])):
            metDict = metadata['columns'][i]
            cDict={'name':metDict['name']
                    ,'structural_type':metDict['structural_type'],
                    'semantic_types':metDict['semantic_types']}
            if('num_distinct_values' in metDict.keys()):
                cDict['num_distinct_values'] = metDict['num_distinct_values']
            if('coverage' in metDict.keys()):
                low=0
                high=0
                for i in range(len(metDict['coverage'])):
                    if(metDict['coverage'][i]['range']['gte']<low):
                        low=metDict['coverage'][i]['range']['gte']
                    if(metDict['coverage'][i]['range']['lte']>high):
                        high=metDict['coverage'][i]['range']['lte']
                cDict['coverage'] = [low,high]
            contextArr.append(cDict)
        contextDict['columns']=contextArr

        if 'temporal_coverage' in metadata.keys():
            temporal_coverage = []
            for i in range(len(metadata['temporal_coverage'])):
                data = metadata['temporal_coverage'][i]
                range_values = [entry['range']['gte'] for entry in data['ranges']] + [entry['range']['lte'] for entry in data['ranges']]
                min_value = datetime.fromtimestamp(min(range_values)).strftime("%Y-%m-%d")
                max_value = datetime.fromtimestamp(max(range_values)).strftime("%Y-%m-%d")
                temporal_dict = {
                    'column_names': data['column_names'],
                    'temporal_resolution': data['temporal_resolution'],
                    'ranges': [min_value, max_value]
                }
                temporal_coverage.append(temporal_dict)
            contextDict['temporal_coverage'] = temporal_coverage

        contextDict['attribute_keywords'] = metadata['attribute_keywords']
        return contextDict
    
    @staticmethod
    def form_context(contextDict, sample, use_profiler, title):
        if not use_profiler:
            return "Dataset title: " + title + "\nDataset sample: \n" + sample
        
        result = ""
        
        max_num = 5
        count = 0

        temporal_columns = []
        if 'temporal_coverage' in contextDict.keys():
            for d in contextDict['temporal_coverage']:
                temporal_columns += d['column_names']
                result += "Column " + d['column_names'][0] + " is a time column with temporal resolution in " + d['temporal_resolution'] + ". "
                result += "The temporal coverage is from " + d['ranges'][0] + " to " + d['ranges'][1] + ". \n"
                count += 1
        
        if count < max_num:
            for d in contextDict['columns']:
                if d['name'] in temporal_columns:
                    continue
                if count >= max_num:
                    break
                result += "Column " + d['name'] + " is a " + d['structural_type'] + ". "
                if 'num_distinct_values' in d.keys():
                    result += "There are " + str(d['num_distinct_values']) + " distinct values. "
                if 'coverage' in d.keys():
                    result += "The range of values is from " + str(d['coverage'][0]) + " to " + str(d['coverage'][1]) + ". "
                if len(d['semantic_types']) > 0:
                    result += "The semantic types are: "
                    for s in d['semantic_types']:
                        result += s + ", "
                    result = result[:-2] + ". "
                result += "\n"
                count += 1
        
        final = "Dataset title: " + title + "\nDataset sample: \n" + sample + "\nColumn profiling: \n" + result
        return final

    
    def num_tokens_from_string(self, string, encoding_name="gpt-3.5-turbo"):
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens