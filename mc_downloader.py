import math
import os
import platform
import shutil
import tkinter as tk
import tkinter.ttk as ttk

import classes as cl
import constants as cn
import functions as fn
from utils.config import cfg
import utils.logger as logger


class MainWindow(tk.Tk):
    def __init__(self):
        logger.log('s', '#----------------------------------#')
        logger.log('s', '#---- Welcome to MCDownloader! ----#')
        logger.log('s', '#----------------------------------#')
        tk.Tk.__init__(self)
        self.geometry("800x600")
        self.title('MCDownloader')
        self.iconbitmap('resources/logo/logo.ico')

        self.version_checkboxes = []
        self.version_checkboxes_vars = []
        self.selected_versions = []
        self.finished_loading_indexes = False

        self.btn_show_versions = tk.Button(self, text='Loading versions...',
                                      command=lambda: handle_btn_show_versions(self, None, None, None, True))
        self.btn_show_versions.grid(row=0, column=0, padx=5, pady=5)

        self.btn_update_mc_version_jsons = tk.Button(self, text='Update Individual MC Version JSONs',
                                           command=lambda: fn.update_mc_version_jsons(self))
        self.btn_update_mc_version_jsons.grid(row=0, column=1, padx=5, pady=5)

        self.btn_purge_data_dir = tk.Button(self, text='Purge Data Directory',
                                                     command=lambda: shutil.rmtree(cfg.data_location, ignore_errors=True))
        self.btn_purge_data_dir.grid(row=0, column=2, padx=5, pady=5)

        # wrapper for the first part (version selection)
        self.frm_scroll_mc_options_wrapper = tk.Frame(self)

        self.mc_selector = cl.VanillaVersionWidget(self.frm_scroll_mc_options_wrapper)
        self.mc_selector.grid(row=1, column=0)

        # wrapper for artefact selection
        # <editor-fold desc="All boxes for client, server, libs, and mass modloader dl">
        """frm_artefacts = tk.Frame(self)
        frm_artefacts.grid(row=2, column=0)

        self.var_cb_client = tk.IntVar()
        self.cb_client = tk.Checkbutton(master=frm_artefacts, text='Client', variable=self.var_cb_client, onvalue=1, offvalue=0,
                                   command=lambda: print('sneed'))
        self.var_cb_server = tk.IntVar()
        self.cb_server = tk.Checkbutton(master=frm_artefacts, text='Server', variable=self.var_cb_server, onvalue=1, offvalue=0,
                                   command=lambda: print('sneed'))
        self.var_cb_libraries = tk.IntVar()
        self.cb_libraries = tk.Checkbutton(master=frm_artefacts, text='Libraries', variable=self.var_cb_libraries, onvalue=1, offvalue=0,
                                   command=lambda: print('sneed'))
        self.var_cb_forge_client_latest = tk.IntVar()
        self.cb_forge_client_latest = tk.Checkbutton(master=frm_artefacts, text='Forge Client (latest)', variable=self.var_cb_forge_client_latest, onvalue=1, offvalue=0,
                                   command=lambda: print('sneed'))
        self.var_cb_forge_client_all = tk.IntVar()
        self.cb_forge_client_all = tk.Checkbutton(master=frm_artefacts, text='Forge Client (all)',
                                                variable=self.var_cb_forge_client_all, onvalue=1, offvalue=0,
                                                command=lambda: print('sneed'))
        self.var_cb_forge_server_latest = tk.IntVar()
        self.cb_forge_server_latest = tk.Checkbutton(master=frm_artefacts, text='Forge Server (latest)',
                                             variable=self.var_cb_forge_server_latest, onvalue=1, offvalue=0,
                                             command=lambda: print('sneed'))
        self.var_cb_forge_server_all = tk.IntVar()
        self.cb_forge_server_all = tk.Checkbutton(master=frm_artefacts, text='Forge Server (all)',
                                                variable=self.var_cb_forge_server_all, onvalue=1, offvalue=0,
                                                command=lambda: print('sneed'))
        self.var_cb_fabric_client_latest = tk.IntVar()
        self.cb_fabric_client_latest = tk.Checkbutton(master=frm_artefacts, text='Fabric client (latest)',
                                             variable=self.var_cb_fabric_client_latest, onvalue=1, offvalue=0,
                                             command=lambda: print('sneed'))
        self.var_cb_fabric_client_all = tk.IntVar()
        self.cb_fabric_client_all = tk.Checkbutton(master=frm_artefacts, text='Fabric client (all)',
                                                 variable=self.var_cb_fabric_client_all, onvalue=1, offvalue=0,
                                                 command=lambda: print('sneed'))
        self.var_cb_fabric_server_latest = tk.IntVar()
        self.cb_fabric_server_latest = tk.Checkbutton(master=frm_artefacts, text='Fabric server (latest)',
                                                 variable=self.var_cb_fabric_server_latest, onvalue=1, offvalue=0,
                                                 command=lambda: print('sneed'))
        self.var_cb_fabric_server_all = tk.IntVar()
        self.cb_fabric_server_all = tk.Checkbutton(master=frm_artefacts, text='Fabric server (all)',
                                              variable=self.var_cb_fabric_server_all, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.var_cb_liteloader_latest = tk.IntVar()
        self.cb_liteloader_latest = tk.Checkbutton(master=frm_artefacts, text='Liteloader (latest)',
                                              variable=self.var_cb_liteloader_latest, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.var_cb_liteloader_all = tk.IntVar()
        self.cb_liteloader_all = tk.Checkbutton(master=frm_artefacts, text='Liteloader (all)',
                                              variable=self.var_cb_liteloader_all, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))"""
        # </editor-fold>

        self.solo_scrws = tk.Frame(self)

        self.frm_forge_versions_client_server_wrapper = tk.Frame(self.solo_scrws, borderwidth=5, relief=tk.GROOVE)
        self.frm_forge_versions_client_server_wrapper.cb_vars = []
        self.scrw_forge_versions = cl.ScrollableWidget(self.frm_forge_versions_client_server_wrapper)
        self.scrw_forge_versions.grid(row=0, column=0)
        self.var_cb_forge_selectall = tk.IntVar()
        def handle_forge_selectall():
            for var in self.frm_forge_versions_client_server_wrapper.cb_vars:
                var.set(self.var_cb_forge_selectall.get())
        self.cb_forge_selectall = tk.Checkbutton(self.frm_forge_versions_client_server_wrapper, text='Select all',
                                              variable=self.var_cb_forge_selectall, onvalue=1, offvalue=0,
                                              command=handle_forge_selectall)
        self.cb_forge_selectall.grid(row=1, column=0)
        self.frm_forge_versions_client_server_wrapper.grid(row=0, column=0)
        self.var_cb_forge_client = tk.IntVar()
        self.cb_forge_client = tk.Checkbutton(self.frm_forge_versions_client_server_wrapper, text='Client', variable=self.var_cb_forge_client, onvalue=1, offvalue=0,
                                  command=lambda: print('sneed'))
        self.cb_forge_client.grid(row=1, column=1)
        self.var_cb_forge_server = tk.IntVar()
        self.cb_forge_server = tk.Checkbutton(self.frm_forge_versions_client_server_wrapper, text='Server',
                                              variable=self.var_cb_forge_server, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.cb_forge_server.grid(row=1, column=2)

        self.frm_fabric_versions_client_mappings_wrapper = tk.Frame(self.solo_scrws, borderwidth=5, relief=tk.GROOVE)
        self.frm_fabric_versions_client_mappings_wrapper.grid(row=0, column=1)
        self.scrw_fabric_versions = cl.ScrollableWidget(self.frm_fabric_versions_client_mappings_wrapper)
        self.scrw_fabric_versions.grid(row=0, column=0)
        self.var_cb_fabric_client = tk.IntVar()
        self.cb_fabric_client = tk.Checkbutton(self.frm_fabric_versions_client_mappings_wrapper, text='Client',
                                              variable=self.var_cb_fabric_client, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.cb_fabric_client.grid(row=1, column=0)
        self.var_cb_fabric_server = tk.IntVar()
        self.cb_fabric_server = tk.Checkbutton(self.frm_fabric_versions_client_mappings_wrapper, text='Server',
                                              variable=self.var_cb_fabric_server, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.cb_fabric_server.grid(row=1, column=1)
        self.var_cb_fabric_mappings = tk.IntVar()
        self.cb_fabric_mappings = tk.Checkbutton(self.frm_fabric_versions_client_mappings_wrapper, text='Mappings',
                                              variable=self.var_cb_fabric_mappings, onvalue=1, offvalue=0,
                                              command=lambda: print('sneed'))
        self.cb_fabric_mappings.grid(row=1, column=2)

        self.scrw_liteloader_versions = cl.ScrollableWidget(self.solo_scrws, borderwidth=5, relief=tk.GROOVE)
        self.scrw_liteloader_versions.grid(row=0, column=2)

        btn_download = tk.Button(self, text='Download', command=lambda: fn.download_selected(self))
        btn_download.grid(row=4, column=0, padx=5, pady=5)

        self.lbl_download_progress = tk.Label(self, wraplength=500, text='')
        self.lbl_download_progress.grid(row=5, column=0)
        self.lbl_currently_downloading = tk.Label(self, wraplength=500, text='')
        self.lbl_currently_downloading.grid(row=6, column=0)

        if cfg.update_indexes:
            downloaded_indexes = fn.download_indexes()
            failed_list = []
            for elem in ['launcher_meta', 'multimc_meta', 'com.mumfrey.liteloader', 'net.fabricmc.fabric-loader',
                         'net.fabricmc.intermediary', 'net.minecraft', 'net.minecraftforge', 'org.lwjgl', 'org.lwjgl3']:
                if elem not in downloaded_indexes:
                    failed_list.append(elem)
            if 'launcher_meta' in failed_list:
                # btn_show_versions.config(text="Error!")
                tk.Label(self, wraplength=500, text=f'Error! Couldn\'t get Minecraft version json!').pack()
                return
            if len(failed_list) > 0:
                tk.Label(self, wraplength=500,
                         text=f'Warning! The following metadata indexes failed to download, you will not be able to download some or all artifacts: {", ".join(failed_list)}').pack()
        self.finished_loading_indexes = True
        self.btn_show_versions.config(text="Select Minecraft version(s)")

"""def handle_cb_select_all(s, var_cb_select_all):
    fn.select_all(s, var_cb_select_all)
    print(s.selected_versions)
    fn.handle_artefact_options(s)"""

def handle_btn_show_versions(s, var_cb_snapshots,
                             var_cb_alphas, var_cb_betas, button=False):
    if not s.finished_loading_indexes:
        return
    if s.frm_scroll_mc_options_wrapper.winfo_ismapped() and button:
        s.frm_scroll_mc_options_wrapper.grid_forget()
        s.btn_show_versions.config(text="Select Minecraft version(s)")
    else:
        s.frm_scroll_mc_options_wrapper.grid(row=1, column=0)
        s.btn_show_versions.config(text="Hide")
        s.mc_selector.scrw_versions.update_elements()

"""def handle_version_check(s, id, cb_var):
    if cb_var.get() and not id in s.selected_versions:
        s.selected_versions.append(id)
    else:
        s.selected_versions = [value for value in s.selected_versions if value != id]
    print(s.selected_versions)
    fn.handle_artefact_options(s)"""

def main():
    window = MainWindow()
    window.mainloop()

if __name__ == "__main__":
    main()