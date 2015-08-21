ATTENTION
---------
**Terribly hacky (well, a bit at least) fork of alchemydumps to integrate
support for GPG encryption. Don't come running if it gobbles up the only copy of
the pictures of your newborn child.**

Other stuff:

* Now saves to a timestamped directory instead of writing everything into one
dir
* Removes dependency on unipath

Thanks @cuducos for creating it in the first place :)

AlchemyDumps
------------

Do you use `Flask <http://flask.pocoo.org>`_ with `SQLAlchemy <http://www.sqlalchemy.org/>`_  and `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_ ? Wow, what a coincidence!

This package lets you backup and restore all your data using `SQLALchemy dumps() method <http://docs.sqlalchemy.org/en/latest/core/serializer.html>`_.

It is an easy way (one single command, I mean it) to save **all** the data stored in your database.

You can save it locally or in a remote server via FTP.

Install
-------

First install the package: ``$ pip install Flask-AlchemyDumps``

Then pass your Flask application and SQLALchemy database to it:

::

    from flask import Flask
    from flask.ext.alchemydumps import AlchemyDumps, AlchemyDumpsCommand
    from flask.ext.script import Manager
    from flask.ext.sqlalchemy import SQLAlchemy

    # init Flask
    app = Flask(__name__)

    # init SQLAlchemy and Flask-Script
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db = SQLAlchemy(app)
    manager = Manager(app)

    # init Alchemy Dumps
    alchemydumps = AlchemyDumps(app, db)
    manager.add_command('alchemydumps', AlchemyDumpsCommand)

* The *second line* imports the objects from the package.
* The *last two lines* instantiate and add AlchemyDumps to the *Flask-Script manager*.

**Remote backup (via FTP)**

If you want to save your backups in a remote server via FTP, just make sure to set these environment variables replacing the placeholder information with the proper credentials:

::

    ALCHEMYDUMPS_FTP_SERVER = 'ftp.server.com'
    ALCHEMYDUMPS_FTP_USER = 'johndoe'
    ALCHEMYDUMPS_FTP_PASSWORD = 'secret'
    ALCHEMYDUMPS_FTP_PATH = '/absolute/path/'

If you want, there is a ``.env.sample`` inside the ``/tests`` folder. Just copy it to your application root folder, rename it to ``.env``, and insert your credentials.

**.gitignore**

You might want to add ``alchemydumps`` to your ``.gitignore``. It is the folder where **AlchemyDumps** save the backup files.

Examples
--------

Considering you have these *models* (that is to say, these `SQLAlchemy mapped classes <http://docs.sqlalchemy.org/en/latest/orm/mapper_config.html>`_):

::

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(140), index=True, unique=True)
        posts = db.relationship('Post', backref='author', lazy='dynamic')

    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(140))
        content = db.Column(db.UnicodeText)
        author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

Just in case: this is a simple example, but you can use *abstract* mapped classes as well.

You can backup all your data
----------------------------

::

    $ python manage.py alchemydumps create

Output:

::

    ==> 3 rows from User saved as /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
    ==> 42 rows from Post saved as /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz

You can list the backups you have already created
-------------------------------------------------
::

    $ python manage.py alchemydumps history

Output:

::

    ==> ID: 20141114203949 (from Nov 15, 2014 at 17:21:07)
        /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
        /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz

    ==> ID: 20141115140629 (from Nov 15, 2014 at 14:06:29)
        /vagrant/alchemydumps/db-bkp-20141115140629-User.gz
        /vagrant/alchemydumps/db-bkp-20141115140629-Post.gz

You can restore a backup
------------------------

::

    $ python manage.py alchemydumps restore -d 20141115172107

Output:

::

    ==> db-bkp-20141115172107-User.gz totally restored.
    ==> db-bkp-20141115172107-Post.gz totally restored.


You can delete an existing backup
---------------------------------

::

    $ python manage.py alchemydumps remove -d 20141115172107

Output:

::

    ==> Do you want to delete the following files?
        /vagrant/alchemydumps/db-bkp-20141115172107-User.gz
        /vagrant/alchemydumps/db-bkp-20141115172107-Post.gz
    ==> Press "Y" to confirm, or anything else to abort: y
        db-bkp-20141115172107-User.gz deleted.
        db-bkp-20141115172107-Post.gz deleted.


And you can use the auto-clean command
--------------------------------------

