import hashlib
import json
import lzma
import os
import shutil
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import zipfile

import requests

import classes as cl
from utils.config import cfg
import utils.logger as logger


user_agent = "mcdownloader"

launcher_meta_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
multimc_meta_url = 'https://meta.multimc.org/v1/'


def write_json(data, json_file):
    json_file.seek(0)
    json.dump(data, json_file, indent=4)
    json_file.truncate()


def list_intersect(lst1, lst2):
    return list(set(lst1) & set(lst2))


def download(url, save_location, hash_=None, hash_type=None, force=False):
    try:
        if not force and os.path.isfile(save_location) and hash_ is None:
            logger.log('i', f'{save_location} already downloaded')
            return True
        elif not force and os.path.isfile(save_location) and hash_ and hash_type and check_hash(save_location, hash_,
                                                                                                hash_type):
            logger.log('i', f'{save_location} already downloaded')
            # print(f'{save_location} already downloaded')
            return True
        # print(f'Downloading {save_location}')
        logger.log('i', f'Downloading {save_location}')
        os.makedirs(os.path.dirname(save_location), exist_ok=True)
        r = requests.get(url, allow_redirects=True, headers={'User-Agent': cfg.user_agent['agent'],
                                                             'From': cfg.user_agent['author']})
        open(save_location, 'wb').write(r.content)
        return True
    except Exception as e:
        logger.log('e', f'Failed to download file from {url}')
        # print(f"Warning! Failed to download file from {url}")
        return False


def download_indexes():
    downloaded_indexes = []

    if download(launcher_meta_url, 'indexes/launcher_meta.json'):  # , force=True):
        downloaded_indexes.append('launcher_meta')
    if download(multimc_meta_url, 'indexes/multimc_meta.json'):  # , force=True):
        downloaded_indexes.append('multimc_meta')

    for package in json.loads(read_text('indexes/multimc_meta.json'))['packages']:
        if download(f'https://meta.multimc.org/v1/{package["uid"]}', f'indexes/{package["uid"]}.json',
                    package['sha256'], 'sha256', force=False):
            downloaded_indexes.append(package['uid'])

    return downloaded_indexes


def read_text(path):
    if not os.path.isfile(path):
        return None
    file = open(path)
    text = file.read()  # .replace("\n", " ")
    file.close()
    return text


def get_hash(path, hash_type):
    # source: https://stackoverflow.com/a/44873382
    h = None
    if hash_type == 'md5':
        h = hashlib.md5()
    elif hash_type == 'sha1':
        h = hashlib.sha1()
    elif hash_type == 'sha256':
        h = hashlib.sha256()
    if h is None:
        return
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    # print(h.hexdigest())
    return h.hexdigest()


def check_hash(path, hash_, hash_type):
    # print('.' + hash_ + '.')
    return get_hash(path, hash_type) == hash_


def get_mc_versions():
    return json.loads(read_text('indexes/launcher_meta.json'))['versions']


def get_mc_version_type(t):
    if t not in ['release', 'old_beta', 'old_alpha', 'snapshot']:
        return None
    res = []
    for version in get_mc_versions():
        if version['type'] == t:
            res.append(version)
    return res


def get_mc_ids_by_type(*args):
    arg_list = [item for item in args]
    if len(list_intersect(['release', 'old_beta', 'old_alpha', 'snapshot'], arg_list)) == 0:
        return None
    res = []
    for version in get_mc_versions():
        if version['type'] in arg_list:
            res.append(version['id'])
    return res


def get_mc_version_from_id(id_):
    for version in get_mc_versions():
        if version['id'] == id_:
            return version


# unused
def smart_grid(frame, *args, **kwargs):  # *args are the widgets!
    starting_index = kwargs.pop('starting_index', 0)
    frame.update()
    frame_width = frame.winfo_width()
    print(f'frame_width: {frame_width}')
    row = starting_index
    added = []

    def added_width():
        frame.update()
        sum_ = 0
        for e in added:
            e.update()
            sum_ += e.winfo_width() + 10
        return sum_

    for btn in args:
        # frame.update()
        btn_width = 80  # btn.winfo_width()
        # print(f'btn_width: {btn_width}')
        # print(f'added_width: {added_width()}')
        # print('-------')
        if added_width() + btn_width > frame.winfo_width() - 10:
            added = []
            row += 1
        # else:
        # btn.pack()
        btn.grid(row=row, column=len(added))
        added.append(btn)

    frame.update_idletasks()  # update() #


