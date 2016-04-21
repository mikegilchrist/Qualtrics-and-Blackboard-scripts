from xml.dom import minidom
import sys
import random
from random import randint
import time
import string;
import numpy
from random import shuffle
if 'nltk' in sys.modules:
	import nltk
	from nltk import sent_tokenize, word_tokenize, pos_tag
	from nltk.corpus import stopwords
import csv
import sys
import re
import datetime;

#Set this flag to 0 if you don't want the program to check for similar comments
checkForSimilarityOfComments = 1;
#Set this to the percentage of words that should match across reviews for the program to flag a set of reviews
similarityThreshold = .75
now = datetime.datetime.now()


#Returns the percentage of words that match in 2 comments
def similarityOfComments (comment1, comment2):
        comment1.lower()
        comment2.lower()
        text1Set = comment1.split(' ')
        text2Set = comment2.split(' ')
	if 'nltk' in sys.modules:
		Stopwords = stopwords.words('english')
	else:
		Stopwords = [];
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


try:
	inputFile = open(sys.argv[1], "r")
	inputFile.close();
except:
	print "Opening the xml input document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv seed[Optional]"
	exit(0);

try:
	formatFile = open(sys.argv[2], "r")
	formatFile.close();
except:
	print "Opening the format document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv seed[Optional]"
	exit(0);

try:
	OUTPUT = open(sys.argv[3], "w");
except:
	print "Opening the output document failed";
	print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv seed[Optional]"
	exit(0);

if(len(sys.argv) == 5):
	try:
		seed = float(sys.argv[4]);
		random.seed(seed)
	except:
		print "Invalid Seed";
		print "Useage: python processBlackboardForQualtrics.py input.xml format.csv output.csv seed[Optional]"
		exit(0);
else:
	seed = randint(0, 100);
	random.seed(seed)


hasCompletedSurvey = []
studentsWithDuplicateComments = {};
commentSimilarity = {};
studentsWhoDidntFinishSurvey = [];
studentsWhoDidntContribute = [];
peerNames = {}

try:
	xmldoc = minidom.parse(sys.argv[1])
except:
	print "Was unable to parse input.xml file."
	print sys.exc_info()[0]
	print sys.exc_info()[1]
	exit(1);

Responses = xmldoc.getElementsByTagName('Response')
if(len(Responses) == 0):	
	print "There were no tags in the xml file named 'Response'"
	print "Either change the input.xml file to have tags named 'Response' or change that this line looks for"
	exit(1);


#Dictionary of scores and comments for each student keyed on their student ID
Reviews = {}

#This will be used to remove any non-printable characters
printable = set(string.printable)

printInfo = 1;
if(printInfo) printInfoContribute = 1; #set specific flag so that lack of contribute tag message is printed only once.

print "Seed used = " + str(seed);
print "Time of execution = " + now.strftime("%Y-%m-%d %H:%M");
print "Git version number = 7";
sys.stdout.write("Arguments used = ");
for i in range(0, len(sys.argv)):
	sys.stdout.write(sys.argv[i] + "  ");
print 
print



