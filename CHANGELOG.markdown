# `pypln.api`'s Change Log

## 0.2.0

- Use the REST API instead of parsing HTML from old PyPLN Web
- Ability to use new authentication method (access token)
- Access to document properties
- Better test cases (but now using mocking instead of real PyPLN server) and
  added coverage
- Ability to list all user documents (not only documents linked to a certain
  corpus)

## 0.1.1

- Adds `add_documents` method to `PyPLN.Corpus`

## 0.1.0

Initial release! Features:

- Log-in and out from the Web interface
- Add corpus
- List corpora
- Add document to a corpus
- List documents in a corpus
- Doing everthing parsing HTML (RESTful API needed)
