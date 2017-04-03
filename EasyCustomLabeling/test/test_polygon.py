import qgis
from qgis.core import QgsPoint 
from qgis.PyQt import  QtCore

obj = QtCore.QObject()

#geom2 = qgis.core.QgsGeometry.fromPolygon(obj)

geom2 = qgis.core.QgsGeometry.fromPolygon([[QgsPoint(0,0),QgsPoint(1,0),QgsPoint(1,1),QgsPoint(0,1)]]     )        

geom = qgis.core.QgsGeometry.fromMultiPolygon([[[QgsPoint(0,0),QgsPoint(1,0),QgsPoint(1,1),QgsPoint(0,1)]],\
                                                                           [[QgsPoint(2,2),QgsPoint(3,2),QgsPoint(3,3),QgsPoint(2,3)]]]     )
                                                                           
                                                            
                                                                           
print(geom2.asPolygon())
print(geom2.asMultiPolygon())
tt = geom.asMultiPolygon()

print(type(geom))