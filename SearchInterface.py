import sys
import json
import time
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer
from os import path
import math
from nltk.corpus import stopwords


class SearchInterface:
    def __init__(self):
        if path.exists("termByteIndex.txt"):
            with open("termByteIndex.txt", 'r') as termbyteindex:
                self.tbi = json.loads(termbyteindex.readline())
        with open('urlMap.txt', 'r') as f:
            self.urlmap = {}
            line = f.readline()
            while line:
                self.urlmap.update(json.loads(line))
                line = f.readline()

    def matchingDocuments(self, terms, index):
        terms = sorted([t.lower() for t in terms])
        combined_index = open(index, "r")
        postings = []
        corpus_size = len(self.urlmap)
        for term in terms:
            if term in self.tbi:
                combined_index.seek(self.tbi[term])
                posting_list = json.loads(combined_index.readline())[term]
                posting_list = self.tf_idf(posting_list, corpus_size)
                postings.append(posting_list)
            else:
                return []
        return self.inter(postings)

    def inter(self, postings):
        sets = []
        rankdict = defaultdict(float)  # dict of frequencies
        if len(postings) == 1:
            docs = []
            for p in postings[0]:
                docs.append(p[0])
                rankdict[p[0]] += (p[1] + p[2])  # add to frequency dict
        else:
            for posting in postings:
                docs = []
                for p in posting:
                    docs.append(p[0])
                    rankdict[p[0]] += p[1] + p[2] # add to frequency dict
                sets.append(set(docs))
            docs = list(sets[0].intersection(*sets[1:]))
        docs = sorted(docs, key=rankdict.get, reverse=True)

        return docs

    # parse search for query terms, or get from command line
    def getQuery(self, search=None):
        #Porter2 Stemmer
        snowball = EnglishStemmer()

        # gets the search query from the commandline
        if not search:
            query = []  # list of terms from the given query
            for arg in sys.argv[1:]:
                query.append(snowball.stem(arg))

            return self.stopWordCheck(query)
        else:
            query = []
            for part in search:
                query.append(snowball.stem(part))
            return self.stopWordCheck(query)

    def stopWordCheck(self, query):
        stopword_list = set(stopwords.words('english'))
        stop_count = 0
        stop_ratio = 0.5
        for word in query:
            if word in stopword_list:
                stop_count += 1
        if stop_count/len(query) < stop_ratio:
            return [w for w in query if w not in stopword_list]

        return query

    def getURLs(self, doc_list):
        urlList = []
        for docID in doc_list:
            ID = str(docID)
            url = self.urlmap.get(ID)
            if url:
                urlList.append(url)
        return urlList

    def tf_idf(self, posting_list, corpus_size):
        # (1+log(tf)) x log(N/df)
        for i in range(len(posting_list)):
            posting_list[i][1] = posting_list[i][1] * math.log10(corpus_size/len(posting_list))
        return posting_list




def main():
    interface = SearchInterface()
    start = time.time()
    terms = interface.getQuery()
    print(terms)
    if not terms:
        print("No query specified.")
        return

    docs = interface.matchingDocuments(terms, "combinedIndex.txt")
    urls = interface.getURLs(docs)
    print("total results: ", len(docs), "\n")
    print("top five results: ")
    for i in range(len(urls)):
        if i > 4:
            break
        print(urls[i])
    end = time.time()
    print("total query time: ", end-start)


if __name__ == '__main__':
    main()
