import openai

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
    
def get_summary(history_context):
    prompt = open_file('prompt/system_summary.txt').format(history_context=history_context)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',  # Use the selected model name
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=0.0,  # Set temperature
        max_tokens=2048,  # Set max tokens
        stream=False,
    )
    summary = response.choices[0].message.content
    return summary