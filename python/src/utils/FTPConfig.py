from utils.FileManager import FileManager
from configparser import ConfigParser


class FTPConfig:
    file_manager = None
    host = ''
    username = ''
    password = ''
    replace_path = ''
    http_url = ''
    config = ConfigParser()
    profile_tag = ''

    def __init__(self, config_file, script_name='', unique_run_id=''):
        self.file_manager = FileManager(script_name, self.__class__.__name__, unique_run_id)
        self.config.read(config_file)

    def load(self, profile_tag):
        self.host = ""
        self.username = ""
        self.password = ""
        self.replace_path = ""
        self.http_url = ""
        self.profile_tag = profile_tag

        is_loaded = False
        if profile_tag in self.config:
            self.host = self.config.get(profile_tag, 'ftpHost', fallback='')
            self.username = self.config.get(profile_tag, 'ftpUser', fallback='')
            self.password = self.config.get(profile_tag, 'ftpPass', fallback='')
            self.replace_path = self.config.get(profile_tag, 'ftpReplace', fallback='')
            self.http_url = self.config.get(profile_tag, 'httpUrl', fallback='')
            is_loaded = True
        else:
            self.file_manager.log("Unknown profile: " + profile_tag + " ; Please check ftp.ini.")
            self.file_manager.out("Unknown ftp profile: " + profile_tag, "FTPConfig.error.txt")
        return is_loaded
