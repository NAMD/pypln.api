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

import urllib
import urlparse
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
    DOCUMENTS_PAGE = '/documents/'

    def __init__(self, *args, **kwargs):
        self.auth = None
        for key, value in kwargs.items():
            setattr(self, key, value)

        splited_url = urlparse.urlsplit(self.url)
        self.base_url = "{}://{}".format(splited_url.scheme, splited_url.netloc)

    def __repr__(self):
        return '<Corpus: {} ({})>'.format(self.name, self.url)

    def __eq__(self, other):
        return (self.name == other.name) and \
                (self.description == other.description) and \
                (self.created_at == other.created_at) and \
                (self.owner == other.owner) and \
                (self.url == other.url)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))

    @classmethod
    def from_url(cls, url, auth):
        result = requests.get(url, auth=auth)
        if result.status_code == 200:
            return cls(auth=auth, **result.json())
        else:
            raise RuntimeError("Getting corpus details failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def add_document(self, file_object, auth=None):
        '''Add a document to this corpus'''
        # update credentials if auth is provided
        if auth is not None:
            self.auth = auth

        if self.auth is None:
            raise AttributeError("You need to determine your credentials in "
                    "order to add documents.")

        documents_url = urllib.basejoin(self.base_url, self.DOCUMENTS_PAGE)
        data = {"corpus": self.url}
        files = {"blob": file_object}
        result = requests.post(documents_url, data=data, files=files,
                    auth=self.auth)
        if result.status_code == 201:
            return result.json()
        else:
            raise RuntimeError("Corpus creation failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def add_documents(self, file_objects, filenames):
        '''Add more than one document using the same API call'''
        pass

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
            return Corpus(**result.json())
        else:
            raise RuntimeError("Corpus creation failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def corpora(self):
        '''Return list of corpora'''
        result = requests.get(self.base_url + self.CORPORA_PAGE, auth=self.auth)
        if result.status_code == 200:
            return [Corpus(**corp) for corp in result.json()]
        else:
            raise RuntimeError("Listing corpora failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))
