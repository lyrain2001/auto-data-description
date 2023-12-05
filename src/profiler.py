import datamart_profiler
from datetime import datetime

class Profiler:
    def __init__(self, sample_size=1000):
        self.sample_size = sample_size
        self.context = ""
        self.contextArr = []

    def build_context(self, df, sample_size=None):
            if sample_size is None:
                sample_size = self.sample_size
            try:
                contextArr = self.profiler(df)
                self.contextArr = contextArr
                if sample_size <= len(df):
                    df_sample = df.sample(sample_size)
                else:
                    df_sample = df
                sample = df_sample.to_csv(index=False)

                context=self.form_context(contextArr,sample)
                num_tokens = self.num_tokens_from_string(context)

                # Decrease the sample size iteratively until the number of tokens is less than or equal to 4000
                while num_tokens > 4000:
                    sample_size -= 1

                    if sample_size <= len(df):
                        df_sample = df.sample(sample_size)
                    else:
                        df_sample = df
                    sample = df_sample.to_csv(index=False)

                    context = self.form_context(contextArr, sample)
                    num_tokens = self.num_tokens_from_string(context)
            except Exception as e:
                print(f"An exception occurred: {e}")
                context = ""
            self.context = context
            return context


    @staticmethod
    def profiler(data_frame):
        metadata = datamart_profiler.process_dataset(data_frame)
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