import re
import os
import json
import openai
from time import time,sleep
import textwrap
from io import BytesIO
import requests
import re
import sys

        
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)
        
def save_file2(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = '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'

def replace_name(text, old_name, new_name):
    """
    This function is used for replacing a name in a text with a character and name combo

    Sometimes in the description of a scene it doesn't say the character type

    IE
    Instead of "Timmy the Whale looks at the sky" it will say "Timmy looks at the sky"

    This leads to errors in the image generation

    """
    # Create a case-insensitive regular expression pattern for the old name
    pattern = re.compile(old_name, re.IGNORECASE)

    # Replace all occurrences of the old name with the new name
    result = pattern.sub(new_name, text)

    return result


def make_prompt_dict(prompt_string):
    prompt_dict = {}
    split_prompts = prompt_string.split('\n')

    for prompt in split_prompts:
        if prompt.startswith("Character Prompt:"):
            prompt_dict['character_prompt'] = prompt[len("Character Prompt:"):].strip()
        elif prompt.startswith("Scene Prompt:"):
            prompt_dict['scene_prompt'] = prompt[len("Scene Prompt:"):].strip()
        elif prompt.startswith("Character placement:"):
            prompt_dict['character_placement'] = prompt[len("Character placement:"):].strip()

    return prompt_dict


def generate_section_prompts(params, section):
    # Load the scene description
    scene_description = section.description
    # Update the scene description with the character name and type
    updated_description = replace_name(scene_description, params['character_name'], params['character_name'] + " the " + params['character'])

    # Load the illustrator prompt and replace the section description
    illustrator_role = open_file('Book_Types/short_book_prompts/illustrator_role_v1.txt')
    illustrator_role = illustrator_role.replace('<<SECTION>>', updated_description)
    
    # Generate the prompts for the scene
    prompts = chat_gpt(illustrator_role, engine='gpt-4', temp=0.1, role=illustrator_role)

    # Generate the prompts dictionary
    prompts_dict = make_prompt_dict(prompts)

    return prompts_dict


def generate_character_description(params, content):
    #char_desc_prompt = open_file('Book_Types/short_book_prompts/Prompt_Gen/Char_Desc.txt')
    char_desc_prompt = open_file('Book_Types/short_book_prompts/Prompt_Gen/Char_Keyword.txt')
    char_desc_prompt = char_desc_prompt.replace("<<SETTING>>", params["setting"])
    char_desc_prompt = char_desc_prompt.replace("<<CONTENT>>", content)
    char_desc_prompt = char_desc_prompt.replace("<<GENDER>>", params["gender"])
    char_desc_prompt = char_desc_prompt.replace("<<CHARACTER>>", params["character"])
    char_desc_prompt = char_desc_prompt.replace("<<CHAR_NAME>>", params["character_name"])
    
    char_desc = chat_gpt(char_desc_prompt, temp=0.4)

    return char_desc


def generate_scene_description(params, content):
    #scene_desc_prompt = open_file('Book_Types/short_book_prompts/Prompt_Gen/Scene_Desc.txt')
    scene_desc_prompt = open_file('text_to_image/spread_keyword.txt')
    scene_desc_prompt = scene_desc_prompt.replace("<<SETTING>>", params["setting"])
    scene_desc_prompt = scene_desc_prompt.replace("<<BLOCK>>", content)

    scene_desc = chat_gpt(scene_desc_prompt, temp=0)

    return scene_desc


def chatgpt_convo(user_input, conversation, temperature=0.2, frequency_penalty=0.2, presence_penalty=0):
    # Define a function to make an API call to the OpenAI ChatCompletion endpoint

    # Read the content of a file containing the chatbot's prompt
    chatbot = "You are an experienced children's book writer with over 20 years experience. You specialize in creating best-selling picture books for children between the ages of 2 and 8."

    # Update conversation by appending the user's input
    conversation.append({"role": "user", "content": user_input})

    # Insert prompt/s into message history 
    # - By inserting the chatbot's prompt message into the conversation history before making an API call 
    #   to the OpenAI ChatCompletion endpoint, the function ensures that the chatbot's response will be generated 
    #   in the correct context and take into account any previous messages in the conversation history. 
    #   This can improve the quality and relevance of the chatbot's responses.
    messages_input = conversation.copy()
    prompt = [{"role": "system", "content": chatbot}]
    prompt_item_index = 0
    for prompt_item in prompt:
        messages_input.insert(prompt_item_index, prompt_item)
        prompt_item_index += 1

    # Make an API call to the ChatCompletion endpoint with the updated messages
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messages_input)

    # Extract the chatbot's response from the API response
    chat_response = completion['choices'][0]['message']['content']

    # Update conversation by appending the chatbot's response
    conversation.append({"role": "assistant", "content": chat_response})

    # Return the chatbot's response
    return chat_response, conversation


