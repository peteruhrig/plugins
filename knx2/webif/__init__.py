#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-     <AUTHOR>                                   <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.5 and
#  upwards.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import datetime
import time
import os

from lib.item import Items
from lib.model.smartplugin import SmartPluginWebIf

# ------------------------------------------
#    Webinterface of the plugin
# ------------------------------------------

import cherrypy
import csv
from jinja2 import Environment, FileSystemLoader


class WebInterface(SmartPluginWebIf):

    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.items = Items.get_instance()

        self.tplenv = self.init_template_environment()
        self.knxdeamon = ''
        if os.name != 'nt':
            if self.get_process_info("ps cax|grep eibd") != '':
                self.knxdeamon = 'eibd'
            if self.get_process_info("ps cax|grep knxd") != '':
                if self.knxdeamon != '':
                    self.knxdeamon += ' and '
                self.knxdeamon += 'knxd'
        else:
            self.knxdeamon = 'can not be determined when running on Windows'

    def get_process_info(self, command):
        """
        returns output from executing a given command via the shell.
        """
        ## get subprocess module
        import subprocess

        ## call date command ##
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        # Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
        # Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
        # Wait for process to terminate. The optional input argument should be a string to be sent to the child process, or None, if no data should be sent to the child.
        (result, err) = p.communicate()

        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()
        return str(result, encoding='utf-8', errors='strict')


    @cherrypy.expose
    def index(self, reload=None, knxprojfile=None):
        """
        Build index.html for cherrypy

        Render the template and return the html file to be delivered to the browser

        :return: contents of the template after being rendered
        """
        if knxprojfile is not None:
            sh = self.plugin.get_sh()
            upload_path = sh.get_basedir()
            upload_filename = 'ETS5.knxproj'

            upload_file = os.path.normpath(
                os.path.join(upload_path, upload_filename))
            size = 0
            with open(upload_file, 'wb') as out:
                while True:
                    data = knxprojfile.file.read(8192)
                    if not data:
                        break
                    out.write(data)
                    size += len(data)
            out = "File received.\nFilename: {}\nLength: {}\nMime-type: {}\n".format(knxprojfile.filename, size, knxprojfile.content_type, data)

        plgitems = []
        for item in self.items.return_items():
            if any(elem in item.property.attributes  for elem in [KNX_DPT,KNX_STATUS,KNX_SEND,KNX_REPLY,KNX_CACHE,KNX_INIT,KNX_LISTEN,KNX_POLL]):
                plgitems.append(item)

        tmpl = self.tplenv.get_template('index.html')
        # add values to be passed to the Jinja2 template eg: tmpl.render(p=self.plugin, interface=interface, ...)
        return tmpl.render(p=self.plugin, items=sorted(self.items.return_items(), key=lambda k: str.lower(k['_path'])))


    @cherrypy.expose
    def get_data_html(self, dataSet=None):
        """
        Return data to update the webpage

        For the standard update mechanism of the web interface, the dataSet to return the data for is None

        :param dataSet: Dataset for which the data should be returned (standard: None)
        :return: dict with the data needed to update the web page.
        """
        if dataSet is None:
            # get the new data
            data = {}

            # data['item'] = {}
            # for i in self.plugin.items:
            #     data['item'][i]['value'] = self.plugin.getitemvalue(i)
            #
            # return it as json the the web page
            # try:
            #     return json.dumps(data)
            # except Exception as e:
            #     self.logger.error("get_data_html exception: {}".format(e))
        return {}