# -*- coding:utf8 -*-
from __future__ import unicode_literals
import pyblish
import os
import tempfile
from socketsOutput import socketsOutput
from mxthread import run_on_main_thread


class ExtractAnimBone(pyblish.api.InstancePlugin):
    u"""烘焙并导出Socket骨骼

    """

    families = [
        'Max Bone Layer',
    ]
    label = '导出Socket Bone'

    def process(self, instance):
        context = instance.context
        pub_dir = context.data["arcolab_publish_main_dir"]
        objs = instance.data['objs']
        layer_name = instance.data['layer_name']
        path = f'{pub_dir}\\{layer_name}.fbx'
        # 确保路径支持中文
        path = os.path.abspath(path)
        run_on_main_thread(socketsOutput, objs, path)
        context.data['components'].append({
            'name': layer_name,
            'type': 'Socket',
            'path': path,
        })
