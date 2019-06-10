import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import pymel.core.datatypes as dt


def getNamespace(uName):
    """Gets the namespace of the object.

    Args:
        uItem (str): the object
    Returns:
        str: the namespace
    """
    lSplit = uName.rsplit(':', 1)
    if len(lSplit) > 1:
        return lSplit[0]
    else:
        return ''


def getObjectName(uName):
    """Gets the name of the object without namespaces.

    Args:
        oItem (str or PyNode): the object
    Returns:
        str: the name of the object
    """
    try:
        return uName.rsplit(':', 1)[1]
    except IndexError:
        return uName


def reposition(oParent, oChild, uType='parent'):
    """Repositions the transforms based on the type of constraint provided.

    A single parent or list of parents can be provided. A single child or list of children can
    be provided. If multiple children are provided, the reposition will be performed on each
    child individually based on the parent(s) provided.

    Args:
        oParent (xform or list of xforms): parent or parents
        oChild (xform or list of xforms): child or children
        uType (str): type of action to perform (parent, point, orient)
    """
    lParent = _getListOfObjectNames(oParent)
    lChild = _getListOfObjectNames(oChild)
    for uChild in lChild:
        if uType == 'point':
            constraint = cmds.pointConstraint(lParent, uChild)
        elif uType == 'orient':
            constraint = cmds.orientConstraint(lParent, uChild)
        else:
            constraint = cmds.parentConstraint(lParent, uChild)
        cmds.delete(constraint)


def _getListOfObjectNames(oObj):
    """Converts a given object into a list of strings.

    Converts a single PyMel object or list of PyMel objects into
    a list of the objects' long names. Converts a string that refers to
    an object to a list containing that string.

    Args:
        oObj (xform or list of xforms): given object
    Returns:
        list: list of names of the objects
    """
    if isinstance(oObj, basestring):
        lObj = [oObj]
    elif isinstance(oObj, pm.nodetypes.DagNode):
        lObj = [oObj]
    else:
        lObj = oObj
    try:
        lObj = [x.longName() for x in lObj]
    except AttributeError:
        pass
    return lObj


def getHierarchy(xStart, xEnd):
    """Returns a list that contains the hierarchy of nodes from the start node to the end node.

    Args:
        xStart (node): start node
        xEnd (node): end node
    Returns:
        list: ordered hierarchy of nodes from the start node to the end node
    """
    # Check if both nodes are hierarchically connected
    if all([node != xEnd for node in pm.listRelatives(xStart, ad=True)]):
        pm.error('There is no hierarchical connection from {} to {}.'.format(xStart, xEnd))
    # Build a list that will contain all the nodes from start to end
    lNodes = [xEnd]
    current = xEnd
    # Keep adding nodes to the front of the list until you get to the start node
    while current != xStart:
        current = current.getParent()
        lNodes.insert(0, current)
    return lNodes


def parentShapes(lShapes, xParent):
    """Parents all the given shapes to the given transform

    The shapes will be parented under the transform without being moved.

    Args:
        lShapes (list of shapes): a list containing all the shapes to add
        xformParent (transform): the transform that the shapes will be parented under
    """
    for shapeNode in lShapes:
        # Reparent the shape node under the new parent with the absolute flag
        pm.parent(shapeNode, xParent, s=True, a=True)
        # This will cause a transform to be created above the shape node
        xAdded = shapeNode.getParent()
        # Freeze transforms and set the transform's parent to the world
        pm.makeIdentity(xAdded, a=True, t=True, r=True, s=True, n=0, pn=True)
        pm.parent(xAdded, w=True)
        # This will allow parenting to the new parent with the relative flag and no
        # offsetting or movement of the shape
        pm.parent(shapeNode, xParent, s=True, r=True)
        # Delete the extra transform
        pm.delete(xAdded)


def checkContinuousHierarchy(lJoints):
    """Checks that the joints (or transforms) provided are in an unbroken hierarchy.

    Checks that all joints or transforms are in an unbroken hierarchy. The first joint in the list
    should be at the top of the hierarchy. If any joint or transform is found in the hierarchy but
    not in the list, it will be added to the list.

    Keyword arguments:
    lJoints -- list of joints or transforms in a hierarchy with the first item being the top
    """
    i = 1
    while i < len(lJoints):
        if not lJoints[i].getParent() in lJoints:
            pm.warning(('{} does not influence the mesh, but a child of it does. '
                        'Adding it to the selection').format(lJoints[i].getParent().name()))
            lJoints.insert(i, lJoints[i].getParent())
        else:
            i += 1
    return lJoints


