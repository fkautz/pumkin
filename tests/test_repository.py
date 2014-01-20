import hashlib
import os
import tempfile
import unittest
import time

from pumkin.errors import RepositoryExistsError, RepositoryDoesNotExistError
from pumkin.repository import Repository


__author__ = 'fkautz'


class TestUtils(object):
    @staticmethod
    def create_test_dir() -> tempfile.TemporaryDirectory:
        tempdir = tempfile.TemporaryDirectory("pumkin")
        with open(tempdir.name + "/hello.txt", 'w'):
            pass
        return tempdir

    @staticmethod
    def destroy_test_dir(repo):
        repo.cleanup()


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.repo = TestUtils.create_test_dir()

    def tearDown(self):
        TestUtils.destroy_test_dir(self.repo)
        self.repo = None

    def test_create_repository_non_existing_fails_with_exception(self):
        with self.assertRaises(NotADirectoryError):
            Repository.create('/tmp/not_a_pumkin_repo')

    def test_create_repository(self):
        Repository.create(self.repo.name)
        self.assertTrue(os.path.isdir(self.repo.name + "/.pumkin"), "pumkin dir not created")
        self.assertTrue(os.path.isdir(self.repo.name + "/.pumkin/images"), "pumkin images dir not created")

    def test_create_repository_on_existing_repository_fails_with_exception(self):
        Repository.create(self.repo.name)
        with self.assertRaises(RepositoryExistsError):
            Repository.create(self.repo.name)

    def test_repository_returns_false_without_repo(self):
        self.assertFalse(Repository.exists(self.repo.name), "Repository.exists should return false")

    def test_repository_returns_false_with_repo(self):
        Repository.create(self.repo.name)
        self.assertTrue(Repository.exists(self.repo.name), "Repository.exists should return true")

    def test_sync_without_repository(self):
        with self.assertRaises(RepositoryDoesNotExistError):
            Repository.sync(self.repo.name)

    def test_sync_with_no_previous_syncs(self):
        Repository.create(self.repo.name)
        repo = Repository.get_metadata_dir(self.repo.name) + "/images"
        dirs_before = os.listdir(repo)
        Repository.sync(self.repo.name)
        dirs_after = os.listdir(repo)
        self.assertGreater(len(dirs_after), len(dirs_before))

    def test_sync_with_previous_syncs(self):
        Repository.create(self.repo.name)
        repo = Repository.get_metadata_dir(self.repo.name) + "/images"
        dirs_before_sync = os.listdir(repo)
        Repository.sync(self.repo.name)
        dirs_after_first_sync = os.listdir(repo)
        self.assertGreater(len(dirs_after_first_sync), len(dirs_before_sync))
        with open(self.repo.name + '/hello2.txt', 'w'):
            pass
        time.sleep(.01)  # prevent name collision in sync
        Repository.sync(self.repo.name)
        dirs_after_second_sync = os.listdir(repo)
        self.assertGreater(len(dirs_after_second_sync), len(dirs_after_first_sync))
        with open(self.repo.name + '/hello3.txt', 'w'):
            pass
        time.sleep(.01)  # prevent name collision in sync
        Repository.sync(self.repo.name)
        dirs_after_third_sync = os.listdir(repo)
        self.assertGreater(len(dirs_after_third_sync), len(dirs_after_second_sync))

    def test_sync_image_name_is_sha1sum(self):
        Repository.create(self.repo.name)
        images_directory = Repository.get_metadata_dir(self.repo.name) + "/images"
        Repository.sync(self.repo.name)
        image_file = os.listdir(images_directory)[0]
        with open(os.path.join(images_directory, image_file), 'rb') as f:
            blob = f.read()
        summer = hashlib.sha1()
        summer.update(blob)
        digest = summer.hexdigest()
        self.assertEquals(digest + ".tar.gz", image_file)

    def test_sync_image_head_tagged(self):
        pass

    def test_sync_image_creates_manifest(self):
        pass

    def test_get_metadata_dir_throws_exception_if_not_repo(self):
        with self.assertRaises(RepositoryDoesNotExistError):
            Repository.get_metadata_dir(self.repo.name)

    def test_get_metadata_dir_returns(self):
        Repository.create(self.repo.name)
        self.assertEquals(self.repo.name + "/.pumkin", Repository.get_metadata_dir(self.repo.name))
