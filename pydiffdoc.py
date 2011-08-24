import pysvn
import random
import os
import sys
import difflib
import string

def DiffDoc(wcPath, tmpPath, file, revision, diffFile="diff_file.txt"):
	"""
	This function performs a diff on two Word documents managed by Subversion,
	one in a local working copy and one in the repository.

	    wcPath: path to working copy
	    tmpPath: path to directory where temporary files are stored
	    file: the name of the Word document to diff, relative to wcPath
	    revision: which revision to compare with in the repository
	    diffFile: output file where the diff is stored

	"""

	#Add trailing "/" if needed
	wcPath = wcPath.rstrip("/")
	wcPath += "/"
	tmpPath = tmpPath.rstrip("/")
	tmpPath += "/"

	#External programs and settings
	catdoc = "/usr/bin/catdoc"

	#Create pysvn client object
	client = pysvn.Client()

	#Get repository url associated with working copy
	repoUrl = client.info(wcPath)["url"]

	#Export tmp copy of Word document from desired revision
	print "Exporting repository file..."
	sys.stdin.flush()
	tmpFile = tmpPath + RandomString(10) + "_repo.doc"
	repoFile = repoUrl + "/" + file
	repoFile = repoFile.replace(" ", "%20")
	print repoFile
	client.export(repoFile, tmpFile, revision = revision)

	#Extract pure text from word docs
	print "Extracting pure text from Word documents"
	sys.stdin.flush()
	tmpDoc1 = tmpPath + RandomString(10) + "_repofile.txt"
	tmpDoc2 = tmpPath + RandomString(10) + "_wcfile.txt"
	cmd = "%s %s >> %s" % (catdoc, repr(tmpFile), repr(tmpDoc1))
	print cmd
	os.system(cmd)
	cmd = "%s %s >> %s" % (catdoc, repr(wcPath+file), repr(tmpDoc2))
	print cmd
	os.system(cmd)

	#Get diff of the two files
	print "Performing diff..."
	sys.stdin.flush()
	fh = open(tmpDoc1, "r")
	txt1 = fh.readlines()
	fh.close()
	fh = open(tmpDoc2, "r")
	txt2 = fh.readlines()
	fh.close()
	diff = difflib.unified_diff(txt1, txt2)

	#Clean up
	os.system("rm %s %s %s" % (tmpDoc1, tmpDoc2, tmpFile))

	#Save the diff
	fh = open(diffFile, "w")
	for line in diff:
		fh.write(line)
	fh.close()


def RandomString(length):
	"""
	Return string of length 'length' with random alphabetic
	characters.
	"""
	random.seed(None)
	stringSeq = [chr(i) for i in range(97,122)]
	outStr = ""
	for i in range(length):
		outStr += random.choice(stringSeq)

	return outStr


class RevisionTypes:
	HEAD = pysvn.Revision(pysvn.opt_revision_kind.head)
	BASE = pysvn.Revision(pysvn.opt_revision_kind.head)
	NUM = lambda self, rev : pysvn.Revision(pysvn.opt_revision_kind.number, rev)



if len(sys.argv) == 4:
	wcPath = sys.argv[1]
	tmpPath = sys.argv[2]
	file = sys.argv[3]
	revision = eval(sys.argv[4])
	DiffDoc(wcPath, tmpPath, file, revision)
