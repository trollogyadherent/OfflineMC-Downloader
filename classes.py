import json
import math
import os
import platform
import tkinter as tk
import tkinter.ttk as ttk

import functions as fn
import constants as cn
from utils.config import cfg
import utils.logger as logger


# Thanks to:
# https://gist.github.com/JackTheEngineer/81df334f3dcff09fd19e4169dd560c59
# https://github.com/flatplanet/Intro-To-TKinter-Youtube-Course/blob/master/full_scroll.py
class ScrollableWidget(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.wrapper = tk.Frame(self)
        self.wrapper.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.wrapper)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.canvas.bind('<Enter>', lambda e: self._bind_to_mousewheel(e))
        self.canvas.bind('<Leave>', lambda e: self._unbind_from_mousewheel(e))
        self.scrollbar = ttk.Scrollbar(self.wrapper, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.element_frame = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.element_frame, anchor="nw")

    def _on_mousewheel_win(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_other(self, scroll):
        self.canvas.yview_scroll(int(scroll), "units")

    def _bind_to_mousewheel(self, event):
        if platform.system() == 'Windows':
            self.canvas.bind_all("<MouseWheel>", lambda e=event: self._on_mousewheel_win(e))
        else:
            self.canvas.bind_all("<Button-4>", lambda scroll=-1: self._on_mousewheel_other(scroll))
            self.canvas.bind_all("<Button-5>", lambda scroll=1: self._on_mousewheel_other(scroll))

    def _unbind_from_mousewheel(self, event):
        if platform.system() == 'Windows':
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def update_elements(self):
        self.canvas.update()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class BulkOptions(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, borderwidth=5, relief=tk.GROOVE, *args, **kwargs)
        self.var_cb_forge_client_latest = tk.IntVar()
        self.cb_forge_client_latest = tk.Checkbutton(self, text='Forge Client (latest)',
                                                     variable=self.var_cb_forge_client_latest, onvalue=1, offvalue=0)
        self.cb_forge_client_latest.grid(row=0, column=0)

        self.var_cb_forge_client_all = tk.IntVar()
        self.cb_forge_client_all = tk.Checkbutton(self, text='Forge Client (all)',
                                                  variable=self.var_cb_forge_client_all, onvalue=1, offvalue=0)
        self.cb_forge_client_all.grid(row=0, column=1)

        self.var_cb_forge_server_latest = tk.IntVar()
        self.cb_forge_server_latest = tk.Checkbutton(self, text='Forge Server (latest)',
                                                     variable=self.var_cb_forge_server_latest, onvalue=1, offvalue=0)
        self.cb_forge_server_latest.grid(row=0, column=2)

        self.var_cb_forge_server_all = tk.IntVar()
        self.cb_forge_server_all = tk.Checkbutton(self, text='Forge Server (all)',
                                                  variable=self.var_cb_forge_server_all, onvalue=1, offvalue=0)
        self.cb_forge_server_all.grid(row=0, column=3)

        self.var_cb_fabric_client_latest = tk.IntVar()
        self.cb_fabric_client_latest = tk.Checkbutton(self, text='Fabric client (latest)',
                                                      variable=self.var_cb_fabric_client_latest, onvalue=1, offvalue=0)
        self.cb_fabric_client_latest.grid(row=1, column=0)

        self.var_cb_fabric_client_all = tk.IntVar()
        self.cb_fabric_client_all = tk.Checkbutton(self, text='Fabric client (all)',
                                                   variable=self.var_cb_fabric_client_all, onvalue=1, offvalue=0)
        self.cb_fabric_client_all.grid(row=1, column=1)

        self.var_cb_fabric_server_latest = tk.IntVar()
        self.cb_fabric_server_latest = tk.Checkbutton(self, text='Fabric server (latest)',
                                                      variable=self.var_cb_fabric_server_latest, onvalue=1, offvalue=0)
        self.cb_fabric_server_latest.grid(row=1, column=2)

        self.var_cb_fabric_server_all = tk.IntVar()
        self.cb_fabric_server_all = tk.Checkbutton(self, text='Fabric server (all)',
                                                   variable=self.var_cb_fabric_server_all, onvalue=1, offvalue=0)
        self.cb_fabric_server_all.grid(row=1, column=3)

        self.var_cb_liteloader_latest = tk.IntVar()
        self.cb_liteloader_latest = tk.Checkbutton(self, text='Liteloader (latest)',
                                                   variable=self.var_cb_liteloader_latest, onvalue=1, offvalue=0)
        self.cb_liteloader_latest.grid(row=2, column=0)

        self.var_cb_liteloader_all = tk.IntVar()
        self.cb_liteloader_all = tk.Checkbutton(self, text='Liteloader (all)',
                                                variable=self.var_cb_liteloader_all, onvalue=1, offvalue=0)
        self.cb_liteloader_all.grid(row=2, column=1)


class LoaderVersionWidget(tk.Frame):
    def __init__(self, master, population_list_getter, name, *args, **kwargs):
        super().__init__(master, borderwidth=5, relief=tk.GROOVE, *args, **kwargs)
        self.population_list_getter = population_list_getter
        self.name = name
        self.cb_vars = []
        self.selected_versions = []

        self.scrw_versions = ScrollableWidget(self)
        self.scrw_versions.grid(row=1, column=0)

        self.name_label = tk.Label(self, text=self.name)
        self.name_label.grid(row=0, column=0)

        self.var_cb_selectall = tk.IntVar()
        self.cb_select_all = tk.Checkbutton(self, text='Select all',
                                            variable=self.var_cb_selectall, onvalue=1, offvalue=0,
                                            command=self._select_all)
        self.cb_select_all.grid(row=2, column=0)

        self.var_cb_client = tk.IntVar()
        self.cb_client = tk.Checkbutton(self, text='Client', variable=self.var_cb_client, onvalue=1, offvalue=0)
        self.cb_client.grid(row=2, column=1)

        self.var_cb_server = tk.IntVar()
        self.cb_server = tk.Checkbutton(self, text='Server', variable=self.var_cb_server, onvalue=1, offvalue=0)
        self.cb_server.grid(row=2, column=2)

        self._populate()

    def _populate(self):
        children = self.population_list_getter()
        for i in range(len(children)):
            self.cb_vars.append(tk.IntVar())
            var = self.cb_vars[-1]
            tk.Checkbutton(self.scrw_versions.element_frame, text=f'{children[i]}', variable=var, onvalue=1,
                           offvalue=0).grid(row=i, column=0)
        if len(children) == 0 and self.name != 'Minecraft':
            tk.Label(self.get_element_frame(), text=f'No {self.name} versions available').grid(row=0,
                                                                                               column=0)
        self.scrw_versions.update_elements()

    def _depopulate(self):  # luv ya mr Schwab <3
        self.cb_vars = []
        for child in self.scrw_versions.element_frame.winfo_children():
            child.destroy()

    def _select_all(self):
        for var in self.cb_vars:
            var.set(self.var_cb_selectall.get())

    def get_selected_versions(self):
        res = []
        children = self.scrw_versions.element_frame.winfo_children()
        if len(self.cb_vars) == 0:
            return []
        for i in range(len(children)):
            if self.cb_vars[i].get():
                res.append(children[i].cget('text'))
        return res

    def get_client(self):
        return self.var_cb_client.get()

    def get_server(self):
        return self.var_cb_server.get()

    def get_element_frame(self):
        return self.scrw_versions.element_frame


class VanillaVersionWidget(LoaderVersionWidget):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, lambda: [], 'Minecraft', *args, **kwargs)

        self.modloader_version_widgets = []
        self.bulk_options = None

        self.var_cb_assets = tk.IntVar()
        self.cb_assets = tk.Checkbutton(self, text='assets',
                                        variable=self.var_cb_assets, onvalue=1, offvalue=0)
        self.cb_assets.grid(row=2, column=3)

        self.var_cb_libs = tk.IntVar()
        self.cb_libs = tk.Checkbutton(self, text='libraries',
                                      variable=self.var_cb_libs, onvalue=1, offvalue=0)
        self.cb_libs.grid(row=2, column=4)

        self.var_cb_snapshots = tk.IntVar()
        self.cb_snapshots = tk.Checkbutton(self, text='Snapshots',
                                           variable=self.var_cb_snapshots, onvalue=1, offvalue=0,
                                           command=self._repopulate)
        self.cb_snapshots.grid(row=3, column=0)

        self.var_cb_alphas = tk.IntVar()
        self.cb_alphas = tk.Checkbutton(self, text='Old Alphas',
                                        variable=self.var_cb_alphas, onvalue=1, offvalue=0, command=self._repopulate)
        self.cb_alphas.grid(row=3, column=1)

        self.var_cb_betas = tk.IntVar()
        self.cb_betas = tk.Checkbutton(self, text='Old Betas',
                                       variable=self.var_cb_betas, onvalue=1, offvalue=0, command=self._repopulate)
        self.cb_betas.grid(row=3, column=2)

        self.__populate()

    def _select_all(self):
        for var in self.cb_vars:
            var.set(self.var_cb_selectall.get())
        self._handle_version_check()

    def __populate(self):
        release_types = ['release']
        if self.var_cb_snapshots.get():
            release_types.append('snapshot')
        if self.var_cb_alphas.get():
            release_types.append('old_alpha')
        if self.var_cb_betas.get():
            release_types.append('old_beta')
        children = fn.get_mc_ids_by_type(*release_types)
        for i in range(len(children)):
            self.cb_vars.append(tk.IntVar())
            var = self.cb_vars[-1]
            tk.Checkbutton(self.scrw_versions.element_frame, text=f'{children[i]}', variable=var, onvalue=1,
                           offvalue=0, command=self._handle_version_check).grid(row=i, column=0)
        if len(children) == 0:
            tk.Label(self.get_element_frame(), text='No Minecraft versions available').grid(row=0,
                                                                                            column=0)
        self.scrw_versions.update_elements()

    def _repopulate(self):
        self._depopulate()
        self.__populate()

    def _handle_version_check(self):
        for widget in self.modloader_version_widgets:
            widget.grid_forget()
        if self.bulk_options:
            self.bulk_options.grid_forget()
            self.bulk_options = None
        if len(self.get_selected_versions()) == 1:
            forge_versions_widget = LoaderVersionWidget(self,
                                                        lambda: fn.get_forge_versions_for_mc_ver(
                                                            self.get_selected_versions()[0]), "Forge")
            self.modloader_version_widgets.append(forge_versions_widget)
            forge_versions_widget.grid(row=4, column=0)

            fabric_versions_widget = LoaderVersionWidget(self,
                                                         lambda: fn.get_fabric_versions_for_mc_ver(
                                                             self.get_selected_versions()[0]), "Fabric")
            self.modloader_version_widgets.append(fabric_versions_widget)
            fabric_versions_widget.grid(row=4, column=1)

            liteloader_versions_widget = LoaderVersionWidget(self,
                                                             lambda: fn.get_liteloader_versions_for_mc_ver(
                                                                 self.get_selected_versions()[0]), "Liteloader")
            self.modloader_version_widgets.append(liteloader_versions_widget)
            liteloader_versions_widget.grid(row=4, column=2)
        elif len(self.get_selected_versions()) > 1:
            self.bulk_options = BulkOptions(self)
            self.bulk_options.grid(row=4, column=0)

    def get_loader_data(self, loader):
        if loader != 'minecraft':
            for widget in self.modloader_version_widgets:
                if widget.name == loader[0].upper() + loader[1:]:
                    options = []
                    if widget.var_cb_client.get():
                        options.append('client')
                    if widget.var_cb_server.get():
                        options.append('server')
                    return {'versions': widget.get_selected_versions(), 'options': options}
            return {'versions': [], 'options': []}
        else:
            options = []
            if self.var_cb_client.get():
                options.append('client')
            if self.var_cb_server.get():
                options.append('server')
            if self.var_cb_assets.get():
                options.append('assets')
            if self.var_cb_libs.get():
                options.append('libs')
            return {'versions': self.get_selected_versions(), 'options': options}

    def get_bulk_options(self):
        return self.bulk_options


