# -*- coding:utf8 -*-
from __future__ import unicode_literals
import pyblish.api
import os
import tempfile
import pymxs
from mxthread import run_on_main_thread


def export_mesh_abc(abc_file, meshes=None, exp_options={}):
    """导出abc."""
    # 确保路径支持中文：转换为绝对路径
    abc_file = os.path.abspath(abc_file)
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
    
    # 统一导出单位为厘米
    # 获取场景单位并计算ScaleFactor
    try:
        # 获取场景系统单位（0=英寸, 1=英尺, 2=英里, 3=毫米, 4=厘米, 5=米, 6=千米）
        system_unit = rt.units.SystemType
        if system_unit == 4:  # 厘米
            scale_factor = 1.0
        elif system_unit == 5:  # 米
            scale_factor = 100.0  # 米转厘米
        elif system_unit == 3:  # 毫米
            scale_factor = 0.1  # 毫米转厘米
        else:
            # 其他单位，默认使用1.0（假设已经是厘米或需要手动调整）
            scale_factor = 1.0
        # Alembic导出器支持ScaleFactor参数
        if 'ScaleFactor' not in default_options:
            default_options['ScaleFactor'] = scale_factor
    except:
        # 如果获取单位失败，使用默认值1.0
        if 'ScaleFactor' not in default_options:
            default_options['ScaleFactor'] = 1.0

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

    # 确保路径正确传递给MaxScript（使用Unicode字符串）
    rt.exportFile(rt.name(abc_file),
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
        # 确保路径支持中文
        path = os.path.abspath(path)
        self.log.info(f'export abc: {path}')
        run_on_main_thread(export_mesh_abc, path, objs)
        context.data['components'].append({
            'name': layer_name,
            'type': layer_type,
            'path': path,
            'dcc': 'max',
        })
