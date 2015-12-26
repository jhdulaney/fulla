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

"""Interact with Digital Ocean account"""

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO
import pycurl
import json
from fulla import settings

Null = json.dumps(None)


def get_info(location):
    """Retreive Droplet data from Digital Ocean"""
    buff = BytesIO()
    auth = 'Authorization: Bearer ' + settings.token
    curler = pycurl.Curl()
    curler.setopt(curler.URL, settings.api_url + location)
    curler.setopt(curler.HTTPHEADER, [auth])
    curler.setopt(curler.WRITEDATA, buff)
    try:
        curler.perform()
    except:
        raise
    curler.close()

    results = buff.getvalue()
    results = results.decode('iso-8859-1')
    results = json.loads(results)
    return results


def send_request(location, request):
    location = settings.api_url + location

    class _Buffer(object):
        def __init__(self):
            self.data = ''

        def incoming(self, buff):
            self.data += buff.decode('iso-8859-1')


    auth = 'Authorization: Bearer ' + settings.token
    post_request = json.dumps(request)
    try:
        buff = _Buffer()
        curler = pycurl.Curl()
        curler.setopt(curler.HTTPHEADER, [auth, "Content-type: application/json"])
        curler.setopt(curler.URL, location)
        curler.setopt(curler.POSTFIELDS, post_request)
        curler.setopt(curler.WRITEFUNCTION, buff.incoming)
        curler.perform()
        curler.close()
        return buff.data
    except:
        raise


def send_delete(location):
    location = settings.api_url + location

    buff = BytesIO()
    auth = 'Authorization: Bearer ' + settings.token
    try:
        curler = pycurl.Curl()
        curler.setopt(curler.HTTPHEADER, [auth, "Content-type: application/json"])
        curler.setopt(curler.URL, location)
        curler.setopt(curler.CUSTOMREQUEST, "DELETE")
        curler.setopt(curler.WRITEDATA, buff)
        curler.perform()
        curler.close()
        result = json.loads(buff.getvalue().decode('iso-8859-1'))
        return result
    except:
        raise


class Account(object):
    """Digital Ocean Account object"""
    def __init__(self):
        self.droplet_limit = 0
        self.email = ''
        self.uuid = ''
        self.email_verified = None
        self.status = ''
        self.status_message = ''

    def get_data(self):
        """Retreive user data from Digital Ocean"""
        results = get_info('account')
        try:
            results = results['account']
            self.droplet_limit = results['droplet_limit']
            self.email = results['email']
            self.uuid = results['uuid']
            self.email_verified = results['email_verified']
            self.status = results['status']
            self.status_message = ['status_message']
        except:
            print(results['id'], results['message'])
            raise
        return 0


def get_droplets():
    """Retreive Droplet data from Digital Ocean"""
    results = get_info('droplets')
    try:
        droplets = results['droplets']
        num_droplets = results['meta']['total']
    except:
        print(results['id'], results['message'])
    return droplets, num_droplets


def get_imagelist():
    """Get list of available images"""
    results = get_info('images?page=1')
    try:
        num_pages = int(results['links']['pages']['last'].rsplit('=', 1)[1])
    except:
        print(results['id'], results['message'])
        raise
    image_list = results['images']
    for page in range(2, num_pages + 1):
        results = get_info('images?page=' + str(page))
        image_list += results['images']
    return image_list


def get_keys():
    results = get_info('account/keys')
    try:
        num_keys = int(results['meta']['total'])
        keys = results['ssh_keys']
    except:
        print(results['id'], results['message'])
        raise
    return keys, num_keys


def create_droplet(name, region, size, image_slug, ssh_keys, user_data=Null, private_networking=Null, ipv6=Null, backups=Null):
    """Create new droplet
       Note:  ssh_keys *must* be a list
    """
    images = get_imagelist()
    droplet = None
    for image in images:
        if (image_slug == image['slug'] or image_slug == image['id']):
            droplet = {"name": name, "region": region, "size": size, "image": image_slug,
                       "ssh_keys": ssh_keys, "backups": backups, "ipv6": ipv6,
                       "user_data": user_data, "private_networking": private_networking}
    if droplet is not None:
        result = send_request('droplets', droplet)
        try:
            result = json.loads(result)
        except:
            print(result['id'], result['message'])
            raise
        return result
    else:
        print("Image does not exist")
        raise


def delete_droplet(droplet_id):
    send_delete('droplets/' + str(droplet_id))
    return 0


def reboot_droplet(droplet_id):
    """Reboot droplet"""
    request = 'droplets/' + str(droplet_id) + '/actions'
    result = send_request(request, '{"type":"reboot"}')
    return result

print(get_droplets()[0][0]['id'])
print(reboot_droplet(7963175))
#create_droplet('test', 'nyc3', '512mb', 'ubuntu-14-04-x64', [625940], Null, Null)

#keys, num_keys = get_keys()

#print(json.dumps(keys, indent=4))
#print(num_keys)
