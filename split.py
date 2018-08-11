#!/usr/bin/python3
import os
import sys
import argparse
from colorama import *


def parse_args(args):
    """ Create the arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="infile", help="File to split")
    parser.add_argument("-s", dest="size", help="Filesize in kb (default 50000kb)", type=int, default=100000)

    if len(sys.argv) < 2:
        parser.print_help()
    
    argsp = parser.parse_args(args)
    if not argsp.infile:
        parser.print_help()
    return argsp

def new_file(infile, id=""):
    """
    Creates a new file based on the infile
    New name = infile + filenumber + infile's extension
    """
    if not infile:
        raise ValueError("Infile in new_file() cannot be empty.")
    filename, fileExtension = os.path.splitext(infile)
    filePath = os.path.dirname(os.path.realpath(__file__))
    newName = "{}{}{}".format(filename, str(id), fileExtension)
    try:
        file = open(os.path.join(filePath, newName), "wb")
    except IOError:
        raise IOError("Failed on creating new file '{0}'".format(newName))
    return file

def getChunk(fh, size):
    """
    Returns a buffer with a chunk of the given file
    """
    if not os.path.isfile(fh.name):
        raise FileExistsError("Cannot find the file '{}'".format(fh.name))
    
    buffer = b""
    try:
        # Get chunk
        buffer = fh.read(size)

        # Get the rest of the line
        byte = b""
        while buffer[-1:] != b'\n':
            chunk = fh.read(1)
            if not chunk:
                break
            buffer += chunk
        return buffer

    except IOError:
        raise IOError("Error reading from file '{0}' in getChunk()".format(fh.name))

def calc(fh, size):
    """
    Calculates chunk size and number of times we must load chunks into memory
    """
    try:
        fileSize = os.path.getsize(fh.name)
        turns = fileSize // size
        chunkSize = fileSize // turns
        return turns, chunkSize
    except IOError:
        raise IOError("Error calculating chunk size in calc()")

def getFileSize(file):
    return os.path.getsize(file) / 1024.0

def split(inFile, size):
    with open(inFile, "rb") as fh:
        turns, chunkSize = calc(fh, size)
        for i in range(turns):
            output = new_file(inFile, i)
            output.write(getChunk(fh, chunkSize))
            output.close()

            print(Fore.GREEN + "[+] " + Style.RESET_ALL + "Saving file {0} with total size of {1:.3f} kb".format(output.name, getFileSize(output.name)))
        
    print("\n" + Fore.BLUE + "[i] " + Style.RESET_ALL + "Done.")

if __name__ == "__main__":
    init()
    options = parse_args(sys.argv[1:])

    if os.path.isfile(options.infile):
        split(options.infile, options.size)
    else:
        raise FileNotFoundError("Cannot find the file '{}'".format(options.infile))