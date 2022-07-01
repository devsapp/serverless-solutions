import json
import os
import subprocess
import time

name = "publish.yaml"


def get_version(name):
    version = ""
    with open(name, "r") as f:
        line = f.readline()
        while line:
            if len(line.strip()) > 0:
                if line.find('Version') > -1:
                    version = line.split(':')[1].strip()
                    return version
            line = f.readline()


def seek_publish(dir, name):
    file_list = {}
    for root, _, files in os.walk(dir):
        if name in files:
            version = get_version(root + "/" + name)
            print(root, version)
            file_list[root] = version
    return file_list


root_dir = os.getcwd()
publish_list = seek_publish('./', name)
with open('version.md', "w") as f:
    for key, value in publish_list.items():
        f.write('%s %s\n' % (key, value))

publish_max_retries = 3
for app_path in publish_list:
    publish_retries = 1
    print("------------------------------------------------------------------------------------------------------------")
    print("Publishing", app_path, publish_list[app_path])
    os.chdir(root_dir)
    while publish_retries <= publish_max_retries:
        # publish_script = 'https://serverless-registry.oss-cn-hangzhou.aliyuncs.com/publish-file/python3/hub-publish.py'
        # command = 'cd %s && wget %s && python hub-publish.py' % (app_path, publish_script)
        command = 'python registry.py %s' % (app_path)
        child = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, )
        stdout, stderr = child.communicate()
        if child.returncode == 0:
            print("stdout:", app_path, stdout.decode("utf-8"))
            break
        else:
            time.sleep(3)
            if publish_retries == publish_max_retries:
                print("stdout:", app_path, stdout.decode("utf-8"))
                print("stderr:", app_path, stderr.decode("utf-8"))
        publish_retries = publish_retries + 1
