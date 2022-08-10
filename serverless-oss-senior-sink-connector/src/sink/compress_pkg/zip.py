# -*- coding: utf-8 -*-
import zipfile
import os
import logging

logger = logging.getLogger()

def compress_file_with_zip(client, path, file_name, data):
    try:
        os.chdir('/tmp')
        # init file param
        local_zip_file = file_name + ".zip"
        remote_zip_file= path + local_zip_file

        # create a local file and append data
        f = open(file_name, "w+")
        f.write(data)
        f.close()

        # zip local file
        zf = zipfile.ZipFile(local_zip_file, 'w', zipfile.ZIP_DEFLATED)
        zf.write(file_name)
        zf.close()

        # upload local zip file to oss
        return client.put_object_from_file(remote_zip_file, local_zip_file)
    except Exception as e:
        logger.info(e)
        raise e

