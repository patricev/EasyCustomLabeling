vl = iface.activeLayer()
stmana= vl.styleManager()     #QgsMapLayerStyleManager
stmananame = stmana.currentStyle ()
maplayersyle = vl.styleManager().style(stmananame )         #QgsMapLayerStyle 



renderer = vl.rendererV2()  #QgsFeatureRendererV2
print(renderer.__class__)

#print(renderer.symbol())



#print(maplayersyle.xmlData () )



#tt = qgis.gui.QgsCategorizedSymbolRendererWidget(vl)

#tt = qgis.gui.QgsSimpleLineSymbolLayerV2Widget(vl)
#tt = qgis.gui.QgsLinePatternFillSymbolLayerWidget(vl)
#tt = qgis.gui.QgsMarkerLineSymbolLayerV2Widget(vl)
#tt = qgis.gui.QgsArrowSymbolLayerWidget (vl)
#tt = qgis.gui.QgsGeometryGeneratorSymbolLayerWidget(vl)
#tt = qgis.gui.QgsLinePatternFillSymbolLayerWidget(vl) 
#tt = qgis.gui.QgsMapLayerStyleManagerWidget(vl,iface.mapCanvas())

#QgsPanelWidget

#QgsLayerPropertiesWidget (QgsSymbolLayerV2 *layer, const QgsSymbolV2 *symbol, const QgsVectorLayer *vl, QWidget *parent=nullptr)
#tt = qgis.gui.QgsLayerPropertiesWidget(renderer.symbol().symbolLayer(0),   renderer.symbol() , vl)

#QgsSingleSymbolRendererV2Widget (QgsVectorLayer *layer, QgsStyleV2 *style, QgsFeatureRendererV2 *renderer)
#tt = qgis.gui.QgsSingleSymbolRendererV2Widget(vl,  qgis.core.QgsStyleV2.defaultStyle() ,renderer)
#tt.setDockMode(False)


#tt = qgis.gui.QgsRendererV2PropertiesDialog(vl,qgis.core.QgsStyleV2.defaultStyle(),True)
#tt.exec_()
#tt.onOK ()


tt = qgis.gui.QgsSymbolV2SelectorDialog( vl.rendererV2().symbol(),     qgis.core.QgsStyleV2.defaultStyle(),
    vl,  # QgsVectorLayer
    None,  # Parent
    False  # Embedded
    )
if tt.exec_():
    
    vl.triggerRepaint()
#qgis.gui.QgsPanelWidget.openPanel(tt)
#res = tt.openPanel(tt)
print('res',res)
#tt.applyChanges ()
#vl.setRendererV2(tt.renderer())
#tt.showSymbolLevelsDialog(renderer)

#QgsStyleV2ManagerDialog (QgsStyleV2 *style, QWidget *parent=nullptr)
#tt = qgis.gui.QgsStyleV2ManagerDialog(qgis.core.QgsStyleV2.defaultStyle() )
#QgsSymbolV2SelectorWidget (QgsSymbolV2 *symbol, QgsStyleV2 *style, const QgsVectorLayer *vl, QWidget *parent=nullptr)
#tt = qgis.gui.QgsSymbolV2SelectorWidget(renderer.symbol(),qgis.core.QgsStyleV2.defaultStyle() , vl )

#tt.show()
#tt.exec_()
print('ok')
#tt.exec_()
#vl.setRendererV2(tt.renderer())
#vl.triggerRepaint()

