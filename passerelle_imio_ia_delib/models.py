#!/usr/bin/env python
# -*- coding: utf-8 -*-
# passerelle-imio-ia-delib - passerelle connector to IA DELIB IMIO PRODUCTS.
# Copyright (C) 2016  Entr'ouvert
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# https://demo-pm.imio.be/ws4pm.wsdl
# https://demo-pm.imio.be/
# http://trac.imio.be/trac/browser/communesplone/imio.pm.wsclient/trunk/src/imio/pm/wsclient/browser/settings.py#L211
# http://svn.communesplone.org/svn/communesplone/imio.pm.ws/trunk/docs/README.txt
import base64
import json
import magic
import suds

from requests.exceptions import ConnectionError
from django.db import models
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404

from passerelle.base.models import BaseResource
from passerelle.utils.api import endpoint
from passerelle.utils.jsonresponse import APIError
from .soap import get_client as soap_get_client

from suds.xsd.doctor import ImportDoctor, Import
from suds.transport.http import HttpAuthenticated

def get_client(model):
    try:
        return soap_get_client(model)
    except ConnectionError as e:
        raise APIError('i-ImioIaDelib error: %s' % e)


def format_type(t):
    return {'id': unicode(t), 'text': unicode(t)}


def format_file(f):
    return {'status': f.status, 'id': f.nom, 'timestamp': f.timestamp}


class FileError(Exception):
    pass


class FileNotFoundError(Exception):
    http_status = 404


class PayloadInterceptor(suds.plugin.MessagePlugin):
    def __init__(self, *args, **kwargs):
        self.last_payload = None

    def received(self, context):
        #recieved xml as a string
        print "%s bytes received" % len(context.reply)
        self.last_payload = context.reply
        #clean up reply to prevent parsing
        context.reply = ""
        return context


class IImioIaDelib(BaseResource):
    wsdl_url = models.CharField(max_length=128, blank=False,
            verbose_name=_('WSDL URL'),
            help_text=_('WSDL URL'))
    verify_cert = models.BooleanField(default=True,
            verbose_name=_('Check HTTPS Certificate validity'))
    username = models.CharField(max_length=128, blank=True,
            verbose_name=_('Username'))
    password = models.CharField(max_length=128, blank=True,
            verbose_name=_('Password'))
    keystore = models.FileField(upload_to='iparapheur', null=True, blank=True,
            verbose_name=_('Keystore'),
            help_text=_('Certificate and private key in PEM format'))

    category = _('Business Process Connectors')

    class Meta:
        verbose_name = _('i-ImioIaDelib')

    @classmethod
    def get_verbose_name(cls):
        return cls._meta.verbose_name

    @endpoint()
    def test(self):
        return 'True'

    @endpoint(serializer_type='json-api', perm='can_access')
    def testConnection(self, request):
        client = get_client(self)
        # payload_interceptor = PayloadInterceptor()
        # client.options.plugins = [payload_interceptor]
        return dict(client.service.testConnection(''))

    @endpoint(serializer_type='json-api', perm='can_access')
    def test_createItem(self, request):
        client = get_client(self)
        return dict(client.service.createItem('meeting-config-college', 'dirgen',
                                  {'title': 'CREATION DE POINT TS2',
                                  'description': 'My new item description',
                                  'decision': 'My decision'}))

    #createItem?meetingConfigId=meeting-config-college&proposingGroupId=dirgen&title=Mon%20nouveau%20point&description=Ma%20nouvelle%20description&decision=Ma%20nouvelle%20decision
    @endpoint(serializer_type='json-api', perm='can_access')
    def createItem(self, request, meetingConfigId, proposingGroupId, title, description,decision):
        creationData ={'title':title,
                       'description':description,
                       'decision':decision
                      }
        client = get_client(self)
        return dict(client.service.createItem(meetingConfigId,
                                              proposingGroupId,
                                              creationData))