def midpoint((x1, y1, z1), (x2, y2, z2)):
    """Gets the midpoint of two points."""
    return ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2)


def isclose(a, b, rel_tol=1e-09, abs_tol=0.00001):
    """Determines if two points are close based on a tolerance."""
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def getVariable(uVariable):
    """Gets the value of globally defined mel variables."""
    uType = mel.eval('whatIs "${}"'.format(uVariable)).split(' ')[0]
    return mel.eval('$temp{} = ${}'.format(uType, uVariable))

def calculateClosestPointOnPlane(vecPlane1, vecPlane2, vecPlane3, vecPoint):
    """Calculates the closest point on a plane defined by 3 points from a provided point.

    Args:
        vecPlane1 (dt.Vector): point1 on plane
        vecPlane2 (dt.Vector): point2 on plane
        vecPlane3 (dt.Vector): point3 on plane
        vecPoint (dt.Vector): point to find the closest point from
    Returns:
        dt.Vector: point on the plane closest to vecPoint
    """
    vecPlaneNormal = ((vecPlane2 - vecPlane1).cross(vecPlane3 - vecPlane1)).normal()
    distance = vecPlaneNormal.dot(vecPoint - vecPlane1)
    return vecPoint + -distance * vecPlaneNormal


def renameUnitConversion(attrDest):
    """Renames the connected Unit Conversion node based on the input attribute.

    Args:
        attrDest (Attribute): attribute that the unit conversion node is connected to
    """
    # Get the unit conversion node connected to the attribute
    lUnitConversion = pm.listConnections(attrDest, t='unitConversion')
    if lUnitConversion:
        unitcNode = lUnitConversion[0]
        # Get the attribute that is connected to unit conversion input
        lUnitConversionInputAttr = pm.listConnections(unitcNode.input, d=False, p=True)
        if lUnitConversionInputAttr:
            attrSrc = lUnitConversionInputAttr[0]
            # Create a list from the attribute's name delimited on '_' and '.'
            lNewName = attrSrc.name().replace('.', '_').split('_')
            if lNewName[0] == 'Jnt':
                # If the connected attribute is from a joint, remove the joint flags from the name
                del lNewName[3]
            lNewName[0] = 'UnitC'
            # Add a number to the end so that multiple unit conversion nodes from
            # the same attribute can be created.
            lNewName.append('1')
            pm.rename(unitcNode, '_'.join(lNewName))


def hasOffsetXform(xCtrl):
    """Checks if the provided transform's parent is an offset transform.

    If the parent transform does not have a shape node as a child, the function returns true.
    If the parent transform has at least one shape node as a child, the function return false.
    Used to determine if an offset group needs to be created for properly oriented rigging controls.

    Args:
        xCtrl (xform): transform (control curve) to check the parent of
    Returns:
        bool: whether or not the parent is an offset transform
    """
    xParent = xCtrl.getParent()
    if xParent is None:
        # xCtrl is a parented to the world
        return False
    elif pm.listRelatives(xParent, s=True):
        # There is a shape node associated with the parent
        return False
    elif len(pm.listRelatives(xParent, typ='transform')) > 1:
        # There is more than one transform child of the parent
        return False
    return True


def createOffsetXform(xCtrl, xDriven=None):
    """Creates an offset transform for the provided controller.

    The pivot position and orientation of the xCtrl controller will match the provided xDriven
    transform. If no xDriven transform is provided, the offset group will match the pivot of the
    controller. The controller shape will not appear to move and the controller's transform
    will be zeroed out.

    Args:
        xCtrl (xform): transform (control curve) to create the offset group for
        xDriven (xform, optional): transform to get pivot position and orientation from
    Returns:
        xform: the offset transform
    """
    lSplit = xCtrl.split('_')
    # Ctrl_L_Hand
    # Xform_L_HandCtrl
    xOffset = pm.createNode('transform', n='Xform_{}_{}{}'.format(lSplit[1], lSplit[2], lSplit[0]))
    if xDriven is None:
        reposition(xCtrl, xOffset)
    else:
        reposition(xDriven, xOffset)
        # Set the controller's pivot to match the driven object's pivot
        lDrivenRotatePivot = pm.xform(xDriven, q=True, rp=True, ws=True)
        pm.xform(xCtrl, piv=lDrivenRotatePivot, ws=True)
    pm.parent(xOffset, xCtrl.getParent())
    pm.parent(xCtrl, xOffset)
    pm.makeIdentity(xCtrl, a=True, t=True, r=True, s=True, n=0, pn=True)
    return xOffset
