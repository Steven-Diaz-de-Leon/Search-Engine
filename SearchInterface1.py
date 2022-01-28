import sys
import fileinput
import json
import re
import time
class SearchInterface:

    # TODO searches the index for the given terms and returns best matches
    def matchingDocuments(self, terms, index):
        terms = [t.lower() for t in terms]
        combined_index = open(index, "r")
        query = {}
        while True:
            line = combined_index.readline()
            if not line:
                break
            pattern = re.findall(r'"(.+?)"', line)
            if pattern[0] in terms:
                query.update(json.loads(line))
        sorted_query = sorted(query, key=lambda k: len(query[k]), reverse=True)
        if not sorted_query:
            return []
        lowestTerm = sorted_query[0]
        lowestTermDocs = []
        docs_list = []
        for posting in query[lowestTerm]:
                lowestTermDocs.append(posting)
        if len(sorted_query) == 1:
                lowestTermDocs.sort(key = lambda x: x[1], reverse=True)
                return lowestTermDocs



        # Trying to get the intersection of the postings of the search terms
        # lowestTermDoc is the postings of the lowest search term


        intersection = []
        for term in sorted_query[1:]:
            postingList = query[term]
            intersection = self.intersection(lowestTermDocs, postingList)
            lowestTermDocs = intersection

        return intersection

    def intersection(self, posting1, posting2):
        iter1 = 0
        iter2 = 0
        intersection = []
        while iter1 != len(posting1) and iter2 != len(posting2):
            if (posting1[iter1])[0] == (posting2[iter2])[0]:
                intersection.append(posting1[iter1])
                iter1 += 1
                iter2 += 1
            elif (posting1[iter1])[0] < (posting2[iter2])[0]:
                iter1 += 1
            else:
                iter2 += 1
        intersection.sort(key = lambda x: x[1], reverse=True)
        return intersection
    # should probably put this and its utilities in its on class/file
    def mergeIndexes(self):
        # open the files to multi-way merge
        index1 = open("index1.txt", "r")
        index2 = open("index2.txt", "r")
        index3 = open("index3.txt", "r")
        output_file = open("combinedIndex.txt", "w")


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
            output_file.write(json.dumps(output_line) + "\n")
        return

    # merges the data into one dict for json format
    def mergeData(self, data):
        word = list(data[0].keys())[0]
        new_dict = {word: []}
        for d in data:
            new_dict[word].extend(d[word])
        return new_dict

    # gets the search query from the commandline
    def getQuery(self):
        argsc = len(sys.argv)
        query = []              # list of terms from the given query
        for arg in sys.argv:
            query.append(arg)
        query.remove(sys.argv[0])
        return query

    def getURLs(self, doc_list, file):
        f = open(file, "r")
        urlmap = {}
        line = f.readline()
        urlList = []
        while line:
            urlmap.update(json.loads(line))
            line = f.readline()
        for docID in doc_list:
            ID = str(docID[0])
            url = urlmap.get(ID)
            if url:
                urlList.append(url)
        return urlList



def main():
    interface = SearchInterface()
    terms = interface.getQuery()
    #TODO uncomment this to merge
    #interface.mergeIndexes()
    docs = interface.matchingDocuments(terms, "combinedIndex.txt")
    urls = interface.getURLs(docs, "urlMap.txt")
    print("doc_list: ", docs)
    if not docs:
        print("no matches found.")
    print("urls: ", urls)
    print("doc list size: ", len(docs))


if __name__ == '__main__':
    main()

