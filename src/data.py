import pickle
import pandas as pd

dataset_sample = pickle.load(open("dataset_sample", "rb"))
print(dataset_sample.keys())