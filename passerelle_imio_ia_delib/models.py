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

# Decorateurs des endpoints:
# serializer_type='json-api' : Permet de serializer la reponse directement dans un data + format automatique pour un raise exception.
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
        return dict(client.service.testConnection(''))

    @endpoint(serializer_type='json-api', perm='can_access')
    def test_createItem(self, request):
        client = get_client(self)
        return dict(client.service.createItem('meeting-config-college', 'dirgen',
                                  {'title': 'CREATION DE POINT TS2',
                                  'description': 'My new item description',
                                  'decision': 'My decision'}))

    # uid="uidplone", showExtraInfos="1", showAnnexes="0", showTemplates="0"
    @endpoint(serializer_type='json-api', perm='can_access', methods=['post','get'])
    def getItemInfos(self, request, *args, **kwargs):
        id_delib_extraInfos = {}
        if request.body:
            load = json.loads(request.body)
            ws_params = load['extra']
            uid = ws_params['uid']
            showExtraInfos = ws_params['showExtraInfos'] or "1"
            showAnnexes = ws_params['showAnnexes'] or "0"
            showTemplates = ws_params['showTemplates'] or "0"
        else:
            get = request.GET
            uid = "uid" in get and get["uid"]
            showExtraInfos = "showExtraInfos" in get and get["showExtraInfos"] or "1" 
            showAnnexes = "showAnnexes" in get and get["showAnnexes"] or "0"
            showTemplates = "showTemplates" in get and get["showTemplates"] or "0"
        client = get_client(self)
        ia_delib_point_all_informations =  client.service.getItemInfos(uid,
                                           showExtraInfos,
                                           showAnnexes,
                                           showTemplates)
        ia_delib_extraInfos = len(ia_delib_point_all_informations) > 0 and ia_delib_point_all_informations[0]['extraInfos']
        if not ia_delib_extraInfos:
           raise Exception("Don't find UID IA Delib point")
        return dict(ia_delib_extraInfos)
    
    @endpoint(serializer_type='json-api', perm='can_access', methods=['post'])
    def createItem_OLD(self, request, meetingConfigId, proposingGroupId, title, description,decision):
        creationData ={'title':title,
                       'description':description,
                       'decision':decision
                      }
        client = get_client(self)
        return dict(client.service.createItem(meetingConfigId,
                                              proposingGroupId,
                                              creationData))
    
    @endpoint(serializer_type='json-api', perm='can_access', methods=['post'])
    def createItem(self, request, *args, **kwargs):
        data = dict([(x, request.GET[x]) for x in request.GET.keys()])
        if request.body:
            load = json.loads(request.body)
            # get fields from form.
            data.update(load.get("fields"))
            ws_params = load['extra']
        if 'extraAttrs' in ws_params:
            # pass all extraAttrs in a unqiue "extraAttrs" parameter list of dictionary : 
            # [{'key': 'detailedDescription', 'value' : 'lala'},{'key': 'internalNotes', 'value' : 'notes'}] in workflow
            extraAttrs = [dict((k.encode('utf8'), v.encode('utf8')) for k, v in ws_params['extraAttrs'][0].items())]
        else:
            # pass differents extraAttrs in different parameter like :  
            # detailedDescription = "lala" 
            # internalNotes = "notes" 
            detailedDescription = "detailedDescription" in ws_params and "<p>{}</p>".format(ws_params['detailedDescription']) or "<p></p>"
            extraAttrs = [{'key':'detailedDescription','value':detailedDescription}]
        
        creationData ={'title':ws_params['title'],
                       'description':ws_params['description'],
                       'decision':ws_params['decision'],
                       'extraAttrs':extraAttrs
                      }
        client = get_client(self)
        new_point = dict(client.service.createItem(ws_params['meetingConfigId'],
                                              ws_params['proposingGroupId'],
                                              creationData))
        return new_point