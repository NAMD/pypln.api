# PyPLN Application Programming Interface

PyPLN is a distributed pipeline for natural language processing, made in
Python. Learn more at [the PyPLN website](http://www.pypln.org/).


`pypln.api` is a package that interacts with PyPLN HTTP API to do everything
programatically, in a Pythonic way. Basically, you are able to add/list
corpora, add/list documents and retrieve documents' properties (resulted from
the pipeline processing by the backend).


## Installation

`pypln.api` is available at [Python Package Index](http://pypi.python.org/).
So, to install it, just execute:

    pip install pypln.api


## Example - Usage

You can see docstrings inside `pypln.api.PyPLN`, but the general usage will be
something like this:

```python
from pypln.api import PyPLN

# Start an authenticated session to PyPLN demo server
pypln = PyPLN('http://fgv.pypln.org/', ('username', 'password'))

# You could also use your authentication token:
#pypln = PyPLN('http://fgv.pypln.org/', 'my-auth-token')

# Add a new corpus to your account
new_corpus = pypln.add_corpus(name='test', description='my new corpus')

# Add a document to this new corpus
with open('my-file.pdf') as fp:
    new_doc = new_corpus.add_document(fp)
print('Document added: {}'.format(new_doc))

# Retrieve all available (processed) properties for your brand new document
print('Processed properties:')
for document_property in new_doc.properties:
    print(' - {}'.format(document_property))

# Retrieve one document property:
print('Extracted text from our PDF:')
print(new_doc.get_property('text'))

# Retrieve a document using it's url:
from pypln.api import Document
# Make sure you replace this url for the url of a document you have access to!
my_doc = Document.from_url('http://fgv.pypln.org/documents/1/',
    ('username', 'password'))
print(my_doc.get_property('text'))

# Retrieve wordcloud image built from the document
with open("wordcloud_{}.png".format(doc_id), 'w') as fd:
    fd.write(base64.b64decode(my_doc.get_property("wordcloud")))
```

> ProTip™: use [ipython](http://ipython.org/) to discover all methods available
> at `PyPLN`, `Corpus` and `Document` classes - they are very simple and
> straightford to use.


## License

`pypln.api` is free software, released under the
[GPLv3](https://gnu.org/licenses/gpl-3.0.html).
