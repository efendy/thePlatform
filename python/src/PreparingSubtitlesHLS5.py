#!/usr/bin/env python3
import os
import ftplib
import datetime
from utils.FileManager import FileManager
from utils.FTPConfig import FTPConfig

ROOT = os.path.realpath(__file__).split("/src/")[0]
SCRIPT_NAME = os.path.basename(__file__).split(".")[0]
UNIQUE_RUN_ID = "caf1aeb2-52b0-47d8-b37d-5a7f39f4da59"
FILE_ERROR_OUT = SCRIPT_NAME + ".error.txt"


class PreparingSubtitlesHLS5:
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

                    manifest_extension = "m3u8"
                    local_media_hls = local_input_directory + "manifest." + manifest_extension
                    remote_hls_storage_host = ""
                    remote_hls_basepath = ""
                    manifest_info_file = local_input_directory + manifest_extension + "_info.txt"
                    with open(manifest_info_file, "r") as hls_basepath_file:
                        self.file_manager.log("OPEN [" + media_id + "] manifest_info_file:" + manifest_info_file)
                        for hls_basepath_line in hls_basepath_file:
                            self.file_manager.log("READLN [" + media_id + "] hls_basepath_line:" + hls_basepath_line)
                            hls_basepath_line = str(hls_basepath_line).replace('\n', '')
                            remote_hls_storage_host = hls_basepath_line.split(",")[0]
                            remote_hls_basepath = hls_basepath_line.split(",")[1]
                            self.file_manager.log("STORE [" + media_id + "] " +
                                                  "remote_hls_storage_host:" + input_file +
                                                  ", remote_hls_storage_host:" + input_directory)

                    count_match = 0
                    if os.path.exists(local_media_hls):
                        self.file_manager.log("CONTINUE [" + media_id + "] (exists) local_media_hls:" + local_media_hls)
                        with open(local_media_hls) as manifest_hls_file:
                            for manifest_hls_line in manifest_hls_file:
                                manifest_hls_line = str(manifest_hls_line).replace('\n', '')
                                #EXT-X-MEDIA:TYPE=SUBTITLES
                                # 27chars
                                if manifest_hls_line.find("EXT-X-MEDIA:TYPE=SUBTITLES") >= 0:
                                    count_match += 1
                                    cue_time = datetime.datetime(100,1,1,0,0,0)
                                    cue_time_minute = -1
                                    subtitle_language = self.getValue(manifest_hls_line, "LANGUAGE")
                                    subtitle_segment_uri = self.getValue(manifest_hls_line, "URI")
                                    subtitle_segment_uri_layers = str(subtitle_segment_uri).split("/")

                                    if subtitle_language and subtitle_segment_uri and len(subtitle_segment_uri_layers) == 2:
                                        self.file_manager.log("PROCESS [" + media_id + "]" +
                                                              " subtitle_language: " + subtitle_language +
                                                              ", subtitle_segment_uri: " + subtitle_segment_uri)

                                        subtitle_segment_dir = subtitle_segment_uri_layers[0]
                                        subtitle_segment_file = subtitle_segment_uri_layers[1]

                                        remote_vtt_basepath = remote_hls_basepath + subtitle_segment_dir + "/"
                                        local_replace_basepath = "replace/" + media_id + "/"
                                        local_rollback_basepath = "rollback/" + media_id + "/"
                                        local_replace_sourcepath = local_replace_basepath + subtitle_language + "/"
                                        local_rollback_sourcepath = local_rollback_basepath + subtitle_language + "/"
                                        self.file_manager.validate_dir(self.file_manager.out_path, local_replace_sourcepath) # ensure folder exists
                                        self.file_manager.validate_dir(self.file_manager.out_path, local_rollback_sourcepath) # ensure folder exists
                                        local_replace_base_fullpath = self.file_manager.out_path + "/" + local_replace_basepath
                                        local_rollback_base_fullpath = self.file_manager.out_path + "/" + local_rollback_basepath
                                        local_replace_source_fullpath = self.file_manager.out_path + "/" + local_replace_sourcepath
                                        local_rollback_source_fullpath = self.file_manager.out_path + "/" + local_rollback_sourcepath

                                        # download m3u8 subtitle segments to local (save as language code)
                                        remote_location = remote_hls_basepath + subtitle_segment_uri
                                        local_replace_subtitle_segment = local_replace_source_fullpath + subtitle_segment_file
                                        if self.download(remote_location, local_replace_subtitle_segment, remote_hls_storage_host):
                                            self.file_manager.log("DOWNLOAD [" + media_id + "] Subtitle Segment " +
                                                                  " remote_hls_storage_host: " + remote_hls_storage_host +
                                                                  ", subtitle_language: " + subtitle_language +
                                                                  ", remote_location: " + remote_location +
                                                                  ", local_replace_subtitle_segment: " + local_replace_subtitle_segment)
                                            fixed_subtitle_input = local_input_directory + subtitle_language + ".vtt"

                                            # parse and stored fixed time interval into array list
                                            list_of_time_intervals = []
                                            with open(fixed_subtitle_input) as fixed_subtitle_input_file:
                                                for fixed_subtitle_input_line in fixed_subtitle_input_file:
                                                    if fixed_subtitle_input_line.find(" --> ") >= 0:
                                                        list_of_time_intervals.append(fixed_subtitle_input_line)

                                            time_interval_index = 0
                                            # find remote webvtt to local
                                            with open(local_replace_subtitle_segment) as local_replace_subtitle_segment_file:
                                                for local_replace_subtitle_segment_line in local_replace_subtitle_segment_file:
                                                    local_replace_subtitle_segment_line = str(local_replace_subtitle_segment_line).replace('\n', '')

                                                    if local_replace_subtitle_segment_line.find(".webvtt") >= 0:
                                                        subtitle_uri = local_replace_subtitle_segment_line
                                                        # download remote webvtt to local for rollback
                                                        remote_vtt_location = remote_vtt_basepath + subtitle_uri
                                                        local_rollback_vtt_sourcefile = local_rollback_source_fullpath + subtitle_uri
                                                        self.file_manager.log("PROCESS [" + media_id + "] Rollback preparation - START " +
                                                                              " remote_vtt_location: " + remote_vtt_location +
                                                                              ", local_rollback_vtt_sourcefile: " + local_rollback_vtt_sourcefile)
                                                        if self.download(remote_vtt_location, local_rollback_vtt_sourcefile, remote_hls_storage_host):
                                                            self.file_manager.out(media_id + "," + local_rollback_vtt_sourcefile + "," +
                                                                                  remote_hls_storage_host + "," +
                                                                                  remote_vtt_location,
                                                                                  manifest_extension + "_rollback.txt")
                                                        else:
                                                            self.file_manager.log("FAILED [" + media_id + "]" +
                                                                                  " to download source vtt for backup" +
                                                                                  ", subtitle_language: " + subtitle_language +
                                                                                  ", remote_hls_storage_host: " + remote_hls_storage_host +
                                                                                  ", remote_vtt_location: " + remote_vtt_location)

                                                        self.file_manager.log("PROCESS [" + media_id + "] Rollback preparation - END ")

                                                        if os.path.exists(local_rollback_vtt_sourcefile):
                                                            # preparing replace files
                                                            local_replace_vtt_sourcefile = local_replace_source_fullpath + subtitle_uri
                                                            self.file_manager.log("PROCESS [" + media_id + "] Replace preparation - START" +
                                                                                  ", local_replace_vtt_sourcefile: " + local_replace_vtt_sourcefile)
                                                            with open(local_rollback_vtt_sourcefile) as local_rollback_vtt_file:
                                                                # write to local_replace_vtt_sourcefile
                                                                cue_time_minute += 1
                                                                for local_rollback_vtt_line in local_rollback_vtt_file:
                                                                    line_entry = local_rollback_vtt_line
                                                                    if local_rollback_vtt_line.find(" --> ") >= 0:
                                                                        line_entry = list_of_time_intervals[time_interval_index]
                                                                        time_interval_index += 1
                                                                    if local_rollback_vtt_line.find("LOCAL:00:00:00.000")  >= 0:
                                                                        idt = cue_time + datetime.timedelta(minutes=cue_time_minute)
                                                                        header_local = "LOCAL:" + idt.strftime("%H:%M:%S.000")
                                                                        line_entry = local_rollback_vtt_line.replace("LOCAL:00:00:00.000", header_local)

                                                                    line_entry = line_entry.replace("\n","")
                                                                    self.file_manager.out(line_entry, local_replace_sourcepath + subtitle_uri)

                                                            self.file_manager.out(media_id + "," + local_replace_vtt_sourcefile + "," +
                                                                                  remote_hls_storage_host + "," +
                                                                                  remote_vtt_location,
                                                                                  manifest_extension + "_replace.txt")


                                                        self.file_manager.log("PROCESS [" + media_id + "] Replace preparation - END")
                                        else:
                                            self.file_manager.log("FAILED [" + media_id + "]" +
                                                                  " to download subtitle segment for further processing" +
                                                                  " remote_hls_storage_host: " + remote_hls_storage_host +
                                                                  ", remote_location: " + remote_location)
                                    else:
                                        self.file_manager.log("SKIP [" + media_id + "] Subtitle has empty values" +
                                                              " subtitle_language: " + subtitle_language +
                                                              ", subtitle_segment_uri: " + subtitle_segment_uri)
                    else:
                        self.file_manager.log("FAILED [" + media_id + "]" +
                                              " cannot find local HLS file URI:" + local_media_hls)

                    if count_match == 0:
                        self.file_manager.log("SKIP [" + media_id + "] Manifest doesn't have subtitles, mediaId: " + media_id)

        self.file_manager.log("--END -- :" + input_file)
        return True

    def getValue(self, line, key):
        if line:
            arr = str(line).split(",")
            for item in arr:
                if item.startswith(key):
                    keyval = item.split("=")
                    if len(keyval) == 2:
                        return keyval[1].replace("\"", "")
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

folder = "12001-13000"
instance = PreparingSubtitlesHLS5(UNIQUE_RUN_ID+"/"+folder)
instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.final.txt",
             ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "13001-14000"
# instance = PreparingSubtitlesHLS5(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.final.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")
# folder = "14001-14355"
# instance = PreparingSubtitlesHLS5(UNIQUE_RUN_ID+"/"+folder)
# instance.run(ROOT+"/in/DownloadStorageFiles/"+folder+"/mediaIds-valid-idonly.final.txt",
#              ROOT+"/out/DownloadStorageFiles/"+UNIQUE_RUN_ID+"/")

exit(0)