# unused
def place_checkboxes(s, handle_version_check, snapshots=False, alphas=False, betas=False):
    for version in get_mc_versions():
        if version['type'] == 'release':
            found = False
            for cb in s.version_checkboxes:
                if version['id'] == cb.cget('text'):
                    found = True
                    break
            if found:
                continue
            s.version_checkboxes_vars.append(tk.IntVar())
            s.version_checkboxes.append(ttk.Checkbutton(master=s.scrw_mc_versions.element_frame, text=version['id'],
                                                        variable=s.version_checkboxes_vars[-1], onvalue=1, offvalue=0,
                                                        command=lambda version_=version,
                                                                       cb_var=s.version_checkboxes_vars[
                                                                           -1]: handle_version_check(s, version_['id'],
                                                                                                     cb_var)))
        elif version['type'] == 'snapshot':
            index = None
            for i in range(len(s.version_checkboxes)):
                if version['id'] == s.version_checkboxes[i].cget('text'):
                    index = i
                    break
            if index:
                if not snapshots:
                    s.version_checkboxes[index].grid_forget()
                    del s.version_checkboxes[index]
                    del s.version_checkboxes_vars[index]
                continue
            elif snapshots:
                s.version_checkboxes_vars.append(tk.IntVar())
                s.version_checkboxes.append(
                    ttk.Checkbutton(master=s.scrw_mc_versions.element_frame, text=version['id'],
                                    variable=s.version_checkboxes_vars[-1],
                                    onvalue=1, offvalue=0, command=lambda version_=version,
                                                                          cb_var=s.version_checkboxes_vars[
                                                                              -1]: handle_version_check(s,
                                                                                                        version_['id'],
                                                                                                        cb_var)))
        elif version['type'] == 'old_alpha':
            index = None
            for i in range(len(s.version_checkboxes)):
                if version['id'] == s.version_checkboxes[i].cget('text'):
                    index = i
                    break
            if index:
                if not alphas:
                    s.version_checkboxes[index].grid_forget()
                    del s.version_checkboxes[index]
                    del s.version_checkboxes_vars[index]
                continue
            elif alphas:
                s.version_checkboxes_vars.append(tk.IntVar())
                s.version_checkboxes.append(
                    ttk.Checkbutton(master=s.scrw_mc_versions.element_frame, text=version['id'],
                                    variable=s.version_checkboxes_vars[-1],
                                    onvalue=1, offvalue=0, command=lambda version_=version,
                                                                          cb_var=s.version_checkboxes_vars[
                                                                              -1]: handle_version_check(s,
                                                                                                        version_['id'],
                                                                                                        cb_var)))
        elif version['type'] == 'old_beta':
            index = None
            for i in range(len(s.version_checkboxes)):
                if version['id'] == s.version_checkboxes[i].cget('text'):
                    index = i
                    break
            if index:
                if not betas:
                    s.version_checkboxes[index].grid_forget()
                    del s.version_checkboxes[index]
                    del s.version_checkboxes_vars[index]
                continue
            elif betas:
                s.version_checkboxes_vars.append(tk.IntVar())
                s.version_checkboxes.append(
                    ttk.Checkbutton(master=s.scrw_mc_versions.element_frame, text=version['id'],
                                    variable=s.version_checkboxes_vars[-1],
                                    onvalue=1, offvalue=0, command=lambda version_=version,
                                                                          cb_var=s.version_checkboxes_vars[
                                                                              -1]: handle_version_check(s,
                                                                                                        version_['id'],
                                                                                                        cb_var)))
    clear_checkboxes(s.version_checkboxes)
    for i in range(len(s.version_checkboxes)):
        s.version_checkboxes[i].grid(row=i, column=0)


# unused
def clear_checkboxes(version_checkboxes):
    for cb in version_checkboxes:
        cb.grid_forget()


# unused
def select_all(s, var_cb_select_all):
    for var in s.version_checkboxes_vars:
        var.set(var_cb_select_all.get())
    if var_cb_select_all.get():
        for cb in s.version_checkboxes:
            if not cb['text'] in s.selected_versions:
                s.selected_versions.append(cb['text'])
    else:
        s.selected_versions = []


def get_forge_versions():
    return json.loads(read_text('indexes/net.minecraftforge.json'))['versions']


def get_forge_versions_for_mc_ver(mcversion):
    res = []
    for ver in get_forge_versions():
        for req in ver['requires']:
            if req['uid'] == 'net.minecraft' and req['equals'] == mcversion:
                res.append(ver['version'])
    return res


def get_fabric_mappings():
    return json.loads(read_text('indexes/net.fabricmc.intermediary.json'))['versions']


def get_fabric_versions():
    return json.loads(read_text('indexes/net.fabricmc.fabric-loader.json'))['versions']


def get_fabric_versions_for_mc_ver(mcversion):
    found = False
    for ver in get_fabric_mappings():
        for req in ver['requires']:
            if req['uid'] == 'net.minecraft' and req['equals'] == mcversion:
                found = True
    if not found:
        return []
    res = []
    for ver in get_fabric_versions():
        res.append(ver['version'])
    return res


def get_liteloader_versions():
    return json.loads(read_text('indexes/com.mumfrey.liteloader.json'))['versions']


