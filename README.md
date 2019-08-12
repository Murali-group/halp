halp: Hypergraph Algorithms Package<br>
==========

_halp_ is a Python software package that provides both a directed and an undirected hypergraph implementation, as well as several important and canonical algorithms that operate on these hypergraphs.

See [http://murali-group.github.io/halp/](http://murali-group.github.io/halp/) for documentation, code examples, and more information.

### Development & Testing Notes
To run the unit tests (called in Travis CI, requires `coveralls` to be installed):
```
coverage run --source=halp setup.py test
```
See the `.travis.yml` file for more information.  You can also just run `pytest -x` (you may have to run `python setup.py test` to install `pytest`).

*2018-10-27* updated code to work with [both NetworkX 1.11 and 2.0](https://networkx.github.io/documentation/stable/release/migration_guide_from_1.x_to_2.0.html).  To run multiple versions of python packages w/ Travis CI: see [this page](https://docs.travis-ci.com/user/languages/python/#testing-against-multiple-versions-of-dependencies-eg-django-or-flask).

To keep this branch up-to-date with master: `git merge master`
