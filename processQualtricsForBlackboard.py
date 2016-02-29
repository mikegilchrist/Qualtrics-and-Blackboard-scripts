from xml.dom import minidom
from random import shuffle
import csv
import sys
import re


#inputFile = open(sys.argv[0], "r");
try:
	xmldoc = minidom.parse(sys.argv[1])
except:
	print "Opening the xml input document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv"
	exit(0);

try:
	formatFile = open(sys.argv[2], "r")
	formatFile.close();
except:
	print "Opening the format document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv"
	exit(0);

try:
	sys.stdout = open(sys.argv[3], "w");
except:
	print "Opening the output document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv"
	exit(0);

Responses = xmldoc.getElementsByTagName('Response')

hasCompletedSurvey = []

#Dictionary of scores and comments for each student keyed on their student ID
Reviews = {}

for Response in Responses:
	netid = Response.getElementsByTagName('netid')[0];
	hasCompletedSurvey.append(netid.firstChild.data);

	i = 0;
	while(1):
		i += 1;
		peer = "netid" + str(i);
		Online = "Online_" + str(i);
		O_peer = "O_peer" + str(i);
	
		try:	
			peerNetID = Response.getElementsByTagName(peer)[0]
		#The try fails because you got to the last peer, so then you should break
		except:
			break;
		if(peerNetID.firstChild == None):
			continue;

		try:	
			scoreNode = Response.getElementsByTagName(Online)[0]
			score = scoreNode.firstChild.data
		except:
			score = 0;

		try:	
			commentNode = Response.getElementsByTagName(O_peer)[0]
			comment = commentNode.firstChild.data
		except:
			comment = ""

		#Remove any quotes from the comment
		comment = re.sub('"', '', comment);
		peerID = peerNetID.firstChild.data
		
		if(peerID not in Reviews):
			Reviews[peerID] = [];
		Reviews[peerID].append(score);
		Reviews[peerID].append(comment);

with open(sys.argv[2], 'rb') as csvfile:
	spamreader = csv.reader(csvfile)
	count = 0;
	for row in spamreader:
		count += 1;
		#Print out the format
		if(count == 1):
			for index, item in enumerate(row):
				sys.stdout.write(str(item));
				if(index != len(row) - 1):
					sys.stdout.write(",");
				else:
					print;
			continue;
		netID = row[2];
		netID = re.sub("\"", "", netID);
		try:
			reviews = Reviews[netID];
		except:
			reviews = [];
		totalScore = 0;
		totalReviews = 0;
		comments = []
		for index, review in enumerate(reviews):
			if(index % 2 == 0):
				totalScore += float(review)
				totalReviews += 1;
			else:
				comments.append(review);
		if(totalReviews == 0):
			finalScore = 1.0;
		else:
			finalScore = totalScore / totalReviews / 10.0

		finalScore = round(finalScore, 3);
		peerScore = finalScore;

		if(netID not in hasCompletedSurvey):
			finalScore = 0;
		shuffle(comments)
		row[6] = str(finalScore);
		row[9] = "\"<html><b><u>Peer Score =</u></b> " + str(peerScore) + " ";
		for index, comment in enumerate(comments):
			if(comment != ""):
				row[9] += "</br>"
				row[9] += str(index + 1);
				row[9] += ") " + comment;
		if(netID not in hasCompletedSurvey):
			row[9] += "</br><b>**DID NOT SUBMIT RATINGS FOR OTHER TEAM MEMBERS. STUDENT RECEVING 0 CREDIT**</b>";
		row[9] += "</html>\""
			
		for index, item in enumerate(row):
			sys.stdout.write(str(item));
			if(index != len(row) - 1):
				sys.stdout.write(",");
		print;

