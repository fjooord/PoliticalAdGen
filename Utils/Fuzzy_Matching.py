from fuzzywuzzy import process

"""
This file will hold functions that are used to match strings 

All functions will be used to match strings in a fuzzy way with the fuzzywuzzy library
"""

def find_closest_match(query, choices):
    best_match, match_score = process.extractOne(query, choices)
    return best_match
