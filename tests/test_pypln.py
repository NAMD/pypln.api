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
from mock import call, patch, Mock
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
        mocked_get.return_value.json.return_value = \
                {u'count': 1,
                 u'next': None,
                 u'previous': None,
                 u'results': [self.example_corpus]}

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
            "properties": "http://pypln.example.com/documents/1/properties/",
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

    @patch("pypln.api.Corpus.add_document")
    def test_add_multiple_documents_to_corpus(self, mocked_add_document):
        example_document_2 = copy.deepcopy(self.example_document)
        example_document_2['url'] = "http://pypln.example.com/documents/2/",
        results = [self.example_document, example_document_2]
        mocked_add_document.side_effect = results

        corpus = Corpus(**self.example_json)
        result = corpus.add_documents(["content_1", "content_2"],
                    auth=(self.user, self.password))

        expected_calls = [call("content_1", auth=(self.user, self.password)),
            call("content_2", auth=(self.user, self.password))]
        mocked_add_document.assert_has_calls(expected_calls)

        expected = ([self.example_document, example_document_2], [])
        self.assertEqual(result, expected)

    @patch("pypln.api.Corpus.add_document")
    def test_adding_multiple_documents_returns_an_error(self, mocked_add_document):
        results = [self.example_document, RuntimeError]
        mocked_add_document.side_effect = results

        corpus = Corpus(**self.example_json)
        result = corpus.add_documents(["content_1", "content_2"],
                    auth=(self.user, self.password))

        expected_calls = [call("content_1", auth=(self.user, self.password)),
            call("content_2", auth=(self.user, self.password))]
        mocked_add_document.assert_has_calls(expected_calls)

        expected = ([self.example_document], [("content_2", RuntimeError())])
        # How should we test this? The second element of the 'errors' tuple is
        # a different instance of RuntimeError, so it doesn't evaluate as equal
        # to the one raise in the mock. For now I'll just check everything
        # separatedly.
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1][0][0], expected[1][0][0])
        self.assertIsInstance(expected[1][0][1], RuntimeError)

class DocumentTest(unittest.TestCase):

    def setUp(self):
        self.example_json = {
            "owner": "user",
            "corpus": "http://pypln.example.com/corpora/1/",
            "size": 238953,
            "properties": "http://pypln.example.com/documents/1/properties/",
            "url": "http://pypln.example.com/documents/1/",
            "blob": "/example.pdf",
            "uploaded_at": "2013-10-25T17:10:00.000Z"
        }
        self.user = "user"
        self.password = "password"

    def test_instantiate_document_from_json(self):
        document = Document(**self.example_json)

        for k,v in self.example_json.items():
            if k != "properties":
                self.assertEqual(getattr(document, k), v)
        self.assertEqual(document.properties_url,
                            self.example_json['properties'])

    def test_compare_equal_documents(self):
        document_1 = Document(**self.example_json)
        document_2 = Document(**self.example_json)

        self.assertEqual(document_1, document_2)

    def test_compare_documents_with_different_urls(self):
        document_1 = Document(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['url'] = 'http://pypln.example2.com/documents/1/'
        document_2 = Document(**json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_size(self):
        document_1 = Document(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['size'] = 1
        document_2 = Document(**json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_upload_dates(self):
        document_1 = Document(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['uploaded_at'] = '2013-10-29T17:00:00.000Z'
        document_2 = Document(**json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_owners(self):
        document_1 = Document(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['owner'] = "user_2"
        document_2 = Document(**json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_corpora(self):
        document_1 = Document(**self.example_json)

        json_2 = copy.deepcopy(self.example_json)
        json_2['corpus'] = "http://pypln.example.com/corpora/2/"
        document_2 = Document(**json_2)

        self.assertNotEqual(document_1, document_2)

    @patch("requests.get")
    def test_instantiate_document_from_url(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        document = Document.from_url(url, (self.user, self.password))
        auth = (self.user, self.password)

        mocked_get.assert_called_with(url, auth=auth)

        self.assertIsInstance(document, Document)

        for k,v in self.example_json.items():
            if k != "properties":
                self.assertEqual(getattr(document, k), v)
        self.assertEqual(document.properties_url,
                            self.example_json['properties'])

        self.assertEqual(document.auth, auth)

    @patch("requests.get")
    def test_instantiating_document_from_url_fails(self, mocked_get):
        mocked_get.return_value.status_code = 403
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        with self.assertRaises(RuntimeError):
            document = Document.from_url(url, (self.user, self.password))

    @patch("requests.get")
    def test_properties_is_a_list_of_properties(self, mocked_get):
        """ When accessing `document.properties' the user should get a list of
        properties, not a url for the resource."""
        expected_properties = [
            "mimetype",
            "freqdist",
            "average_sentence_repertoire",
            "language",
            "average_sentence_length",
            "sentences",
            "momentum_1",
            "pos",
            "momentum_3",
            "file_metadata",
            "tokens",
            "repertoire",
            "text",
            "tagset",
            "momentum_4",
            "momentum_2"
        ]

        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = {'properties': [
                self.example_json['properties'] + prop + '/'
                for prop in expected_properties]}

        auth = (self.user, self.password)
        document = Document(auth=auth, **self.example_json)

        self.assertEqual(document.properties, expected_properties)
        mocked_get.assert_called_with(self.example_json['properties'], auth=auth)

    @patch("requests.get")
    def test_getting_properties_returns_an_error(self, mocked_get):
        mocked_get.return_value.status_code = 403
        document = Document(auth=("user", "user"), **self.example_json)

        with self.assertRaises(RuntimeError):
            document.properties

    @patch("requests.get")
    def test_get_specific_property(self, mocked_get):
        text = "This is a test file with some test text."

        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = {'value': text}

        auth = (self.user, self.password)
        document = Document(auth=auth, **self.example_json)

        self.assertEqual(document.get_property('text'), text)
        mocked_get.assert_called_with(self.example_json['properties'] + 'text',
                auth=auth)

    def test_getting_specific_property_needs_auth(self):
        document = Document(**self.example_json)
        with self.assertRaises(AttributeError):
            document.get_property('text')

    @patch("requests.get")
    def test_getting_specific_property_returns_an_error(self, mocked_get):
        mocked_get.return_value.status_code = 403
        document = Document(auth=("user", "user"), **self.example_json)

        with self.assertRaises(RuntimeError):
            document.get_property('text')
