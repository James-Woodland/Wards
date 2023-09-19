import numpy as np
import matplotlib.pyplot as plt
import os
import json
from scipy.stats import gaussian_kde
from sklearn import preprocessing
import seaborn as sns
from adjustText import adjust_text
import requests
import wget
from zipfile import ZipFile
import shutil
import datetime

folders = os.listdir("BayesData")
for i in folders:
    shutil.rmtree("BayesData/{}".format(i))
    
folders = os.listdir("WardMaps")
for i in folders:
    shutil.rmtree("WardMaps/{}".format(i))


r = requests.post('https://lolesports-api.bayesesports.com/auth/login', json={"username": "Bayes Username", "password": "Bayes Password"})

abc = r.json()

r = requests.get('https://lolesports-api.bayesesports.com/historic/v1/riot-lol/teams', headers = {"Authorization": 'Bearer {}'.format(abc["accessToken"])})
print(json.dumps(r.json(), indent = 4))
teamId = ""
teamName = "TEAM NAME"
for i in r.json():
    if i["name"].upper() == teamName.upper():
        print(i)
        teamId = i["id"]

r = requests.get('https://lolesports-api.bayesesports.com/historic/v1/riot-lol/matches', headers = {"Authorization": 'Bearer {}'.format(abc["accessToken"])}, params={"teamIds":[teamId], "size": 10})

matches = r.json()["results"]
print(json.dumps(matches, indent = 4))

matchCount = 0
for i in matches:
    for j in range(len(i["match"]["games"])):
        matchCount = matchCount + 1
        r = requests.get('https://lolesports-api.bayesesports.com/historic/v1/riot-lol/games/{}/download'.format(i["match"]["games"][len(i["match"]["games"]) - j - 1]["id"]), headers = {"Authorization": 'Bearer {}'.format(abc["accessToken"])})
        print(json.dumps(r.json(), indent = 4))
        response = wget.download(r.json()["url"], "BayesData/{}.zip".format(i["match"]["games"][len(i["match"]["games"]) - j - 1]["id"]))
        with ZipFile("BayesData/{}.zip".format(i["match"]["games"][len(i["match"]["games"]) - j - 1]["id"]), 'r') as zipObj:
            #Extract all the contents of zip file in current directory
            zipObj.extractall("BayesData/{}".format(i["match"]["games"][len(i["match"]["games"]) - j - 1]["id"]))
        os.remove("BayesData/{}.zip".format(i["match"]["games"][len(i["match"]["games"]) - j - 1]["id"]))
        if matchCount == 10:
            break
    if matchCount == 10:
        break


path = 'BayesData/'

teamCode = ""
team = "TEAM TRICODE"

folders = os.listdir(path)
print(folders)
counter = 0
# Create data
x1 = [[],[],[],[],[]]
y1 = [[],[],[],[],[]]
texts = [[],[],[],[],[]]
WardType = [[],[],[],[],[]]
title = teamName
for i in folders:
    playerId = []
    folderPath = path + "/" + i
    files = os.listdir(folderPath)
    count = 1
    for i in range(len(files)):
        filed = files[i]
        filed = filed[:-5]
        files[i] = filed
    files = [int(x) for x in files]
    files.sort()
    files = [str(x) for x in files]
    for i in range(len(files)):
        filed = files[i]
        filed = filed + ".json"
        files[i] = filed
    for j in files:
        f = open(folderPath + "/"+ j)
        abc = json.load(f)
        f.close()
        if j == "1.json":
            print(json.dumps(abc, indent = 4))
            if str(abc["payload"]["payload"]["payload"]["teams"][0]["participants"][0]["name"].split(" ")[0]) == team:
                teamCode = abc["payload"]["payload"]["payload"]["teams"][0]["urn"]
                for player in abc["payload"]["payload"]["payload"]["teams"][0]["participants"]:
                    playerId.append(player["urn"])
            if str(abc["payload"]["payload"]["payload"]["teams"][1]["participants"][0]["name"].split(" ")[0]) == team:
                teamCode = abc["payload"]["payload"]["payload"]["teams"][1]["urn"]
                for player in abc["payload"]["payload"]["payload"]["teams"][1]["participants"]:
                    playerId.append(player["urn"])
        if abc["payload"]["payload"]["action"] == "PLACED_WARD":
            remainingSecs = (abc["payload"]["payload"]["payload"]["gameTime"]%60000)
            minutes = int((abc["payload"]["payload"]["payload"]["gameTime"] - (abc["payload"]["payload"]["payload"]["gameTime"]%60000))/60000)
            seconds = str(int((remainingSecs - (remainingSecs%1000))/1000)).zfill(2)
            print(json.dumps(abc, indent = 4))
            print(str(minutes) + ":" + str(seconds))
            if minutes > 7:
                break
            if abc["payload"]["payload"]["payload"]["placerTeamUrn"] == teamCode and abc["payload"]["payload"]["payload"]["gameTime"] <= 600000 and (abc["payload"]["payload"]["payload"]["wardType"] == "control" or abc["payload"]["payload"]["payload"]["wardType"] == "yellowTrinket") and abc["payload"]["payload"]["payload"]["gameTime"] >= 120000:                
                count = 0
                for player in playerId:
                    if player == abc["payload"]["payload"]["payload"]["placerUrn"]:
                        x1[count].append(abc["payload"]["payload"]["payload"]["position"][0])
                        y1[count].append(abc["payload"]["payload"]["payload"]["position"][1])
                            
                        if abc["payload"]["payload"]["payload"]["wardType"] == "control":
                            color = 'red'
                        else:
                            color = 'yellow'
                        WardType[count].append(color)
                        remainingSecs = (abc["payload"]["payload"]["payload"]["gameTime"]%60000)
                        minutes = int((abc["payload"]["payload"]["payload"]["gameTime"] - (abc["payload"]["payload"]["payload"]["gameTime"]%60000))/60000)
                        seconds = str(int((remainingSecs - (remainingSecs%1000))/1000)).zfill(2)
                        texts[count].append([abc["payload"]["payload"]["payload"]["position"][0],abc["payload"]["payload"]["payload"]["position"][1],str(minutes) + ":" + str(seconds), color, 7])
                    count = count + 1
    #for i in range(len(x1)):
        #plt.annotate(str(minutes[i]) + ":" + str(seconds[i]),
                 #(x1[i],y1[i]), # these are the coordinates to position the label
                 #textcoords="offset points", # how to position the text
                 #xytext=(0,5), # distance from text to points (x,y)
                 #ha='center',
                 #fontsize = 10)
