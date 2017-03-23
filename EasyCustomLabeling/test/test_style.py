import qgis
from qgis.PyQt import  QtCore

tt = qgis.gui.QgsSimpleLineSymbolLayerV2Widget(iface.activeLayer())
tt.setAttribute(QtCore.Qt.WA_DeleteOnClose)
#tt.exec_()
tt.show()