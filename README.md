# Auto Dataset Description Generation
### Environment
```
    pip install -r requirements.txt
```
### Generate samples and profiler
```
    ./bash/profiler.sh
 ```   
### Generate description (GPT3.5)
```
    python src/generate_description.py task[index]
```
where index can be replaced with 1 and 2.

### Generate description (Llama)
```
    cd src
    git clone https://github.com/ggerganov/llama.cpp.git
    python llama.py
```
### Prompts

- Prompt 1: sample
- Prompt 2: sample + profiler
- Prompt 3: sample + profiler + template