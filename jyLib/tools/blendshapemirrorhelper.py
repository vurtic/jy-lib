import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from .. import common
from .. import commonui

class BlendshapeMirrorHelper(object):

    def __init__(self):
        gToolOptionBoxTemplateFrameSpacing = common.getVariable('gToolOptionBoxTemplateFrameSpacing')

        cmds.setUITemplate('ToolOptionBoxTemplate', pst=True)

        self.formMain = pm.formLayout()
        self.blendshapeSelector = commonui.Selector('Blendshapes:', 'BlendshapeSelector1')
        self.baseSelector = commonui.Selector('Base:', 'BaseSelector1')
        self.btnLeft = pm.button()
        self.btnLeft.setLabel('Reset Left')
        self.btnLeft.setCommand(pm.Callback(self._resetSideCallback, 'left'))
        self.btnRight = pm.button()
        self.btnRight.setLabel('Reset Right')
        self.btnRight.setCommand(pm.Callback(self._resetSideCallback, 'right'))

        self.formMain.attachForm(self.blendshapeSelector.formMain, 'left', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachForm(self.blendshapeSelector.formMain, 'top', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachForm(self.blendshapeSelector.formMain, 'right', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachNone(self.blendshapeSelector.formMain, 'bottom')
        self.formMain.attachForm(self.baseSelector.formMain, 'left', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachControl(self.baseSelector.formMain, 'top', gToolOptionBoxTemplateFrameSpacing, self.blendshapeSelector.formMain)
        self.formMain.attachForm(self.baseSelector.formMain, 'right', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachNone(self.baseSelector.formMain, 'bottom')
        self.formMain.attachPosition(self.btnLeft, 'left', 0, 10)
        self.formMain.attachControl(self.btnLeft, 'top', gToolOptionBoxTemplateFrameSpacing*3, self.baseSelector.formMain)
        self.formMain.attachPosition(self.btnLeft, 'right', 0, 45)
        self.formMain.attachNone(self.btnLeft, 'bottom')
        self.formMain.attachPosition(self.btnRight, 'left', 0, 55)
        self.formMain.attachControl(self.btnRight, 'top', gToolOptionBoxTemplateFrameSpacing*3, self.baseSelector.formMain)
        self.formMain.attachPosition(self.btnRight, 'right', 0, 90)
        self.formMain.attachNone(self.btnRight, 'bottom')

        cmds.setUITemplate(ppt=True)

    def _resetSideCallback(self, side):
        # Input validation
        if not self.blendshapeSelector.lItems:
            cmds.error('Select blendshape(s) to edit.')
        if not self.baseSelector.lItems:
            cmds.error('Select a base shape.')
        elif len(self.baseSelector.lItems) > 1:
            cmds.warning('More than one base shape is selected. Using {} as the base shape'.format(self.baseSelector.lItems[0]))

        resetSide(self.blendshapeSelector.lItems, self.baseSelector.lItems[0], side)


def resetSide(lBlendshapeMeshes, xBaseMesh, side):
    """Moves blendshape verticies to their base positions on one side.

    The verticies on the provided side of the provided blendshape meshes will be reset to their positions
    on the provided base mesh. Verticies on the center will be moved half-way. When two matching blendshapes
    from both sides are set to 1, the center verticies will move to the correct positions.

    Left, Right, and Center are based the +Z direction being forward.
    
    Args:
        lBlendshapeMeshes (list of meshes): blendshapes to edit
        xBaseMesh (mesh): base mesh to compare to
        side (str): side to reset (left, right)
    """
    # Get info about the base mesh
    dictBaseSorted = _sortVerticies(xBaseMesh)
    for xBlendshapeMesh in lBlendshapeMeshes:
        # Perform this action on each blendshape
        if len(xBlendshapeMesh.vtx) != len(xBaseMesh.vtx):
            # Warning about potential non-matching blendshape and base meshes
            cmds.warning("{} and {} have different vertex counts.".format(xBlendshapeMesh.name(), xBaseMesh.name()))
        for i, iSide in dictBaseSorted.iteritems():
            # Iterate through each vertex index
            # Position of the base vertex
            lBaseVtxPos = cmds.pointPosition('{}.vtx[{}]'.format(xBaseMesh.name(), i))
            # Position of the blendshape vertex
            lBlendshapeVtxPos = cmds.pointPosition('{}.vtx[{}]'.format(xBlendshapeMesh.name(), i))
            if lBaseVtxPos != lBlendshapeVtxPos:
                if iSide == side:
                    cmds.xform('{}.vtx[{}]'.format(xBlendshapeMesh.name(), i), ws=True, t=lBaseVtxPos)
                elif iSide == 'center':
                    cmds.xform('{}.vtx[{}]'.format(xBlendshapeMesh.name(), i), ws=True, t=common.midpoint(lBaseVtxPos, lBlendshapeVtxPos))


def _sortVerticies(xMesh):
    """Returns a dictionary of vertex indicies and their side (left, right, center)
    
    Left, Right, and Center are based the +Z direction being forward.
    
    Args:
        xMesh (mesh): the mesh to sort
    """
    dictResult = {}
    uMesh = xMesh.longName()
    for i in xrange(len(xMesh.vtx)):
        lPos = cmds.pointPosition('{}.vtx[{}]'.format(uMesh, i), world=True)
        if common.isclose(0, lPos[0], abs_tol=0.000001):
            dictResult[i] = 'center'
        elif lPos[0] > 0:
            dictResult[i] = 'left'
        else:
            dictResult[i] = 'right'
    return dictResult




