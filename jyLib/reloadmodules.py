import jyLib

def refresh():
    reload(jyLib)
    reload(jyLib.common)
    reload(jyLib.commonui)
    reload(jyLib.curves)

    reload(jyLib.tools)
    reload(jyLib.tools.blendshapemirrorhelper)
    reload(jyLib.tools.curvecreator)