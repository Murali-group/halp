import sys
from distutils.core import setup

from setuptools.command.test import test as TestCommand


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
    name='Hypergraph',
    version='0.1dev',
    packages=['hypergraph'],
    license='TBD',
    long_description=open('README.md').read(),

    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