The ``autoclean`` command follows these rules to delete backups:

* It keeps **all** the backups from the last 7 days.
* It keeps **the most recent** backup **from each week of the last month**.
* It keeps **the most recent** backup **from each month of the last year**.
* It keeps **the most recent** backup **from each remaining year**.

::

    $ python manage.py alchemydumps autoclean

Output:

::

    ==> 8 backups will be kept:

        ID: 20130703225903 (from Jul 03, 2013 at 22:59:03)
        /vagrant/alchemydumps/db-bkp-20130703225903-User.gz
        /vagrant/alchemydumps/db-bkp-20130703225903-Post.gz

        ID: 20120405013054 (from Apr 05, 2012 at 01:30:54)
        /vagrant/alchemydumps/db-bkp-20120405013054-User.gz
        /vagrant/alchemydumps/db-bkp-20120405013054-Post.gz

        ID: 20101123054342 (from Nov 23, 2010 at 05:43:42)
        /vagrant/alchemydumps/db-bkp-20101123054342-User.gz
        /vagrant/alchemydumps/db-bkp-20101123054342-Post.gz

        ID: 20090708100815 (from Jul 08, 2009 at 10:08:15)
        /vagrant/alchemydumps/db-bkp-20090708100815-User.gz
        /vagrant/alchemydumps/db-bkp-20090708100815-Post.gz

        ID: 20081208191908 (from Dec 08, 2008 at 19:19:08)
        /vagrant/alchemydumps/db-bkp-20081208191908-User.gz
        /vagrant/alchemydumps/db-bkp-20081208191908-Post.gz

        ID: 20070114122922 (from Jan 14, 2007 at 12:29:22)
        /vagrant/alchemydumps/db-bkp-20070114122922-User.gz
        /vagrant/alchemydumps/db-bkp-20070114122922-Post.gz

        ID: 20060911035318 (from Sep 11, 2006 at 03:53:18)
        /vagrant/alchemydumps/db-bkp-20060911035318-User.gz
        /vagrant/alchemydumps/db-bkp-20060911035318-Post.gz

        ID: 20051108082503 (from Nov 08, 2005 at 08:25:03)
        /vagrant/alchemydumps/db-bkp-20051108082503-User.gz
        /vagrant/alchemydumps/db-bkp-20051108082503-Post.gz

    ==> 11 backups will be deleted:

        ID: 20120123032442 (from Jan 23, 2012 at 03:24:42)
        /vagrant/alchemydumps/db-bkp-20120123032442-User.gz
        /vagrant/alchemydumps/db-bkp-20120123032442-Post.gz

        ID: 20101029100412 (from Oct 29, 2010 at 10:04:12)
        /vagrant/alchemydumps/db-bkp-20101029100412-User.gz
        /vagrant/alchemydumps/db-bkp-20101029100412-Post.gz

        ID: 20100526185156 (from May 26, 2010 at 18:51:56)
        /vagrant/alchemydumps/db-bkp-20100526185156-User.gz
        /vagrant/alchemydumps/db-bkp-20100526185156-Post.gz

        ID: 20100423085529 (from Apr 23, 2010 at 08:55:29)
        /vagrant/alchemydumps/db-bkp-20100423085529-User.gz
        /vagrant/alchemydumps/db-bkp-20100423085529-Post.gz

        ID: 20081006074458 (from Oct 06, 2008 at 07:44:58)
        /vagrant/alchemydumps/db-bkp-20081006074458-User.gz
        /vagrant/alchemydumps/db-bkp-20081006074458-Post.gz

        ID: 20080429210254 (from Apr 29, 2008 at 21:02:54)
        /vagrant/alchemydumps/db-bkp-20080429210254-User.gz
        /vagrant/alchemydumps/db-bkp-20080429210254-Post.gz

        ID: 20080424043716 (from Apr 24, 2008 at 04:37:16)
        /vagrant/alchemydumps/db-bkp-20080424043716-User.gz
        /vagrant/alchemydumps/db-bkp-20080424043716-Post.gz

        ID: 20080405110244 (from Apr 05, 2008 at 11:02:44)
        /vagrant/alchemydumps/db-bkp-20080405110244-User.gz
        /vagrant/alchemydumps/db-bkp-20080405110244-Post.gz

        ID: 20060629054914 (from Jun 29, 2006 at 05:49:14)
        /vagrant/alchemydumps/db-bkp-20060629054914-User.gz
        /vagrant/alchemydumps/db-bkp-20060629054914-Post.gz

        ID: 20060329020048 (from Mar 29, 2006 at 02:00:48)
        /vagrant/alchemydumps/db-bkp-20060329020048-User.gz
        /vagrant/alchemydumps/db-bkp-20060329020048-Post.gz

        ID: 20050324012859 (from Mar 24, 2005 at 01:28:59)
        /vagrant/alchemydumps/db-bkp-20050324012859-User.gz
        /vagrant/alchemydumps/db-bkp-20050324012859-Post.gz

    ==> Press "Y" to confirm, or anything else to abort. y
        db-bkp-20120123032442-User.gz deleted.
        db-bkp-20120123032442-Post.gz deleted.
        db-bkp-20101029100412-User.gz deleted.
        db-bkp-20101029100412-Post.gz deleted.
        db-bkp-20100526185156-User.gz deleted.
        db-bkp-20100526185156-Post.gz deleted.
        db-bkp-20100423085529-User.gz deleted.
        db-bkp-20100423085529-Post.gz deleted.
        db-bkp-20081006074458-User.gz deleted.
        db-bkp-20081006074458-Post.gz deleted.
        db-bkp-20080429210254-User.gz deleted.
        db-bkp-20080429210254-Post.gz deleted.
        db-bkp-20080424043716-User.gz deleted.
        db-bkp-20080424043716-Post.gz deleted.
        db-bkp-20080405110244-User.gz deleted.
        db-bkp-20080405110244-Post.gz deleted.
        db-bkp-20060629054914-User.gz deleted.
        db-bkp-20060629054914-Post.gz deleted.
        db-bkp-20060329020048-User.gz deleted.
        db-bkp-20060329020048-Post.gz deleted.
        db-bkp-20050324012859-User.gz deleted.
        db-bkp-20050324012859-Post.gz deleted.

