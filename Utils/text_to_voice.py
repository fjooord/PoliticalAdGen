import requests
import os
import sys

"""
This file holds the functions for generated the voiceovers for the book

It uses elevenlabs to create the voiceovers

"""

"""
This function takes in a text string and a voice id and creates a voiceover for the text

The voice is currently set to only be the Adam voice, but this will be changable in the future
"""
def create_voiceover(text, filepath, voice_id = 'I7HuGicNVaGqWVmMYOw6', max_retries = 5):
        
    url = 'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id
    
    # Set the eleven labs api key
    evl_api_key = 'c931ba70bc933ae495a5105a7ab63317'
    
    # Set up the header
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': evl_api_key,
        'Content-Type': 'application/json'
    }
    
    # Set the data to send to request point
    data = {
        'text': text,
        'voice_settings': {
            'stability': 0.2,
            'similarity_boost': 1.0
        }
    }
    
    retries = 0
    for i in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print('Text-to-speech conversion successful')
                break
        except Exception as e:
            print(f"Error occurred: {e}")
            retries += 1
            if retries == max_retries:
                print("Reached maximum retries, exiting.")
                raise

            
    