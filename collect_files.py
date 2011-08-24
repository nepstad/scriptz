#!/usr/bin/env python

import os
import argparse
import hashlib
import string
import shutil

def GetFiles(dest, level=0):
    """Get all files under dest

    Returns (flat) list of files with full path

    """

    destHash = hashlib.sha1(os.path.basename(dest)).hexdigest()
    print "%sTraversing %s" % (' '*level, destHash)

    #Get content of folder
    folderContent = ["%s/%s" % (dest, el) for el in os.listdir(dest)]

    #Call self for all subfolders
    subFolders = filter(os.path.isdir, folderContent)
    files = map(lambda x: GetFiles(x, level+1), subFolders)
    files += filter(os.path.isfile, folderContent)

    #Flatten list of files
    filesFlat = []
    for f in files:
        if isinstance(f, list):
            map(filesFlat.append, f)
        else:
            filesFlat.append(f)

    return filesFlat


def GetRenameList(fileList, filePattern):
    """Return a list of tuples, (oldname, newname)

    All files in fileList that matches filePattern (exactly) are scheduled for
    renaming. A list of tuples (oldname, newname) is constructed, where newname
    is the name of the folder in which the file 'oldname' resides. Preserves
    file type ending.

    """

    renameList = []
    for f in fileList:
        pathElems = string.split(f, sep=os.path.sep)
        oldName = pathElems[-1]
        newName = pathElems[-2]

        fnameExt = oldName.split(".")[-1]
        newName += ".%s" % fnameExt

        if oldName == filePattern:
            renameList.append((f, newName))

    return renameList


def RenameAndCollect(renameList, collectDest):
    """Rename and copy files to folder 'collectDest'

    renameList is a list of tuples (oldname, newname).

    """
    assert os.path.exists(collectDest), "Collect destination does not exists!"
    print "Renaming and collecting files..."
    for old, new in renameList:
        newAbsPath = "%s/%s" % (collectDest, new)
        shutil.copy(old, newAbsPath)
    print "   done!"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect matching files in subfolders and rename them")
    parser.add_argument("src", type=str,
        help="Perform collection+rename on files under src")
    parser.add_argument("dest", type=str,
        help="Collect files in folder dest")
    parser.add_argument("filename_pattern", type=str,
        help="All files matching this patters are collected and renamed")

    #Parse them args
    args = parser.parse_args()

    #Get all files at given destination
    src = os.path.abspath(args.src)
    files = GetFiles(src)
    print
    print "Found %i files" % len(files)

    renameList = GetRenameList(files, args.filename_pattern)
    print "Renaming %i files" % len(renameList)
    RenameAndCollect(renameList, args.dest)