Requirements & Dependencies
---------------------------

**AlchemyDumps** is tested and should work in Python 2.7+ and 3.4+.

**AlchemyDumps** was designed to work together with `Flask <http://flask.pocoo.org>`_ applications that uses `SQLAlchemy <http://www.sqlalchemy.org/>`_. It runs through the `Flask-Script <http://flask-script.readthedocs.org/en/latest/>`_ manager. Thus, these packages are essential requirements. **AlchemyDumps** also uses `Unipath <https://github.com/mikeorr/Unipath>`_ package. All these packages, if needed, will be installed once you install **AlchemyDumps**.

Tests
-----

If you wanna run the tests:

::

    $ git clone git@github.com:cuducos/alchemydumps.git
    $ cd /alchemydumps
    $ pip install -r tests/requirements.txt
    $ python setup.py develop
    $ nosetests

If you want to include remote (FTP) tests you have to rename ``/tests/.env.sample`` to ``/tests/.env`` and edit it with valid FTP credentials.

Contributing
------------

You can `report issues <https://github.com/cuducos/alchemydumps/issues>`_ or:

* Fork this repo
* Create a new branch: ``git checkout -b my-new-feature``
* Commit your changes: ``git add -A . && commit -m 'Add some feature'``
* Push to the branch: ``git push origin my-new-feature``
* And create new `pull request`

Contributors
------------

Thanks `Kirill Sumorokov <https://github.com/clayman74>`_, `spikergit1 <https://github.com/spikergit1>`_ and `Walter <https://github.com/antwal>`_ for the pull requests, issues reported, feedback and support.

Changelog
---------

**Version 0.0.8**
    * Python 3 support.
**Version 0.0.7**
    * Add support for abstract models.
**Version 0.0.6**
    * Remote backup/restore via FTP.
    * General code improvements.
**Version 0.0.5**
    * Re-written as a Flask extension.
    * Built-in Flask app within the test suite.
**Version 0.0.4**
    * Fix bug in the installation process.
**Version 0.0.3**
    * New command to auto-clean backup folder.
**Version 0.0.2**
    * New command: delete a single backup.
    * Proper message when ID is not found in restore and delete commands.
    * Avoid breaking the process when get_id() fails.
    * Minor code improvements.

License
-------

Copyright (c) 2015 Eduardo Cuducos.

Licensed under the `MIT License <http://opensource.org/licenses/MIT>`_.
