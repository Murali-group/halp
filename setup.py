import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import setup


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name="halp",
    packages=find_packages(),
    version="1.0.0",
    description = "Hypergraph Algorithms Package",
    author = "Brendan Avent",
    author_email = "bavent@vt.edu",
    url = "http://tmmurali.github.io/halp/",
    download_url = "https://github.com/tmmurali/halp/tarball/master",
    keywords = ["halp", "hypergraph", "algorithms", "applications", "graph", "network", "directed hypergraph", "undirected hypergraph"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics"
        ],
    license = "GNU GPLv3",
    long_description="halp is a Python software package that provides both a directed and an undirected hypergraph implementation, as well as several important and canonical algorithms that operate on these hypergraphs.",
    tests_require=["pytest"],
    cmdclass={"test": PyTest}
)