for Response in Responses:

	try:
		scoreNode = Response.getElementsByTagName('netid')[0]
	except:
		print sys.exc_info()[0]
		print sys.exc_info()[1]
		print "The responses do not have the 'netid' tag"
		print "Either change the input.xml file to have tags named 'netid' or change what this line looks for"
		exit(1);

	netid = Response.getElementsByTagName('netid')[0];
	hasCompletedSurvey.append(netid.firstChild.data);

	i = 0;
	commentsByStudent = [];
	try:
		finished = Response.getElementsByTagName('Finished')[0].firstChild.data;
	except:
		print sys.exc_info()[0]
		print sys.exc_info()[1]
		print "A response did not have the 'Finished' tag"
		print "Either change the input.xml file to have tags named 'Finished' or change what this line looks for"
		exit(1);

	if(finished != '1'):
		studentsWhoDidntFinishSurvey.append(netid.firstChild.data);
		continue;

	try:
		Contribute = Response.getElementsByTagName('Contribute')[0].firstChild.data;
	except IndexError: # test for specific error
                Contribute = '1' #tag not found so set value to 1
		if(printInfoContribute):
			print sys.exc_info()[0]
			print sys.exc_info()[1]
			print "Response lacking 'Contribute' tag"
			print "Variable 'Contribute' begin set to '1' for this and all other entries."
                        printInfoContribute=0;
			print;
			#printInfo = 0; #commented out by mikeg. Not sure why you want to stop the printing.

	if(Contribute != '1'):
		studentsWhoDidntContribute.append(netid.firstChild.data);
		continue;

	while(1):
		i += 1;
		peer = "netid" + str(i);
		Online = "Online_" + str(i);
		O_peer = "O_peer" + str(i);
	
		
		finished = Response.getElementsByTagName('Finished')[0].firstChild.data;

		#Test to ensure the tags are properly named
		

		try:	
			peerNetID = Response.getElementsByTagName(peer)[0]
		#The try fails because you got to the last peer, so then you should break
		except:
			break;

		if(peerNetID.firstChild == None):
			continue;

		try:
			scoreNode = Response.getElementsByTagName(Online)[0]
		except:
			print sys.exc_info()[0]
			print sys.exc_info()[1]
			print "The responses do not have the 'Online_' tag"
			print "Either change the input.xml file to have tags named 'Online_' or change what this line looks for"
			print "Specifically, this failed for the response by " + netid.firstChild.data;
			exit(1);
		try:	
			score = scoreNode.firstChild.data
		except:
			score = 0;

		try:	
			commentNode = Response.getElementsByTagName(O_peer)[0]
		except:
			print sys.exc_info()[0]
			print sys.exc_info()[1]
			print "The responses do not have the 'O_peer' tag"
			print "Either change the input.xml file to have tags named 'O_peer' or change what this line looks for"
			print "Specifically, this failed for the response by " + netid.firstChild.data;
			exit(1);

		try:
			comment = commentNode.firstChild.data
		except:
			comment = ""

		newComment = "";

		#Remove non-printable characters
		for letter in comment:
			if(letter in printable):
				newComment += letter;	

		comment = newComment;
		
		#Remove any quotes from the comment
		comment = re.sub('"', '', comment);
		peerID = peerNetID.firstChild.data
		
		#Remove any newlines;
		comment = comment.replace('\n', ' ');
		comment = comment.replace('\r', ' ');
		if(peerID not in Reviews):
			Reviews[peerID] = [];
		if(peerID not in peerNames):
			peerNames[peerID] = [];
		Reviews[peerID].append(score);
		Reviews[peerID].append(comment);
		peerNames[peerID].append(netid.firstChild.data);
		peerNames[peerID].append(score);
		peerNames[peerID].append(comment);
		commentsByStudent.append(comment);

	if(checkForSimilarityOfComments):
		for index, comment in enumerate(commentsByStudent):
			for index2, comment2 in enumerate(commentsByStudent):
				if(comment != "" and index != index2 and similarityOfComments(comment, comment2) >= similarityThreshold):
					studentsWithDuplicateComments[netid.firstChild.data] = commentsByStudent;
					commentSimilarity[netid.firstChild.data] = similarityOfComments(comment, comment2);
					break;
			
studentsScores = [];
rawScores = [];
gradeIndex = -1;
commentIndex = -1;
netIDIndex = -1;
incompleteCount = 0;

