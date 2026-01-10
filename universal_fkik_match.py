# -*- coding: utf-8 -*-
"""
FK/IK Matching Tool V2.1
Universal FK/IK matching utility for Maya animation
Uses Blend Joints as reference for accurate matching

Made by niexiongtao
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import json
import os
import math
from contextlib import contextmanager

# 常量 / Constants
RAD_TO_DEG = 180.0 / math.pi


# ============================================================================
# 多语言 / Localization
# ============================================================================

LANGUAGES = {
    'en': {
        'window_title': 'FK/IK Matching Tool V2.1',
        'language': 'Language (语言)',
        'chinese': '中文',
        'english': 'English',
        
        # Limb Management
        'limbs': 'Saved Limbs',
        'limb_list': 'Saved Limbs',
        'remove_limb': 'Remove Selected',
        'limb_name': 'Limb Name:',
        'edit_limb': 'Edit Selected Limb',
        
        # Definition Section
        'definition': 'Limb Settings',
        'blend_joints': 'Blend Joints (Reference)',
        'load_blend': 'Load Selected as Blend Chain',
        'fk_controls': 'FK Controls',
        'load_fk': 'Load Selected as FK Controls',
        'ik_control': 'IK Control',
        'load_ik': 'Load Selected as IK Control',
        'pole_vector': 'Elbow/Knee Control (Pole Vector)',
        'load_pv': 'Load Selected as Control',
        'save_limb': 'Save This Limb',
        'clear_current': 'Clear Current',
        
        # Preset Section
        'presets': 'Presets',
        'save_preset': 'Save All Limbs',
        'load_preset': 'Load Preset',
        'preset_saved': 'Preset saved!',
        'preset_loaded': 'Preset loaded! Limbs: ',
        'preset_error': 'Preset error: ',
        
        # Action Section
        'actions': 'Matching Actions',
        'match_all_ik_to_fk': 'Match All IK to FK (Use for changing to IK Mode)',
        'match_all_fk_to_ik': 'Match All FK to IK (Use for changing to FK Mode)',
        'match_sel_ik_to_fk': 'Selected: IK → FK (Use for changing to IK Mode)',
        'match_sel_fk_to_ik': 'Selected: FK → IK (Use for changing to FK Mode)',
        'calibrate_all': 'Calibrate All Limbs',
        'calibrate_success': 'Calibration complete! Limbs: ',
        'calibrate_note': '* Put rig in bind pose before calibrating',
        
        # Settings
        'settings': 'Settings',
        'auto_key': 'Auto Keyframe',
        'use_matrix': 'Use Matrix Matching',
        
        # Messages
        'no_selection': 'Please select objects first',
        'no_limb_selected': 'Please select a limb from the list',
        'limb_saved': 'Limb saved: ',
        'limb_removed': 'Limb removed: ',
        'match_success': 'Matching completed!',
        'need_blend': 'Please load Blend Joints first',
        'need_fk': 'Please load FK Controls first',
        'need_ik': 'Please load IK Control first',
        'obj_not_exist': 'Object does not exist: ',
        'enter_limb_name': 'Please enter a limb name',
        
        # Help
        'help': 'How to Use',
        'help_text': 'Limb Configuration:\n'
                     '1. Enter limb name\n'
                     '2. Select Blend joints (Root to End) → Load\n'
                     '   (If no Blend chain, select skin joints)\n'
                     '3. Select FK controls (Root to End) → Load\n'
                     '4. Select IK control → Load\n'
                     '5. Select Elbow/Knee control → Load\n'
                     '6. Save This Limb\n'
                     '7. Repeat for other limbs\n'
                     '8. Save All Limbs as preset (optional)\n'
                     '9. Put rig in Bind Pose → Calibrate All Limbs\n'
                     'Animation FK/IK Switching:\n'
                     '• Load preset (optional)\n'
                     '• Key FKIK controller at current frame, then click Match\n'
                     '• Move 1 frame, switch FKIK, then key again',
        
        # Author
        'author': 'Made by niexiongtao',
        'contact': 'Contact: niexiongtao@gmail.com',
    },
    'zh': {
        'window_title': 'FK/IK Matching Tool V2.1',
        'language': '语言 (Language)',
        'chinese': '中文',
        'english': 'English',
        
        # Limb Management
        'limbs': '已保存肢体',
        'limb_list': '已保存肢体',
        'remove_limb': '删除选中',
        'limb_name': '肢体名称:',
        'edit_limb': '编辑选中肢体',
        
        # Definition Section
        'definition': '肢体设置',
        'blend_joints': '融合骨骼（参考）',
        'load_blend': '加载选中物体为融合骨骼链',
        'fk_controls': 'FK 控制器',
        'load_fk': '加载选中物体为 FK 控制器',
        'ik_control': 'IK 控制器',
        'load_ik': '加载选中物体为 IK 控制器',
        'pole_vector': '肘/膝朝向控制器 (极向量)',
        'load_pv': '加载选中物体为朝向控制器',
        'save_limb': '保存此肢体',
        'clear_current': '清除当前',
        
        # Preset Section
        'presets': '预设',
        'save_preset': '保存所有肢体',
        'load_preset': '加载预设',
        'preset_saved': '预设已保存！',
        'preset_loaded': '预设已加载！肢体数量: ',
        'preset_error': '预设错误: ',
        
        # Action Section
        'actions': '匹配操作',
        'match_all_ik_to_fk': '全部 IK 匹配到 FK (切换IK模式时使用)',
        'match_all_fk_to_ik': '全部 FK 匹配到 IK (切换FK模式时使用)',
        'match_sel_ik_to_fk': '选中肢体: IK → FK (切换IK模式时使用)',
        'match_sel_fk_to_ik': '选中肢体: FK → IK (切换FK模式时使用)',
        'calibrate_all': '校准所有肢体',
        'calibrate_success': '校准完成！肢体数量: ',
        'calibrate_note': '* 校准前请将角色放到绑定姿势',
        
        # Settings
        'settings': '设置',
        'auto_key': '自动打Key',
        'use_matrix': '使用矩阵匹配',
        
        # Messages
        'no_selection': '请先选择物体',
        'no_limb_selected': '请先从列表选择一个肢体',
        'limb_saved': '肢体已保存: ',
        'limb_removed': '肢体已删除: ',
        'match_success': '匹配完成！',
        'need_blend': '请先加载融合骨骼',
        'need_fk': '请先加载 FK 控制器',
        'need_ik': '请先加载 IK 控制器',
        'obj_not_exist': '物体不存在: ',
        'enter_limb_name': '请输入肢体名称',
        
        # Help
        'help': '使用说明',
        'help_text': '肢体配置：\n'
                     '1. 输入肢体名称\n'
                     '2. 选择融合骨骼(Blend) [按顺序从根部到末端] → 加载\n'
                     '   (如果没有单独Blend链，请选择最终驱动蒙皮的骨骼链)\n'
                     '3. 选择FK控制器 [按顺序从根部到末端] → 加载\n'
                     '4. 选择IK控制器 → 加载\n'
                     '5. 选择肘/膝朝向控制器 → 加载\n'
                     '6. 保存此肢体\n'
                     '7. 重复添加其他肢体\n'
                     '8. 保存所有肢体为预设（可选）\n'
                     '9. 将角色放到绑定姿势 → 点击校准所有肢体\n'
                     '动画阶段FKIK切换：\n'
                     '• 加载预设（可选）\n'
                     '• 切换前在当前帧给FKIK控制器k帧后点击匹配按钮\n'
                     '• 后挪一帧切换FKIK属性后再给FKIK控制器k帧',
        
        # Author
        'author': 'Made by niexiongtao',
        'contact': '联系方式: niexiongtao@gmail.com',
    }
}


# ============================================================================
# 工具函数 / Utility Functions
# ============================================================================

def get_world_position(obj):
    """获取世界空间位置"""
    return cmds.xform(obj, query=True, worldSpace=True, translation=True)


def get_world_rotation(obj):
    """获取世界空间旋转"""
    return cmds.xform(obj, query=True, worldSpace=True, rotation=True)


def get_world_matrix(obj):
    """获取世界矩阵"""
    return cmds.xform(obj, query=True, worldSpace=True, matrix=True)


def set_world_position(obj, pos):
    """设置世界空间位置"""
    cmds.xform(obj, worldSpace=True, translation=pos)


def set_world_rotation(obj, rot):
    """设置世界空间旋转"""
    cmds.xform(obj, worldSpace=True, rotation=rot)


def match_transform_matrix(source, target, translate=True, rotate=True):
    """
    使用矩阵精确匹配变换
    
    Args:
        source: 要移动的物体
        target: 目标物体
        translate: 是否匹配位移
        rotate: 是否匹配旋转
    """
    if not cmds.objExists(source) or not cmds.objExists(target):
        return False
    
    target_matrix = get_world_matrix(target)
    parent = cmds.listRelatives(source, parent=True)
    
    if parent:
        parent_matrix = cmds.xform(parent[0], query=True, worldSpace=True, matrix=True)
        parent_m = om2.MMatrix(parent_matrix)
        target_m = om2.MMatrix(target_matrix)
        local_m = target_m * parent_m.inverse()
        transform_m = om2.MTransformationMatrix(local_m)
        
        if rotate:
            rotation = transform_m.rotation(asQuaternion=False)
            cmds.setAttr(f'{source}.rotateX', rotation.x * RAD_TO_DEG)
            cmds.setAttr(f'{source}.rotateY', rotation.y * RAD_TO_DEG)
            cmds.setAttr(f'{source}.rotateZ', rotation.z * RAD_TO_DEG)
        
        if translate:
            translation = transform_m.translation(om2.MSpace.kTransform)
            cmds.setAttr(f'{source}.translateX', translation.x)
            cmds.setAttr(f'{source}.translateY', translation.y)
            cmds.setAttr(f'{source}.translateZ', translation.z)
    else:
        cmds.xform(source, worldSpace=True, matrix=target_matrix)
    
    return True


def match_transform_simple(source, target, translate=True, rotate=True):
    """简单变换匹配"""
    if not cmds.objExists(source) or not cmds.objExists(target):
        return False
    
    if translate:
        set_world_position(source, get_world_position(target))
    if rotate:
        set_world_rotation(source, get_world_rotation(target))
    
    return True


def match_rotation_with_offset(source, target, offset_data=None):
    """
    使用预计算的四元数偏移匹配旋转
    
    公式: IK_quat = Offset_quat × Blend_quat
    
    这个函数用于解决IK控制器和Blend骨骼局部坐标系不同导致的旋转偏差问题。
    偏移四元数在校准阶段（T-Pose）计算，记录了两者之间的纯旋转差异。
    
    Args:
        source: IK控制器（要设置旋转的对象）
        target: Blend骨骼（参考旋转来源）
        offset_data: 预计算的偏移数据:
                     - 4个浮点数 [x,y,z,w] = 四元数（新格式）
    
    Returns:
        bool: 成功返回True，失败返回False
    """
    if not cmds.objExists(source) or not cmds.objExists(target):
        return False
    
    # 获取目标（Blend骨骼）的世界旋转四元数
    target_world_m = om2.MMatrix(get_world_matrix(target))
    target_transform = om2.MTransformationMatrix(target_world_m)
    target_quat = target_transform.rotation(asQuaternion=True)
    
    # 应用旋转偏移
    if offset_data and len(offset_data) == 4:
        # 新格式：四元数 [x, y, z, w]
        offset_quat = om2.MQuaternion(offset_data[0], offset_data[1], offset_data[2], offset_data[3])
        # 最终旋转 = 偏移四元数 × Blend四元数
        final_quat = offset_quat * target_quat
    elif offset_data and len(offset_data) == 16:
        # 旧格式：矩阵（兼容性一般）
        offset_m = om2.MMatrix(offset_data)
        final_world_m = offset_m * target_world_m
        final_transform = om2.MTransformationMatrix(final_world_m)
        final_quat = final_transform.rotation(asQuaternion=True)
    else:
        final_quat = target_quat
    
    # 将四元数转换为欧拉角
    final_euler = final_quat.asEulerRotation()
    
    # 考虑source的父级空间，计算局部旋转
    parent = cmds.listRelatives(source, parent=True)
    if parent:
        # 获取父级的世界旋转
        parent_world_m = om2.MMatrix(cmds.xform(parent[0], q=True, ws=True, m=True))
        parent_transform = om2.MTransformationMatrix(parent_world_m)
        parent_quat = parent_transform.rotation(asQuaternion=True)
        
        # 局部旋转 = 父级逆 × 世界旋转
        local_quat = parent_quat.inverse() * final_quat
        local_euler = local_quat.asEulerRotation()
        
        cmds.setAttr(f'{source}.rotateX', local_euler.x * RAD_TO_DEG)
        cmds.setAttr(f'{source}.rotateY', local_euler.y * RAD_TO_DEG)
        cmds.setAttr(f'{source}.rotateZ', local_euler.z * RAD_TO_DEG)
    else:
        # 无父级时，直接使用世界旋转
        cmds.setAttr(f'{source}.rotateX', final_euler.x * RAD_TO_DEG)
        cmds.setAttr(f'{source}.rotateY', final_euler.y * RAD_TO_DEG)
        cmds.setAttr(f'{source}.rotateZ', final_euler.z * RAD_TO_DEG)
    
    return True


def calculate_pole_vector_position(start_pos, mid_pos, end_pos, distance=1.0):
    """计算极向量位置"""
    start = om2.MVector(start_pos)
    mid = om2.MVector(mid_pos)
    end = om2.MVector(end_pos)
    
    start_end = end - start
    start_mid = mid - start
    
    if start_end.length() < 0.001:
        return list(mid)
    
    projection = start + start_end * ((start_mid * start_end) / (start_end * start_end))
    pv_direction = mid - projection
    
    if pv_direction.length() < 0.001:
        pv_direction = om2.MVector(0, 0, 1)
    else:
        pv_direction.normalize()
    
    pv_pos = mid + pv_direction * distance * (start_end.length() * 0.5)
    return [pv_pos.x, pv_pos.y, pv_pos.z]


def get_preset_directory():
    """获取预设存储目录"""
    script_dir = cmds.internalVar(userScriptDir=True)
    preset_dir = os.path.join(script_dir, 'fkik_match_presets')
    if not os.path.exists(preset_dir):
        os.makedirs(preset_dir)
    return preset_dir


@contextmanager
def undo_chunk():
    """上下文管理器：将操作包装在单个撤销块中"""
    cmds.undoInfo(openChunk=True)
    try:
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


# ============================================================================
# 肢体数据类 / Limb Data Class
# ============================================================================

class LimbData:
    """存储单个肢体的FK/IK配置"""
    
    def __init__(self, name=''):
        self.name = name
        self.blend_joints = []  # 融合骨骼（参考来源）
        self.fk_controls = []   # FK控制器（匹配目标）
        self.ik_control = None  # IK控制器
        self.pole_vector = None # 极向量
        self.rotation_offset = None  # 旋转偏移量 [rx, ry, rz]（校准时记录）
    
    def to_dict(self):
        return {
            'name': self.name,
            'blend_joints': self.blend_joints,
            'fk_controls': self.fk_controls,
            'ik_control': self.ik_control,
            'pole_vector': self.pole_vector,
            'rotation_offset': self.rotation_offset
        }
    
    @classmethod
    def from_dict(cls, data):
        limb = cls(data.get('name', ''))
        limb.blend_joints = data.get('blend_joints', [])
        limb.fk_controls = data.get('fk_controls', [])
        limb.ik_control = data.get('ik_control')
        limb.pole_vector = data.get('pole_vector')
        limb.rotation_offset = data.get('rotation_offset')
        return limb


# ============================================================================
# 主UI类 / Main UI Class
# ============================================================================

class FKIKMatchUI:
    """FK/IK 匹配工具 UI V4 - 使用融合骨骼作为参考"""
    
    WINDOW_NAME = 'fkik_match_window_v4'
    
    def __init__(self, language='en'):
        self.language = language
        
        # 所有肢体列表
        self.limbs = {}  # {name: LimbData}
        
        # 当前编辑的肢体
        self.current_limb = LimbData()
        
        # UI 元素
        self.limb_list_ui = None
        self.limb_name_field = None
        self.blend_list = None
        self.fk_list = None
        self.ik_field = None
        self.pv_field = None
        self.auto_key_cb = None
        self.use_matrix_cb = None
        
        self.create_ui()
    
    def get_text(self, key):
        return LANGUAGES[self.language].get(key, key)
    
    def create_ui(self):
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)
        
        self.window = cmds.window(
            self.WINDOW_NAME,
            title=self.get_text('window_title'),
            widthHeight=(400, 800),
            sizeable=True
        )
        
        cmds.scrollLayout(childResizable=True)
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        # ============ 语言切换 ============
        cmds.frameLayout(
            label=self.get_text('language'),
            collapsable=True,
            collapse=True,
            marginWidth=10,
            marginHeight=5
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180))
        cmds.button(label=self.get_text('chinese'), command=lambda x: self.switch_language('zh'), width=170)
        cmds.button(label=self.get_text('english'), command=lambda x: self.switch_language('en'), width=170)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 肢体设置 (先配置) ============
        cmds.frameLayout(
            label=self.get_text('definition'),
            collapsable=True,
            marginWidth=10,
            marginHeight=10
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        # 肢体名称
        cmds.text(label=self.get_text('limb_name'), align='left', font='boldLabelFont')
        self.limb_name_field = cmds.textField(placeholderText='e.g., L_Arm, R_Leg, Thumb')
        
        cmds.separator(height=10, style='in')
        
        # Blend Joints
        cmds.text(label=self.get_text('blend_joints') + ':', align='left', font='boldLabelFont')
        self.blend_list = cmds.textScrollList(height=50, allowMultiSelection=True)
        cmds.button(
            label=self.get_text('load_blend'),
            command=self.load_blend_joints,
            backgroundColor=(0.5, 0.7, 0.5)
        )
        
        cmds.separator(height=8, style='in')
        
        # FK Controls
        cmds.text(label=self.get_text('fk_controls') + ':', align='left')
        self.fk_list = cmds.textScrollList(height=50, allowMultiSelection=True)
        cmds.button(
            label=self.get_text('load_fk'),
            command=self.load_fk_controls,
            backgroundColor=(0.4, 0.6, 0.8)
        )
        
        cmds.separator(height=8, style='in')
        
        # IK Control
        cmds.text(label=self.get_text('ik_control') + ':', align='left')
        self.ik_field = cmds.textField(editable=True)
        cmds.button(
            label=self.get_text('load_ik'),
            command=self.load_ik_control,
            backgroundColor=(0.8, 0.5, 0.4)
        )
        
        cmds.separator(height=8, style='in')
        
        # Pole Vector
        cmds.text(label=self.get_text('pole_vector') + ':', align='left')
        self.pv_field = cmds.textField(editable=True)
        cmds.button(label=self.get_text('load_pv'), command=self.load_pole_vector)
        
        cmds.separator(height=10, style='none')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180))
        cmds.button(
            label=self.get_text('save_limb'),
            command=self.save_current_limb,
            width=170,
            height=35,
            backgroundColor=(0.3, 0.6, 0.3)
        )
        cmds.button(
            label=self.get_text('clear_current'),
            command=self.clear_current,
            width=170,
            height=35
        )
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 已保存肢体列表 ============
        cmds.frameLayout(
            label=self.get_text('limbs'),
            collapsable=True,
            marginWidth=10,
            marginHeight=10,
            backgroundColor=(0.25, 0.28, 0.32)
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        
        cmds.text(label=self.get_text('limb_list') + ':', align='left', font='boldLabelFont')
        self.limb_list_ui = cmds.textScrollList(
            height=80,
            allowMultiSelection=False,
            selectCommand=self.on_limb_selected
        )
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180))
        cmds.button(
            label=self.get_text('edit_limb'),
            command=self.edit_selected_limb,
            width=170
        )
        cmds.button(
            label=self.get_text('remove_limb'),
            command=self.remove_selected_limb,
            width=170,
            backgroundColor=(0.6, 0.3, 0.3)
        )
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 预设 ============
        cmds.frameLayout(
            label=self.get_text('presets'),
            collapsable=True,
            marginWidth=10,
            marginHeight=10
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180))
        cmds.button(label=self.get_text('save_preset'), command=self.save_preset, width=170, backgroundColor=(0.3, 0.5, 0.3))
        cmds.button(label=self.get_text('load_preset'), command=self.load_preset, width=170, backgroundColor=(0.3, 0.3, 0.5))
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 匹配操作 ============
        cmds.frameLayout(
            label=self.get_text('actions'),
            collapsable=True,
            marginWidth=10,
            marginHeight=10
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8)
        
        cmds.button(
            label=self.get_text('match_all_ik_to_fk'),
            command=self.match_all_ik_to_fk,
            height=50,
            backgroundColor=(0.3, 0.7, 0.4)
        )
        cmds.button(
            label=self.get_text('match_all_fk_to_ik'),
            command=self.match_all_fk_to_ik,
            height=50,
            backgroundColor=(0.7, 0.4, 0.3)
        )
        
        cmds.separator(height=5, style='in')
        
        cmds.button(
            label=self.get_text('match_sel_ik_to_fk'),
            command=self.match_selected_ik_to_fk,
            height=35
        )
        cmds.button(
            label=self.get_text('match_sel_fk_to_ik'),
            command=self.match_selected_fk_to_ik,
            height=35
        )
        
        cmds.separator(height=10, style='in')
        
        # 校准按钮
        cmds.text(label=self.get_text('calibrate_note'), align='left', font='smallObliqueLabelFont')
        cmds.button(
            label=self.get_text('calibrate_all'),
            command=self.calibrate_all_limbs,
            height=35,
            backgroundColor=(0.5, 0.5, 0.7)
        )
        
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 设置 ============
        cmds.frameLayout(label=self.get_text('settings'), collapsable=True, collapse=True, marginWidth=10, marginHeight=10)
        cmds.columnLayout(adjustableColumn=True)
        self.auto_key_cb = cmds.checkBox(label=self.get_text('auto_key'), value=False)
        self.use_matrix_cb = cmds.checkBox(label=self.get_text('use_matrix'), value=True)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # ============ 帮助 ============
        cmds.frameLayout(label=self.get_text('help'), collapsable=True, collapse=False, marginWidth=10, marginHeight=10)
        cmds.columnLayout(adjustableColumn=True)
        cmds.scrollField(
            text=self.get_text('help_text'),
            editable=False,
            wordWrap=True,
            height=180,
            font='smallPlainLabelFont'
        )
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        
        
        # ============ 作者 ============
        cmds.separator(height=10, style='none')
        cmds.text(label=self.get_text('author'), align='center', font='smallObliqueLabelFont')
        cmds.text(label=self.get_text('contact'), align='center', font='smallObliqueLabelFont')
        cmds.separator(height=5, style='none')
        
        cmds.showWindow(self.window)
    
    def switch_language(self, lang):
        """
        切换语言 - 使用 evalDeferred 避免窗口重建竞态条件
        """
        # 1. 保存当前数据到临时变量
        self._saved_limbs = self.limbs.copy()
        self._saved_current = self.current_limb
        
        # 2. 更新语言设置
        self.language = lang
        
        # 3. 延迟执行UI重建（等待当前窗口完全销毁后）
        cmds.evalDeferred(self._do_rebuild_ui)
    
    def _do_rebuild_ui(self):
        """
        延迟执行的UI重建函数
        在 Maya 空闲时执行，确保旧窗口已完全销毁
        """
        try:
            # 重建UI
            self.create_ui()
            
            # 恢复数据
            if hasattr(self, '_saved_limbs'):
                self.limbs = self._saved_limbs
                self.current_limb = self._saved_current
                
                # 清理临时变量
                del self._saved_limbs
                del self._saved_current
            
            # 刷新列表
            if self.limbs:
                self.update_limb_list_ui()
                
        except RuntimeError as e:
            cmds.warning(f'UI rebuild failed: {e}')
    
    def update_limb_list_ui(self):
        """更新肢体列表UI"""
        cmds.textScrollList(self.limb_list_ui, edit=True, removeAll=True)
        for name in self.limbs.keys():
            cmds.textScrollList(self.limb_list_ui, edit=True, append=name)
    
    def update_current_limb_ui(self):
        """更新当前肢体编辑区UI"""
        cmds.textField(self.limb_name_field, edit=True, text=self.current_limb.name)
        
        cmds.textScrollList(self.blend_list, edit=True, removeAll=True)
        for jnt in self.current_limb.blend_joints:
            cmds.textScrollList(self.blend_list, edit=True, append=jnt)
        
        cmds.textScrollList(self.fk_list, edit=True, removeAll=True)
        for ctrl in self.current_limb.fk_controls:
            cmds.textScrollList(self.fk_list, edit=True, append=ctrl)
        
        cmds.textField(self.ik_field, edit=True, text=self.current_limb.ik_control or '')
        cmds.textField(self.pv_field, edit=True, text=self.current_limb.pole_vector or '')
    
    # ============ 加载功能 ============
    
    def load_blend_joints(self, *args):
        """加载融合骨骼"""
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning(self.get_text('no_selection'))
            return
        self.current_limb.blend_joints = selection
        cmds.textScrollList(self.blend_list, edit=True, removeAll=True)
        for jnt in selection:
            cmds.textScrollList(self.blend_list, edit=True, append=jnt)
    
    def load_fk_controls(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning(self.get_text('no_selection'))
            return
        self.current_limb.fk_controls = selection
        cmds.textScrollList(self.fk_list, edit=True, removeAll=True)
        for ctrl in selection:
            cmds.textScrollList(self.fk_list, edit=True, append=ctrl)
    
    def load_ik_control(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning(self.get_text('no_selection'))
            return
        self.current_limb.ik_control = selection[0]
        cmds.textField(self.ik_field, edit=True, text=selection[0])
    
    def load_pole_vector(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning(self.get_text('no_selection'))
            return
        self.current_limb.pole_vector = selection[0]
        cmds.textField(self.pv_field, edit=True, text=selection[0])
    
    def clear_current(self, *args):
        self.current_limb = LimbData()
        self.update_current_limb_ui()
    
    # ============ 肢体管理 ============
    
    def save_current_limb(self, *args):
        """保存当前肢体到列表"""
        name = cmds.textField(self.limb_name_field, query=True, text=True).strip()
        if not name:
            cmds.warning(self.get_text('enter_limb_name'))
            return
        
        # 从UI读取最新值
        self.current_limb.name = name
        self.current_limb.ik_control = cmds.textField(self.ik_field, query=True, text=True) or None
        self.current_limb.pole_vector = cmds.textField(self.pv_field, query=True, text=True) or None
        
        # 保存到字典
        self.limbs[name] = LimbData.from_dict(self.current_limb.to_dict())
        
        self.update_limb_list_ui()
        print(self.get_text('limb_saved') + name)
        
        # 清空当前编辑区
        self.clear_current()
    
    def on_limb_selected(self, *args):
        pass
    
    def edit_selected_limb(self, *args):
        """编辑选中的肢体"""
        selected = cmds.textScrollList(self.limb_list_ui, query=True, selectItem=True)
        if not selected:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        name = selected[0]
        if name in self.limbs:
            self.current_limb = LimbData.from_dict(self.limbs[name].to_dict())
            self.update_current_limb_ui()
    
    def remove_selected_limb(self, *args):
        """删除选中的肢体"""
        selected = cmds.textScrollList(self.limb_list_ui, query=True, selectItem=True)
        if not selected:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        name = selected[0]
        if name in self.limbs:
            del self.limbs[name]
            self.update_limb_list_ui()
            print(self.get_text('limb_removed') + name)
    
    # ============ 预设功能 ============
    
    def _get_match_settings(self):
        """获取匹配设置（减少重复代码）"""
        use_matrix = cmds.checkBox(self.use_matrix_cb, query=True, value=True)
        auto_key = cmds.checkBox(self.auto_key_cb, query=True, value=True)
        return use_matrix, auto_key
    
    def save_preset(self, *args):
        if not self.limbs:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        result = cmds.fileDialog2(
            fileMode=0,
            caption='Save FK/IK Preset',
            fileFilter='JSON Files (*.json)',
            startingDirectory=get_preset_directory()
        )
        
        if not result:
            return
        
        file_path = result[0]
        preset_data = {name: limb.to_dict() for name, limb in self.limbs.items()}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)
        
        cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("preset_saved")}</span>', pos='midCenter', fade=True)
    
    def load_preset(self, *args):
        result = cmds.fileDialog2(
            fileMode=1,
            caption='Load FK/IK Preset',
            fileFilter='JSON Files (*.json)',
            startingDirectory=get_preset_directory()
        )
        
        if not result:
            return
        
        file_path = result[0]
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            
            self.limbs = {name: LimbData.from_dict(data) for name, data in preset_data.items()}
            self.update_limb_list_ui()
            
            cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("preset_loaded")}{len(self.limbs)}</span>', pos='midCenter', fade=True)
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            cmds.warning(self.get_text('preset_error') + str(e))
    
    # ============ 匹配功能 ============
    
    def match_limb_ik_to_fk(self, limb, use_matrix=True, auto_key=False):
        """
        匹配单个肢体的IK到FK
        
        核心逻辑：将IK控制器移动到Blend末端的位置
        """
        if not limb.blend_joints:
            return False
        
        if not limb.ik_control or not cmds.objExists(limb.ik_control):
            return False
        
        # 参考末端 = Blend骨骼的最后一个
        ref_end = limb.blend_joints[-1]
        
        if not cmds.objExists(ref_end):
            return False
        
        target_pos = get_world_position(ref_end)

        # 0. 优先设置极向量 (PV)
        # 必须先设置PV，因为PV的位置决定了IK链的平面朝向
        # 如果后设置PV，会导致IK Solver更新骨骼，从而改变末端骨骼的旋转，导致之前的旋转设置失效
        if limb.pole_vector and cmds.objExists(limb.pole_vector) and len(limb.blend_joints) >= 3:
            pv_pos = calculate_pole_vector_position(
                get_world_position(limb.blend_joints[0]),
                get_world_position(limb.blend_joints[1]),
                get_world_position(limb.blend_joints[-1])
            )
            set_world_position(limb.pole_vector, pv_pos)
            
            if auto_key:
                cmds.setKeyframe(limb.pole_vector)
        
        # 混合匹配策略：
        # 位置：使用简单世界空间匹配（直接复制）
        # 旋转：使用预校准偏移矩阵匹配（补偿IK控制器和Blend骨骼的朝向差异）
        
        # 1. 匹配位置 - 简单世界空间
        set_world_position(limb.ik_control, target_pos)
        
        # 2. 匹配旋转 - 使用四元数偏移补偿IK控制器和Blend骨骼的朝向差异
        if limb.rotation_offset:
            match_rotation_with_offset(limb.ik_control, ref_end, limb.rotation_offset)
        else:
            # 没有校准数据时回退到直接匹配
            match_transform_matrix(limb.ik_control, ref_end, translate=False, rotate=True)
        
        # 打Key
        if auto_key:
            cmds.setKeyframe(limb.ik_control)
        
        return True
    
    def match_limb_fk_to_ik(self, limb, use_matrix=True, auto_key=False):
        """
        匹配单个肢体的FK到IK
        
        核心逻辑：将FK控制器旋转匹配到对应的Blend骨骼
        """
        if not limb.fk_controls or not limb.blend_joints:
            return False
        
        # 遍历FK控制器，匹配到对应的Blend骨骼
        for i, fk_ctrl in enumerate(limb.fk_controls):
            if not cmds.objExists(fk_ctrl):
                continue
            if i < len(limb.blend_joints):
                blend_jnt = limb.blend_joints[i]
                if cmds.objExists(blend_jnt):
                    if use_matrix:
                        # 只有第一个FK控制器(根部)需要匹配位移，其他只匹配旋转
                        match_transform_matrix(fk_ctrl, blend_jnt, translate=(i == 0), rotate=True)
                    else:
                        if i == 0:
                            set_world_position(fk_ctrl, get_world_position(blend_jnt))
                        set_world_rotation(fk_ctrl, get_world_rotation(blend_jnt))
        
        if auto_key:
            for fk_ctrl in limb.fk_controls:
                if cmds.objExists(fk_ctrl):
                    cmds.setKeyframe(fk_ctrl, attribute='rotate')
        
        return True
    
    def match_all_ik_to_fk(self, *args):
        """匹配所有肢体 IK -> FK"""
        use_matrix, auto_key = self._get_match_settings()
        
        with undo_chunk():
            for limb in self.limbs.values():
                self.match_limb_ik_to_fk(limb, use_matrix, auto_key)
            
            cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("match_success")}</span>', pos='midCenter', fade=True)
    
    def match_all_fk_to_ik(self, *args):
        """匹配所有肢体 FK -> IK"""
        use_matrix, auto_key = self._get_match_settings()
        
        with undo_chunk():
            for limb in self.limbs.values():
                self.match_limb_fk_to_ik(limb, use_matrix, auto_key)
            
            cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("match_success")}</span>', pos='midCenter', fade=True)
    
    def calibrate_all_limbs(self, *args):
        """
        校准所有肢体的旋转偏移
        
        在绑定姿势（T-Pose）下执行，记录 IK控制器 和 Blend骨骼 之间的旋转差
        这个差值会在匹配时应用，确保旋转正确传递
        """
        if not self.limbs:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        calibrated_count = 0
        
        for name, limb in self.limbs.items():
            # 检查必要的对象是否存在
            if not limb.ik_control or not cmds.objExists(limb.ik_control):
                continue
            
            if not limb.blend_joints or len(limb.blend_joints) == 0:
                continue
            
            ref_end = limb.blend_joints[-1]
            if not cmds.objExists(ref_end):
                continue
            
            # 提取纯旋转（四元数）- 避免位移干扰
            ik_transform = om2.MTransformationMatrix(om2.MMatrix(get_world_matrix(limb.ik_control)))
            blend_transform = om2.MTransformationMatrix(om2.MMatrix(get_world_matrix(ref_end)))
            
            ik_quat = ik_transform.rotation(asQuaternion=True)
            blend_quat = blend_transform.rotation(asQuaternion=True)
            
            # 使用四元数计算纯旋转偏移: offset_quat = IK_quat × Blend_quat⁻¹
            # 这只捕捉旋转差异，不受位移影响
            blend_quat_inv = blend_quat.inverse()
            offset_quat = ik_quat * blend_quat_inv
            
            # 存储四元数的4个分量 [x, y, z, w]
            limb.rotation_offset = [offset_quat.x, offset_quat.y, offset_quat.z, offset_quat.w]
            
            calibrated_count += 1
        
        cmds.inViewMessage(
            amg=f'<span style="color:#aaaaff;">{self.get_text("calibrate_success")}{calibrated_count}</span>',
            pos='midCenter',
            fade=True
        )

    
    def match_selected_ik_to_fk(self, *args):
        """匹配选中肢体 IK -> FK"""
        selected = cmds.textScrollList(self.limb_list_ui, query=True, selectItem=True)
        if not selected:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        name = selected[0]
        if name in self.limbs:
            use_matrix, auto_key = self._get_match_settings()
            
            with undo_chunk():
                self.match_limb_ik_to_fk(self.limbs[name], use_matrix, auto_key)
                cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("match_success")}</span>', pos='midCenter', fade=True)
    
    def match_selected_fk_to_ik(self, *args):
        """匹配选中肢体 FK -> IK"""
        selected = cmds.textScrollList(self.limb_list_ui, query=True, selectItem=True)
        if not selected:
            cmds.warning(self.get_text('no_limb_selected'))
            return
        
        name = selected[0]
        if name in self.limbs:
            use_matrix, auto_key = self._get_match_settings()
            
            with undo_chunk():
                self.match_limb_fk_to_ik(self.limbs[name], use_matrix, auto_key)
                cmds.inViewMessage(amg=f'<span style="color:#00ff00;">{self.get_text("match_success")}</span>', pos='midCenter', fade=True)


# ============================================================================
# 启动函数 / Launch Function
# ============================================================================

def show_ui(language='en'):
    return FKIKMatchUI(language=language)


if __name__ == '__main__':
    show_ui('en')
