import os
import json
from bs4 import BeautifulSoup
import PartA
from urllib.parse import urldefrag
import math
from simhash import Simhash, SimhashIndex
import re

# <token, posting_list>
# posting [docID, ,frequency, importance score(Term in title, header, bold, etc..),]
# should probably sort by docID in the posting list

#TODO changes are:
# computeImportance() line 60
# tf score for tf-id line 139
# posting updated to posting = [siteID, tf_score, importance_score]
# Part A tokenize is where porter2 stemming is happening.
# to install NTK: python3 -m pip install --user -U nltk
# still need to implement tf-id score in search interface

class Index:
    def __init__(self, start_path):
        self.start_path = start_path
        self.index = {}
        self.lastUsedIndex = 0
        self.url_list = {}
        self.num_sites = 0
        self.total_sites = 55393
        self.current_batch = 1
        self.simhashIndex = SimhashIndex([], k=3)

    def seen(self, text, url):
        hash = Simhash(self.get_features(text))
        dups = self.simhashIndex.get_near_dups(hash)
        if len(dups) == 0:
            self.simhashIndex.add(url, hash)
            return False
        else:
            return True

    def get_features(self, text):
        text = text.lower()
        text = re.sub(r'[^\w]+', ' ', text)
        return text

    def assignUrlID(self, url):
        return len(self.url_list)

    # gets all the document paths
    def getDocuments(self):
        doc_list = []
        for root, dirs, files in os.walk(self.start_path):
            for file in files:
                doc_list.append(os.path.join(root, file))
                self.num_sites += 1
        return doc_list

    # write the current index to the disk and empty it
    def writeToDisk(self):
        file_name = "index" + str(self.current_batch) + ".txt"
        self.current_batch += 1
        partial_index = open(file_name, "w")
        for word in sorted(self.index):
            temp_dict = {word: self.index[word]}
            partial_index.write(json.dumps(temp_dict)+"\n")
        return

    def writeUrlList(self):
        urlMap = open("urlMap.txt", "w")
        for siteID in self.url_list:
            temp_dict = {siteID: self.url_list[siteID]}
            urlMap.write(json.dumps(temp_dict) + "\n")


    #TODO
    # check various high importance HTML tags for keyword/token
    def computeImportance(self, important_tags, word, scores):
        # important tags are header, bold, title, and h1 - h6
        score = 0
        for tags in important_tags:
            for tag in tags:
                if word in str(tag):
                    score += scores[str(tag.name)]

        return score

    # builds the index/map from the provided folder containing the json files
    def buildIndex(self):
        doc_list = self.getDocuments()
        batch1 = int(self.total_sites/3)
        batch2 = int(2*self.total_sites/3)
        siteID = 0
        for file in doc_list:
            # write to disk on each batch and empty the current index
            if siteID == batch1 or siteID == batch2:
                self.writeToDisk()
                self.index = {}
            with open(file, "r") as auto:
                site = json.load(auto)
                # Json format is site, content, encoding
                siteID = self.assignUrlID(site['url'])
                soup = BeautifulSoup(site['content'], "lxml")
                [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
                visible_text = soup.getText()
                if self.seen(visible_text, urldefrag(site['url'])):
                    continue
                token_list = PartA.tokenize(visible_text)
                # map containing token, frequency
                temp_map = PartA.computeWordFrequencies(token_list)

                header = soup.find_all("header")  # worth 4 points
                title = soup.find_all("title")  # worth 3 points
                bold = soup.find_all("b")  # worth 1 points
                h1 = soup.find_all("h1")  # worth 2 points
                h2 = soup.find_all("h2")  # worth 1 point
                h3 = soup.find_all("h3")  # worth .5 points
                h4 = soup.find_all("h4")  # worth 0.25 points
                h5 = soup.find_all("h5")  # worth 0.12 points
                h6 = soup.find_all("h6")  # worth 0.06 points
                important_tags = [header, title, bold, h1, h2, h3, h4, h5, h6]
                scores = {"header": 4, "title": 3, "b": 1, "h1": 2, "h2": 1, "h3": 0.5, "h4": 0.25, "h5": 0.12, "h6": 0.6}

                self.url_list[siteID] = list(urldefrag(site['url']))[0]
                for word in temp_map:
                    # posting [siteID, frequency, importance score(term in title, header, bold, etc..)]
                    importance_score = self.computeImportance(important_tags, word, scores)
                    # compute tf score
                    tf_score = 0
                    if temp_map[word] > 0:
                        tf_score = 1 + math.log10(temp_map[word])
                    posting = [siteID, tf_score, importance_score]
                    if word in self.index:
                        self.index[word].append(posting)
                    else:
                        self.index[word] = []
                        self.index[word].append(posting)
        self.writeToDisk()
        self.writeUrlList()

    def mergeIndexes(self):
        # open the files to multi-way merge
        index1 = open("index1.txt", "r")
        index2 = open("index2.txt", "r")
        index3 = open("index3.txt", "r")
        output_file = open("combinedIndex.txt", "w")

        termToByte = {}

        line1 = "1"
        line2 = "1"
        line3 = "1"
        data1 = {}
        data2 = {}
        data3 = {}

        # while we havent hit the limit read the lines and get the current position then choose the lowest
        # termID and merge all the postings then write it to the new merged index
        while True:
            if line1 == "1":
                line1 = index1.readline()
            if line2 == "1":
                line2 = index2.readline()
            if line3 == "1":
                line3 = index3.readline()
            if not line1 and not line2 and not line3:
                # if the lines are all empty break
                break

            # the postings in json format: "word: posting[docID, Frequency]"
            if line1:
                data1 = json.loads(line1)
                word1 = list(data1.keys())[0]
            else:
                data1 = {}
                word1 = ""
            if line2:
                data2 = json.loads(line2)
                word2 = list(data2.keys())[0]
            else:
                data2 = {}
                word2 = ""
            if line3:
                data3 = json.loads(line3)
                word3 = list(data3.keys())[0]
            else:
                data3 = {}
                word3 = ""

            # Get lowest termID and merge all posting lists for that termID and write
            sortedWords = sorted([word1, word2, word3])
            lowestTerm = ""

            # dont select an empty word
            for word in sortedWords:
                if word != "":
                    lowestTerm = word
                    break

            # cases for matching words
            output_line = ""
            if lowestTerm == word1 and lowestTerm == word2 and lowestTerm == word3:
                output_line = self.mergeData([data1, data2, data3])
                line1, line2, line3 = "1", "1", "1"
            elif lowestTerm == word1 and lowestTerm == word2:
                output_line = self.mergeData([data1, data2])
                line1, line2 = "1", "1"
            elif lowestTerm == word1 and lowestTerm == word3:
                output_line = self.mergeData([data1, data3])
                line1, line3 = "1", "1"
            elif lowestTerm == word2 and lowestTerm == word3:
                output_line = self.mergeData([data2, data3])
                line2, line3 = "1", "1"
            elif lowestTerm == word1:
                output_line = self.mergeData([data1])
                line1 = "1"
            elif lowestTerm == word2:
                output_line = self.mergeData([data2])
                line2 = "1"
            elif lowestTerm == word3:
                output_line = self.mergeData([data3])
                line3 = "1"

            # write to output file
            termToByte[lowestTerm] = output_file.tell()
            output_file.write(json.dumps(output_line) + "\n")
        return termToByte

    # merges the data into one dict for json format
    def mergeData(self, data):
        word = list(data[0].keys())[0]
        new_dict = {word: []}
        for d in data:
            new_dict[word].extend(d[word])
        return new_dict

    def metaIndex(self,):
        termToByte = self.mergeIndexes()
        with open("termByteIndex.txt", "w") as ttbf:
            ttbf.write(json.dumps(termToByte))

def main():
    ind = Index('DEV')
    ind.buildIndex()
    ind.metaIndex()
    print("number of sites: ", len(ind.url_list))
    print("number of unique tokens: ", len(ind.index))


if __name__ == '__main__':
    main()