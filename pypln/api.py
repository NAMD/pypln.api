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

def get_session_with_credentials(credentials):
    session = requests.Session()
    if isinstance(credentials, tuple):
        session.auth = credentials
    elif isinstance(credentials, str):
        session.headers.update(
            {'Authorization': 'Token {}'.format(credentials)})
    else:
        raise TypeError("`credentials` must be a tuple (for HTTP Basic authentication) or a string (for Token authentication).")

    return session


class Document(object):
    '''Class that represents a Document in PyPLN'''
    def __init__(self, session, *args, **kwargs):
        self.session = session
        for key, value in kwargs.items():
            # The `properties' attr should be the content of the resource under
            # /properties/, not it's url. So we save the url here and retrieve
            # the list of available properties when the user accesses it.
            if key == "properties":
                self.properties_url = value
            else:
                setattr(self, key, value)

    def __repr__(self):
        return '<Document: {} ({})>'.format(self.blob, self.url)

    def __eq__(self, other):
        # The URL is supposed to be unique, so it should be enough to compare
        # two documents
        return (self.url == other.url) and \
                (self.size == other.size) and \
                (self.uploaded_at == other.uploaded_at) and \
                (self.owner == other.owner) and \
                (self.corpus == other.corpus)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))

    @classmethod
    def from_url(cls, url, credentials):
        session = get_session_with_credentials(credentials)
        result = session.get(url)
        if result.status_code == 200:
            return cls(session=session, **result.json())
        else:
            raise RuntimeError("Getting document details failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def get_property(self, prop):
        url = urlparse.urljoin(self.properties_url, prop)
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()['value']
        else:
            raise RuntimeError("Getting property {} failed with status "
                               "{}. The response was: '{}'".format(prop,
                                   response.status_code, response.text))

    @property
    def properties(self):
        response = self.session.get(self.properties_url)
        if response.status_code == 200:
            properties = []
            for prop in response.json()['properties']:
                properties.append(prop.replace(self.properties_url, ''))

            # There should be a better way to do this.
            properties = [prop.split(self.properties_url)[1].replace('/', '')
                    for prop in response.json()['properties']]

            return properties
        else:
            raise RuntimeError("Getting document properties failed with status "
                               "{}. The response was: '{}'".format(response.status_code,
                                response.text))


class Corpus(object):
    '''Class that represents a Corpus in PyPLN'''
    DOCUMENTS_PAGE = '/documents/'

    def __init__(self, session, *args, **kwargs):
        ''' Initializes a Corpus class

        `session` must be `requests.Session` object with authentication data
        '''
        self.session = session
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
    def from_url(cls, url, credentials):
        session = get_session_with_credentials(credentials)
        result = session.get(url)
        if result.status_code == 200:
            return cls(session=session, **result.json())
        else:
            raise RuntimeError("Getting corpus details failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def add_document(self, document):
        '''
        Add a document to this corpus

        `document' is passed to `requests.post', so it can be a file-like
        object, a string (that will be sent as the file content) or a tuple
        containing a filename followed by any of these two options.
        '''

        documents_url = urllib.basejoin(self.base_url, self.DOCUMENTS_PAGE)
        data = {"corpus": self.url}
        files = {"blob": document}
        result = self.session.post(documents_url, data=data, files=files)
        if result.status_code == 201:
            return result.json()
        else:
            raise RuntimeError("Corpus creation failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def add_documents(self, documents):
        '''
        Adds more than one document using the same API call

        Returns two lists: the first one contains the successfully uploaded
        documents, and the second one tuples with documents that failed to be
        uploaded and the exceptions raised.
        '''
        result, errors = [], []
        for document in documents:
            try:
                result.append(self.add_document(document))
            except RuntimeError as exc:
                errors.append((document, exc))

        return result, errors

class PyPLN(object):
    """
    Class to connect to PyPLN's API and execute some actions
    """
    CORPORA_PAGE = '/corpora/'
    DOCUMENTS_PAGE = '/documents/'

    def __init__(self, base_url, credentials):
        """
        Initialize the API object, setting the base URL for the REST
        API, as well as the username and password to be used.
        """
        self.base_url = base_url
        self.session = get_session_with_credentials(credentials)

    def add_corpus(self, name, description):
        '''Add a corpus to your account'''
        corpora_url = self.base_url + self.CORPORA_PAGE
        data = {'name': name, 'description': description}
        result = self.session.post(corpora_url, data=data)
        if result.status_code == 201:
            return Corpus(session=self.session, **result.json())
        else:
            raise RuntimeError("Corpus creation failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def corpora(self):
        '''Return list of corpora owned by user'''
        result = self.session.get(self.base_url + self.CORPORA_PAGE)
        if result.status_code == 200:
            corpora_list = result.json()['results']
            #TODO: what if we have more than one results page?
            return [Corpus(session=self.session, **corpus_data)
                    for corpus_data in corpora_list]
        else:
            raise RuntimeError("Listing corpora failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))

    def documents(self):
        '''Return list of documents owned by user'''
        result = self.session.get(self.base_url + self.DOCUMENTS_PAGE)
        if result.status_code == 200:
            documents_list = result.json()['results']
            #TODO: what if we have more than one results page?
            return [Document(session=self.session, **document_data)
                    for document_data in documents_list]
        else:
            raise RuntimeError("Listing documents failed with status "
                               "{}. The response was: '{}'".format(result.status_code,
                                result.text))