def short_book_gen(params):
    template_in = open_file('Book_Types/short_book_prompts/short_template.txt')
    # Replace placeholders with values from the params dictionary
    template_in = template_in.replace("<<AGE>>", str(params["age"]))
    template_in = template_in.replace("<<SETTING>>", params["setting"])
    template_in = template_in.replace("<<THEME>>", params["theme"])
    template_in = template_in.replace("<<GENDER>>", params["gender"])
    template_in = template_in.replace("<<CHARACTER>>", params["character"])
    template_in = template_in.replace("<<CHAR_NAME>>", params["character_name"])
        

    # Initialize an empty list to store the conversation
    conversation = []
    print('----- Starting Template', file=sys.stderr)
    template, conversation = chatgpt_convo(template_in,conversation) # Call the chatgpt_convo function with user input
    print('----- Starting Outline', file=sys.stderr)
    outline, conversation = chatgpt_convo('From the template in the previous response, make an outline for a childrens book.',conversation)

    # Generate story form template
    story_in = open_file('Book_Types/short_book_prompts/short_story.txt')
    story_in = story_in.replace('<<LENGTH>>', str(params['book_length']))
    story_in = story_in.replace('<<AGE>>', str(params['age']))
    story_in = story_in.replace('<<GENDER>>', params['gender'])

    print('----- Starting Story Content', file=sys.stderr)
    story, conversation = chatgpt_convo(story_in,conversation)
    pattern = r"Page \d+:"

    # Replace the matched pattern with an empty string
    story = re.sub(pattern, "", story)

    # Generate image prompts
    image_prompt_in = open_file('Book_Types/short_book_prompts/short_image_prompts.txt')
    print('----- Starting Image Prompts', file=sys.stderr)
    image_prompts, conversation = chatgpt_convo(image_prompt_in,conversation)
    # Replace the matched pattern with an empty string
    image_prompts = re.sub(pattern, "", image_prompts)

    # Get the content and prompt arrays
    content = story.split('||')
    prompts = image_prompts.split('||')

    return content, prompts


def chat_gpt(prompt, engine='gpt-3.5-turbo', temp=0.75, top_p=1.0, tokens=3000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf'], role=None):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    if role is None:
        role = "You are an experienced children's book writer with over 20 years of expertise in creating best-selling picture books for children aged 2-8"
    else:
        role = role.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            completion = openai.ChatCompletion.create(
              model=engine,
              messages=[
                {"role": "system", "content": role,
                 "role": "user", "content": prompt}
              ],
              temperature=temp,
              top_p=top_p,
              max_tokens=tokens,
              frequency_penalty=freq_pen,
              presence_penalty=pres_pen,
            )

            text = completion.choices[0].message['content']
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def generalized_gpt_prompt(path, tag_values, index = -1, role=None):
    """
    This function takes in the path to the original prompt file
    and the current tags with their corresponding values

    We then iterate through all the tags and replace the tag in the prompt with the value
        - Any tag that exist will get replaced, but those that don't exist will do nothing 
        - This may increase runtime slightly, but reduces the number of functions that will be needed

    We pass the prompt to chat gpt and take the return value

    Note: The post processing may vary for each call
    """
    prompt = open_file(path)
    
    for tag, value in tag_values.items():
        try:
            prompt = prompt.replace(tag, value)
        except:
            if index != -1:
                try:
                    prompt = prompt.replace(tag, value[index])
                except:
                    continue

    return chat_gpt(prompt, role=role).strip()

