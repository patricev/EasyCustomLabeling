import qgis.core
import qgis.utils

#import PyQT
from qgis.PyQt import QtCore
#import posttelemac
from .labeledlayer_pluginlayer import LabeledPluginLayer


class LabeledLayerPluginLayerType(qgis.core.QgsPluginLayerType):

    def __init__(self):
        #qgis.core.QgsPluginLayerType.__init__(self, SelafinPluginLayer.LAYER_TYPE)
        qgis.core.QgsPluginLayerType.__init__(self, LabeledPluginLayer.LAYER_TYPE)
        
        self.iface = qgis.utils.iface
        
        
    def createLayer(self):
        return LabeledPluginLayer()
        
    #if False:
    def showLayerProperties(self, layer):
        self.iface.showLayerProperties(layer.headerlinelayer)
        
        #tt = qgis.gui.QgsSimpleLineSymbolLayerV2Widget(iface.activeLayer())
        
        """
        self.iface.addDockWidget( QtCore.Qt.RightDockWidgetArea, layer.propertiesdialog )
        self.iface.mapCanvas().setRenderFlag(True)
        return True
        """
        #print('properties')
        #self.iface.showLayerProperties(layer)
        return True


    def addToRegistry(self):
        #Add telemac_viewer in QgsPluginLayerRegistry
        if u'labeledlayer' in QgsPluginLayerRegistry.instance().pluginLayerTypes():
            QgsPluginLayerRegistry.instance().removePluginLayerType('labeledlayer')
        self.pluginLayerType = self()
        QgsPluginLayerRegistry.instance().addPluginLayerType(self.pluginLayerType)
 