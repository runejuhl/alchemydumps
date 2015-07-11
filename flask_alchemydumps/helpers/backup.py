# coding: utf-8

import gnupg
import gzip
import re
from datetime import datetime
from flask import current_app
from ftplib import FTP, error_perm
from tempfile import mkstemp
from time import gmtime, strftime
from unipath import Path


class Backup(object):
    """Manages backup files through local or FTP file systems"""

    def __init__(self, file_prefix='db-bkp', encrypt=False, keys=[], passphrase=None):
        self.ftp = self.__get_ftp()
        self.path = self.__get_path()
        self.files = self.__get_files()
        self.file_prefix = file_prefix
        self.encrypt = encrypt

        if self.encrypt:
            self.gpg = gnupg.GPG()
            self.keys = keys
            self.passphrase = passphrase

    # core methods

    def create_file(self, name, contents):
        """
        Creates a gzip file, optionally encrypted
        :param name: (str) name of the file to be created
        :param contents: (str) contents to be written in the file
        :return: (str or False) path of the created file
        """
        # write a tmp file
        tmp = mkstemp()[1]
        with gzip.open(tmp, 'wb') as handler:
            handler.write(contents)

        # encrypt the file
        if self.encrypt:
            # import ipdb; ipdb.set_trace()
            tmp_encrypted_file = mkstemp()[1]
            encrypted_contents = self.gpg.encrypt_file(open(tmp, 'rb'),
                                                       self.keys,
                                                       armor=False)
            with open(tmp_encrypted_file, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_contents.data)
            Path(tmp).remove()
            tmp = tmp_encrypted_file

        # send it to the FTP server
        if self.ftp:
            self.ftp.storbinary('STOR {}'.format(name), open(tmp, 'rb'))
            return '{}{}'.format(self.path, name)

        # or save it locally
        else:
            new_path = Path(self.path).child(name)
            tmp_path = Path(tmp)
            tmp_path.copy(new_path)
            if new_path.exists():
                return new_path.absolute()
            return False

    def read_file(self, name):
        """Reads the contents of a gzip file"""

        if self.ftp:
            path = mkstemp()[1]
            with open(path, 'wb') as tmp:
                self.ftp.retrbinary('RETR {}'.format(name), tmp.write)
        else:
            path = Path(self.path).child(name)

        if self.encrypt:
            encrypted_path = path
            # strip '.gpg' from file name
            path = path[:-4]
            with open(encrypted_path, 'rb') as ehandler:
                g = self.gpg.decrypt_file(ehandler, passphrase=self.passphrase)
            if not g.ok:
                raise Exception('unable to decrypt file')

            with open(path, 'wb') as handler:
                handler.write(g.data)


        with gzip.open(path, 'rb') as handler:
            return handler.read()

    def delete_file(self, name):
        """Delete a specific file"""
        if self.ftp:
            self.ftp.delete(name)
        else:
            path = Path(self.path).child(name)
            path.remove()

    # helper methods

    def filter_files(self, date_id):
        """
        Gets the list of all backup files with a given timestamp ID
        :param date_id: Timestamp numeric ID as filter
        :return: (list of strings) The list of backup file names
        """
        return [f for f in self.files if date_id == self.__get_id(f)]

    @staticmethod
    def create_id(reference=False):
        """Creates a numeric timestamp ID from a datetime"""
        if not reference:
            reference = gmtime()
        return str(strftime("%Y%m%d%H%M%S", reference))

    def get_ids(self):
        """Gets the different existing timestamp numeric IDs"""
        file_ids = list()
        for f in self.files:
            file_id = self.__get_id(f)
            if file_id and file_id not in file_ids:
                file_ids.append(file_id)
        return file_ids

    def valid(self, date_id):
        """Check backup files for the given timestamp numeric ID"""
        if date_id and date_id in self.get_ids():
            return True
        print('==> Invalid id. Use "history" to list existing downloads')
        return False

    def get_name(self, date_id, class_name):
        """
        Creates a backup file name given the nuemric timestamp ID and the name
        of the SQLAlchemy mapped class
        """
        name = '{}-{}-{}.gz'.format(self.file_prefix, date_id, class_name)
        if self.encrypt:
            name += '.gpg'
        return name

    @staticmethod
    def parsed_id(date_id):
        """Transforms a timestamp ID in a humanized date"""
        date_parsed = datetime.strptime(date_id, '%Y%m%d%H%M%S')
        return date_parsed.strftime('%b %d, %Y at %H:%M:%S')

    def close_connection(self):
        """If is there any open FTP connection, closes it"""
        if self.ftp:
            self.ftp.quit()

    # internal methods

    @staticmethod
    def __get_id(file_name):
        """
        Gets the timestamp numeric ID of a given file
        :param file_name: (string) name of a file generated by AlchemyDumps
        :return: (string of False) the backup numeric id
        """
        pattern = r'(-)([0-9]{14,14})(-)'
        match = re.search(pattern, file_name)
        if match:
            return match.group(2)
        return False

    def __get_files(self):
        """Gets the list of all backup files"""
        if self.ftp:
            list_files = self.ftp.nlst()
            return [f for f in list_files if self.__get_id(f)]
        else:
            return [f.name for f in Path(self.path).listdir()]

    def __get_path(self):
        """
        Gets the path to the backup location
        :return: Unipath if local, string if FTP
        """
        if self.ftp:
            return 'ftp://{}{}'.format(self.ftp_server,
                                       self.__slashes(self.ftp_path))
        else:
            basedir = current_app.extensions['alchemydumps'].basedir
            backup_dir = basedir.child('alchemydumps')
            if not backup_dir.exists():
                backup_dir.mkdir()
            return self.__slashes(str(backup_dir.absolute()))

    def __get_ftp(self):

        # look for FTP configuration
        server = current_app.config.get('ALCHEMYDUMPS_FTP_SERVER', False)
        user = current_app.config.get('ALCHEMYDUMPS_FTP_USER', False)
        password = current_app.config.get('ALCHEMYDUMPS_FTP_PASSWORD', False)
        path = current_app.config.get('ALCHEMYDUMPS_FTP_PATH', False)

        # try to connect using FTP settings
        if server and user and password:
            try:
                ftp = FTP(server, user, password)
                change_path = ftp.cwd(path)
                if change_path[0:6] != '250 OK':
                    ftp.quit()
            except error_perm:
                address = '{}:{}@{}{}'.format(user,
                                              '*' * len(password),
                                              server,
                                              path)
                print("==> Couldn't connect to ftp://{}".format(address))
                return False
            self.ftp_server = server
            self.ftp_path = path
            return ftp
        return False

    @staticmethod
    def __slashes(string):
        """Adds, if needed, a slash to the beginning and ending of a string"""
        if string and len(string) > 1:
            if string[0:1] != '/':
                string = '/{}'.format(string)
            if string[-1] != '/':
                string = '{}/'.format(string)
        return string
