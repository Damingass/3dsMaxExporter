# -*- coding:utf8 -*-
from __future__ import unicode_literals
import pyblish.api
import os
import tempfile
import pymxs
from mxthread import run_on_main_thread


def export_mesh_abc(abc_file, meshes=None, exp_options={}):
    """导出abc."""
    default_options = {
        'selectedOnly': True,  # not abc option
        'ArchiveType': 'Ogawa',
        'AnimTimeRange': 'TimeSlider',
        'CoordinateSystem': 'YUp',
        'Hidden': True,
        'ShapeSuffix': False,
        'SamplesPerFrame': 1,
        'UVs': True,
        'Normals': True,
        'VertexColors': True,
        'ExtraChannels': True,
        'Velocity': True,
        'MaterialIDs': True,
        'Visibility': True,
        'LayerName': True,
        'MaterialName': True,
        'ObjectID': True,
        'CustomAttributes': False,
        'ParticleAsMesh': False
    }

    rt = pymxs.runtime
    default_options.update(exp_options)
    if default_options.get('StartFrame') and default_options.get('EndFrame'):
        default_options['AnimTimeRange'] = 'StartEnd'

    if meshes:
        tmp_meshes = []
        for i in meshes:
            if isinstance(i, str):
                i = rt.getNodeByName(i)
            tmp_meshes.append(i)
        rt.select(tmp_meshes)
    else:
        default_options['selectedOnly'] = False

    for k, v in default_options.items():
        if k in ['selectedOnly']:
            continue
        if k in ['ArchiveType', 'AnimTimeRange', 'CoordinateSystem']:
            v = rt.name(v)
        rt.AlembicExport.setmxsprop(k, v)

    rt.exportFile(abc_file,
                  rt.name('NOPROMPT'),
                  using=rt.AlembicExport,
                  selectedOnly=default_options['selectedOnly'])


class ExtractAnimABC(pyblish.api.InstancePlugin):
    u"""烘焙并导出动画ABC

    """

    families = [
        'Max Char Layer',
        'Max Prop Layer',
    ]
    label = '导出动画ABC（Char，Props）'

    def process(self, instance):
        context = instance.context
        pub_dir = context.data["arcolab_publish_main_dir"]
        objs = instance.data['objs']
        layer_name = instance.data['layer_name']
        layer_type = instance.data['layer_type']
        path = f'{pub_dir}\\{layer_name}.abc'
        self.log.info(f'export abc: {path}')
        run_on_main_thread(export_mesh_abc, path, objs)
        context.data['components'].append({
            'name': layer_name,
            'type': layer_type,
            'path': path,
            'dcc': 'max',
        })