positions = ["Top", "Jungle", "Mid", "Bot", "Support"]
print(texts)
for i in range(5):
    fig, axes = plt.subplots()
    plt.title(title + " - " + positions[i])
    axes.scatter(x1[i],y1[i], s = 10, c = WardType[i])
    axes.scatter(x1[i],y1[i], s = 1000, c = WardType[i], alpha = 0.25)
    plt.axis('off')
    axes.set_ylim(-120, 14980)
    axes.set_xlim(-120, 14870)
    labels = []
    for j in texts[i]:
        labels.append(axes.text(j[0], j[1], j[2], color = j[3], fontsize = j[4]))
    img = plt.imread("map11.png")
    axes.imshow(img, extent=[-120, 14870, -120, 14980])
    adjust_text(labels, force_text = (0,0))
    plt.savefig("WardMaps/"+title + "_" + positions[i]+'.png', bbox_inches = 'tight')
    #input()
    #plt.show()
    plt.clf()
    
            

#for i in files:
#    f = open(path + i)
#    abc = json.load(f)
#    if abc["payload"]["payload"]["payload"]["placerTeamUrn"] == "live:lol:riot:team:105532791598779236" and abc["payload"]["payload"]["payload"]["gameTime"] <= 600000:
#        x1.append(abc["payload"]["payload"]["payload"]["position"][0])
#        y1.append(abc["payload"]["payload"]["payload"]["position"][1])
#        remainingSecs = (abc["payload"]["payload"]["payload"]["gameTime"]%60000)
#        minutes.append(int((abc["payload"]["payload"]["payload"]["gameTime"] - (abc["payload"]["payload"]["payload"]["gameTime"]%60000))/60000))
#        seconds.append(int((remainingSecs - (remainingSecs%1000))/1000))

# Plot
#sns.set_style("ticks")
#sns.kdeplot(x=x1, y=y1, thresh=0.2, bw_adjust=.75, cmap="RdYlGn")
#plt.scatter(x1,y1)
#for i in range(len(x1)):
 #   plt.annotate(str(minutes[i]) + ":" + str(seconds[i]),
 #                (x1[i],y1[i]), # these are the coordinates to position the label
 #                textcoords="offset points", # how to position the text
 #                xytext=(0,5), # distance from text to points (x,y)
 #                ha='center',
 #                fontsize = 5)
#plt.show()

#fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize = (5,5))
#axes.set_ylim(-120, 14980)
#axes.set_xlim(-120, 14870)
#img = plt.imread("map11.png")
#axes.imshow(img, extent=[-120, 14870, -120, 14980])
#sns.set_style("ticks")
#sns.kdeplot(x=x2, y=y2, thresh=0.2, bw_adjust=.75, cmap="RdYlGn", fill=True, alpha = 0.75)
#plt.show()


