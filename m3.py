# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from os import path
import xml.etree.ElementTree as ET
import struct


m3_structs_xml = {struct.get('tag'): struct for struct in ET.parse(path.join(path.dirname(__file__), 'structs.xml')).getroot().findall('struct')}
m3_structs = {}
for tag, val in m3_structs_xml.items():
    m3_structs[tag] = {}
    for version in val.findall('version'):
        num = int(version.get('num'))
        m3_structs[tag][num] = {}
        m3_structs[tag][num]['bin'] = ''
        m3_structs[tag][num]['size'] = 0
        m3_structs[tag][num]['keys'] = []
        for field in val.findall('field'):
            if (int(field.get('vermin')) if field.get('vermin') else 0) > num:
                continue
            if (int(field.get('vermax')) if field.get('vermax') else 255) < num:
                continue
            m3_structs[tag][num]['bin'] += field.get('bin')
            m3_structs[tag][num]['size'] += struct.calcsize(field.get('bin'))
            m3_structs[tag][num]['keys'].append({'name': field.get('name'), 'bin': field.get('bin'), 'size': struct.calcsize(field.get('bin'))})


def read_m3(dirname):
    m3 = open(dirname, 'rb') if path.isfile(dirname) else None
    if not m3:
        return

    md34 = struct.unpack('4s5I', m3.read(24))
    m3.seek(md34[1])

    sections = []
    for indice in [struct.unpack('4s3I', m3.read(16)) for ii in range(md34[2])]:
        m3.seek(indice[1])
        m3_struct = m3_structs.get(indice[0].decode('ascii')[::-1])[indice[3]]
        sections.append(tuple(struct.iter_unpack(m3_struct['bin'], m3.read(m3_struct['size'] * indice[2]))))

    return sections


# from timeit import timeit
# timenum = 50
# print(timeit(lambda: read_m3('C:\\Users\\John Wharton\\Documents\\_Base Assets\\Terran\\Units\\Goliath\\Goliath.m3'), number=timenum) / timenum)
