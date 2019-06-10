import itertools
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import pymel.core.datatypes as dt
from .. import common

def create(lJoints):
    """Creates matching IK and FK chains and connects them with the bind chain with blend colors.

    Duplicates the provided joint chain twice to create an IK and FK chain. Creates blend
    color nodes so that the rotations of the IK chain can blend into the FK chain and vice
    versa.

    Args:
        lJoints (list of joints): bind chain
    Returns:
        list, list: list of IK joints, list of FK joints
    """
    lJoints = common.checkContinuousHierarchy(lJoints)

    lIKJoints = []
    lFKJoints = []
    lBlendColors = []

    for jntCurrent in lJoints:
        # Create the duplicate IK and FK joints and add them to their respective lists
        lSplit = jntCurrent.name().split('_')

        jntIK = pm.duplicate(jntCurrent, n='{}_{}_{}IK_d'.format(lSplit[0], lSplit[1], lSplit[2]),
                             po=True)[0]
        jntIK.radius.set(jntCurrent.radius.get() * 0.7)
        lIKJoints.append(jntIK)

        jntFK = pm.duplicate(jntCurrent, n='{}_{}_{}FK_d'.format(lSplit[0], lSplit[1], lSplit[2]),
                             po=True)[0]
        jntFK.radius.set(jntCurrent.radius.get() * 0.4)
        lFKJoints.append(jntFK)

    for i in xrange(len(lIKJoints)-1, 0, -1):
        # Parent the IK and FK joints to create the heierachy
        pm.parent(lIKJoints[i], lIKJoints[i-1])
        pm.parent(lFKJoints[i], lFKJoints[i-1])

    for (jntBind, jntIK, jntFK) in itertools.izip(lJoints, lIKJoints, lFKJoints):
        lSplit = jntBind.split('_')
        blendcCurrent = pm.createNode('blendColors', n='BlendC_{}_{}'.format(lSplit[1], lSplit[2]))
        lBlendColors.append(blendcCurrent)

        jntFK.rotate >> blendcCurrent.color1
        jntIK.rotate >> blendcCurrent.color2
        blendcCurrent.output >> jntBind.rotate

        blendcCurrent.blender.set(0)

    return (lIKJoints, lFKJoints, lBlendColors)


def rig(lIKJoints, lFKJoints, lBlendColors, uName, xIKEndCtrl=None, xIKPVCtrl=None,
        lFKCtrls=None, xIKFKSwitchCtrl=None):
    """Rigs the IKFK limb to the provided controls.

    Creates an IK Handle to control the IK chain. Constrains provided end effector controls
    and pole vector controls to the IK Handle. Constrains provided FK controls to control
    the FK chain. Sets up a blending attribute on a provided switch controller. If there
    is no IKFK attribute on the switch controller, one is created.

    Args:
        lIKJoints (list of joints): the IK chain
        lFKJoints (list of joints): the FK chain
        lBlendColors (list of blend colors): the blend color nodes for the matching chains
        uName (str): name of the limb
        xIKEndCtrl (xform, optional): the IK end controller
        xIKPVCtrl (xform, optional): the IK pole vector controller
        lFKCtrls (list of xforms, optional): the list of FK controllers matching the chain
        xIKFKSwitchCtrl (xform, optional): the IKFK switch controller
    """
    lIKHandle = pm.ikHandle(sj=lIKJoints[0], ee=lIKJoints[-1], n='IKH_{}'.format(uName))
    pm.rename(lIKHandle[1], 'IKE_{}'.format(uName))
    if xIKEndCtrl is not None:
        # If an IK End Control is provided
        if not common.hasOffsetXform(xIKEndCtrl):
            # If the IK End Control does not have an offset transform
            common.createOffsetXform(xIKEndCtrl, lIKJoints[-1])
        # Have the controller drive the IK Handle's position
        pm.pointConstraint(xIKEndCtrl, lIKHandle[0])
        # Have the controller drive the IK end joint's orientation
        pm.orientConstraint(xIKEndCtrl, lIKJoints[-1])
    if xIKPVCtrl is not None:
        # If an IK PV Control is provided
        if not common.hasOffsetXform(xIKPVCtrl):
            # If the IK PV Control does not have an offset transform
            xIKPVCtrlOffset = common.createOffsetXform(xIKPVCtrl)
        # Position the IK PV Control onto the same plane as the IK
        vecIKJoint1 = dt.Vector(pm.xform(lIKJoints[0], q=True, rp=True, ws=True))
        vecIKJoint2 = dt.Vector(pm.xform(lIKJoints[1], q=True, rp=True, ws=True))
        vecIKJoint3 = dt.Vector(pm.xform(lIKJoints[-1], q=True, rp=True, ws=True))
        vecIKPV = dt.Vector(pm.xform(xIKPVCtrlOffset, q=True, rp=True, ws=True))
        vecResult = common.calculateClosestPointOnPlane(vecIKJoint1, vecIKJoint2,
                                                        vecIKJoint3, vecIKPV)
        pm.xform(xIKPVCtrlOffset, t=vecResult, ws=True)
        # Have the PV control the IK
        pm.poleVectorConstraint(xIKPVCtrl, lIKHandle[0])
    if lFKCtrls is not None:
        for (xFKCtrl, xFKJnt) in itertools.izip(lFKCtrls, lFKJoints):
            if not common.hasOffsetXform(xFKCtrl):
                # If the FK controller does not have an offset transform
                common.createOffsetXform(xFKCtrl, xFKJnt)
            # Have each FK controller drive each FK joint
            pm.orientConstraint(xFKCtrl, xFKJnt)
    if xIKFKSwitchCtrl is not None:
        try:
            # Check if the IKFK attribute exists
            xIKFKSwitchCtrl.IKFK.set(0)
        except AttributeError:
            # Create the IKFK attribute if it does not exist
            pm.addAttr(xIKFKSwitchCtrl, ln='IKFK', at='double', min=0, max=10, dv=0)
            pm.setAttr(xIKFKSwitchCtrl.IKFK, e=True, k=True)

        # Set Driven Key the IKFK attribute to each blend colors blender
        for blendcCurrent in lBlendColors:
            pm.setDrivenKeyframe(blendcCurrent.blender, v=0, cd=xIKFKSwitchCtrl.IKFK, dv=0,
                                 itt='linear', ott='linear')
            pm.setDrivenKeyframe(blendcCurrent.blender, v=1, cd=xIKFKSwitchCtrl.IKFK, dv=10,
                                 itt='linear', ott='linear')
