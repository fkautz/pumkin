import hashlib
import os
import tarfile

from pumkin.errors import RepositoryExistsError, RepositoryDoesNotExistError


__author__ = 'fkautz'


def filter_pumkin_from_tar(x):
    if '.pumkin' in x.name:
        return None
    return x


class Repository(object):
    @staticmethod
    def create(param):
        pumkin_path = param + "/.pumkin"
        if os.path.isdir(param):
            if not os.path.isdir(pumkin_path):
                os.mkdir(param + "/.pumkin")
                os.mkdir(param + "/.pumkin/images")
            else:
                raise RepositoryExistsError("Repository " + pumkin_path)
        else:
            raise NotADirectoryError(param)

    @staticmethod
    def sync(repo):
        if not Repository.exists(repo):
            raise RepositoryDoesNotExistError(repo)
        metadata = Repository.get_metadata_dir(repo)
        # make tarball in .pumkin/images
        tmp_image = metadata + "/tmp.tar.gz"
        if os.path.exists(tmp_image):
            os.remove(tmp_image)
        with tarfile.open(tmp_image, "w:gz") as tar:
            tar.add(repo, arcname=os.path.basename(repo), filter=filter_pumkin_from_tar)
        m = hashlib.sha1()
        with open(tmp_image, 'rb') as f:
            blob = f.read(1024 * 1024 * 64)
            if blob:
                m.update(blob)
        digest = m.hexdigest()
        os.rename(tmp_image, os.path.join(metadata, "images", digest + ".tar.gz"))
        try:
            with open(os.path.join(metadata, 'COMMITS'), 'r') as f:
                old_commits = f.read()
        except FileNotFoundError:
            old_commits = ""
        with open(os.path.join(metadata, "COMMITS"), "wb") as f:
            if old_commits.strip() != "":
                f.write(str.encode(old_commits + '\n'))
            f.write(str.encode(digest))

    @staticmethod
    def exists(param):
        if os.path.isdir(param):
            if os.path.isdir(param + "/.pumkin"):
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def get_metadata_dir(repo):
        if not Repository.exists(repo):
            raise RepositoryDoesNotExistError
        return repo + "/.pumkin"
