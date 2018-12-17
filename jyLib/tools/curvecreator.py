import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from .. import common
from .. import curves


class CurveCreator(object):

    def __init__(self):
        gToolOptionBoxTemplateFrameSpacing = common.getVariable('gToolOptionBoxTemplateFrameSpacing')

        cmds.setUITemplate('ToolOptionBoxTemplate', pst=True)

        self.formMain = pm.formLayout()

        column = pm.columnLayout(cat=('both', 5), rs=5, bgc=(1, 0, 0))
        for uType, dictInfo in curves.CURVEINFO.iteritems():
            btn = pm.button()
            btn.setLabel(uType)
            btn.setCommand(pm.Callback(curves.create, uType))

        self.formMain.attachForm(column, 'left', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachForm(column, 'top', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachForm(column, 'right', gToolOptionBoxTemplateFrameSpacing)
        self.formMain.attachForm(column, 'bottom', gToolOptionBoxTemplateFrameSpacing)

        cmds.setUITemplate(ppt=True)

    