halp: Hypergraph Algorithms Package<br>
==========

_halp_ is a Python software package that provides both a directed and an undirected hypergraph implementation, as well as several important and canonical algorithms that operate on these hypergraphs.

See [http://murali-group.github.io/halp/](http://murali-group.github.io/halp/) for documentation, code examples, and more information.

### Testing
To run the unit tests (called in Travis CI, requires `coveralls` to be installed):
```
coverage run --source=halp setup.py test
```
See the `.travis.yml` file for more information.
