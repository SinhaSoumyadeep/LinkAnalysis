import os
import re
import json
import sys
import requests
import time

from bs4 import BeautifulSoup

#This is the path where the corpus downloaded in the Previous Assignment is stored.
directory = "../../Assignment1/files/DownloadHTML/['Carbon_footprint']"

#This is the path of the file where the 1000 urls are stored.
buildLinkDirectoryPath = "../../Assignment1/files/"

#This the file for which 1000 urls are crawled. you can change the file name here to generate the graph.
globalFile = "Carbon_footprint"#"focusedFile"

#This is a dictionary that stores the inlink
inlink = {}

#This flage is set to True if we need to crawl from the web else it will be crawled from the downloaded corpus.
readFromWeb = True

#Set the timelapse before hitting another request.
politeness = 1

#This function is used to filter out keywords from the soup object.
def filter(soup, tag):
    for content in soup.find_all(tag):
        content.extract()
    return soup

#This function is used to fetch the filename by splitting the url.
def getfilename(path):
    fileurl = str(path).split("/")
    filename = fileurl[fileurl.__len__() - 1]
    return  filename

#This function adds domain name to the list of urls.
def addDomain(link):
    p = re.compile("^/wiki/(.)*")
    m = p.match(link)

    if m:
        return "https://en.wikipedia.org" + link
    else:
        return link

#This function is used to filter out urls with ":".
def checkForColon(link):
    p = re.compile("https://en.wikipedia.org/wiki/(.)*:(.)*")
    m = p.match(link)
    if m:
        return True
    else:
        return False

#This function is used to validate urls and filter out external links.
def isValidUrl(str):
    p = re.compile("https://en.wikipedia.org/wiki/(.)*")
    m = p.match(str)
    if m:
        return True
    else:
        return False

#This function is used to hit request to a particular page
# and returns a soup object and save the raw html pages if the write flag is set to true.
def getPage(url):
    print(url)
    time.sleep(politeness)
    soup = None
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

    except:
        print("inside exception!!!!!")
        soup = None

    return soup

#This function is used to crawl and validate the urls encountered and returns the list of urls for that url.
def extractUniqueUrlsFromFile(file):
    print("*********** crawling file "+file+" *****************")
    uniqueListOfUrl =[]
    filtertag = ["table", "img"]

    if not readFromWeb:
        try:
            fileContent = open(directory+"/"+file, "r", encoding="utf-8")

        except:
            print(file+" file doesnot exist!")
            return
        soup = BeautifulSoup(fileContent.read(), 'html.parser')
    else:
        soup = getPage("https://en.wikipedia.org/wiki/"+file)



    soup = extractbodytag(soup)

    for tag in filtertag:
        soup = filter(soup, tag)

    for link in soup.find_all('a'):
        url = str(link.get('href'))
        url = addDomain(url)
        if (isValidUrl(url)):
            if "disambiguation" not in url and \
                    "#" not in url and \
                    ".jpg" not in url and \
                    ".png" not in url and \
                    ".pdf" not in url and \
                    "Main_Page" not in url and \
                    not checkForColon(url):
                if url.upper() not in (url.upper() for url in uniqueListOfUrl):
                    uniqueListOfUrl.append(getfilename(url))


    return uniqueListOfUrl



#This function is used to extract the Body of the Html page.
def extractbodytag(soup):
    for content in soup.find_all("body"):
        soup = content.extract()
    return soup

#This method is used to initialize the Inlink Dictionary.
def buildlinkDirectory(filename):
    file = open(buildLinkDirectoryPath+filename, "r");
    for line in file:
       key = getfilename(line[:line.find("#")])
       if key not in inlink:
           inlink[key]=[]

#This method is used to write the Inlinks to a file.
def writeInlinks(filename):
    if not os.path.exists("../Inlinks"):
        os.mkdir("../Inlinks")

    f = open("../Inlinks/inlink"+filename+"JSON.json", "w")
    convertedJson = json.dumps(inlink)
    f.write(convertedJson)
    f.close()

    ftext = open("../Inlinks/inlink"+filename+"Graph.txt", "w")
    for key in inlink.keys():
        ftext.write("\n\n"+key+":\n\n")
        for inlinks in inlink[key]:
            ftext.write("\t"+inlinks+", ")

#This method is used to write the Inlinks Stats to file.
def writeStats(filename):
    outlink = findOutLinks(inlink)
    #print(outlink)

    pages_with_no_inlinks = 0
    pages_with_no_outlinks = 0
    max_indegree = 0
    max_outdegree = 0


    for key in outlink:
        if max_outdegree < len(outlink[key]):
            max_outdegree = len(outlink[key])

        if len(outlink[key]) == 0:
            pages_with_no_outlinks += 1

    for key in inlink:
        if max_indegree < len(inlink[key]):
            max_indegree = len(inlink[key])

        if len(inlink[key]) == 0:
            pages_with_no_inlinks += 1


    fstats = open("../Inlinks/stats_"+filename+".txt", "w")
    fstats.write("Page with no inlinks:\t" + str(pages_with_no_inlinks)+"\n")
    fstats.write("Page with no outlinks:\t" + str(pages_with_no_outlinks)+"\n")
    fstats.write("max_indegree:\t" + str(max_indegree)+"\n")
    fstats.write("max_outdegree:\t" + str(max_outdegree))

