#!/usr/bin/env python3
#
import os
import ftplib
from src.utils.FileManager import FileManager
from src.utils.FTPConfig import FTPConfig

ROOT = os.path.realpath(__file__).split("/src/")[0]
SCRIPT_NAME = os.path.basename(__file__).split(".")[0]
UNIQUE_RUN_ID = "caf1aeb2-52b0-47d8-b37d-5a7f39f4da59"
FILE_ERROR_OUT = SCRIPT_NAME + ".error.txt"


class DownloadStorageFiles5:
    file_manager = None
    ftp_config = None
    ftp = None

    def __init__(self):
        self.file_manager = FileManager(SCRIPT_NAME, self.__class__.__name__, UNIQUE_RUN_ID)
        self.ftp_config = FTPConfig(ROOT+"/resources/DownloadStorageFiles/ftp.ini", SCRIPT_NAME, UNIQUE_RUN_ID)

    def download(self, input_file):
        self.file_manager.log("--Download START -- :" + input_file)
        with open(input_file, "r") as f:
            for line in f:
                line_path = str(line).replace('\n', '')
                data = str(line_path).split(',')
                if len(data) >= 3:
                    media_id = data[0]
                    self.file_manager.validate_dir(self.file_manager.out_path, media_id + "/") # ensure folder exists

                    storage_filehost = data[1]
                    storage_filepath = data[2]

                    source_filename = storage_filepath.split('/')[-1]
                    source_basepath = storage_filepath.replace(source_filename,'')

                    # file_name = source_filename.split('.')[0]
                    file_extension = source_filename.split('.')[-1]

                    # local_filename = source_filename
                    local_filename = "manifest." + file_extension
                    if len(data) == 4:
                        local_filename = data[3] + "." + file_extension
                    else:
                        self.file_manager.out(storage_filehost + "," + source_basepath, media_id + "/" + file_extension+"_info.txt", True)

                    try:
                        if self.ftp_config.profile_tag != storage_filehost:
                            if self.ftp is not None:
                                self.ftp.quit()
                            self.ftp_config.load(storage_filehost) # load storage_host as profile_tag
                            self.ftp = ftplib.FTP(self.ftp_config.host)
                            self.ftp.login(self.ftp_config.username, self.ftp_config.password)

                        local_filepath = self.file_manager.get_outfile(media_id + "/" + local_filename)
                        local_file = open(local_filepath, 'wb')
                        self.file_manager.log("Download: " + storage_filepath + " >> " +
                                              self.ftp.retrbinary('RETR ' + storage_filepath, local_file.write))
                        local_file.close()
                    except ftplib.error_perm:
                        err_msg = "FTP file does not exist,mediaId:" + media_id + ",filepath:" + storage_filepath
                        self.file_manager.log(err_msg)
                        self.file_manager.out(err_msg, FILE_ERROR_OUT)
                        self.file_manager.delete_outfile(media_id + "/" + local_filename)
                    except ftplib.all_errors:
                        err_msg = "FTP all errors,mediaId:" + media_id
                        self.file_manager.log(err_msg)
                        self.file_manager.out(err_msg, FILE_ERROR_OUT)
                        self.file_manager.delete_outfile(media_id + "/" + local_filename)

                else:
                    self.file_manager.log("Line data not enough info:" + line_path)
                    self.file_manager.out("Line data not enough info:" + line_path, FILE_ERROR_OUT)

        self.file_manager.log("--Download END -- :" + input_file)


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

dsf = DownloadStorageFiles5()
# folder = "00001-00002" # Trial
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "00001-01000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "01001-02000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "02001-03000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "03001-04000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "04001-05000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "05001-06000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "06001-07000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "07001-08000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "08001-09000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "09001-10000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH-cont.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "10001-11000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "11001-12000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "12001-13000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "13001-14000"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")
# folder = "14001-14355"
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-DASH.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/manifest-HLS.txt")
# dsf.download(ROOT+"/in/DownloadStorageFiles/"+folder+"/subtitles.txt")

exit(0)

