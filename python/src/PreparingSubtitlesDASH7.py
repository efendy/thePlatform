#!/usr/bin/env python3
#
#
import os
import ftplib
from xml.dom import minidom
from shutil import copyfile
from utils.FileManager import FileManager
from utils.FTPConfig import FTPConfig

ROOT = os.path.realpath(__file__).split("/src/")[0]
SCRIPT_NAME = os.path.basename(__file__).split(".")[0]
UNIQUE_RUN_ID = "caf1aeb2-52b0-47d8-b37d-5a7f39f4da59"
FILE_ERROR_OUT = SCRIPT_NAME + ".error.txt"


class PreparingSubtitlesDASH7:
    file_manager = None
    ftp_config = None
    ftp = None
    language_code_map = dict({"en": "en",
                              "id": "id",
                              "ko": "ko",
                              "ms": "ms", #Malay
                              "th": "th",
                              "vi": "vi",
                              "ar": "ar",
                              "my": "my", #Burmese,
                              "zz": "zz", #(Other)
                              "zh": "zh",
                              "zho": "zh",
                              "zh-Hans": "zh-Hans",
                              "zh-Hant": "zh-Hant",
                              "mis": "zz"})

    def __init__(self, sub_folder):
        self.file_manager = FileManager(SCRIPT_NAME, self.__class__.__name__, sub_folder)
        self.ftp_config = FTPConfig(ROOT+"/resources/DownloadStorageFiles/ftp.ini", SCRIPT_NAME, sub_folder)

    def run(self, input_file, input_directory):
        self.file_manager.log("FUNCTION run() args -> input_file:" + input_file +
                              ", input_directory:" + input_directory)
        with open(input_file, "r") as f:
            self.file_manager.log("OPEN input_file:" + input_file)
            for line in f:
                media_id = str(line).replace('\n', '')
                self.file_manager.log("READLN media_id:" + media_id)
                if media_id:
                    local_input_directory = input_directory + media_id + "/"

                    manifest_extension = "mpd"
                    local_media_dash = local_input_directory + "manifest." + manifest_extension
                    # replace_list = local_media_directory + manifest_extension + "_replace.txt"
                    # rollback_list = local_media_directory + manifest_extension + "_rollback.txt"
                    remote_dash_storage_host = ""
                    remote_dash_basepath = ""
                    manifest_info_file = local_input_directory + manifest_extension + "_info.txt"
                    with open(manifest_info_file, "r") as dash_basepath_file:
                        self.file_manager.log("OPEN [" + media_id + "] manifest_info_file:" + manifest_info_file)
                        for dash_basepath_line in dash_basepath_file:
                            self.file_manager.log("READLN [" + media_id + "] dash_basepath_line:" + dash_basepath_line)
                            dash_basepath_line = str(dash_basepath_line).replace('\n', '')
                            remote_dash_storage_host = dash_basepath_line.split(",")[0]
                            remote_dash_basepath = dash_basepath_line.split(",")[1]
                            self.file_manager.log("STORE [" + media_id + "] " +
                                                  "remote_dash_storage_host:" + input_file +
                                                  ", remote_dash_storage_host:" + input_directory)

                    count_match = 0
                    if os.path.exists(local_media_dash):
                        self.file_manager.log("CONTINUE [" + media_id + "] (exists) local_media_dash:" + local_media_dash)
                        manifest_dom = minidom.parse(local_media_dash)

                        for docAdaptationSet in manifest_dom.getElementsByTagName('AdaptationSet'):
                            if docAdaptationSet.attributes['contentType']:
                                if docAdaptationSet.attributes['contentType'].value == 'text':
                                    count_match += 1
                                    self.file_manager.log("AdaptationSet contentType is text")
                                    subtitle_language = docAdaptationSet.attributes['lang'].value #lang="zh-Hans"
                                    docRepresentation = self.getNodeByName(docAdaptationSet, "Representation")
                                    docBaseURL = self.getNodeByName(docRepresentation, "BaseURL")
                                    subtitle_uri = ""
                                    if docBaseURL:
                                        subtitle_uri = self.getNodeText(docBaseURL)

                                    if subtitle_language and subtitle_uri:
                                        self.file_manager.log("PROCESS [" + media_id + "]" +
                                                              " subtitle_language: " + subtitle_language +
                                                              ", subtitle_uri: " + subtitle_uri)
                                        local_replace_sourcepath = "replace/" + media_id + "/"
                                        local_rollback_sourcepath = "rollback/" + media_id + "/"
                                        self.file_manager.validate_dir(self.file_manager.out_path, local_replace_sourcepath) # ensure folder exists
                                        self.file_manager.validate_dir(self.file_manager.out_path, local_rollback_sourcepath) # ensure folder exists
                                        local_replace_sourcepath = self.file_manager.out_path + "/" + local_replace_sourcepath
                                        local_rollback_sourcepath = self.file_manager.out_path + "/" + local_rollback_sourcepath

                                        # Copy vtt from DownloadStorageFiles and rename
                                        fixed_subtitle_input = local_input_directory + subtitle_language + ".vtt"
                                        local_replace_sourcefile = local_replace_sourcepath + subtitle_uri
                                        self.file_manager.log("COPY START [" + media_id + "] Replace preparation " +
                                                              " fixed_subtitle_input: " + fixed_subtitle_input +
                                                              ", local_replace_sourcefile: " + local_replace_sourcefile)
                                        copyfile(fixed_subtitle_input, local_replace_sourcefile)
                                        self.file_manager.log("COPY END [" + media_id + "] Replace preparation " +
                                                              " fixed_subtitle_input: " + fixed_subtitle_input +
                                                              ", local_replace_sourcefile: " + local_replace_sourcefile)

                                        # Download remote vtt file
                                        remote_location = remote_dash_basepath + subtitle_uri
                                        local_rollback_sourcefile = local_rollback_sourcepath + subtitle_uri
                                        self.file_manager.log("COPY START [" + media_id + "] Rollback preparation " +
                                                              " remote_location: " + remote_location +
                                                              ", local_rollback_sourcefile: " + local_rollback_sourcefile)

                                        if self.download(remote_location, local_rollback_sourcefile, remote_dash_storage_host):
                                            self.file_manager.out(media_id + "," + local_replace_sourcefile + "," +
                                                                  remote_dash_storage_host + "," +
                                                                  remote_location,
                                                                  manifest_extension + "_replace.txt")
                                            self.file_manager.out(media_id + "," + local_rollback_sourcefile + "," +
                                                                  remote_dash_storage_host + "," +
                                                                  remote_location,
                                                                  manifest_extension + "_rollback.txt")
                                        else:
                                            self.file_manager.log("FAILED [" + media_id + "]" +
                                                                  " to download source vtt for backup")

                                        self.file_manager.log("COPY END [" + media_id + "] Rollback preparation " +
                                                              " remote_location: " + remote_location +
                                                              ", local_rollback_sourcefile: " + local_rollback_sourcefile)

                                    else:
                                        self.file_manager.log("SKIP [" + media_id + "] Subtitle has empty values" +
                                                              " subtitle_language: " + subtitle_language +
                                                              ", subtitle_uri: " + subtitle_uri)

                    else:
                        self.file_manager.log("SKIP [" + media_id + "] (do not exist) local_media_dash:" + local_media_dash)

                    if count_match == 0:
                        self.file_manager.log("SKIP [" + media_id + "] Manifest doesn't have subtitles, mediaId: " + media_id)

        self.file_manager.log("--END -- :" + input_file)
        return True

    def getNodeByName(self, nodes, name):
        if nodes:
            for node in nodes.childNodes:
                if node.nodeName == name:
                    return node
        return None

    def getNodeText(self, nodes):
        if nodes:
            for node in nodes.childNodes:
                if node.wholeText:
                    return node.wholeText
        return ""

    def download(self, source_file, destination_file, profile_tag):
        is_success = True
        try:
            if self.ftp_config.profile_tag != profile_tag:
                if self.ftp is not None:
                    self.ftp.quit()
                self.ftp_config.load(profile_tag) # load storage_host as profile_tag
                self.ftp = ftplib.FTP(self.ftp_config.host)
                self.ftp.login(self.ftp_config.username, self.ftp_config.password)

            # local_filepath = self.file_manager.get_outfile(destination_file)
            local_file = open(destination_file, 'wb')
            self.file_manager.log("Download: " + source_file + " >> " +
                                  self.ftp.retrbinary('RETR ' + source_file, local_file.write))
            local_file.close()
        except ftplib.error_perm:
            err_msg = "ERROR FTP file does not exist, filepath:" + source_file
            self.file_manager.log(err_msg)
            self.file_manager.out(err_msg, FILE_ERROR_OUT)
            self.file_manager.delete_outfile(destination_file)
            is_success = False
        except ftplib.all_errors:
            err_msg = "ERROR FTP all errors, filepath:" + source_file
            self.file_manager.log(err_msg)
            self.file_manager.out(err_msg, FILE_ERROR_OUT)
            self.file_manager.delete_outfile(destination_file)
            is_success = False

        return is_success


def path_form(first, *entries):
    final_entries = []

    def work_of_magic(value):
        items = value.split('/')
        for item in items:
            if item is not '':
                final_entries.append(item)

    if first is not '':
        first_items = first.split('/')
        if first_items[0] is '':
            final_entries.append('')

    work_of_magic(first)

    for entry in entries:
        work_of_magic(entry)

    return '/'.join(final_entries)

# folder = "00001-01000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "01001-02000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "02001-03000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "03001-04000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "04001-05000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "05001-06000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "06001-07000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "07001-08000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "08001-09000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "09001-10000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "10001-11000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "11001-12000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "12001-13000"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
folder = "13001-14000"
instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly-prep-dash-cont.txt",
             ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "14001-14355"
# instance = PreparingSubtitlesDASH7(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")

exit(0)