#This method is used to write the Raw inlink count to a file.
def writePageRankByRawInlinkCount(filename):
    inlinkcount = {}
    for key in inlink.keys():
        inlinkcount[key] = len(inlink[key])

    inlinkPrSorted = sorted(inlinkcount.items(), key=lambda kv: kv[1], reverse=True)
    frawinlink = open("../Inlinks/PR_By_Raw_Inlink_Count_task3_" + filename + ".txt", "w")
    counter = 1
    for element in inlinkPrSorted[:20]:
        frawinlink.write(str(counter)+".\t"+str(element[0])+"\t"+str(element[1])+"\n")
        counter+=1

#This method is used to build the Inlink graph.
def buildGraph(filename):
    #filename = getfilename(url)
    buildlinkDirectory(filename)
    for key in inlink.keys():
        links = extractUniqueUrlsFromFile(key)
        if links != None:

            for eachLink in links:
                if eachLink != key:
                    if eachLink in inlink.keys():
                        if key not in inlink[eachLink]:
                            inlink[eachLink].append(key)


    writeInlinks(filename)
    writePageRankByRawInlinkCount(filename)
    writeStats(filename)


#This method is used to generate the page ranking.
def PageRanking(easyGraph, filename, damp, task):
    fL1Norm = open("../Inlinks/L1Norm_"+task+"_"+filename+"_"+str(damp)+"_Graph.txt", "w")
    fL1Norm.write("\n\n**************************\tL1Norm for "+filename+"\t**************************\n\n")
    OutLink = findOutLinks(easyGraph)
    S = findSinkNodes(OutLink)
    count = 0
    breakCount = 0
    P = easyGraph.keys()
    N = P.__len__()
    d = damp
    PR = {}
    newPR = {}


    for p in P:
        PR[p] = 1/N

    while 1:

        #print(count)
        fL1Norm.write("\n\nIteration:\t"+str(count)+":\n")
        sinkPR = 0

        for p in S:
            sinkPR += PR[p]
        for p in P:
            newPR[p] = (1-d)/N
            newPR[p] += d * sinkPR / N

            for q in easyGraph[p]:
                Lq = OutLink[q].__len__()
                newPR[p] += (d * PR[q]) / Lq

        newPRSum = 0
        for p in newPR:
            newPRSum=newPRSum+newPR[p]

        fL1Norm.write("\n\tnewPRSum:\t" + str(newPRSum))

        if task == "task2":
            if calculateL1Norm(newPR, PR, P, fL1Norm) < 0.001:
                breakCount += 1
            else:
                breakCount = 0

            if breakCount >= 4:
                break


        for p in newPR:
            PR[p] = newPR[p]

        if task == "task3":
            if count == 4:
                break

        count += 1

    fL1Norm.close()
    return PR


#This method is used to calculate the L1Norm.
def calculateL1Norm(newPR, PR, P, fL1Norm):
    L1 = 0
    for p in P:
        L1 = L1 + abs(newPR[p]-PR[p])
    #print("::::> ",L1)
    fL1Norm.write("\n\tL1Norm:\t"+str(L1))
    return L1

#This method is used to find the Sink node.
def findSinkNodes(OutLink):

    sinkNode = []
    for key in OutLink.keys():
        if len(OutLink[key]) == 0:
            sinkNode.append(key)

    return sinkNode

#This method is used to find the OutLink.
def findOutLinks(easyGraph):
    outlink = {}

    for key in easyGraph.keys():
        if key not in outlink:
            outlink[key] = []

        for findkey in easyGraph.keys():
            if key in easyGraph[findkey] and key != findkey:
                if findkey not in outlink[key]:
                    outlink[key].append(findkey)

    return outlink


#This method is used to read the json file which contains the inlink graph.
def readInlinkGraph(filename):
    with open("../Inlinks/inlink"+filename+"JSON.json") as f:
        data = json.load(f)

    return data

#This method is used to find the get Page Rank.
def getPageRanks(filename, d, task):
    pageranking = PageRanking(readInlinkGraph(filename),filename, d, task)

    prsorted = sorted(pageranking.items(), key=lambda kv: kv[1], reverse=True)

    frank= open("../Inlinks/Page_Ranking_"+task+"_"+str(d)+"_"+ filename + ".txt", "w")

    counter = 1
    for key in prsorted[:50]:
        frank.write(str(counter)+".\t"+str(key[0])+":\t"+str(key[1])+"\n\n")
        counter+=1

    print(prsorted)

#This is the main method.
def main():
    #buildGraph(globalFile)
    getPageRanks(globalFile, 0.85, "task2")
    getPageRanks(globalFile, 0.50, "task2")
    getPageRanks(globalFile, 0.65, "task2")
    getPageRanks(globalFile, 0.85, "task3")









if __name__ == '__main__':
    main();