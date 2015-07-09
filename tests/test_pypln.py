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

import base64
import unittest

try:
    from unittest.mock import call, patch, Mock, mock_open
except ImportError:
    from mock import call, patch, Mock, mock_open

import requests

from pypln.api import PyPLN, Corpus, Document, __version__


class PyPLNTest(unittest.TestCase):
    def setUp(self):
        self.user = "user"
        self.password = "password"
        self.auth = (self.user, self.password)
        self.corpus_data = {"name": "corpus", "description": "Test Corpus"}
        self.base_url = "http://pypln.example.com"

        self.example_corpus = {'created_at': '2013-10-25T17:00:00.000Z',
                               'description': 'Test Corpus',
                               'documents': [],
                               'name': 'test',
                               'owner': 'user',
                               'url': 'http://pypln.example.com/corpora/1/'}
        self.example_document_1 = \
                {
                 'owner': 'user',
                 'corpus': 'http://pypln.example.com/corpora/42/',
                 'size': 42,
                 'properties': 'http://pypln.example.com/documents/123/properties',
                 'url': 'http://pypln.example.com/documents/123/',
                 'blob': '/test_1.txt',
                 'uploaded_at': '2013-10-25T17:00:00.000Z',
                 }
        self.example_document_2 = \
                {
                 'owner': 'user',
                 'corpus': 'http://pypln.example.com/corpora/42/',
                 'size': 43,
                 'properties': 'http://pypln.example.com/documents/124/properties',
                 'url': 'http://pypln.example.com/documents/124/',
                 'blob': '/test_2.txt',
                 'uploaded_at': '2013-10-25T17:00:01.000Z',
                 }

    def test_basic_auth_is_correctly_set(self):
        credentials = (self.user, self.password)
        pypln = PyPLN(self.base_url, credentials)
        self.assertEqual(pypln.session.auth, credentials)

    def test_token_auth_is_correctly_set(self):
        credentials = 'ea92019a4bdf5d1c122c58b53de3e8d36fe9ae6a'
        pypln = PyPLN(self.base_url, credentials)
        self.assertEqual(pypln.session.headers['Authorization'],
                'Token {}'.format(credentials))

    def test_raise_an_error_if_auth_is_not_str_or_tuple(self):
        """If the `auth` argument is not a tuple (for basic auth) or a string
        (for token auth), an error should be raised."""
        with self.assertRaises(TypeError):
            pypln = PyPLN(self.base_url, 1)

    def test_is_sending_pyplnapi_version_as_user_agent(self):
        pypln = PyPLN(self.base_url, (self.user, self.password))
        self.assertIn('pypln.api/{}'.format(__version__),
                pypln.session.headers['User-Agent'])

    @patch("requests.Session.post")
    def test_create_corpus(self, mocked_post):
        mocked_post.return_value.status_code = 201
        mocked_post.return_value.json.return_value = self.example_corpus

        pypln = PyPLN(self.base_url, (self.user, self.password))
        result = pypln.add_corpus(**self.corpus_data)

        mocked_post.assert_called_with(self.base_url + "/corpora/",
                                       data=self.corpus_data)
        for key, value in self.example_corpus.items():
            self.assertEqual(value, getattr(result, key))

        # Corpus objects should link `session` object from PyPLN
        self.assertIs(result.session, pypln.session)

    @patch("requests.Session.post")
    def test_corpus_creation_fails_if_wrong_auth(self, mocked_post):
        mocked_post.return_value.status_code = 403
        with self.assertRaises(RuntimeError):
            pypln = PyPLN(self.base_url, ('wrong_user', 'my_precious'))
            result = pypln.add_corpus(**self.corpus_data)

    @patch("requests.Session.get")
    def test_list_corpora(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = \
                {u'count': 1,
                 u'next': None,
                 u'previous': None,
                 u'results': [self.example_corpus]}

        pypln = PyPLN(self.base_url, (self.user, self.password))
        result = pypln.corpora()

        mocked_get.assert_called_with(self.base_url + "/corpora/")

        for key, value in self.example_corpus.items():
            self.assertEqual(value, getattr(result[0], key))

        # Corpus objects should link `session` object from PyPLN
        self.assertIs(result[0].session, pypln.session)

    @patch("requests.Session.get")
    def test_listing_corpora_fails_if_wrong_auth(self, mocked_get):
        mocked_get.return_value.status_code = 403

        pypln = PyPLN(self.base_url, ('wrong_user', 'my_precious'))

        self.assertRaises(RuntimeError, pypln.corpora)

    @patch("requests.Session.get")
    def test_list_documents(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = \
                {u'count': 2,
                 u'next': None,
                 u'previous': None,
                 u'results': [self.example_document_1,
                              self.example_document_2]}

        pypln = PyPLN(self.base_url, (self.user, self.password))
        result = pypln.documents()

        mocked_get.assert_called_with(self.base_url + "/documents/")

        retrieved_document_1 = result[0]
        retrieved_document_2 = result[1]

        for key, value in self.example_document_1.items():
            # `properties` is a method on `Document` class, so replacing with
            # `properties_url` to test each key/value
            if key == 'properties':
                key = 'properties_url'
            self.assertEqual(value, getattr(retrieved_document_1, key))
        for key, value in self.example_document_2.items():
            # `properties` is a method on `Document` class, so replacing with
            # `properties_url` to test each key/value
            if key == 'properties':
                key = 'properties_url'
            self.assertEqual(value, getattr(retrieved_document_2, key))

        # Document objects should link `session` object from PyPLN
        self.assertIs(retrieved_document_1.session, pypln.session)
        self.assertIs(retrieved_document_2.session, pypln.session)


    @patch("requests.Session.get")
    def test_listing_documents_fails_if_wrong_auth(self, mocked_get):
        mocked_get.return_value.status_code = 403

        pypln = PyPLN(self.base_url, ('wrong_user', 'my_precious'))

        self.assertRaises(RuntimeError, pypln.documents)

    #TODO: test list documents in more than one page

    #TODO: test list corpora in more than one page


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
        self.auth = (self.user, self.password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def test_instantiate_corpus_from_json(self):
        corpus = Corpus(session=None, **self.example_json)

        for k,v in self.example_json.items():
            self.assertEqual(getattr(corpus, k), v)

    def test_compare_equal_corpora(self):
        corpus_1 = Corpus(session=None, **self.example_json)
        corpus_2 = Corpus(session=None, **self.example_json)

        self.assertEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_names(self):
        corpus_1 = Corpus(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['name'] = 'other_name'
        corpus_2 = Corpus(session=None, **json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_descriptions(self):
        corpus_1 = Corpus(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['description'] = 'Test Corpus 2'
        corpus_2 = Corpus(session=None, **json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_creation_dates(self):
        corpus_1 = Corpus(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['created_at'] = '2013-10-29T17:00:00.000Z'
        corpus_2 = Corpus(session=None, **json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_owners(self):
        corpus_1 = Corpus(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['owner'] = 'admin'
        corpus_2 = Corpus(session=None, **json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    def test_compare_corpora_with_different_urls(self):
        corpus_1 = Corpus(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['url'] = 'http://pypln.example.com.br/corpora/1/'
        corpus_2 = Corpus(session=None, **json_2)

        self.assertNotEqual(corpus_1, corpus_2)

    @patch("requests.Session.get")
    def test_instantiate_corpus_from_url(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        corpus = Corpus.from_url(url, self.auth)

        mocked_get.assert_called_with(url)

        self.assertIsInstance(corpus, Corpus)

        for k, v in self.example_json.items():
            self.assertEqual(getattr(corpus, k), v)

        self.assertEqual(corpus.session.auth, self.auth)

    @patch("requests.Session.get")
    def test_instantiating_corpus_from_url_fails(self, mocked_get):
        mocked_get.return_value.status_code = 403
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        with self.assertRaises(RuntimeError):
            corpus = Corpus.from_url(url, ('wrong_user', 'my_precious'))

    @patch("requests.Session.post")
    def test_adding_document_to_corpus_fails(self, mocked_post):
        mocked_post.return_value.status_code = 403

        session = requests.Session()
        session.auth = ('wrong_user', 'my_precious')
        corpus = Corpus(session=session, **self.example_json)
        with self.assertRaises(RuntimeError):
            corpus.add_document("example.pdf")

    @patch("requests.Session.post")
    def test_add_document_to_corpus(self, mocked_post):
        mocked_post.return_value.status_code = 201
        mocked_post.return_value.json.return_value = self.example_document

        corpus = Corpus(session=self.session, **self.example_json)
        result = corpus.add_document("content.")

        # requests takes either a file-like object or a string. Both should
        # work.
        files = {"blob": "content."}
        data = {"corpus": corpus.url}

        mocked_post.assert_called_with("http://pypln.example.com/documents/",
                                       data=data, files=files)

        self.assertIs(type(result), Document)

        for key, value in self.example_document.items():
            if key == 'properties':
                key = 'properties_url'
            self.assertEqual(value, getattr(result, key))

    @patch("requests.Session.post")
    def test_add_multiple_documents_to_corpus(self, mocked_post):
        example_document_2 = self.example_document.copy()
        example_document_2['url'] = "http://pypln.example.com/documents/2/"

        mock1, mock2 = Mock(), Mock()
        mock1.status_code = mock2.status_code = 201
        mock1.json.return_value = self.example_document
        mock2.json.return_value = example_document_2
        mocked_post.side_effect = [mock1, mock2]

        corpus = Corpus(session=self.session, **self.example_json)
        result = corpus.add_documents(["content_1", "content_2"])
        documents, errors = result

        self.assertEqual(errors, [])

        self.assertIs(type(documents[0]), Document)
        self.assertIs(type(documents[1]), Document)

        for key, value in self.example_document.items():
            if key == 'properties':
                key = 'properties_url'
            self.assertEqual(value, getattr(documents[0], key))
        for key, value in example_document_2.items():
            if key == 'properties':
                key = 'properties_url'
            self.assertEqual(value, getattr(documents[1], key))

    @patch("pypln.api.Corpus.add_document")
    def test_adding_multiple_documents_returns_an_error(self, mocked_add_document):
        results = [self.example_document, RuntimeError]
        mocked_add_document.side_effect = results

        corpus = Corpus(session=self.session, **self.example_json)
        result = corpus.add_documents(["content_1", "content_2"])

        expected_calls = [call("content_1"), call("content_2")]
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
        self.auth = (self.user, self.password)
        self.session = requests.Session()
        self.session.auth = self.auth

    def test_instantiate_document_from_json(self):
        document = Document(session=self.session, **self.example_json)

        for k,v in self.example_json.items():
            if k != "properties":
                self.assertEqual(getattr(document, k), v)
        self.assertIs(document.session, self.session)
        self.assertEqual(document.properties_url,
                         self.example_json['properties'])

    def test_compare_equal_documents(self):
        document_1 = Document(session=None, **self.example_json)
        document_2 = Document(session=self.session, **self.example_json)
        # `session` object (that holds authentication information) does not
        # matter for equality of `Document` objects

        self.assertEqual(document_1, document_2)

    def test_compare_documents_with_different_urls(self):
        document_1 = Document(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['url'] = 'http://pypln.example2.com/documents/1/'
        document_2 = Document(session=None, **json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_sizes(self):
        document_1 = Document(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['size'] = 1
        document_2 = Document(session=None, **json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_upload_dates(self):
        document_1 = Document(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['uploaded_at'] = '2013-10-29T17:00:00.000Z'
        document_2 = Document(session=None, **json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_owners(self):
        document_1 = Document(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['owner'] = "user_2"
        document_2 = Document(session=None, **json_2)

        self.assertNotEqual(document_1, document_2)

    def test_compare_documents_with_different_corpora(self):
        document_1 = Document(session=None, **self.example_json)

        json_2 = self.example_json.copy()
        json_2['corpus'] = "http://pypln.example.com/corpora/2/"
        document_2 = Document(session=None, **json_2)

        self.assertNotEqual(document_1, document_2)

    @patch("requests.Session.get")
    def test_instantiate_document_from_url(self, mocked_get):
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        document = Document.from_url(url, self.auth)

        mocked_get.assert_called_with(url)

        self.assertIsInstance(document, Document)

        for k,v in self.example_json.items():
            if k != "properties":
                self.assertEqual(getattr(document, k), v)
        self.assertEqual(document.properties_url,
                         self.example_json['properties'])

        self.assertEqual(document.session.auth, self.auth)

    @patch("requests.Session.get")
    def test_instantiating_document_from_url_fails(self, mocked_get):
        mocked_get.return_value.status_code = 403
        mocked_get.return_value.json.return_value = self.example_json

        url = self.example_json['url']

        with self.assertRaises(RuntimeError):
            document = Document.from_url(url, ('wrong_user', 'my_precious'))

    @patch("requests.Session.get")
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

        document = Document(session=self.session, **self.example_json)

        self.assertEqual(document.properties, expected_properties)
        mocked_get.assert_called_with(self.example_json['properties'])

    @patch("requests.Session.get")
    def test_getting_properties_returns_an_error(self, mocked_get):
        mocked_get.return_value.status_code = 403
        session = requests.Session()
        session.auth = ('wrong_user', 'my_precious')
        document = Document(session=session, **self.example_json)

        with self.assertRaises(RuntimeError):
            document.properties

    @patch("requests.Session.get")
    def test_get_specific_property(self, mocked_get):
        text = "This is a test file with some test text."

        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = {'value': text}

        document = Document(session=self.session, **self.example_json)

        self.assertEqual(document.get_property('text'), text)
        mocked_get.assert_called_with(self.example_json['properties'] + 'text')

    @patch("requests.Session.get")
    def test_getting_specific_property_returns_an_error(self, mocked_get):
        mocked_get.return_value.status_code = 403
        session = requests.Session()
        session.auth = ('wrong_user', 'my_precious')
        document = Document(session=session, **self.example_json)

        with self.assertRaises(RuntimeError):
            document.get_property('text')

    @patch("requests.Session.get")
    def test_download_wordcloud(self, mocked_get):
        png = "This is not really a png.\n".encode('ascii')
        encoded_png = base64.b64encode(png)

        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = {'value': encoded_png}

        document = Document(session=self.session, **self.example_json)

        import sys
        if sys.version < '3':
            builtins_module = '__builtin__'
        else:
            builtins_module = 'builtins'

        m = mock_open()
        with patch('{}.open'.format(builtins_module), m, create=True):
            document.download_wordcloud('test.png')

        m.assert_called_once_with('test.png', 'w')
        handle = m()
        handle.write.assert_called_once_with(png.decode('ascii'))
        mocked_get.assert_called_with(self.example_json['properties'] +
                'wordcloud')
