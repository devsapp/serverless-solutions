# -*- coding: utf-8 -*-
import snappy
import os
import logging

logger = logging.getLogger()

def compress_file_with_hadoop_snappy(client, file_name, data):
    try:
        os.chdir('/tmp')
        # init file param
        local_snappy_file = file_name + ".snappy"
        remote_snappy_file= local_snappy_file

        # create a local file and append data
        f = open(file_name, "w+")
        f.write(data)
        f.close()

        # compress local file with snappy
        with open(file_name, 'rb') as in_file, open(local_snappy_file, 'wb') as out_file:
            snappy.hadoop_stream_compress(in_file, out_file)
            in_file.close()
            out_file.close()

        # upload local snappy file to oss
        return client.put_object_from_file(remote_snappy_file, local_snappy_file)
    except Exception as e:
        logger.error(e)
        raise e

