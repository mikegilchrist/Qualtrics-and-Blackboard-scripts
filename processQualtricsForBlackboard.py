from xml.dom import minidom
from random import shuffle
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.corpus import stopwords
import csv
import sys
import re
import nltk



def similarityOfComments (comment1, comment2):
        comment1.lower()
        comment2.lower()
        text1Set = word_tokenize(comment1)
        text2Set = word_tokenize(comment2)
        Stopwords = stopwords.words('english')
        Stopwords.append(',')
        Stopwords.append('.')
        content1 = []
        content2 = []


        for word in text1Set:
                if(word not in Stopwords):
                        content1.append(word);

        for word in text2Set:
                if(word not in Stopwords):
                        content2.append(word);

	if(len(content1) > len(content2)):
		totalWords = len(content1);
	else:
		totalWords = len(content2);	

        totalCommonWords = 0;
        for word in content1:
                if(word in content2):
                        totalCommonWords += 1;

        if(totalWords == 0):
                return 0;

        return totalCommonWords * 1.0 / totalWords


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
	OUTPUT = open(sys.argv[3], "w");
except:
	print "Opening the output document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv"
	exit(0);

Responses = xmldoc.getElementsByTagName('Response')

hasCompletedSurvey = []
studentsWithDuplicateComments = {};

#Dictionary of scores and comments for each student keyed on their student ID
Reviews = {}

for Response in Responses:
	netid = Response.getElementsByTagName('netid')[0];
	hasCompletedSurvey.append(netid.firstChild.data);

	i = 0;
	commentsByStudent = [];
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
		commentsByStudent.append(comment);

#	print commentsByStudent
	for index, comment in enumerate(commentsByStudent):
		for index2, comment2 in enumerate(commentsByStudent):
			if(comment != "" and index != index2 and similarityOfComments(comment, comment2) >= .75):
				studentsWithDuplicateComments[netid.firstChild.data] = commentsByStudent;
				break;
		
		
with open(sys.argv[2], 'rb') as csvfile:
	spamreader = csv.reader(csvfile)
	count = 0;
	for row in spamreader:
		hadPointsReduced = 0;
		count += 1;
		#Print out the format
		if(count == 1):
			for index, item in enumerate(row):
				OUTPUT.write(str(item));
				if(index != len(row) - 1):
					OUTPUT.write(",");
				else:
					print >>OUTPUT;
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

		if(netID in studentsWithDuplicateComments):
			print netID + " Seems to have duplicate or very similar comments. Those comments are:"
			for comment in studentsWithDuplicateComments[netID]:
				print  comment;
			print netID + "'s current score is " + str(finalScore);
			print "Enter what percentage you would like to deduct from the student's score. From 0 for none of it, to 1 for all of it"
			deduction = float(raw_input())
			while(deduction < 0 or deduction > 1):
				print "Invalid input: The deduction needs to be between 0 and 1" 
				print "Please, try again";
				deduction = float(raw_input())
			if(deduction > 0):
				hadPointsReduced = 1;
			finalScore = finalScore - finalScore * float(deduction);
			finalScore = round(finalScore, 3);
			print netID + "'s new score is " + str(finalScore);
			print "";
			print "";




		shuffle(comments)
		row[6] = str(finalScore);
		row[9] = "\"<html><b><u>Peer Score =</u></b> " + str(peerScore) + " ";
		index = 1;
		for comment in comments:
			if(comment != ""):
				row[9] += "</br>"
				row[9] += str(index);
				row[9] += ") " + comment;
				index += 1;
		if(hadPointsReduced):
			row[9] += "</br><b>**YOU DID NOT GIVE UNIQUE FEEDBACK TO YOUR PEERS, THEREFORE YOUR GRADE WAS REDUCED**</b>";
		
			
		if(netID not in hasCompletedSurvey):
			row[9] += "</br><b>**DID NOT SUBMIT RATINGS FOR OTHER TEAM MEMBERS. STUDENT RECEVING 0 CREDIT**</b>";
		row[9] += "</html>\""
			
		for index, item in enumerate(row):
			OUTPUT.write(str(item));
			if(index != len(row) - 1):
				OUTPUT.write(",");
		print >>OUTPUT;

