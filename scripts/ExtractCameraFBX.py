# -*- coding:utf8 -*-
from __future__ import unicode_literals
import pyblish
import tempfile
import cameraOutput
from mxthread import run_on_main_thread


class ExtractCameraFBX(pyblish.api.InstancePlugin):
    u"""烘焙并导出相机FBX

    """

    families = [
        'Max Camera Layer',
    ]
    label = '导出相机FBX'

    def process(self, instance):
        context = instance.context
        pub_dir = context.data["arcolab_publish_main_dir"]
        camera = instance.data['camera']
        path = f'{pub_dir}\\camera.fbx'
        # 确保路径支持中文
        import os
        path = os.path.abspath(path)
        self.log.info(f'export abc: {path}')
        run_on_main_thread(
            cameraOutput.cameraOutput,
            camera.name,
            outFile=path,
        )
        context.data['components'].append({
            'name': camera.name,
            'type': 'Camera',
            'path': path,
        })
