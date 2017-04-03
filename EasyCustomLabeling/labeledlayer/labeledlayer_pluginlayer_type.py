import qgis.core
import qgis.utils
import qgis

from qgis.PyQt import QtCore
from .labeledlayer_pluginlayer import LabeledPluginLayer
try:
    from qgis.PyQt.QtGui import QDialog, QVBoxLayout, QDialogButtonBox
except:
    from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox


class LabeledLayerPluginLayerType(qgis.core.QgsPluginLayerType):

    def __init__(self):
        qgis.core.QgsPluginLayerType.__init__(self, LabeledPluginLayer.LAYER_TYPE)
        self.iface = qgis.utils.iface
        
    def createLayer(self):
        return LabeledPluginLayer()
        
    def showLayerProperties(self, layer):
        if False:
            if not layer.styledlg is None and layer.styledlg.exec_():
                #layer.headerlinelayer.styleChanged.disconnect(layer.saveheaderstyle)
                if True:
                    layer.headerlinelayer.setRendererV2(layer.tt.renderer())
                    #layer.headerlinelayer.triggerRepaint()
                    #layer.triggerRepaint()
                if False:
                    layer.tt.applyChanges()
                return True
            else:
                return False
                
        if True:
            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                tt = qgis.gui.QgsSymbolV2SelectorDialog( layer.headerlinelayer.rendererV2().symbol(),     qgis.core.QgsStyleV2.defaultStyle(),
                    layer.headerlinelayer,  # QgsVectorLayer
                    None,  # Parent
                    False  # Embedded
                    )
            elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                tt = qgis.gui.QgsSymbolSelectorDialog( layer.headerlinelayer.renderer().symbol(),     qgis.core.QgsStyle.defaultStyle(),
                    layer.headerlinelayer,  # QgsVectorLayer
                    None,  # Parent
                    False  # Embedded
                    )
            if tt.exec_():
                
                layer.triggerRepaint()
                layer.headerlinelayer.styleChanged.emit()
            return True


    def addToRegistry(self):
        #Add labeledlayer in QgsPluginLayerRegistry
        if u'labeledlayer' in QgsPluginLayerRegistry.instance().pluginLayerTypes():
            QgsPluginLayerRegistry.instance().removePluginLayerType('labeledlayer')
        self.pluginLayerType = self()
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.pluginLayerType)
 