# -*- coding:utf8 -*-
"""
主UI模块
仅包含界面逻辑，所有功能实现都在对应的模块中
"""
from PySide6 import QtCore
from PySide6 import QtWidgets
import qtmax
import os
import sys

# 确保系统默认编码支持UTF-8（用于中文路径）
if sys.platform == 'win32':
    if hasattr(sys, '_enablelegacywindowsfsencoding'):
        sys._enablelegacywindowsfsencoding = False

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(__file__)

# 添加到 sys.path（优先级最高）
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# 导入各个功能模块
from ExportItem import collect_export_nodes, get_default_export_name, make_safe_filename, export_fbx
from SelectItem import select_hierarchy, select_related, select_group
from SmoothNormal import smooth_normal_to_vertex_color
from DrawNormal import visualize_normals


class PyMaxDockWidget(QtWidgets.QDockWidget):
    """3ds Max导出器主窗口"""
    
    def __init__(self, parent=None):
        super(PyMaxDockWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('MaxExporter')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        qtmax.DisableMaxAcceleratorsOnFocus(self, True)
        self._init_ui()

    def _init_ui(self):
        """初始化UI界面"""
        main_layout = QtWidgets.QVBoxLayout()

        # 根层级设置
        depth_layout = QtWidgets.QHBoxLayout()
        depth_label = QtWidgets.QLabel("根层级:")
        depth_label.setToolTip("0 表示追溯到根节点；1 表示追溯到根节点的子节点；以此类推。")
        depth_layout.addWidget(depth_label)

        self.root_depth_spin = QtWidgets.QSpinBox()
        self.root_depth_spin.setRange(0, 10)
        self.root_depth_spin.setValue(0)
        self.root_depth_spin.setToolTip("控制向上追溯的层级，避免同根节点时全选整个场景。")
        depth_layout.addWidget(self.root_depth_spin)
        depth_layout.addStretch()

        main_layout.addLayout(depth_layout)

        # 选择相关按钮
        select_btn = QtWidgets.QPushButton("选中父子级")
        select_btn.clicked.connect(self.on_select_hierarchy)
        main_layout.addWidget(select_btn)
        
        select_related_btn = QtWidgets.QPushButton("选中关联项")
        select_related_btn.clicked.connect(self.on_select_related)
        main_layout.addWidget(select_related_btn)

        select_group_btn = QtWidgets.QPushButton("全选组")
        select_group_btn.clicked.connect(self.on_select_group)
        main_layout.addWidget(select_group_btn)

        # 导出按钮
        export_btn = QtWidgets.QPushButton("导出")
        export_btn.clicked.connect(self.on_export_selection)
        main_layout.addWidget(export_btn)

        # 添加分隔线
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(separator)

        # 法线工具标签
        normal_label = QtWidgets.QLabel("法线工具:")
        normal_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(normal_label)

        # 平滑法线按钮
        smooth_normal_btn = QtWidgets.QPushButton("平滑法线")
        smooth_normal_btn.setToolTip("将选中对象的平滑法线烘焙到顶点色通道")
        smooth_normal_btn.clicked.connect(self.on_smooth_normal)
        main_layout.addWidget(smooth_normal_btn)

        # 绘制法线按钮
        visualize_normal_btn = QtWidgets.QPushButton("绘制法线")
        visualize_normal_btn.setToolTip("可视化显示顶点法线方向（调试用）")
        visualize_normal_btn.clicked.connect(self.on_visualize_normals)
        main_layout.addWidget(visualize_normal_btn)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setWidget(widget)
        self.setMinimumSize(260, 220)
        self.resize(320, 300)

    # === 事件处理方法 ===
    
    def on_select_hierarchy(self):
        """选中父子级按钮点击事件"""
        success, error_msg = select_hierarchy(ancestor_depth=self.root_depth_spin.value())
        if not success:
            QtWidgets.QMessageBox.warning(self, "警告", error_msg)

    def on_select_related(self):
        """选中关联项按钮点击事件"""
        success, error_msg = select_related()
        if not success:
            QtWidgets.QMessageBox.information(self, "提示", error_msg)

    def on_select_group(self):
        """全选组按钮点击事件"""
        success, error_msg = select_group()
        if not success:
            QtWidgets.QMessageBox.information(self, "提示", error_msg)

    def on_export_selection(self):
        """导出按钮点击事件"""
        # 收集导出节点
        success, nodes, export_name, error_msg = collect_export_nodes(
            ancestor_depth=self.root_depth_spin.value()
        )
        
        if not success:
            QtWidgets.QMessageBox.warning(self, "警告", error_msg)
            return
        
        # 获取默认文件名
        if export_name:
            default_name = make_safe_filename(export_name)
        else:
            default_name = get_default_export_name()
        
        # 弹出文件保存对话框
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存FBX文件",
            f"{default_name}.fbx",
            "FBX Files (*.fbx)",
        )
        
        if not file_path:
            return
        
        # 执行导出
        success, error_msg = export_fbx(nodes, file_path)
        
        if success:
            QtWidgets.QMessageBox.information(self, "成功", f"FBX文件已导出到:\n{file_path}")
        else:
            QtWidgets.QMessageBox.critical(self, "错误", f"导出失败:\n{error_msg}")

    def on_smooth_normal(self):
        """平滑法线按钮点击事件"""
        success, error_msg = smooth_normal_to_vertex_color()
        if not success:
            QtWidgets.QMessageBox.warning(self, "提示", error_msg)

    def on_visualize_normals(self):
        """绘制法线按钮点击事件"""
        success, error_msg = visualize_normals()
        if not success:
            QtWidgets.QMessageBox.warning(self, "提示", error_msg)


def main():
    """启动主窗口"""
    main_window = qtmax.GetQMaxMainWindow()
    dock = PyMaxDockWidget(parent=main_window)
    dock.setFloating(True)
    dock.show()


if __name__ == '__main__':
    main()
