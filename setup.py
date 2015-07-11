# coding: utf-8

from setuptools import setup, find_packages

setup(name='Flask-AlchemyDumps',
      version='0.0.9',
      description='SQLAlchemy backup/dump tool for Flask',
      long_description=open('README.rst').read(),
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: MIT License',
                   'Framework :: Flask',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Intended Audience :: Developers',
                   'Topic :: Database',
                   'Topic :: System :: Archiving :: Backup',
                   'Topic :: Utilities'],
      keywords='backup, sqlalchemy, flask, restore, dumps, serialization, ' + \
               'ftp, gpg'
      url='https://github.com/cuducos/alchemydumps',
      author='Eduardo Cuducos',
      author_email='cuducos@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      install_requires=['Flask',
                        'Flask-Script',
                        'Flask-SQLAlchemy',
                        'python-gnupg',
                        'SQLAlchemy',
                        'Unipath'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
