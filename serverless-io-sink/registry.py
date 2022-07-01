import json
import os
import sys
import zipfile

import requests


def get_content(file_list):
    for eveFile in file_list:
        try:
            with open(eveFile) as f:
                return f.read()
        except:
            pass
    return None


def path_is_parent(parent_path, child_path):
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])


def is_ignored(target_path, ignores):
    for ignore in ignores:
        if os.path.relpath(target_path, ignore) == '.' or path_is_parent(ignore, target_path):
            return True
    return False


os.chdir(sys.argv[1])
publish_url = "https://registry.devsapp.cn/package/publish"
publish = get_content(['./publish.yaml', './publish.yml'])
readme = get_content(['./readme.md', './README.md', './README.MD'])
version_body = get_content(['./version.md', './VERSION.md', './VERSION.MD'])
ignores_content = get_content(['./.signore', './.SIGNORE'])
syaml = get_content(['./src/s.yaml', './src/s.yml'])
ignores_list = []
resolved_ignores_list = []
default_ignore_list = ['./.git', './.github',
                       './.idea', './.DS_Store', './.vscode']

if ignores_content is not None:
    ignores_list = ignores_content.split('\n')
    resolved_ignores_list = list(
        filter(None, set(ignores_list + default_ignore_list)))
else:
    resolved_ignores_list = default_ignore_list

data = {
    "safety_code": os.environ.get("publish_token"),
    "publish": publish,
    "version_body": version_body,
    "readme": readme,
    "syaml": syaml
}

try:
    response = requests.post(url=publish_url, data=data,
                             verify=False).content.decode("utf-8")
except requests.exceptions.RequestException as err:
    raise SystemExit(err)
print(response)

response = json.loads(response)['Response']
if 'url' not in response.keys():
    print(response)
    exit()

upload_url = response['url']
with zipfile.ZipFile('package.zip', mode="w") as f:
    for dirpath, dirnames, filenames in os.walk('./'):
        if dirpath != './' and is_ignored(dirpath, resolved_ignores_list):
            continue
        for filename in filenames:
            absoult_file_path = os.path.join(dirpath, filename)
            if not is_ignored(absoult_file_path,
                              resolved_ignores_list) and "hub-publish.py" not in filename and "package.zip" not in filename:
                f.write(os.path.join(dirpath, filename), os.path.join(
                    "devsapp-package/" + dirpath, filename))

with open("./package.zip", 'rb') as f:
    files = f.read()

print(requests.put(url=upload_url, data=files, verify=False, timeout=6000).content)
