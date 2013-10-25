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

'''Implements a Python-layer to access PyPLN's API through HTTP'''

import requests

__version__ = '0.1.1'

CORPUS_URL = '{}/corpora/{}'

class Document(object):
    '''Class that represents a Document in PyPLN'''
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        corpora = ', '.join([repr(corpus) for corpus in self.corpora])
        return '<Document: {} ({})>'.format(self.filename, corpora)

    def __eq__(self, other):
        return type(self) == type(other) and \
               self.corpora == other.corpora and \
               self.filename == other.filename

    def __hash__(self):
        return hash(repr(self))

class Corpus(object):
    '''Class that represents a Corpus in PyPLN'''

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<Corpus: {} ({})>'.format(self.name, self.slug)

    def __eq__(self, other):
        return type(self) == type(other) and \
               self.pypln.base_url == other.pypln.base_url and \
               self.slug == other.slug

    def __hash__(self):
        return hash(repr(self))

    def add_document(self, file_object, filename):
        '''Add a document to this corpus'''
        response = self.pypln._session.get(self.url)
        csrf = get_csrf(response.text)
        data = {'csrfmiddlewaretoken': csrf}
        files = {'blob': (filename, file_object)}
        response = self.pypln._session.post(self.url, data=data, files=files)
        return Document(filename=filename, corpora=[self]) #TODO: slug, URL

    def add_documents(self, file_objects, filenames):
        '''Add more than one document using the same API call'''
        response = self.pypln._session.get(self.url)
        csrf = get_csrf(response.text)
        data = {'csrfmiddlewaretoken': csrf}
        files = [('blob', (filename, file_object))
                 for filename, file_object in zip(filenames, file_objects)]
        response = self.pypln._session.post(self.url, data=data, files=files)
        return [Document(filename=filename, corpora=[self])
                for filename in filenames] # TODO: slug, URL

    def documents(self):
        '''List documents on this corpus'''
        url = CORPUS_URL.format(self.pypln.base_url, self.slug)
        response = self.pypln._session.get(url)
        documents = []
        for document in extract_documents_from_html(response.text):
            document['corpora'] = [self]
            documents.append(Document(**document))
        return documents

class PyPLN(object):
    """
    Class to connect to PyPLN's API and execute some actions
    """
    CORPORA_PAGE = '/corpora/'

    def __init__(self, base_url, username, password):
        """
        Initialize the API object, setting the base URL for the REST
        API, as well as the username and password to be used.
        """
        self.base_url = base_url
        self.auth = username, password

    def add_corpus(self, name, description):
        '''Add a corpus to your account'''
        corpora_url = self.base_url + self.CORPORA_PAGE
        data = {'name': name, 'description': description}
        result = requests.post(corpora_url, data=data, auth=self.auth)
        if result.status_code == 201:
            return result.json()
        else:
            raise RuntimeError("Corpus creation failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def corpora(self):
        '''Return list of corpora'''
        result = requests.get(self.base_url + self.CORPORA_PAGE, auth=self.auth)
        if result.status_code == 200:
            return result.json()
        else:
            raise RuntimeError("Listing corpora failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))
