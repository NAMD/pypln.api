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
LOGIN_URL = '/account/login/'
CORPORA_PAGE = '/corpora/'
CORPUS_URL = '{}/corpora/{}'

CSRF_SPLIT = "<input type='hidden' name='csrfmiddlewaretoken' value='"
def get_csrf(html):
    '''Given an HTML, return the value of field "csrfgmiddlewaretoken"'''
    return html.split(CSRF_SPLIT)[1].split("'")[0]

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

def extract_data_from_html_table(html, table_id, field_names):
    split_string = '<table id="{}"'.format(table_id)
    data = html.split(split_string)[1].split('</table>')[0]
    raw_rows = data.split('<tr>')[2:]
    rows = []
    for raw_row in raw_rows:
        row_data = [x.split('</td>')[0] for x in raw_row.split('<td>')[1:]]
        row_dict = dict(zip(field_names, row_data))
        rows.append(row_dict)
    return rows

def extract_documents_from_html(html):
    '''Given an HTML, extracts and returns all documents listed there'''
    field_names = ('filename', 'size', 'upload_date', 'owner')
    rows = extract_data_from_html_table(html, 'table_documents', field_names)
    for row in rows:
        row['owner'] = row['owner'].split('>')[1].split('<')[0]
        filename_and_slug = row['filename']
        row['filename'] = filename_and_slug.split('>')[1].split('<')[0]
        row['slug'] = filename_and_slug.split('"')[1].replace('/documents/', '')
    return rows

def extract_corpora_from_html(html):
    '''Given an HTML, extracts and returns all corpora listed'''
    field_names = ('name', 'created_on', 'last_modified',
                   'number_of_documents', 'owner')
    rows = extract_data_from_html_table(html, 'table_corpora', field_names)
    for row in rows:
        name_and_slug = row['name']
        row['owner'] = row['owner'].split('>')[1].split('<')[0]
        row['name'] = row['name'].split('>')[1].split('<')[0]
        row['slug'] = name_and_slug.split('"')[1].replace('/corpora/', '')
    return rows

class PyPLN(object):
    '''Class to connect to PyPLN's API and execute some actions'''

    def __init__(self, base_url):
        '''Initialize the API object, setting the base URL for the HTTP API'''

        self._session = requests.session()
        self.base_url = base_url
        self.logged_in = False
        self.username = None
        self.password = None

    def login(self, username, password):
        '''Log-in into this API session '''
        login_url = self.base_url + LOGIN_URL
        login_page = self._session.get(login_url)
        csrf_token = get_csrf(login_page.text)
        data = {'username': username, 'password': password,
                'csrfmiddlewaretoken': csrf_token}
        result = self._session.post(login_url, data=data)
        self.logged_in = 'sessionid' in result.cookies
        if self.logged_in:
            self.username = username
            self.password = password
        return self.logged_in

    def logout(self):
        '''Log-out'''
        self._session.get(self.base_url + '/account/logout')
        self._session = requests.session()
        self.logged_in = False
        self.username = None
        self.password = None
        return True

    def add_corpus(self, name, description):
        '''Add a corpus to your account'''
        corpora_page_url = self.base_url + CORPORA_PAGE
        corpora_page = self._session.get(corpora_page_url)
        csrf_token = get_csrf(corpora_page.text)
        data = {'name': name, 'description': description,
                'csrfmiddlewaretoken': csrf_token}
        result = self._session.post(corpora_page_url, data=data)
        corpora = extract_corpora_from_html(result.text)
        this_corpus = [x for x in corpora if x['name'] == name]
        if not this_corpus:
            raise RuntimeError('Could not add this corpus')
        else:
            corpus = this_corpus[0]
            corpus['description'] = description
            corpus['_session'] = self._session
            corpus['url'] = CORPUS_URL.format(self.base_url, corpus['slug'])
            corpus['pypln'] = self
            return Corpus(**corpus)

    def corpora(self):
        '''Return list of corpora'''
        result = self._session.get(self.base_url + CORPORA_PAGE)
        corpora = extract_corpora_from_html(result.text)
        corpora_list = []
        for corpus in corpora:
            #TODO: add description
            corpus['pypln'] = self
            corpora_list.append(Corpus(**corpus))
        return corpora_list
