import qgis
import xml.etree.ElementTree as ET
import xml

vl = iface.activeLayer()

prop = vl.customProperty("labeling/ddProperties")

#print(prop,type(prop))

tree = ET.ElementTree(ET.fromstring(prop))
root = tree.getroot()
print(prop)
temp = root[0][1][0]
print(temp.attrib)
print(temp[0].attrib)
print(temp[1].attrib)
print(temp[2].attrib)

print(root[0],len(root[0]))



"""for elem in tree.iter():
        #print(elem.tag, elem.attrib)
        if 'name' in elem.attrib.keys():
                if elem.attrib['name'] == 'PositionX':
                        changexactive = True
            #print(elem.attrib['value'])
            #elem.attrib['value'] = '2'
"""

#print(xml.etree.ElementTree.tostring(root, encoding='utf8', method='xml'))
#print(xml.etree.ElementTree.tostring(root))