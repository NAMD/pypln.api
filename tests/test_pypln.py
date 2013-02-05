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

import unittest

from random import choice, randint
from string import ascii_letters

from pypln.api import PyPLN, Corpus, Document


BASE_URL = 'http://localhost:8000'
USERNAME = 'admin'
PASSWORD = 'admin'

def random_name():
    return ''.join([choice(ascii_letters) for i in range(randint(5, 10))])

class TestPyPLN(unittest.TestCase):
    def test_login(self):
        pypln = PyPLN(BASE_URL)

        self.assertFalse(pypln.logged_in)
        self.assertIs(pypln.username, None)
        self.assertIs(pypln.password, None)
        self.assertFalse(pypln.login(USERNAME, PASSWORD + 'wrong'))
        self.assertFalse(pypln.logged_in)
        self.assertIs(pypln.username, None)
        self.assertIs(pypln.password, None)

        self.assertTrue(pypln.login(USERNAME, PASSWORD))
        self.assertTrue(pypln.logged_in)
        self.assertEqual(pypln.username, USERNAME)
        self.assertEqual(pypln.password, PASSWORD)

    def test_logout(self):
        pypln = PyPLN(BASE_URL)
        pypln.login(USERNAME, PASSWORD)

        self.assertTrue(pypln.logout())
        self.assertFalse(pypln.logged_in)
        self.assertIs(pypln.username, None)
        self.assertIs(pypln.password, None)

    def test_create_corpus(self):
        pypln = PyPLN(BASE_URL)
        pypln.login(USERNAME, PASSWORD)

        corpus_name = 'My Corpus ' + random_name()
        slug = corpus_name.strip().replace(' ', '-').lower()
        my_corpus = pypln.add_corpus(name=corpus_name, description='test')
        self.assertEqual(type(my_corpus), Corpus)
        self.assertEqual(my_corpus.name, corpus_name)
        self.assertEqual(my_corpus.slug, slug)
        self.assertEqual(my_corpus.description, 'test')
        self.assertEqual(repr(my_corpus),
                         '<Corpus: {} ({})>'.format(corpus_name, slug))

    def test_list_corpora(self):
        pypln = PyPLN(BASE_URL)
        pypln.login(USERNAME, PASSWORD)

        iterations = 5
        corpora = []
        for i in range(iterations):
            corpus_name = 'corpus random ' + random_name()
            my_corpus = pypln.add_corpus(name=corpus_name, description='test')
            corpora.append(my_corpus)

        list_of_corpora = pypln.corpora()
        self.assertGreaterEqual(len(list_of_corpora), iterations)
        for corpus in corpora:
            self.assertIn(corpus, list_of_corpora)

    def test_add_document(self):
        pypln = PyPLN(BASE_URL)
        pypln.login(USERNAME, PASSWORD)

        corpus_name = random_name()
        my_corpus = pypln.add_corpus(name=corpus_name, description='test')

        with open('tests/data/python-wikipedia-en.pdf') as fobj:
            random_filename = random_name() + '.pdf'
            doc = my_corpus.add_document(fobj, filename=random_filename)
        self.assertEqual(type(doc), Document)
        self.assertEqual(doc.filename, random_filename)
        self.assertEqual(doc.corpora, [my_corpus])
        self.assertEqual(repr(doc),
                         '<Document: {} ({})>'.format(random_filename,
                                                      repr(my_corpus)))

    def test_list_documents(self):
        pypln = PyPLN(BASE_URL)
        pypln.login(USERNAME, PASSWORD)

        corpus_name = random_name()
        my_corpus = pypln.add_corpus(name=corpus_name, description='test')

        documents = []
        for i in range(5):
            with open('tests/data/python-wikipedia-en.pdf') as fobj:
                new_document = my_corpus.add_document(fobj,
                        filename='document_{}.pdf'.format(random_name()))
                documents.append(new_document)

        self.assertEqual(set(my_corpus.documents()), set(documents))
