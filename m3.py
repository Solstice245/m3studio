#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
import struct as struct_mod


def read_int(buffer): return int.from_bytes(buffer, 'little', signed=True)
def read_uint(buffer): return int.from_bytes(buffer, 'little', signed=False)
def read_fixed(buffer): return int.from_bytes(buffer, 'little') * 2 / 255 - 1
def read_float(buffer): return struct_mod.unpack('f', buffer)[0]
def read_char(buffer): return str(buffer, 'ascii')
def read_tag(buffer): return str(buffer, 'ascii')[::-1].replace('\00', '')


structs_dict = {struct.get('name'): struct for struct in ET.parse(path.join(path.dirname(__file__), 'structures.xml')).getroot().findall('structure')}
primitive = {
    'int8': {'size': 1, 'read': read_int}, 'int16': {'size': 2, 'read': read_int}, 'int32': {'size': 4, 'read': read_int},
    'uint8': {'size': 1, 'read': read_uint}, 'uint16': {'size': 2, 'read': read_uint}, 'uint32': {'size': 4, 'read': read_uint},
    'fixed8': {'size': 1, 'read': read_fixed}, 'float': {'size': 4, 'read': read_float},
    'char': {'size': 1, 'read': read_char}, 'tag': {'size': 4, 'read': read_tag}
}


def read_struct(struct, buffer):
    entry = {}
    offset = 0

    for field in [field[1] for field in struct.get('fields').items()]:
        if field['type'] in primitive.keys():
            entry[field['name']] = primitive[field['type']]['read'](buffer[offset:offset + primitive[field['type']]['size']])
            offset += primitive[field['type']]['size']
        else:
            f_struct = load_struct(field['type'], int(field.get('type-version', '0')))
            entry[field['name']] = read_struct(f_struct, buffer[offset:offset + f_struct['size']])
            offset += f_struct['size']

    return entry


def load_struct(struct, get_version=0):
    version_dict = {'type': struct, 'version': None, 'size': None, 'fields': {}}

    for version in structs_dict[struct].findall('versions')[0]:
        if int(version.get('number')) == get_version:
            version_dict['version'] = int(version.get('number'))
            version_dict['size'] = int(version.get('size'))

    for field in structs_dict[struct].findall('fields')[0]:
        if get_version >= int(field.get('since-version', '0')) and get_version <= int(field.get('till-version', '99')):
            version_dict['fields'][field.get('name')] = {key: field.get(key) for key in field.keys()}

    return version_dict


def load_sections(filepath):
    sections = []
    with open(filepath, 'rb') as file:
        md34v11 = load_struct('MD34', 11)
        header_bytes = file.read(int(md34v11['size']))
        header = read_struct(md34v11, header_bytes)
        md34v11_index_entry = load_struct('MD34IndexEntry')
        for ii in range(header.get('indexSize')):
            file.seek(header.get('indexOffset') + ii * (int(md34v11_index_entry['size'])))
            index_bytes = file.read(int(md34v11_index_entry['size']))
            section_tag = read_struct(md34v11_index_entry, index_bytes)
            file.seek(section_tag['offset'])
            section_struct = load_struct(section_tag['tag'], section_tag['version'])
            section_entries = [read_struct(section_struct, file.read(section_struct['size'])) for jj in range(section_tag['repetitions'])]
            sections.append({'tag': section_tag['tag'], 'version': section_tag['version'], 'entries': section_entries})

    return sections