class DownloadHelper:
    def __init__(self):
        self.download_queue_list = []

    def download_queue(self, s):
        download_count = 0
        failed_count = 0
        for item in self.download_queue_list:
            download_count += 1
            percentage = math.trunc(download_count / (len(self.download_queue_list) / 100))
            s.lbl_download_progress.config(
                text=f'Downloading file {download_count} of {len(self.download_queue_list)} ({percentage}%)')
            s.lbl_currently_downloading.config(text=f'URL: {item["url"]}')
            s.lbl_download_progress.update()
            s.lbl_currently_downloading.update()
            if not fn.download(item['url'], item['path'], hash_type=item['hash_type'], hash_=item['hash']):
                failed_count += 1
            elif item['path'].endswith('xml'):
                fn.inject_log4j_xml(item['path'])
        self.download_queue_list = []
        s.lbl_download_progress.config(
            text=f'Downloaded {download_count - failed_count} files, {failed_count} failed. Check logs for details')
        s.lbl_currently_downloading.config(text='')
        s.lbl_download_progress.update()
        s.lbl_currently_downloading.update()

    def queue_mc_client_jar(self, version):
        fn.download(fn.get_mc_version_from_id(version)['url'], os.path.join(cfg.data_location,
                                                                            'minecraft/version_indexes',
                                                                            version + '.json'))
        data = json.loads(fn.read_text(os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                    version + '.json')))
        url = data['downloads']['client']['url']
        hash_ = data['downloads']['client']['sha1']
        path = os.path.join(cfg.data_location, 'minecraft/versions', version, 'client', version + '.jar')
        self.download_queue_list.append({'url': url, 'path': path, 'hash_type': 'sha1', 'hash': hash_})

    def queue_mc_server_jar(self, version):
        fn.download(fn.get_mc_version_from_id(version)['url'], os.path.join(cfg.data_location,
                                                                            'minecraft/version_indexes',
                                                                            version + '.json'))
        data = json.loads(fn.read_text(os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                    version + '.json')))
        if 'server' not in data['downloads']:
            logger.log('i', f'Minecraft version {version} has no available server')
            return
        url = data['downloads']['server']['url']
        hash_ = data['downloads']['server']['sha1']
        path = os.path.join(cfg.data_location, 'libs/libraries/net/minecraft/server', version, f'server-{version}.jar')
        self.download_queue_list.append({'url': url, 'path': path, 'hash_type': 'sha1', 'hash': hash_})

    def queue_mc_assets(self, version):
        fn.download(fn.get_mc_version_from_id(version)['url'], os.path.join(cfg.data_location,
                                                                            'minecraft/version_indexes',
                                                                            version + '.json'))
        data = json.loads(fn.read_text(os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                    version + '.json')))
        asset_index_url = data['assetIndex']['url']
        hash_ = data['assetIndex']['sha1']
        assets_index_path = os.path.join(cfg.data_location, 'minecraft/versions', version, 'assets/indexes',
                                         version + '.json')
        fn.download(asset_index_url, assets_index_path, hash_type='sha1', hash_=hash_)
        index_data = json.loads(fn.read_text(assets_index_path))

        for index in index_data['objects']:
            obj = index_data['objects'][index]
            name = obj['hash']
            url = f'http://resources.download.minecraft.net/{name[:2]}/{name}'
            path = os.path.join(cfg.data_location, 'minecraft/versions', version, 'assets/objects', name[:2],
                                name)
            self.download_queue_list.append({'url': url, 'path': path, 'hash_type': None, 'hash': None})
        if 'logging' in data:
            print('logging detected')
            url = data['logging']['client']['file']['url']
            path = os.path.join(cfg.data_location, 'minecraft/versions', version, 'assets/log_configs',
                                data['logging']['client']['file']['id'])
            hash_ = data['logging']['client']['file']['sha1']
            self.download_queue_list.append({'url': url, 'path': path, 'hash_type': 'sha1', 'hash': hash_})

    def queue_mc_libraries(self, version):
        fn.download(fn.get_mc_version_from_id(version)['url'], os.path.join(cfg.data_location,
                                                                            'minecraft/version_indexes',
                                                                            version + '.json'))
        data = json.loads(fn.read_text(os.path.join(cfg.data_location, 'minecraft/version_indexes',
                                                    version + '.json')))
        for library in data['libraries']:
            if 'artifact' in library['downloads']:
                url = library['downloads']['artifact']['url']
                path = os.path.join(cfg.data_location, 'libs/libraries',
                                    library['downloads']['artifact']['path'])
                hash_ = library['downloads']['artifact']['sha1']
                self.download_queue_list.append({'url': url, 'path': path, 'hash_type': 'sha1', 'hash': hash_})

            if 'classifiers' in library['downloads']:
                for key in library['downloads']['classifiers']:
                    if key.startswith('natives-'):
                        url = library['downloads']['classifiers'][key]['url']
                        path = os.path.join(cfg.data_location, 'libs/native',
                                            library['downloads']['classifiers'][key]['path'])
                        hash_ = library['downloads']['classifiers'][key]['sha1']
                        self.download_queue_list.append(
                            {'url': url, 'path': path, 'hash_type': 'sha1', 'hash': hash_})

    def queue_forge_client(self, mc_version, forge_version):
        fn.install_forge_from_queue(mc_version, forge_version, self.download_queue_list)


# group:name:version[:classifier][@extension]
class Artifact:
    def __init__(self):
        self.domain = None
        self.name = None
        self.version = None
        self.classifier = None
        self.extension = 'jar'

        self.path = None
        self.file = None
        self.descriptor = None

    @staticmethod
    def from_(descriptor):
        res = Artifact()
        res.descriptor = descriptor
        pts = descriptor.split(':')
        res.domain = pts[0]
        res.name = pts[1]

        index = pts[-1].find('@')
        if index != -1:
            res.extension = pts[-1][index + 1:]
            pts[-1] = pts[-1][:index]

        res.version = pts[2]
        if len(pts) > 3:
            res.classifier = pts[3]
        res.file = f'{res.name}-{res.version}'
        if res.classifier:
            res.file += '-' + res.classifier
        res.file += '.' + res.extension

        res.path = f"{res.domain.replace('.', '/')}{res.name}/{res.version}/{res.file}"

        return res

    def get_local_path(self, base):
        return os.path.join(base, self.path)
