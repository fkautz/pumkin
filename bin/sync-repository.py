import sys

from pumkin.repository import Repository


__author__ = 'fkautz'


def main(args):
    if len(args) == 1:
        Repository.sync(args[0])


if __name__ == "__main__":
    main(sys.argv[1:])
