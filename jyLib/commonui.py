import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def initWindow(uName):
    """Initilizes a window object with the given name.

    Checks if any windows are open with the given name. If there is one
    delete that window and make a new one. If there are any window
    preferences, delete them.

    Args:
        uName (str): name of window
    Returns:
        winResult: PyNode window
    """
    # Search all windows
    allWindows = pm.lsUI(wnd=True)
    # Find out if the window exists
    try:
        # If so, delete it
        winResult = allWindows[allWindows.index(uName)]
        pm.deleteUI(winResult)
    except ValueError:
        pass
    # Create the window and add window settings
    winResult = pm.window(uName)
    if pm.windowPref(winResult, ex=True):
        pm.windowPref(winResult, r=True)
    return winResult


class Selector(object):
    
    def __init__(self, uLabel='Select:', uName='Selector1'):
        self.formMain = pm.formLayout('formMain{}'.format(uName))
        txtDesc = pm.text('txtDesc{}'.format(uName))
        txtDesc.setLabel(uLabel)
        txtDesc.setAlign('left')
        self.txtlSelected = pm.textScrollList('txtlistSelected{}'.format(uName))
        self.btnSelect = pm.button('btnSelect{}'.format(uName))
        self.btnSelect.setLabel('Select')
        self.btnSelect.setWidth(60)
        self.btnSelect.setCommand(pm.Callback(self._select))
        self.btnClear = pm.button('btnClear{}'.format(uName))
        self.btnClear.setLabel('Clear')
        self.btnClear.setWidth(60)
        self.btnClear.setCommand(pm.Callback(self._clear))

        self.formMain.attachForm(txtDesc, 'left', 20)
        self.formMain.attachForm(txtDesc, 'top', 5)
        self.formMain.attachForm(txtDesc, 'right', 20)
        self.formMain.attachNone(txtDesc, 'bottom')
        self.formMain.attachForm(self.txtlSelected, 'left', 5)
        self.formMain.attachControl(self.txtlSelected, 'top', 5, txtDesc)
        self.formMain.attachControl(self.txtlSelected, 'right', 10, self.btnSelect)
        self.formMain.attachNone(self.txtlSelected, 'bottom')
        self.formMain.attachNone(self.btnSelect, 'left')
        self.formMain.attachControl(self.btnSelect, 'top', 18, txtDesc)
        self.formMain.attachForm(self.btnSelect, 'right', 5)
        self.formMain.attachNone(self.btnSelect, 'bottom')
        self.formMain.attachNone(self.btnClear, 'left')
        self.formMain.attachControl(self.btnClear, 'top', 5, self.btnSelect)
        self.formMain.attachForm(self.btnClear, 'right', 5)
        self.formMain.attachNone(self.btnClear, 'bottom')
        pm.setParent('..')

        self._lItems = []

    
    @property
    def lItems(self):
        return self._lItems

    def _clear(self):
        """Clears the items in the list and text scroll list."""
        self._lItems = []
        self.txtlSelected.removeAll()
    
    def _select(self):
        """Modifies the stored items based on the current selection and current modified keys pressed."""
        intModifiers = cmds.getModifiers()
        if intModifiers & 1 == 0 and intModifiers & 4 == 0:
            # Neither Shift nor Ctrl keys are pressed
            # Set the items to the currently selected only
            self._lItems = pm.ls(sl=True)
            self.txtlSelected.removeAll()
            self.txtlSelected.append([x.longName() for x in self._lItems])
        else:
            # A combination of Shift and Ctrl keys are pressed
            for oItem in pm.ls(sl=True):
                if intModifiers & 1 > 0 and intModifiers & 4 > 0:
                    # Shift and Ctrl keys are both pressed
                    # Add all selected items if they are not already included
                    if oItem not in self._lItems:
                        self._lItems.append(oItem)
                        self.txtlSelected.append(oItem.longName())
                elif intModifiers & 1 > 0:
                    # Only Shift is pressed
                    # Toggle selection of items
                    if oItem in self._lItems:
                        self._lItems.remove(oItem)
                        self.txtlSelected.removeItem(oItem.longName())
                    else:
                        self._lItems.append(oItem)
                        self.txtlSelected.append(oItem.longName())
                elif intModifiers & 4 > 0:
                    # Only Ctrl is pressed
                    # Remove selected itmes if they are included
                    try:
                        self._lItems.remove(oItem)
                        self.txtlSelected.removeItem(oItem.longName())
                    except ValueError:
                        pass


