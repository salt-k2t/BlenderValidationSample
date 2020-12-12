import os
import re
import bpy
from bpy.props import *

bl_info = {
    "name": "ValidateSample",
    "description": "Validate Sample For 2020 Advent Calendar.",
    "author": "salt-k2t",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf > Panel",
    "warning": "",
    "wiki_url": "",
    "category": "Development"
}


STANDARD_JOINT_REGEX = '^[a-zA-Z]+$'  # ex)sample
SIM_JOINT_REGEX = '^[a-zA-Z]+_s$'  # ex)sample_s
ANIM_CHANNEL_ROTATE_REGEX = '^rotation_euler$'

VALID_TEXT = "VALID"
INVALID_TEXT = "INVALID"

ANIMATION = "animation"
JOINT = "joint"
ALL = "all"
DEFAULT = "None"


class ValidateButton(bpy.types.Operator):
    bl_idname = "validate.button"
    bl_label = "Validate Button"
    bl_options = {'REGISTER', 'UNDO'}

    validation_type: StringProperty(default=DEFAULT)

    def execute(self, context):
        message = INVALID_TEXT
        invalid_items = []

        if ANIMATION == self.validation_type:
            if not self.animation_validator():
                invalid_items.append("animation")

        if JOINT == self.validation_type:
            if not self.joint_validator():
                invalid_items.append("joint")

        if ALL == self.validation_type:
            if not self.animation_validator():
                invalid_items.append("animation")
            if not self.joint_validator():
                invalid_items.append("joint")

        if invalid_items:
            message = INVALID_TEXT + " : " + ",".join(invalid_items)
        else:
            message = VALID_TEXT

        self.report({'INFO'}, message)
        return {'FINISHED'}

    def joint_validator(self):
        invalid_joints = []
        for ob in bpy.context.scene.objects:
            if ob.type == 'ARMATURE':
                for bone in ob.data.bones:
                    standard_joint_result = re.match(
                        STANDARD_JOINT_REGEX, bone.name)
                    if standard_joint_result:
                        continue

                    sim_joint_result = re.match(SIM_JOINT_REGEX, bone.name)
                    if sim_joint_result:
                        continue

                    invalid_joints.append(bone.name)
        if invalid_joints:
            print("""Not expected joint name 
{0}""".format(os.linesep.join(invalid_joints)))
            return False
        return True

    def animation_validator(self):
        invalid_animations = []

        for action in bpy.data.actions:
            for fcu in action.fcurves:
                joint_name = fcu.data_path.split('"')[1]
                sim_joint_result = re.match(SIM_JOINT_REGEX, joint_name)
                if sim_joint_result:
                    invalid_animations.append(joint_name)
                    continue
                channel = fcu.data_path.split(".")[-1]
                anim_channel_rotate_result = re.match(
                    ANIM_CHANNEL_ROTATE_REGEX, channel)
                if anim_channel_rotate_result:
                    continue
                invalid_animations.append(joint_name)

        if invalid_animations:
            print("""Not expected animation channel 
{0}""".format(os.linesep.join(invalid_animations)))
            return False
        return True


# PanelUI
class VaridateSamplePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ValidateSample"
    bl_label = "Validate Panel"

    def draw(self, context):
        layout = self.layout

        layout.operator(ValidateButton.bl_idname,
                        text=ANIMATION).validation_type = ANIMATION
        layout.operator(ValidateButton.bl_idname,
                        text=JOINT).validation_type = JOINT
        layout.operator(ValidateButton.bl_idname,
                        text=ALL).validation_type = ALL


# register classs
classs = [
    VaridateSamplePanel,
    ValidateButton
]


# register
def register():
    for c in classs:
        bpy.utils.register_class(c)


# unregister()
def unregister():
    for c in classs:
        bpy.utils.register_class(c)


# script entry
if __name__ == "__main__":
    register()
