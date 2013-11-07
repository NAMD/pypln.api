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

import copy
from mock import patch, Mock
import unittest

from pypln.api import PyPLN, Corpus, Document

class PyPLNTest(unittest.TestCase):
    def setUp(self):
        self.user = "user"
        self.password = "password"
        self.data = {"name": "corpus", "description": "Test Corpus"}
        self.base_url = "http://pypln.example.com"

        self.example_corpus = {'created_at': '2013-10-25T17:00:00.000Z',
                               'description': 'Test Corpus',
                               'documents': [],
                               'name': 'test',
                               'owner': 'user',
                               'url': 'http://pypln.example.com/corpora/1/'}

    @patch("requests.post")
    def test_create_corpus(self, mocked_post):
        mocked_post.return_value.status_code = 201
        mocked_post.return_value.json.return_value = self.example_corpus

        pypln = PyPLN(self.base_url, username=self.user, password=self.password)
        result = pypln.add_corpus(**self.data)

        mocked_post.assert_called_with(self.base_url + "/corpora/",
                                     data=self.data, auth=(self.user, self.password))
        corpus = Corpus(**self.example_corpus)
        self.assertEqual(result, corpus)

    @patch("requests.post")
    def test_corpus_creation_fails(self, mocked_post):
        mocked_post.return_value.status_code = 403
        with self.assertRaises(RuntimeError):
            pypln = PyPLN(self.base_url, username=self.user, password=self.password)
            result = pypln.add_corpus(**self.data)

    @patch("requests.get")
    def test_list_corpora(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = [self.example_corpus]

        pypln = PyPLN(self.base_url, username=self.user, password=self.password)
        result = pypln.corpora()

        mocked_get.assert_called_with(self.base_url + "/corpora/",
                                      auth=(self.user, self.password))

        corpus = Corpus(**self.example_corpus)
        self.assertEqual(result, [corpus])

    @patch("requests.get")
    def test_listing_corpora_fails(self, mocked_get):
        mocked_get.return_value.status_code = 403

        pypln = PyPLN(self.base_url, username=self.user, password=self.password)

        self.assertRaises(RuntimeError, pypln.corpora)

class CorpusTest(unittest.TestCase):

    def setUp(self):
        self.example_json = {'created_at': '2013-10-25T17:00:00.000Z',
                             'description': 'Test Corpus',
                             'documents': [],
                             'name': 'test',
                             'owner': 'user',
                             'url': 'http://pypln.example.com/corpora/1/'}

        self.example_document = {
            "owner": "user",
            "corpus": "http://pypln.example.com/corpora/1/",
            "size": 238953,
            "properties": "http://pypln.example.com/documents/3/properties/",
            "url": "http://pypln.example.com/documents/1/",
            "blob": "/example.pdf",
            "uploaded_at": "2013-10-25T17:10:00.000Z"
        }
        self.user = "user"
        self.password = "password"

    def test_instantiate_corpus_from_json(self):
        corpus = Corpus(**self.example_json)

        for k,v in self.example_json.items():
            self.assertEqual(getattr(corpus, k), v)

    def test_compare_equal_corpora(self):
        corpus_1 = Corpus(**self.example_json)
        corpus_2 = Corpus(**self.example_json)

        self.assertEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_names(self):
        corpus_1 = Corpus(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['name'] = 'other_name'
        corpus_2 = Corpus(**json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_descriptions(self):
        corpus_1 = Corpus(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['description'] = 'Test Corpus 2'
        corpus_2 = Corpus(**json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_creation_dates(self):
        corpus_1 = Corpus(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['created_at'] = '2013-10-29T17:00:00.000Z'
        corpus_2 = Corpus(**json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_owners(self):
        corpus_1 = Corpus(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['owner'] = 'admin'
        corpus_2 = Corpus(**json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_urls(self):
        corpus_1 = Corpus(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['url'] = 'http://pypln.example.com.br/corpora/1/'
        corpus_2 = Corpus(**json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    @patch("requests.get")
    def test_instantiate_corpus_from_url(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        corpus = Corpus.from_url(url, (self.user, self.password))
        auth = (self.user, self.password)

        mocked_get.assert_called_with(url, auth=auth)

        self.assertIsInstance(corpus, Corpus)

        for k, v in self.example_json.items():
            self.assertEqual(getattr(corpus, k), v)

        self.assertEqual(corpus.auth, auth)

    @patch("requests.get")
    def test_instantiating_corpus_from_url_fails(self, mocked_get):
        mocked_get.return_value.status_code = 403
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        with self.assertRaises(RuntimeError):
            corpus = Corpus.from_url(url, (self.user, self.password))

    @patch("requests.post")
    def test_adding_document_to_corpus_requires_auth(self, mocked_post):

        corpus = Corpus(**self.example_json)
        with self.assertRaises(AttributeError):
            corpus.add_document("example.pdf")

        mocked_post.assert_not_called()

        mocked_post.return_value.status_code = 201

        # auth can be set on the constructor
        corpus_2 = Corpus(auth=("user", "passwd"), **self.example_json)
        corpus_2.add_document("example.pdf")
        mocked_post.assert_called()

    @patch("requests.post")
    def test_add_document_to_corpus(self, mocked_post):
        mocked_post.return_value.status_code = 201
        mocked_post.return_value.json.return_value = self.example_document

        corpus = Corpus(**self.example_json)
        result = corpus.add_document("content.",
                    auth=(self.user, self.password))

        # requests takes either a file-like object or a string. Both should
        # work.
        files = {"blob": "content."}
        data = {"corpus": corpus.url}

        mocked_post.assert_called_with("http://pypln.example.com" + "/documents/",
                                     data=data, files=files,
                                     auth=(self.user, self.password))

        self.assertEqual(result, self.example_document)

    @patch("requests.post")
    def test_adding_document_to_corpus_fails(self, mocked_post):
        mocked_post.return_value.status_code = 403

        corpus = Corpus(**self.example_json)
        with self.assertRaises(RuntimeError):
            corpus.add_document("example.pdf", auth=(self.user, self.password))
