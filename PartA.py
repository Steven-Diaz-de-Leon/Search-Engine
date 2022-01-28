import sys
import re
from nltk.stem.snowball import EnglishStemmer

# Tokenizer function that uses a regular expression
# in order to parse a given text file line by line,
# I believe its most likely bounded by O(n) plus some
# value k since it traverses each line and parses each
# line using the regex function.
def tokenize(text):
    tokenList = []
    tokenList.extend(re.findall("[a-zA-Z0-9']+", text))

    #Porter2 Stemmer
    snowball = EnglishStemmer()
    for i, token in enumerate(tokenList):
        tokenList[i] = snowball.stem(token)
    return tokenList

# Function that computes how many times each token in the
# given list appears, runtime is O(n) since we traverse the list
# of n items and do a quick lookup on temp dictionary in O(1)
def computeWordFrequencies(tokenList):
    Map = {}
    for word in tokenList:
        # convert to lowercase in order to meet reqs
        w = word.lower()
        # if the word is in the dict increase count else add it to dict with count = 1
        if w in Map:
            Map[w] += 1
        else:
            Map[w] = 1
    return Map

# Prints each token along with its frequency,
# runs in O(n) time since it has to traverse
# the token list.
def printMap(map):
    # Sort dictionary from highest to lowest
    #f = open("test.txt", "w")
    sortedMap = sorted(map.items(), key=lambda item: item[1], reverse=True)
    for word, frequency in sortedMap:
        #f.write(word + " -> " + str(frequency) + '\n')
        print(word + " -> " + str(frequency))

