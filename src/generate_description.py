import tiktoken
import datamart_profiler
import openai
from datetime import datetime

class AutoDescription:
    def __init__(self, openai_key, sample_size):
        self.sample_size = sample_size
        self.context = None
        self.contextArr = None
        # self.initial_description, self.description_PQ, self.potential_query = self.generate_description(self.context)
        openai.api_key = (openai_key)

    def get_context(self):
        return self.context

    def get_initial_description(self):
        return self.initial_description
    
    def get_description_PQ(self):
        return self.description_PQ
    
    def get_potential_query(self):
        return self.potential_query
            
    def num_tokens_from_string(self, string, encoding_name="gpt-3.5-turbo"):
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    @staticmethod
    def form_context(contextDict,sample):
        result=""

        temporal_columns = []
        if 'temporal_coverage' in contextDict.keys():
            for d in contextDict['temporal_coverage']:
                temporal_columns += d['column_names']
                result+="Column "+d['column_names'][0]+" is a time column with temporal resolution in "+d['temporal_resolution']+". "
                result+="The temporal coverage is from "+d['ranges'][0]+" to "+d['ranges'][1]+". "
                result+="\n"
        print("temporal_columns", temporal_columns)

        for d in contextDict['columns']:
            if d['name'] in temporal_columns:
                continue
            result+="Column "+d['name']+" is a "+d['structural_type']+". "
            if('num_distinct_values' in d.keys()):
                result+="There are "+str(d['num_distinct_values'])+" distinct values. "
            if('coverage' in d.keys()):
                result+="The range of values is from "+str(d['coverage'][0])+" to "+str(d['coverage'][1])+". "
            if len(d['semantic_types'])>0:
                result+="The semantic types are: "
                for s in d['semantic_types']:
                    result+=s+", "
                result=result[:-2]
                result+=". "
            result+="\n"
        
        final = "Input: \n" + sample + "\n\n" + "Context: \n" + result
        return final


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

    def generate_description(self, context, model="gpt-3.5-turbo"):
        initial_description_content = self.generate_description_initial(context, model)
        potential_query_content = self.generate_potential_query(context, model)
        description_PQ_content = self.generate_description_potential_query(initial_description_content, potential_query_content, model)
        return initial_description_content, description_PQ_content, potential_query_content

    def generate_description_initial(self, context, model):
        description = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {
                        "role": "system", 
                        "content": "You are an assistant for a dataset search engine.\
                                    Your goal is to increase the performance of this dataset search engine for keyword queries."},
                    {
                        "role": "user", 
                        "content": "Answer the questions while using the input and context.\
                                    The input is a random sample of the large dataset. \
                                    The context describes what the headers of the dataset are.\n"+context+"\
                                Question:Describe the dataset in sentences.\nAnswer:"},
                ],
            temperature=0.3)
        description_content = description.choices[0]['message']['content']
        return description_content

    def generate_potential_query(self, context, model="gpt-3.5-turbo"):
        description = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {
                        "role": "system", 
                        "content": "You are an assistant for an online dataset search engine.\
                                    Your goal is to increase the performance of this dataset search engine for keyword queries."},
                    {
                        "role": "user", 
                        "content": "Answer the questions while using the input and context.\
                                    The input is a random sample of the large dataset. \
                                    The context describes what the headers of the dataset are.\n"+context+"\
                                Question: What can this dataset be used for? Please output top 3 keyword queries where users want to find this data\nAnswer:"},
                ],
            temperature=0.6)
        description_content = description.choices[0]['message']['content']
        return description_content

    def generate_description_potential_query(self, initial_description_content, potential_query_content, model="gpt-3.5-turbo"):
        description = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {
                        "role": "system", 
                        "content": "You are an assistant for an online dataset search engine.\
                                    Your goal is to increase the performance of this dataset search engine for keyword queries."},
                    {
                        "role": "user", 
                        "content": "Answer the questions while using the following information.\
                                    The description is about a dataset: "+initial_description_content+"\
                                    The suggested queries are top keyword queries that users want to find this dataset.\n"+potential_query_content+"\
                                Question: Based on the suggested keyword queries. Can you improve the current dataset description to cover these keyword queries? \
                                        Only new dataset description is needed in the response.\nAnswer:"},
                ],
            temperature=0.9)
        description_content = description.choices[0]['message']['content']
        return description_content
    
    def generate_description_combined(self, original_description, description_PQ_content, model="gpt-3.5-turbo", temperature=0.9):
        description = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {
                        "role": "system", 
                        "content": "You are an assistant for an online dataset search engine.\
                                    Your goal is to increase the performance of this dataset search engine for keyword queries."},
                    {
                        "role": "user", 
                        "content": "Answer the questions while using the following information.\
                                    This is the original description about this dataset: "+original_description+"\
                                    This is a description based on the suggested keyword queries on this dataset.\n"+description_PQ_content+"\
                                Question: Based on these two descriptions. Can you generate a new description by summarizing and highlighting the important parts of these two versions of descriptions? \
                                        Only return the new description.\nAnswer:"},
                ],
            temperature=temperature)
        description_content = description.choices[0]['message']['content']
        return description_content