try:
	with open(sys.argv[2], 'rb') as csvfile:
		spamreader = csv.reader(x.replace('\0', '') for x in csvfile);
		count = 0;
		for index, row in enumerate(spamreader):
			#Skip blank lines
			if(len(row) == 0):
				continue;
			hadPointsReduced = 0;
			count += 1;
			#Print out the format
			if(count == 1):
				for index, item in enumerate(row):
					#Find the index where the grade and comments go
					if('Total Pts:' in item):
						gradeIndex = index;
					if('Feedback to Learner' in item):
						commentIndex = index;
					if('Username' in item):
						netIDIndex = index;
					OUTPUT.write(str(item));
					if(index != len(row) - 1):
						OUTPUT.write(",");
					else:
						print >>OUTPUT;
					maxIndex = index;
				if(gradeIndex == -1):
					print "The script was unable to detect which index in format was where the students' grade should go."
					print "Please select the index that corrosponds to the index that should contain the students' grades"
					print
					
					for index, item in enumerate(row):
						print str(index) + ":  " + item;

					while(1):
						try:
							gradeIndex = int(raw_input());
							if(gradeIndex < 0 or gradeIndex > maxIndex):
								print "Invalid input, please give a number between 0 and " + str(maxIndex);
							else:
								break;
						except:
							print "Invalid input, please give a number between 0 and " + str(maxIndex);

				if(commentIndex == -1):
					print "The script was unable to detect which index in format was where the students' comments should go."
					print "Please select the index that corrosponds to the index that should contain the students' comments"
					print
					
					for index, item in enumerate(row):
						print str(index) + ":  " + item;

					while(1):
						try:
							commentIndex = int(raw_input());
							if(commentIndex < 0 or commentIndex > maxIndex):
								print "Invalid input, please give a number between 0 and " + str(maxIndex);
							else:
								break;
						except:
							print "Invalid input, please give a number between 0 and " + str(maxIndex);

				if(netIDIndex == -1):
					print "The script was unable to detect which index in format was where the student ID is containted"
					print "Please select the index that corrosponds to the index that contains the student ID"
					print
					
					for index, item in enumerate(row):
						print str(index) + ":  " + item;

					while(1):
						try:
							netIDIndex = int(raw_input());
							if(netIDIndex < 0 or netIDIndex > maxIndex):
								print "Invalid input, please give a number between 0 and " + str(maxIndex);
							else:
								break;
						except:
							print "Invalid input, please give a number between 0 and " + str(maxIndex);
					
				continue;
			netID = row[netIDIndex];
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
			rawScores.append(finalScore);
			peerScore = finalScore;
			if(netID not in hasCompletedSurvey):
				finalScore = 0;

			if(netID in studentsWhoDidntFinishSurvey):
				finalScore = 0;

			if(netID in studentsWhoDidntContribute):
				finalScore = 0;

			if(netID in studentsWithDuplicateComments):
				print netID + " seems to have comments that use at least " + str(round(commentSimilarity[netID] * 100, 2)) + "% of the same words. Those comments are:"
				for index, comment in enumerate(studentsWithDuplicateComments[netID]):
					print  str(index + 1) + ") " + comment;
				print netID + "'s current score is " + str(finalScore);
				print "Enter what percentage you would like to deduct from the student's score. From 0 for none of it, to 1 for all of it"
				while(1):
					try:
						deduction = float(raw_input())
						while(deduction < 0 or deduction > 1):
							print "Invalid input: The deduction needs to be between 0 and 1" 
							print "Please, try again";
							deduction = float(raw_input())
						break;
					except:
						print "Invalid input: The deduction needs to be between 0 and 1" 
						print "Please, try again";
					
				if(deduction > 0):
					hadPointsReduced = 1;
				finalScore = finalScore - finalScore * float(deduction);
				finalScore = round(finalScore, 3);
				print netID + "'s new score is " + str(finalScore);
				print "";
				print "";



			if(netID in hasCompletedSurvey and netID not in studentsWhoDidntFinishSurvey and netID not in studentsWhoDidntContribute):
				studentsScores.append(finalScore);

			shuffle(comments)
			row[gradeIndex] = str(finalScore);
			row[commentIndex] = "\"<html><b><u>Peer Score =</u></b> " + str(peerScore) + " ";
			index = 1;
			if(netID not in studentsWhoDidntContribute):
				for comment in comments:
					if(comment != ""):
						row[commentIndex] += "</br>"
						row[commentIndex] += str(index);
						row[commentIndex] += ") " + comment;
						index += 1;
				if(hadPointsReduced):
					row[commentIndex] += "</br><b>**YOU DID NOT GIVE UNIQUE FEEDBACK TO YOUR PEERS, THEREFORE YOUR GRADE WAS REDUCED**</b>";
			

				
			if(netID not in hasCompletedSurvey or netID in studentsWhoDidntFinishSurvey):
				incompleteCount += 1;
				row[commentIndex] += "</br><b>**DID NOT SUBMIT RATINGS FOR OTHER TEAM MEMBERS. STUDENT RECEVING 0 CREDIT**</b>";
			elif(netID in studentsWhoDidntContribute):
				incompleteCount += 1;
				row[commentIndex] += "</br><b>**Student indicates s/he did not contribute to the assignment. STUDENT RECEVING 0 CREDIT**</b>";
				
			row[commentIndex] += "</html>\""
				
			for index, item in enumerate(row):
				OUTPUT.write(str(item));
				if(index != len(row) - 1):
					OUTPUT.write(",");


			


			print >>OUTPUT;
except:
	print sys.exc_info()[0]
	print "Had an issue with line number " + str(index) + " in the format file"
	print "The line contains: " + str(row);
	exit(1);


for student in studentsWhoDidntContribute:
	print "Student who self-reported that s/he didn't contribute: " + student;
	count = 0;

	if(student in Reviews):
		for review in peerNames[student]:
			if(count % 3 == 0):
				print "Peer ID = " + str(review);
			elif(count % 3 == 1):
				print "Score given = " + str(review);
			else:
				print "Comment given = " + review;
			count += 1 
	else:
		print "No reviews were submitted for " + student;

	print
	print

print "Number of students who did not complete survey = " + str(incompleteCount);
print
print

print "Statistics of grades before setting students grades to 0 if they did not complete the survey"
print "Mean of students' grades = " + str(numpy.mean(rawScores));
print "Standard Deviation of students' grades = " + str(numpy.std(rawScores));
print "Max of students' grades = " + str(max(rawScores));

rawScores = sorted(rawScores);
min = 2;
for score in rawScores:
	if(score != 0):
		min = score;
		break;

try:
	print "Min (excluding 0) of students' grades = " + str(min);


	print
	print

	print "Statistics of grades excluding students who did not complete the survey"
	print "Mean of students' grades = " + str(numpy.mean(studentsScores));
	print "Standard Deviation of students' grades = " + str(numpy.std(studentsScores));
	print "Max of students' grades = " + str(max(studentsScores));

	studentsScores = sorted(studentsScores);
	min = 2;
	for score in studentsScores:
		if(score != 0):
			min = score;
			break;

	print "Min (excluding 0) of students' grades = " + str(min);
except:
	print
	print "It seems according to the input.xml and format.csv files, no one completed the survey."
	print "Please check you are using the correct files"
