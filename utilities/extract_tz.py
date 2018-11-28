import sys
import tarfile
from os import listdir
from os.path import isfile, join


def extract(tFile, opDir):
    tar = tarfile.open(tFile, "r:gz")
    tar.extractall(opDir)
    tar.close()
    print("done {0} => {1}".format(tFile, opDir))


def main():
    iDir = sys.argv[1]
    oDir = sys.argv[2]
    files = [f for f in listdir(iDir) if isfile(join(iDir, f))]
    for f in files:
        name = f.strip().split('.')[0]
        extractDir = oDir + "/" + name
        tarfilePath = iDir + "/" + f
        extract(tarfilePath, extractDir)


if __name__ == "__main__":
    main()