def get_liteloader_versions_for_mc_ver(mcversion):
    res = []
    for ver in get_liteloader_versions():
        for req in ver['requires']:
            if req['uid'] == 'net.minecraft' and req['equals'] == mcversion:
                res.append(ver['version'])
    return res


def download_selected(s):
    if len(s.mc_selector.get_loader_data('minecraft')['versions']) == 0:
        return
    dl_helper = cl.DownloadHelper()
    if len(s.mc_selector.get_loader_data('minecraft')['versions']) == 1:
        mc_data = s.mc_selector.get_loader_data('minecraft')
        mc_version = mc_data['versions'][0]
        mc_options = mc_data['options']
        if 'client' in mc_options:
            dl_helper.queue_mc_client_jar(mc_version)
        if 'server' in mc_options:
            dl_helper.queue_mc_server_jar(mc_version)
        if 'assets' in mc_options:
            dl_helper.queue_mc_assets(mc_version)
        if 'libs' in mc_options:
            dl_helper.queue_mc_libraries(mc_version)

        forge_data = s.mc_selector.get_loader_data('forge')
        forge_versions = forge_data['versions']
        forge_options = forge_data['options']
        if 'client' in forge_options:
            for version in forge_versions:
                dl_helper.queue_forge_client(mc_version, version)
    else:
        pass

    dl_helper.download_queue(s)


def update_mc_version_jsons(s):
    for ver in get_mc_versions():
        s.lbl_download_progress.config(
            text=f'Downloading version json {ver["url"]}')
        download(ver['url'], os.path.join(cfg.data_location, 'minecraft/version_indexes', ver['id'] + '.json'),
                 force=True)
        s.lbl_download_progress.update()
    s.lbl_download_progress.config(
        text='Finished downloading mc version jsons')


def inject_log4j_xml(path):
    xml_text = read_text(path)
    first_inject = '\n<Properties><Property name="logDir">${sys:log.dir}</Property></Properties>'
    second_inject = '\n<RollingRandomAccessFile name="File" fileName="${logDir}/latest.log" filePattern="${logDir}/%d{' \
                    'yyyy-MM-dd}-%i.log.gz"> '
    first_inject_start = xml_text.find('<Configuration status="WARN">') + len('<Configuration status="WARN">')
    second_inject_start = xml_text.find('</Console>') + len('</Console>')
    second_inject_end = xml_text.find('<PatternLayout')
    res = xml_text[
          :first_inject_start] + first_inject + xml_text[
                                                         first_inject_start
                                                         :second_inject_start] + second_inject + xml_text[
                                                                                                    second_inject_end:]
    with open(path, "w") as f:
        f.write(res)


def extract_lzma(archive, output):
    with open(output, 'wb+') as f:
        with lzma.open(archive) as a:
            content = a.read()
            f.write(content)


def safe_delete(file):
    if os.path.exists(file):
        try:
            if os.path.isfile(file):
                os.remove(file)
            else:
                shutil.rmtree(file)
        except:
            logger.log('e', f'Failed to delete {file}')
    else:
        logger.log('w', f'Failed to find file to delete {file}')


def install_forge_from_queue(mc_version, forge_version, download_queue_list):
    def download_minecraft():
        download(get_mc_version_from_id(mc_version)['url'], os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                                         mc_version + '.json'))
        data = json.loads(read_text(os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                 mc_version + '.json')))
        url = data['downloads'][side]['url']
        hash_ = data['downloads'][side]['sha1']
        path = os.path.join(cfg.data_location, 'minecraft/versions', mc_version, side.capitalize(), mc_version + '.jar')
        download(url, path, hash_=hash_, hash_type='sha1')
    """if side not in ['client', 'server']:
        logger.log('w', 'Ignoring Forge installation, unknown side')
        return"""
    # download_minecraft()

    forge_installer_base_url = 'https://maven.minecraftforge.net/net/minecraftforge/forge'
    forge_installer_url = f'{forge_installer_base_url}/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar'
    installer_path = os.path.join(cfg.data_location, 'forge/installers', mc_version, forge_version + '.jar')
    if not download(forge_installer_url, installer_path):
        logger.log('e', f'Could not download forge {forge_version}')
        return

    subprocess.call([cfg.java_location, r'-jar', installer_path, r'--installServer',
                     os.path.join(cfg.data_location, 'libs')])

    with zipfile.ZipFile(installer_path, 'r') as zip_obj:
        zip_obj.extract('version.json', os.path.join(cfg.data_location, 'forge/version_indexes',
                                                     f'{mc_version}-{forge_version}.json'))

    leftovers = [
        os.path.join(cfg.data_location, 'libs/run.bat'),
        os.path.join(cfg.data_location, 'libs/run.sh'),
        os.path.join(cfg.data_location, 'libs/user_jvm_args.txt'),
        os.path.join(cfg.data_location, 'libs/config'),
        os.path.join(cfg.data_location, 'libs/defaultconfigs')
    ]
    for file in leftovers:
        safe_delete(file)
