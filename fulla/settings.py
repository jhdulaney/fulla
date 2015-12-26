#
# fulla -- work with Digital Ocean
#
# Copyright (C) 2015 John H. Dulaney <jdulaney@fedoraproject.org>
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""Configuration for fulla"""

import os
import json


class Settings(object):
    """Create Settings object"""
    def __init__(self):
        self.conf_file = os.path.expanduser('~/.config/fulla/config')
        self.token = None
        self.api_url = 'https://api.digitalocean.com/v2/'


    def setup(self):
        """Check that config exists and read it"""
        if os.path.exists(self.conf_file):
            with open(self.conf_file, 'r') as conf_fd:
                conf_data = conf_fd.read()
            self.token = json.loads(conf_data)['token']
        else:
            os.makedirs(os.path.dirname(self.conf_file))
            conf_data = json.dumps({'token': None}, sort_keys=True, indent=4)
            with open(self.conf_file, 'w') as conf_fd:
                conf_fd.write(conf_data)
