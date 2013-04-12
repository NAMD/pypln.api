# PyPLN Application Programming Interface

PyPLN is a distributed pipeline for natural language processing, made in Python.
Learn more at [the offical website](http://www.pypln.org/).


`pypln.api` is a package that connects to PyPLN using HTTP, so you can add
corpora, list documents and do other actions you can do through the Web
interface. Currently we parse all the HTML returned by `pypln.web`, but in a
near future we'll implement a RESTful API that will return only the JSON-data
we need).


## Installation

`pypln.api` is available at [Python Package Index](http://pypi.python.org/).
So, to install it, just execute:

    pip install pypln.api


## Example - Usage

You can see docstrings inside `pypln.api.PyPLN`, but the general usage will
include calling these methods:

```python
from pypln.api import PyPLN
pypln = PyPLN('http://demo.pypln.org/') # use the installation URL of pypln.web
pypln.login('my_username', 'my_precious')

new_corpus = pypln.add_corpus(name='test', description='my new corpus')
with open('my-file.pdf') as fp:
    new_doc = new_corpus.add_document(fp, filename='my-file.pdf')
print 'Document added: ', new_doc
```

If you want to add more than one document in the same API call (HTTP request),
use `pypln.add_documents`, passing a list of file objects and filenames
(generally it's faster).

## License

`pypln.api` is free software, released under the
[GPLv3](https://gnu.org/licenses/gpl-3.0.html).
