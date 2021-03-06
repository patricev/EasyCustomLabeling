# -*- coding: utf-8 -*-
"""
/***************************************************************************
Layer to labeled layer
                                 A QGIS plugin
Make it possible to use data-defined labeling on existing layer.
The plug-in creates new attributes in the existing shapefile.
                             -------------------
        begin                : 2012-11-01
        copyright            : (C) 2012 by Victor Axbom
        email                : -
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         * 
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
 *                                                                         *
 ***************************************************************************/
"""
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
"""
from  qgis.PyQt import QtCore, QtGui, uic
try:        #qt4
    from qgis.PyQt.QtGui import QDialog
except:     #qt5
    from qgis.PyQt.QtWidgets import  QDialog
import os
from qgis.core import *
from .ui_EasyCustomLabeling import Ui_EasyCustomLabeling

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_EasyCustomLabeling.ui'))

class EasyCustomLabelingDialog(QDialog, FORM_CLASS):
    
    def __init__(self, ldp, parent = None):
        super(EasyCustomLabelingDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.loadFields(ldp)
        
    def loadFields(self,ldp):
        fields = ldp.fieldNameMap()
        """
        for fieldname, index in fields.iteritems():
            self.labelfield.addItem(fieldname)
        """
        for fieldname, index in fields.items():
            self.labelfield.addItem(fieldname)