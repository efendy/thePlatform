#!/usr/bin/env python3
#
#
import os
import ftplib
from utils.FileManager import FileManager
from utils.FTPConfig import FTPConfig
# from urllib import request
import requests
import urllib.parse
from datetime import datetime

ROOT = os.path.realpath(__file__).split("/src/")[0]
SCRIPT_NAME = os.path.basename(__file__).split(".")[0]
UNIQUE_RUN_ID = "caf1aeb2-52b0-47d8-b37d-5a7f39f4da59"
FILE_ERROR_OUT = SCRIPT_NAME + ".error.txt"


class TransferSubtitles:
    file_manager = None
    ftp_config = None
    ftp = None

    def __init__(self):
        self.file_manager = FileManager(SCRIPT_NAME, self.__class__.__name__, UNIQUE_RUN_ID)
        self.ftp_config = FTPConfig(ROOT+"/resources/DownloadStorageFiles/ftp.ini", SCRIPT_NAME, UNIQUE_RUN_ID)

    def run(self, input_file, tag_id):
        self.file_manager.log("SCRIPT RUN() START ------ args -> input_file:" + input_file)
        with open(input_file, "r") as f:
            self.file_manager.log("OPEN input_file:" + input_file)
            for line in f:
                clean_line = str(line).replace('\n', '')
                self.file_manager.log("READLN clean_line:" + clean_line)
                line_items = str(clean_line).split(",")
                if len(line_items) == 4:
                    media_id = line_items[0]
                    source_url = line_items[1]
                    destination_host = line_items[2]
                    destination_url = line_items[3]
                    if self.upload(source_url, destination_url, destination_host):
                        self.file_manager.log("UPLOAD [" + media_id + "] Success")
                        self.file_manager.out(media_id, "success_ids_" + tag_id + ".txt")
                        self.file_manager.out(clean_line, "success_" + tag_id + ".txt")
                        http_url = self.ftp_config.http_url + str(destination_url).replace(self.ftp_config.replace_path,"")
                        self.file_manager.log("INVALIDATE CACHE PARAM [" + media_id + "] URL=" + http_url)
                        http_url = urllib.parse.quote_plus(http_url)
                        r = requests.get('https://api.asia.fox.com/akamai/purge?url='+http_url)
                        self.file_manager.log("INVALIDATE CACHE RESPONSE [" + media_id + "] URL=" + r.text)
                    else:
                        self.file_manager.log("UPLOAD [" + media_id + "] Failed")
                        self.file_manager.out(clean_line, "failed_" + tag_id + ".txt")
                else:
                    self.file_manager.log("PARSE [" + media_id + "] Failed")
                    self.file_manager.out(clean_line, "failed_" + tag_id + ".txt")
        self.file_manager.log("SCRIPT RUN() END ------")
        return True

    def upload(self, source_file, destination_file, profile_tag):
        is_success = True
        try:
            if self.ftp_config.profile_tag != profile_tag:
                if self.ftp is not None:
                    self.ftp.quit()
                self.ftp_config.load(profile_tag) # load storage_host as profile_tag
                self.ftp = ftplib.FTP(self.ftp_config.host)
                self.ftp.login(self.ftp_config.username, self.ftp_config.password)

            # local_filepath = self.file_manager.get_outfile(destination_file)
            local_file = open(source_file, 'rb')
            self.file_manager.log("Upload: " + source_file + " >> " +
                                  self.ftp.storbinary('STOR ' + destination_file, local_file))
            local_file.close()
        except ftplib.error_perm:
            self.file_manager.log("ftplib.error_perm destination_file:" + destination_file)
            is_success = False
        except ftplib.all_errors:
            self.file_manager.log("ftplib.all_errors destination_file:" + destination_file)
            is_success = False

        return is_success


instance = TransferSubtitles()
folder = "00001-00002"
instance.run(ROOT+"/out/PreparingSubtitlesHLS/"+UNIQUE_RUN_ID+"/"+folder+"/m3u8_replace_1.txt",folder)
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_replace_01.txt") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_replace_02.txt") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_replace_03.txt") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_replace_04.txt") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_replace_rest.txt") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH/"+UNIQUE_RUN_ID+"/mpd_rollback.txt")
# instance.run(ROOT+"/out/PreparingSubtitlesDASH2/"+UNIQUE_RUN_ID+"/01001-02000/mpd_replace.txt","01001-02000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH2/"+UNIQUE_RUN_ID+"/02001-03000/mpd_replace.txt","02001-03000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH2/"+UNIQUE_RUN_ID+"/03001-04000/mpd_replace.txt","03001-04000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH3/"+UNIQUE_RUN_ID+"/04001-05000/mpd_replace.txt","04001-05000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH3/"+UNIQUE_RUN_ID+"/05001-06000/mpd_replace.txt","05001-06000") # done <-- round 2 start here!
# instance.run(ROOT+"/out/PreparingSubtitlesDASH4/"+UNIQUE_RUN_ID+"/06001-07000/mpd_replace.txt","06001-07000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH4/"+UNIQUE_RUN_ID+"/07001-08000/mpd_replace.txt","07001-08000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH5/"+UNIQUE_RUN_ID+"/08001-09000/mpd_replace.txt","08001-09000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH5/"+UNIQUE_RUN_ID+"/09001-10000/mpd_replace.txt","09001-10000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH6/"+UNIQUE_RUN_ID+"/10001-11000/mpd_replace.txt","10001-11000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH6/"+UNIQUE_RUN_ID+"/11001-12000/mpd_replace.txt","11001-12000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH7/"+UNIQUE_RUN_ID+"/12001-13000/mpd_replace.txt","12001-13000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH7/"+UNIQUE_RUN_ID+"/13001-14000/mpd_replace.txt","13001-14000") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH6/"+UNIQUE_RUN_ID+"/14001-14355/mpd_replace.txt","14001-14355") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH7/"+UNIQUE_RUN_ID+"/13001-14000/mpd_replace.txt.bak","13001-14000-extra") # done
# instance.run(ROOT+"/out/PreparingSubtitlesDASH5/"+UNIQUE_RUN_ID+"/08001-09000/mpd_replace.txt.bak","08001-09000-extra") # done

exit(0)