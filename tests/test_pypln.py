# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from mock import patch, Mock
import unittest

from pypln.api import PyPLN, Corpus, Document

class PyPLNCorpusTest(unittest.TestCase):
    def setUp(self):
        self.user = "user"
        self.password = "password"
        self.data = {"name": "corpus", "description": "Test Corpus"}
        self.base_url = "http://pypln.example.com"

    @patch("requests.post")
    def test_create_corpus(self, mocked_post):
        mocked_post.return_value.status_code = 201

        pypln = PyPLN(self.base_url, username=self.user, password=self.password)
        result = pypln.add_corpus(**self.data)

        mocked_post.assert_called_with(self.base_url + "/corpora/",
                                     data=self.data, auth=(self.user, self.password))
        # For now, we return True when the corpus is created. Later
        # we'll probably return a Corpus object (if it exists)
        self.assertEqual(result, True)

    @patch("requests.post")
    def test_corpus_creation_fails(self, mocked_post):
        mocked_post.return_value.status_code = 400
        with self.assertRaises(RuntimeError):
            pypln = PyPLN("http://pypln.example.com", username=self.user, password=self.password)
            result = pypln.add_corpus(**self.data)
