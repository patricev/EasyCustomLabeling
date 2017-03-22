# coding: utf-8
"""
/***************************************************************************
 PostTelemac
                                 A QGIS plugin
 Post Traitment or Telemac
                              -------------------
        begin                : 2015-07-07
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Artelia
        email                : patrice.Verchere@arteliagroup.com
 ***************************************************************************/
 
 ***************************************************************************/
 Implementation of QgsPluginLayer class, used to show selafin res
 

 ***************************************************************************/
"""
#unicode behaviour
from __future__ import unicode_literals
#Standart import
import qgis
import qgis.core
import qgis.utils
#Qt
from  qgis.PyQt import QtCore, QtGui
try:        #qt4
    from qgis.PyQt.QtGui import QApplication, QMessageBox
except:     #qt5
    from qgis.PyQt.QtWidgets import  QApplication, QMessageBox

# other import
import collections
import time
import gc
import os
import numpy as np
#plugin impport
from ..EasyCustomLabelingDialog import EasyCustomLabelingDialog

class LabeledPluginLayer( qgis.core.QgsPluginLayer ):
    """
    QgsPluginLayer implmentation for drawing selafin file results
    
    """
    LAYER_TYPE = "labeledlayer"
    
    
    def __init__(self):
        #qgis.core.QgsPluginLayer.__init__(self,'test')
        qgis.core.QgsPluginLayer.__init__(self, LabeledPluginLayer.LAYER_TYPE,None)
        self.prj = qgis.core.QgsProject.instance()
        self.iface = qgis.utils.iface
        self.pixelDistWithNoHeaderLine = 1 #distance in centimeters on map canvas when header line is not shown
        self.pixelDistWithSimpleHeaderLine = 3 #distance in centimeters on map canvas when header line is simple (else double headerline)
        
        
        self.labelFields = [
                        #qgis.core.QgsField( "LblField", QtCore.QVariant.String, "varchar", 255),
                        qgis.core.QgsField( "LblX", QtCore.QVariant.Double, "numeric", 20,10) ,
                        qgis.core.QgsField( "LblY", QtCore.QVariant.Double, "numeric", 20,10) ,
                        qgis.core.QgsField( "LblAlignH", QtCore.QVariant.String, "varchar", 12),
                        qgis.core.QgsField( "LblAlignV", QtCore.QVariant.String, "varchar", 12),
                        qgis.core.QgsField( "LblSize", QtCore.QVariant.Int, "integer", 2 ),
                        qgis.core.QgsField( "LblRot", QtCore.QVariant.Double, "numeric", 10, 2),
                        qgis.core.QgsField( "LblBold", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblItalic", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblColor", QtCore.QVariant.String, "varchar", 7),
                        qgis.core.QgsField( "LblFont", QtCore.QVariant.String, "varchar", 64),
                        qgis.core.QgsField( "LblUnder", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblStrike", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblShow", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblShowCO", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblAShow", QtCore.QVariant.Int, "integer", 1),
                        qgis.core.QgsField( "LblScale", QtCore.QVariant.Double, "numeric", 255) 
                        ]
        
        self.labelfielddefaultvalue = {'LblShow' : 1,
                                        'LblSize' : 9,
                                        'LblAShow' : 1,
                                        'LblAlignV' : 'Half',
                                        'LblAlignH' : 'Center'}
                                        
        self.parent_layer_path = None
        self.parentvectorlayer = None
                                        
        self.headerlinelayer = None
        
        #self.selectedObjects = []
        self.selectedObjectsIds = []
        self.fieldnametolabel = None
        
            
    def loadLabeledPluginLayer(self,vectorlayer = None, parentlayeralreadychecked = False):
        #check and add proper fields to parent layer
        if not vectorlayer is None:
            self.disconnectParentLayer()
        
            self.parentvectorlayer = vectorlayer
            
            try:    #qgis2
                self.setLayerName(vectorlayer.name()+'_HeaderLineLabel')
            except: #qgis3
                self.setName(vectorlayer.name()+'_HeaderLineLabel')
            
            
            success = self.initParentLayer(parentlayeralreadychecked)
            
            if success:
            
                #create Header Line layer
                self.resetHeaderLineLayer()
                self.headerlinelayer.startEditing()
                self.reinitHeaderLineLayer()
                self.headerlinelayer.commitChanges()

                #connecting signals from parent layer - do connexion aftter parent layer check
                self.connectParentLayer()
                #otherwiwe it doesn't show
                self.parentvectorlayer.commitChanges()
                self.setValid(True)
                self.triggerRepaint()
                self.iface.setActiveLayer(self.parentvectorlayer)

                return True
            else:
                return False
        else:
        
            try:
                self.iface.messageBar().pushMessage("Error", QApplication.translate("EasyCustomLabeling", "There is no layer currently selected, \n please click on the vector layer you need to label", None, QApplication.UnicodeUTF8), level=0, duration=3)
            except:
                self.iface.messageBar().pushMessage("Error", QApplication.translate("EasyCustomLabeling", "There is no layer currently selected, \n please click on the vector layer you need to label", None), level=0, duration=3)
            return False

            
            
    #*******************************************************************************************************
    #**************************** connexions                    *******************************************
    #*******************************************************************************************************
        
    def connectParentLayer(self):
        self.parentvectorlayer.attributeValueChanged.connect(self.attributeValueChanged)
        self.parentvectorlayer.geometryChanged.connect(self.geometryChanged)
        self.parentvectorlayer.featuresDeleted.connect(self.featuresDeleted)
        self.parentvectorlayer.featureAdded.connect(self.featureAdded)
        if False:   #not working
            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                self.parentvectorlayer.layerDeleted.connect(self.removeHeaderLineLayer)
            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                self.parentvectorlayer.willBeDeleted.connect(self.removeHeaderLineLayer)
        
        
    def disconnectParentLayer(self):
        try:
            self.parentvectorlayer.attributeValueChanged.disconnect(self.attributeValueChanged)
            self.parentvectorlayer.geometryChanged.disconnect(self.geometryChanged)
            self.parentvectorlayer.featuresDeleted.disconnect(self.featuresDeleted)
            self.parentvectorlayer.featureAdded.disconnect(self.featureAdded)
            if False:   #not working
                if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                    self.parentvectorlayer.layerDeleted.disconnect(self.removeHeaderLineLayer)
                if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                    self.parentvectorlayer.willBeDeleted.disconnect(self.removeHeaderLineLayer)
            
        except:
            pass
            
            
    #*******************************************************************************************************
    #**************************** Plugin Layer methods           *******************************************
    #*******************************************************************************************************
        
        
    def legendSymbologyItems(self, iconSize):
        return []
        
    def isValid(self):
        return True
        
    def crs(self):
        if not self.parentvectorlayer is None:
            return self.parentvectorlayer.crs()
        else:
            return None

    def createMapRenderer(self,rendererContext):
        if not self.headerlinelayer is None:
            self.renderer = self.headerlinelayer.createMapRenderer(rendererContext)
        else:
            self.renderer = None
        return self.renderer
        
    def dataProvider(self):
        if not self.parentvectorlayer is None:
            return self.parentvectorlayer.dataProvider()
        else:
            return None
        
    def extent(self):
        if not self.parentvectorlayer is None:
            return self.parentvectorlayer.extent()
        else:
            return None
        
    def name(self):
        if not self.parentvectorlayer is None:
            return self.parentvectorlayer.name()+'_HeaderLineLabel'
        else:
            return None
        
    def writeXml(self, node, doc):
        """
        implementation of method from QgsMapLayer to save layer in  qgsproject
        return True ifsuccessful
        """
        #prj = qgis.core.QgsProject.instance()
        element = node.toElement()
        element.setAttribute("type", "plugin")                          #must be written to work
        element.setAttribute("name", LabeledPluginLayer.LAYER_TYPE)     #must be written to work
        element.setAttribute("parent_layer", os.path.normpath( self.parentvectorlayer.source() ))
        element.setAttribute("labelfield", self.parentvectorlayer.customProperty("labeling/fieldName") )
        return True
        
    def readXml(self, node):
        """
        implementation of method from QgsMapLayer to load layer from qgsproject
        return True ifsuccessful
        """
        
        element = node.toElement()
        self.parent_layer_path = self.prj.readPath( element.attribute('parent_layer') )
        self.fieldnametolabel = element.attribute('labelfield')
        
        if os.path.isfile(self.parent_layer_path) :
            basename = os.path.basename(self.parent_layer_path).split('.')
            if len(basename)>0:
                basename = basename[0]
            try:    #qgis2
                layers = self.prj.mapLayers()
            except: #qgis3
                layers = qgis.core.QgsMapLayerRegistry.instance().mapLayers().values()
            layerfound = False
            #check if parent layer is already loaded
            for layer in layers:
                if os.path.normpath(layer.source()) == os.path.normpath(self.parent_layer_path):
                    self.parentvectorlayer = layer
                    layerfound = True
                    break

            if not layerfound:  #if not found, wait a temp layer and activate readMapLayer signal when the parent layer will be loaded
                self.parentvectorlayer = qgis.core.QgsVectorLayer(self.parent_layer_path,basename,"ogr")
                self.loadLabeledPluginLayer(self.parentvectorlayer,True)
                self.prj.readMapLayer.connect(self.layerAddedtoProject)
                return True
            else:   #if parent layer is found
                self.loadLabeledPluginLayer(self.parentvectorlayer,True)
                return True
                
        else:
            return False
            
    def layerAddedtoProject(self, layer,node ):  
        if isinstance(layer, qgis.core.QgsVectorLayer):
            if not self.parent_layer_path is None  and os.path.normpath(layer.source()) == os.path.normpath(self.parent_layer_path):
                self.parentvectorlayer = layer
                self.loadLabeledPluginLayer(self.parentvectorlayer,True)
                self.prj.readMapLayer.disconnect(self.layerAddedtoProject)
                
    

    #*******************************************************************************************************
    #**************************** Parent Layer initialization   *******************************************
    #*******************************************************************************************************
        
        
    def initParentLayer(self,parentlayeralreadychecked = False):
        #
        #Layer to be labeled (called parentlayer) validity check and fields creation
        #Return True if operation successfull (parent layer checked, parent layer initialized)
        #
        
        if self.checkParentLayer(parentlayeralreadychecked):        #also disconnect parent layer
            
            
            parentlayerfields = self.parentvectorlayer.fields()
            parenlayerfieldname = [field.name() for field in  parentlayerfields]
            #create fields
            for field in self.labelFields:
                if not field.name() in parenlayerfieldname:
                    parentpr = self.parentvectorlayer.dataProvider()
                    self.parentvectorlayer.startEditing()
                    parentpr.addAttributes([field ])
                    self.parentvectorlayer.updateFields()
                    self.parentvectorlayer.commitChanges()
            
            #assin default values
            self.parentvectorlayer.startEditing()
            for feature in self.parentvectorlayer.getFeatures():
                for key, value in self.labelfielddefaultvalue.items():
                    if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                        if isinstance(feature[key],QtCore.QPyNullVariant) or feature[key] is None :
                            self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName(key), value)
                    elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                        if isinstance(feature[key],QtCore.QVariant) or feature[key] is None :
                            self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName(key), value)
                if len(self.selectedObjectsIds)>0:
                    if feature.id() in self.selectedObjectsIds:
                        self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName("LblShow"), 1)
                    else:
                        self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName("LblShow"), 0)
            self.parentvectorlayer.commitChanges()
            
            
            
            
            # #generic labeling properties
            self.parentvectorlayer.setCustomProperty("labeling/fieldName", self.fieldnametolabel )  # TODO replace default value with dialog input
            self.parentvectorlayer.setCustomProperty("labeling","pal" ) # new gen labeling activated
            self.parentvectorlayer.setCustomProperty("labeling/fontSize","8" ) # default value
            self.parentvectorlayer.setCustomProperty("labeling/multiLineLabels","true" ) # default value
            self.parentvectorlayer.setCustomProperty("labeling/enabled","true" ) # default value
            #self.parentvectorlayer.setCustomProperty("labeling/displayAll", "true") # force all labels to display
            self.parentvectorlayer.setCustomProperty("labeling/priority", "10") # puts a high priority to labeling layer
            self.parentvectorlayer.setCustomProperty("labeling/multilineAlign","1") # multiline align to center
            #self.parentvectorlayer.setCustomProperty("labeling/wrapChar", "%") # multiline break symbol
            
            self.parentvectorlayer.setCustomProperty("labeling/drawLabels","true" ) # default value
            self.parentvectorlayer.setCustomProperty("labeling/isExpression","false" ) # default value

            #line properties case
            self.parentvectorlayer.setCustomProperty("labeling/placement","4" ) 
            
            
            #assign data defined properties
            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                # #data defined properties
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/PositionX", "1~~0~~~~LblX")  
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/PositionY", "1~~0~~~~LblY")  
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Hali", "1~~0~~~~LblAlignH")  
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Vali","1~~0~~~~LblAlignV")  
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Size" ,"1~~0~~~~LblSize") 
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Rotation" ,"1~~0~~~~LblRot" ) 
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Bold" , "1~~0~~~~LblBold")  
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Italic" ,"1~~0~~~~LblItalic") 
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Underline" ,"1~~0~~~~LblUnder")
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Strikeout" ,"1~~0~~~~LblStrike")
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Color" ,"1~~0~~~~LblColor")
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Family" ,"1~~0~~~~LblFont") 
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/Show", "1~~0~~~~LblShow")
                self.parentvectorlayer.setCustomProperty("labeling/dataDefined/AlwaysShow", "1~~0~~~~LblAShow")
                
            elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                # #data defined properties
                self.parentvectorlayer.setCustomProperty("labeling/ddProperties", 
                                                            '<properties><Option type="Map"><Option value="" name="name" type="QString"/><Option name="properties" type="Map">\
                                                            <Option name="AlwaysShow" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblAShow" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Bold" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblBold" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Color" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblColor" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Family" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblFont" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Hali" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblAlignH" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Italic" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblItalic" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="PositionX" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblX" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="PositionY" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblY" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Rotation" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblRot" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Show" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblShow" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Size" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblSize" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Strikeout" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblStrike" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Underline" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblUnder" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            <Option name="Vali" type="Map"><Option value="true" name="active" type="bool"/><Option value="LblAlignV" name="field" type="QString"/><Option value="2" name="type" type="int"/></Option>\
                                                            </Option><Option value="collection" name="type" type="QString"/></Option></properties>')
                
            
            self.connectParentLayer()
            
            return True
        else:
            return False
                
        
        
    def checkParentLayer(self,skipchecking = False):
        #
        #perform control on parent layer
        #Return True if checking sucessfull (no aborting, evrything ok)
        #
        
        self.disconnectParentLayer()
        
        if not skipchecking :   #first time loading

            sourceLayer = self.parentvectorlayer
            
            if not sourceLayer.type() == sourceLayer.VectorLayer:
                try:
                    self.iface.messageBar().pushMessage("Error", QApplication.translate("EasyCustomLabeling", "Current active layer is not a vector layer. \n Please click on the vector layer you need to label", None, QApplication.UnicodeUTF8), level=0, duration=3)
                except:
                    self.iface.messageBar().pushMessage("Error", QApplication.translate("EasyCustomLabeling", "Current active layer is not a vector layer. \n Please click on the vector layer you need to label", None), level=0, duration=3)
                return False
            
          
            # detect if selection exists on that layer
            nbSelectedObjects = sourceLayer.selectedFeatureCount()
            self.selectedObjectsIds = []
            ret = 0
            if not nbSelectedObjects == 0 :
                #dialog to ask if user wants to use current selection or not
                msgBox = QMessageBox() 
                msgBox.setIcon(QMessageBox.Question)
                msgBox.setWindowTitle ("EasyCustomLabeling")
                try:
                    msgBox.setText(QApplication.translate("EasyCustomLabeling", "Use %n selected object(s) only for labeling ?" , None, QApplication.UnicodeUTF8, nbSelectedObjects))
                except:
                    msgBox.setText(QApplication.translate("EasyCustomLabeling", "Use %n selected object(s) only for labeling ?" , None, nbSelectedObjects))
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No |QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                
                ret = msgBox.exec_() #ret_val = 16384 si OK, 4194304 sinon
                
                if ret == 4194304 : # cancel  button finish program
                    self.iface.mapCanvas().freeze(0)
                    #print('dialog keep selection: ' + str(ret))
                    return False
                elif ret == 65536  :  # No button65536  use entire layer
                    pass
                    #print('use entire layer')
                elif ret == 16384 :
                    print('use selection')
                    self.selectedObjectsIds = [fet.id() for fet in sourceLayer.selectedFeatures()]
                   
                    
            #nbSelectedObjects = sourceLayer.selectedFeatureCount()
            

            if sourceLayer.selectedFeatureCount() > 500 :  #alert if  many objects selected

                msgBox = QMessageBox()
                try:
                    msgBox.setText(QApplication.translate("EasyCustomLabeling","Your layer contains many objects. Continue anyway?", None, QApplication.UnicodeUTF8))
                except:
                    msgBox.setText(QApplication.translate("EasyCustomLabeling","Your layer contains many objects. Continue anyway?", None))
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok) # This function was introduced in Qt 4.3.
                ret2 = msgBox.exec_() #ret_val = 1024 si OK, 4194304 sinon
                # print 'dialog many objects: ' + str(ret)
                if ret2 != 1024:
                    print('user cancel on too many object question')
                    return False
                    
                    
                    
            #asks for default field to use as labeling (thanks to Victor Axbom Layer to labeled layer plugin)
            # create the dialog
            self.dlg = EasyCustomLabelingDialog(sourceLayer.dataProvider())
            ret_dlg_field = self.dlg.exec_()
            #cancels if user cancels dialog:
            if ret_dlg_field == 0 :  
                return False
                
            self.fieldnametolabel = self.dlg.labelfield.currentText()
            # show the dialog
            # if self.dlg.exec_():
            #     return True# print 'dialog execution'
            # else :
            #     return

                # self.iface.mapCanvas().refresh()       
                # returns self.dlg.labelfield.currentText() 
                    
                    
            #self.selectedObjects = sourceLayer.selectedFeatures()
            return True
            
        else:
        
            return True
                


    #*******************************************************************************************************
    #**************************** Header Line Layer methods           *******************************************
    #*******************************************************************************************************
        
    def removeHeaderLineLayer(self):
        print('remove')
        self.disconnectParentLayer()
        if not self.parentvectorlayer is None:
            try:
                if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                    qgis.core.QgsMapLayerRegistry.instance().removeMapLayer(self)
                    #self.iface.setActiveLayer(activelayer)
                elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                    qgis.core.QgsProject.instance().removeMapLayer(self)
                    #self.iface.setActiveLayer(activelayer)
            except:
                pass
        
    def resetHeaderLineLayer(self):
        #
        # header line layer creation
        #
        if not self.parentvectorlayer is None:
            type = "LineString?crs="+str(self.parentvectorlayer.crs().authid()) 
            name='temp'
            self.headerlinelayer = qgis.core.QgsVectorLayer(type, name, "memory")
            self.pr = self.headerlinelayer.dataProvider()
            self.headerlinelayer.startEditing()
            # add fields
            self.pr.addAttributes([qgis.core.QgsField("Value", QtCore.QVariant.Double) ])
            self.headerlinelayer.updateFields()
            pathpointvelocityqml = os.path.join(os.path.dirname(__file__), '..','default_label_style.qml')
            self.headerlinelayer.loadNamedStyle(pathpointvelocityqml)
        else:
            self.headerlinelayer = None
        
        
        
            
    def attributeValueChanged(self,FeatureId , idx  , variant):
        #
        #When label position is changed 
        #
        
        DEBUG = False
        
        if DEBUG : print('attributeValueChanged')
        
        if self.parentvectorlayer.fields()[idx].name() in ['LblX','LblY']:
        
            if DEBUG : print('attributeValueChanged', FeatureId,idx,  variant)
            
            self.parentvectorlayer.startEditing()
            self.headerlinelayer.startEditing()
            
            self.disconnectParentLayer()
            
            fet = qgis.core.QgsFeature()
            if self.parentvectorlayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId)).nextFeature(fet):
                if DEBUG : print('ids',[fett.id() for fett in self.headerlinelayer.getFeatures()], [fett.id() for fett in self.parentvectorlayer.getFeatures()])
                if isinstance(fet['LblX'], float) and isinstance(fet['LblY'], float) :
                    fettemp = qgis.core.QgsFeature()
                    if self.headerlinelayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId + 1)).nextFeature(fettemp): #memory layer id start at 1 ...
                        if DEBUG : print('case2 ok')
                        self.adjustFeature(fet, fettemp,update = True)
            self.headerlinelayer.commitChanges()
            self.triggerRepaint()
            self.connectParentLayer()
            
        if self.parentvectorlayer.fields()[idx].name() in ['LblShow']:
            self.headerlinelayer.startEditing()
            fet = qgis.core.QgsFeature()
            if self.parentvectorlayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId)).nextFeature(fet):
                fettemp = qgis.core.QgsFeature()
                if self.headerlinelayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId + 1)).nextFeature(fettemp): #memory layer id start at 1 ...
                    self.adjustFeature(fet, fettemp,update = True)
            self.headerlinelayer.commitChanges()
            self.triggerRepaint()
        
        
    def featuresDeleted(self,list):
        #
        #When parent layer feature is deleted
        #
        DEBUG = False
        self.disconnectParentLayer()
        self.headerlinelayer.startEditing()
        if DEBUG : print('featuresDeleted', list)
        self.reinitHeaderLineLayer()
        self.triggerRepaint()
        self.headerlinelayer.commitChanges()
        self.connectParentLayer()
        
    def featureAdded(self,FeatureId):
        #
        #When parent layer feature is added
        #
        DEBUG = False
        self.disconnectParentLayer()
        self.headerlinelayer.startEditing()
        if DEBUG : print('featureAdded', FeatureId)
        
        if int(FeatureId)<0:   #while editing - create proper fields
            fet = qgis.core.QgsFeature()
            if self.parentvectorlayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId)).nextFeature(fet):
                if DEBUG : print('while editing ok')
                self.checkDefaultFieldValue(fet)
        
        if int(FeatureId)>0:   #editing finished - create header line
            self.reinitHeaderLineLayer()
        self.headerlinelayer.commitChanges()
        self.connectParentLayer()
                
                
    def geometryChanged(self,FeatureId,geom):
        #
        #When parent layer geometry is changed
        #
        self.disconnectParentLayer()
        self.headerlinelayer.startEditing()
        DEBUG = False
        if DEBUG : print('geometryChanged', FeatureId,geom)
        fet = qgis.core.QgsFeature()
        if self.parentvectorlayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId)).nextFeature(fet):
            if DEBUG : print('ids',[fett.id() for fett in self.headerlinelayer.getFeatures()], [fett.id() for fett in self.parentvectorlayer.getFeatures()])
            if isinstance(fet['LblX'], float) and isinstance(fet['LblY'], float) :
                fettemp = qgis.core.QgsFeature()
                if self.headerlinelayer.getFeatures(qgis.core.QgsFeatureRequest().setFilterFid(FeatureId + 1)).nextFeature(fettemp): #memory layer id start at 1 ...
                    if DEBUG : print('case2 ok')
                    self.adjustFeature(fet, fettemp,update = True)
        self.headerlinelayer.commitChanges()
        self.triggerRepaint()
        self.connectParentLayer()
        
        
    
    
    def reinitHeaderLineLayer(self):
        #
        #recreate an header line layer
        #
        
        DEBUG = False
        if DEBUG : print('case1')
        
        if not self.parentvectorlayer is None:
        
            parentlayereditmode = self.parentvectorlayer.isEditable()
            
            self.parentvectorlayer.startEditing()
            self.resetHeaderLineLayer()
            for fet in self.parentvectorlayer.getFeatures():
                if fet.id()>=0:
                    self.checkDefaultFieldValue(fet)
                    fettemp = qgis.core.QgsFeature(self.headerlinelayer.fields())
                    if isinstance(fet['LblX'], float) and isinstance(fet['LblY'], float) :
                        self.adjustFeature(fet, fettemp)
                    self.pr.addFeatures([fettemp])
            if DEBUG : print('ids after ',[fett.id() for fett in self.headerlinelayer.getFeatures()], [fett.id() for fett in self.parentvectorlayer.getFeatures()])
            #self.triggerRepaint()
            #self.parentvectorlayer.commitChanges()
            """
            if parentlayereditmode : 
                self.parentvectorlayer.commitChanges()
                self.parentvectorlayer.startEditing()
            else:
                self.parentvectorlayer.commitChanges()
            """
        
    def checkDefaultFieldValue(self,feature):
        #
        #On feature creation in parent layer, check for default fields
        #
        for key, value in self.labelfielddefaultvalue.items():
            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                if isinstance(feature[key],QtCore.QPyNullVariant) or feature[key] is None :
                    self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName(key), value)
            elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                if isinstance(feature[key],QtCore.QVariant) or feature[key] is None :
                    self.parentvectorlayer.changeAttributeValue(feature.id(),self.parentvectorlayer.fields().indexFromName(key), value)
        
        
        
        
    #*******************************************************************************************************
    #**************************** Header Line Layer core methods           *********************************
    #*******************************************************************************************************
        
    def adjustFeature(self,parentfet, labelfet, update = False):
        #
        #header line creation process - parent layer and headerlinelayer must be on editing mode
        #update means only one feature is changed

        #compute new header line geom
        
        if parentfet["LblShow"] and isinstance(parentfet['LblX'], float) and isinstance(parentfet['LblY'], float) :
            pointlabel = qgis.core.QgsPoint(parentfet['LblX'],parentfet['LblY'])
            #ending point of header line
            if parentfet.geometry().type() == 0 : #point 0 : point 1 : line 2 : polygon
                pointfeature = parentfet.geometry().asPoint()
                
            elif parentfet.geometry().type() == 1 : #point 0 : point 1 : line 2 : polygon
                parentgeom = qgis.core.QgsGeometry(parentfet.geometry())
                parentgeom.convertToSingleType()
                pointfeature = parentgeom.interpolate(.5 * parentgeom.length()).asPoint()   #point in he middle of polyline
                templine = qgis.core.QgsGeometry.fromPolyline([pointlabel,pointfeature])
                if templine.intersects(parentfet.geometry()):
                    intersect = templine.intersection(parentfet.geometry())
                    if len(intersect.asMultiPoint())==0: #single point
                        pointfeature = intersect.asPoint()
                    else:   #mulilines
                        #pass
                        intersect.convertToSingleType()
                        pointfeature = intersect.asPoint()
                
            elif parentfet.geometry().type() == 2 : #point 0 : point 1 : line 2 : polygon
                pointfeature = parentfet.geometry().centroid().asPoint()
                templine = qgis.core.QgsGeometry.fromPolyline([pointlabel,pointfeature])
                if templine.intersects(parentfet.geometry()):
                    intersect = templine.intersection(parentfet.geometry())
                    if len(intersect.asMultiPolyline())==0: #singleline
                        pointfeature = intersect.interpolate(.25 * intersect.length()).asPoint()
                    else:   #mulilines
                        #pass
                        intersect.convertToSingleType()
                        pointfeature = intersect.interpolate(.25 * intersect.length()).asPoint()

            
            newgeom = self.generateHeaderLine(parentfet,pointlabel, pointfeature,update)
            
            if pointlabel.x()<pointfeature.x():
                self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName('LblAlignH'), 'Right')
            else:
                self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName('LblAlignH'), 'Left')
        
        else:   #label not shown
            newgeom = qgis.core.QgsGeometry()
            
        
        #assign new header line geom
        if update:
            self.headerlinelayer.changeGeometry(labelfet.id(),newgeom)
        else:
            labelfet.setGeometry( newgeom )
            
            

    def generateHeaderLine(self,parentfet,pointlabel, pointfeature,update):
    
        if not update:

            if int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 4 :    #qgis2
                if isinstance(parentfet["LblScale"],QtCore.QPyNullVariant) or parentfet["LblScale"] is None :
                    scale = self.iface.mapCanvas().scale()
                    self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName("LblScale"), scale)
                else:
                    scale = parentfet["LblScale"]
                    """
                    self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName("LblScale"), scale)
                    distnoheaderinmeters = scale * self.pixelDistWithNoHeaderLine/100.0
                    distsimpleheaderinmeters = scale * self.pixelDistWithSimpleHeaderLine/100.0
                    """
                    
            elif int(qgis.PyQt.QtCore.QT_VERSION_STR[0]) == 5 :    #qgis3
                if isinstance(parentfet["LblScale"],QtCore.QVariant) or parentfet["LblScale"] is None :
                    scale = self.iface.mapCanvas().scale()
                    self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName("LblScale"), scale)
                else:
                    scale = parentfet["LblScale"]
                    
        else:
            scale = self.iface.mapCanvas().scale()
            self.parentvectorlayer.changeAttributeValue(parentfet.id(),self.parentvectorlayer.fields().indexFromName("LblScale"), scale)
            
                    
                
        distnoheaderinmeters = scale * self.pixelDistWithNoHeaderLine/100.0
        distsimpleheaderinmeters = scale * self.pixelDistWithSimpleHeaderLine/100.0
        #distnoheaderinmeters = self.iface.mapCanvas().mapUnitsPerPixel() * self.pixelDistWithNoHeaderLine
        #distsimpleheaderinmeters = self.iface.mapCanvas().mapUnitsPerPixel() * self.pixelDistWithSimpleHeaderLine
        
        distfeat = qgis.core.QgsGeometry.fromPoint(pointlabel).distance( qgis.core.QgsGeometry.fromPoint(pointfeature))
        if distfeat < distnoheaderinmeters:
            return qgis.core.QgsGeometry()
        elif  distfeat < distsimpleheaderinmeters :
            return qgis.core.QgsGeometry.fromPolyline([pointlabel,pointfeature])
        else:
            headermiddlepoint = qgis.core.QgsGeometry(qgis.core.QgsGeometry.fromPoint(pointlabel))
            if pointlabel.x()<pointfeature.x():
                headermiddlepoint.translate(distnoheaderinmeters,0)
            else:
                headermiddlepoint.translate(-distnoheaderinmeters,0)
            headermiddlepoint = headermiddlepoint.asPoint()
            return qgis.core.QgsGeometry.fromPolyline([pointlabel,headermiddlepoint,pointfeature])
            

        
