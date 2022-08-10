# -*- coding: utf-8 -*-
import gzip
import os
import logging

logger = logging.getLogger()

def compress_file_with_gzip(client, path, file_name, data):
    try:
        os.chdir('/tmp')
        # init file param
        local_gzip_file = file_name + ".gz"
        remote_gzip_file= path + local_gzip_file

        # gzip local file
        gzf = gzip.GzipFile(filename="", mode='wb', compresslevel=9, fileobj=open(local_gzip_file, 'wb'))
        gzf.write(data.encode('utf-8'))
        gzf.close()

        # upload local gzip file to oss
        return client.put_object_from_file(remote_gzip_file, local_gzip_file)
    except Exception as e:
        logger.info(e)
        raise e