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

# * source of file - https://github.com/SC2Mapster/m3addon

import struct
from sys import stderr
from xml.etree import ElementTree as ET


primitive_names = {'U8__', 'I16_', 'U16_', 'I32_', 'U32_', 'I64_', 'U64_', 'FLAG', 'REAL', 'CHAR'}
primitive_field_info = {
    'uint8': {'size': 1, 'format': 'B', 'min': 0, 'max': (1 << 8) - 1},
    'int16': {'size': 2, 'format': 'h', 'min': -1 << 15, 'max': (1 << 15) - 1},
    'uint16': {'size': 2, 'format': 'H', 'min': 0, 'max': (1 << 16) - 1},
    'int32': {'size': 4, 'format': 'i', 'min': -1 << 31, 'max': (1 << 31) - 1},
    'uint32': {'size': 4, 'format': 'I', 'min': 0, 'max': (1 << 32) - 1},
    'uint64': {'size': 8, 'format': 'Q', 'min': 0, 'max': (1 << 64) - 1},
    'float': {'size': 4, 'format': 'f'},
}


def structures_from_tree():

    def parse_hex_str(hex_string):
        if not hex_string:
            return None
        hex_string = hex_string[2:]
        return bytes([int(hex_string[x:x + 2], 16) for x in range(0, len(hex_string), 2)])

    from os import path
    filename = path.join(path.dirname(__file__), 'structures.xml')
    xml_structures = ET.parse(filename).getroot().findall('structure')

    histories = {}

    for xml_structure in xml_structures:
        xml_structure_name = xml_structure.get('name')
        xml_versions = xml_structure.findall('versions')[0].findall('version')
        xml_fields = xml_structure.findall('fields')[0].findall('field')
        version_nums = set([int(xml_version.get('number')) for xml_version in xml_versions])
        version_to_size = {int(xml_version.get('number')): int(xml_version.get('size')) for xml_version in xml_versions}

        all_field_versions = []
        for xml_field in xml_fields:
            str_name = xml_field.get('name')
            str_type = xml_field.get('type')
            str_ref_to = xml_field.get('ref_to')
            str_since_version = xml_field.get('since_version', None)
            str_till_version = xml_field.get('till_version', None)
            str_default_val = xml_field.get('default_value', None)
            str_expected_val = xml_field.get('expected_value', None)
            str_size = xml_field.get('size', None)
            since_version = int(str_since_version) if str_since_version else None
            till_version = int(str_till_version) if str_till_version else None

            if str_type in primitive_field_info and 'int' in str_type:
                default_val = int(str_default_val, 0) if str_default_val else None
                expected_val = int(str_expected_val, 0) if str_expected_val else None
                if default_val is None:
                    default_val = expected_val or 0
                bitmasks = {}
                xml_bits = xml_field.findall('bits')
                if len(xml_bits):
                    bitmasks = {xml_bit.get('name'): int(xml_bit.get('mask'), 0) for xml_bit in xml_bits[0].findall('bit')}
                field = M3FieldInt(str_name, str_type, since_version, till_version, default_val, expected_val, bitmasks)

            elif str_type == 'float':
                default_val = float(str_default_val) if str_default_val else None
                expected_val = float(str_expected_val) if str_expected_val else None
                if default_val is None:
                    default_val = expected_val or 0.0
                field = M3FieldFloat(str_name, str_type, since_version, till_version, default_val, expected_val)

            elif str_type is None:
                size = int(str_size) if str_size else None
                default_val = parse_hex_str(str_default_val)
                expected_val = parse_hex_str(str_expected_val)
                if default_val is None:
                    default_val = expected_val or bytes(size)
                field = M3FieldBytes(str_name, size, since_version, till_version, default_val, expected_val)
            else:
                v_pos = str_type.rfind('V')
                if v_pos != -1:
                    field_name = str_type[:v_pos]
                    field_version = int(str_type[v_pos + 1:])
                else:
                    field_name = str_type
                    field_version = 0
                field_struct_history = histories.get(field_name)
                if field_struct_history is None:
                    raise Exception(f'{field_name} must be defined before {xml_structure_name}')
                field_desc = field_struct_history.get_version(field_version)
                field = M3FieldStructure(str_name, field_desc, since_version, till_version, str_ref_to)

            all_field_versions.append({ii: field for ii in range(since_version or 0, (till_version or max(version_nums)) + 1)})

        histories[xml_structure_name] = M3StructureHistory(xml_structure_name, version_to_size, all_field_versions)

    return histories


class M3StructureHistory:
    ''' Container for information generally related to an M3 structure '''

    def __init__(self, name, version_to_size, field_versions):
        self.name = name
        self.primitive = self.name in primitive_names
        self.field_versions = field_versions
        self.version_to_size = version_to_size
        self.version_to_description = {}
        # create all to check sizes
        for version in version_to_size:
            self.get_version(version)

    def get_version(self, version, md_version=34):
        desc_id = f'MD{md_version}_{version}'

        if (desc := self.version_to_description.get(desc_id)) is None:
            fields = {field.name: field for field_versions in self.field_versions if (field := field_versions.get(version))}
            if md_version == 33:
                for field in fields.values():
                    if type(field) == M3FieldStructure:
                        new_field_desc_name = 'SmallReference' if field.desc.history.name == 'Reference' else field.desc.history.name
                        new_field_desc = structures[new_field_desc_name].get_version(field.desc.version, md_version)
                        fields[field.name] = M3FieldStructure(field.name, new_field_desc, field.since_version, field.till_version, field.ref_to)

            calc_size = sum(field.size for field in fields.values())
            spec_size = self.version_to_size.get(version)
            if calc_size != spec_size and md_version == 34:  # validate the specified size, but skip if model is not md34
                offset = 0
                stderr.write(f'Offsets of {self.name} in version {version}:\n')
                for field in fields:
                    stderr.write(f'{offset}: {field.name}\n')
                    offset += field.size
                raise Exception(f'Size mismatch: {self.name}V{version} specified={spec_size} calculated={calc_size}')
            self.version_to_description[desc_id] = (desc := M3StructureDescription(self, version, fields, calc_size))

        return desc


class M3StructureDescription:
    ''' Container for information relating to a specific version of an M3 structure '''

    def __init__(self, history: M3StructureHistory, version, fields, size):
        self.history = history
        self.version = version
        self.fields = fields
        self.size = size

    def __str__(self):
        return f'{self.history.name}V{self.version}: {{{self.fields}}}'

    def instance(self, buffer=None, offset=0):
        return M3StructureData(self, buffer, offset)

    def instances(self, buffer, count):
        vals = []
        if self.history.primitive:
            struct_format = self.fields['value'].struct_format
            for offset in range(0, count * self.size, self.size):
                vals.append(struct_format.unpack(buffer[offset:offset + self.size])[0])
        else:
            instance_offset = 0
            for ii in range(count):
                vals.append(self.instance(buffer=buffer, offset=instance_offset))
                instance_offset += self.size
        return vals

    def instance_validate(self, instance, instance_name):
        if self.history.primitive:
            self.fields['value'].content_validate(instance, instance_name + '.value')
        else:
            for field in self.fields.values():
                try:
                    field_content = getattr(instance, field.name)
                except AttributeError:
                    raise Exception(f'{instance_name}.{field.name} does not exist')
                field.content_validate(field_content, instance_name + '.' + field.name)

    def instances_to_bytearray(self, instances):
        raw_bytes = bytearray(self.size * len(instances))
        offset = 0
        if self.history.primitive:  # instances of numbers
            struct_format = self.fields['value'].struct_format
            for value in instances:
                struct_format.pack_into(raw_bytes, offset, value)
                offset += self.size
        else:  # instances of M3StructureData
            for value in instances:
                value.to_buffer(raw_bytes, offset)
                offset += self.size
        return raw_bytes


class M3StructureData:
    ''' Container for M3 structure property values '''

    def __init__(self, desc: M3StructureDescription, buffer=None, offset=0):
        self.desc = desc

        if buffer is not None:
            self.from_buffer(buffer, offset)
        else:
            for field in self.desc.fields.values():
                field.default_set(self)

    def __str__(self):
        field_strings = list(f'{field_name}: {getattr(self, field_name)}' for field_name in self.desc.fields)
        return f'{self.desc.history.name}V{self.desc.version} fields: {field_strings}'

    def from_buffer(self, buffer, offset):
        field_offset = offset
        for field in self.desc.fields.values():
            field.from_buffer(self, buffer, field_offset)
            field_offset += field.size

    def to_buffer(self, buffer, offset):
        field_offset = offset
        for field in self.desc.fields.values():
            field.to_buffer(self, buffer, field_offset)
            field_offset += field.size

    def bit_get(self, field_name, bit_name):
        field = self.desc.fields[field_name]
        mask = field.bit_mask_map[bit_name]
        int_val = getattr(self, field_name)
        return int_val & mask != 0

    def bit_set(self, field_name, bit_name, value):
        field = self.desc.fields[field_name]
        mask = field.bit_mask_map[bit_name]
        int_val = getattr(self, field_name)
        if value is True:
            setattr(self, field_name, int_val | mask)
        elif int_val & mask != 0:
            setattr(self, field_name, int_val ^ mask)


class M3Field:
    ''' Container for information relating to a specific field in a M3StructureHistory or M3StructureDescription instance '''

    def __init__(self, name, since_version, till_version):
        self.name = name
        self.since_version = since_version
        self.till_version = till_version

    def default_set(self, data):
        setattr(data, self.name, getattr(self, 'default_value', ''))


class M3FieldStructure(M3Field):

    def __init__(self, name, desc: M3StructureDescription, since_version, till_version, ref_to):
        M3Field.__init__(self, name, since_version, till_version)
        self.desc = desc
        self.size = desc.size
        self.ref_to = ref_to

    def from_buffer(self, data, buffer, offset):
        instance = self.desc.instance(buffer, offset)
        setattr(data, self.name, instance)

    def to_buffer(self, data, buffer, offset):
        instance = getattr(data, self.name)
        instance_offset = offset
        for field in instance.desc.fields.values():
            field.to_buffer(instance, buffer, instance_offset)
            instance_offset += field.size

    def default_set(self, data):
        instance = self.desc.instance()
        setattr(data, self.name, instance)

    def content_validate(self, field_content, field_path):
        self.desc.instance_validate(field_content, field_path)


class M3FieldPrimitive(M3Field):
    ''' Base class for M3FieldBytes, M3FieldInt, M3FieldFloat '''

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        M3Field.__init__(self, name, since_version, till_version)
        self.size = primitive_field_info[type_str]['size']
        self.struct_format = struct.Struct('<' + primitive_field_info[type_str]['format'])
        self.type_str = type_str
        self.default_value = default_value
        self.expected_value = expected_value

    def from_buffer(self, data, buffer, offset):
        value = self.struct_format.unpack_from(buffer, offset)[0]
        if self.expected_value is not None and value != self.expected_value:
            raise Exception(f'{data.desc.history.name}V{data.desc.version}.{self.name} expected to be {self.expected_value}, but it was {value}')
        setattr(data, self.name, value)

    def to_buffer(self, data, buffer, offset):
        value = getattr(data, self.name)
        self.struct_format.pack_into(buffer, offset, value)


class M3FieldBytes(M3FieldPrimitive):
    ''' Inherits methods from M3FieldPrimitive, but is initialized as a M3Field '''

    def __init__(self, name, size, since_version, till_version, default_value, expected_value):
        M3Field.__init__(self, name, since_version, till_version)
        self.size = size
        self.struct_format = struct.Struct(f'<{size}s')
        self.default_value = default_value
        self.expected_value = expected_value

    def content_validate(self, field_content, field_path):
        if type(field_content) != bytes or len(field_content) != self.size:
            raise Exception(f'{field_path} is not a bytes object of size {self.size}')


class M3FieldInt(M3FieldPrimitive):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value, bit_mask_map):
        M3FieldPrimitive.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)
        self.min_val = primitive_field_info[type_str]['min']
        self.max_val = primitive_field_info[type_str]['max']
        self.bit_mask_map = bit_mask_map

    def content_validate(self, field_content, field_path):
        if (type(field_content) != int):
            raise Exception(f'{field_path} {field_content} type is {type(field_content)}, not int')
        if (field_content < self.min_val) or (field_content > self.max_val):
            raise Exception(f'{field_path} {field_content} not in range({self.min_val}, {self.max_val})')


class M3FieldFloat(M3FieldPrimitive):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        M3FieldPrimitive.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)

    def content_validate(self, field_content, field_path):
        if type(field_content) != float:
            raise Exception(f'{field_path} {field_content} type is {type(field_content)}, not float')


class M3SectionList(list):
    ''' List object for M3Section instances '''

    def __init__(self, init_header=False):
        list.__init__(self, [])

        if init_header:
            section = M3Section(desc=structures['MD34'].get_version(11), index_entry=None, references=[], content=[])
            section.content_add().tag = int.from_bytes(b'43DM', 'little')
            self.append(section)

    def __getitem__(self, item):
        return (self[item.index] if item.index and item.entries else []) if type(item) == M3StructureData else super(M3SectionList, self).__getitem__(item)

    def __setitem__(self, item, val):
        assert type(val.desc) == M3StructureDescription
        return super(M3SectionList, self).__setitem__(item, val)

    @classmethod
    def from_index(cls, entry_desc, entry_buffers, md_version=34):
        self = cls()

        for entry_buffer in entry_buffers:
            index_entry = entry_desc.instance(entry_buffer)
            tag_str = index_entry.tag.to_bytes(4, 'little').decode('ascii').replace('\x00', '')[::-1]
            desc = structures[tag_str].get_version(index_entry.version, md_version)
            section = M3Section(desc=desc, index_entry=index_entry, references=[], content=[])

            if section.desc is None:
                stderr.write(f'Unknown section: {tag_str}V{index_entry.version} at offset {index_entry.offset}')

            self.append(section)

        return self

    def section_for_reference(self, structure, field, version=0, pos=-1):
        ref_desc = structures[structure.desc.fields[field].ref_to].get_version(version)
        section = M3Section(desc=ref_desc, index_entry=None, references=[getattr(structure, field)], content=[])

        if type(pos) is int:
            self.insert(pos if pos >= 0 else len(self), section)

        return section

    def validate(self):
        culled_sections = 0
        for ii in range(len(self)):
            section = self[ii - culled_sections]
            if len(section):
                for instance in section:
                    section.desc.instance_validate(instance, section.desc.history.name)
            else:
                del self[ii - culled_sections]
                culled_sections += 1

    def resolve(self):
        aggregate_references = set()
        for ii, section in enumerate(self):
            for reference in section.references:
                if reference in aggregate_references:
                    raise Exception('Cannot have reference index referenced by more than one section', reference, section.references)
                aggregate_references.add(reference)
                reference.index = ii
                reference.entries = len(section)

    def to_index(self):
        buffer_offset = 0
        for section in self:
            section.index_entry = structures['MDIndexEntry'].get_version(34).instance()
            section.index_entry.tag = int.from_bytes(section.desc.history.name[::-1].encode('ascii'), 'little')
            section.index_entry.offset = buffer_offset
            section.index_entry.repetitions = len(section)
            section.index_entry.version = section.desc.version
            section.raw_bytes = section.desc.instances_to_bytearray(section.content)
            section.raw_bytes.extend([0xaa for ii in range(0, len(section.raw_bytes) % 16)])
            buffer_offset += len(section.raw_bytes)

        self[0][0].index_offset = buffer_offset
        self[0][0].index_size = len(self)
        self[0].raw_bytes = self[0].desc.instances_to_bytearray(self[0])
        self[0].raw_bytes.extend([0xaa for ii in range(0, len(self[0].raw_bytes) % 16)])


class M3Section:
    ''' Container for M3StructureData (or primitive) instances '''

    def __init__(self, desc: M3StructureDescription, index_entry: M3StructureData, references: list, content: list):
        self.desc = desc
        self.index_entry = index_entry
        self.references = references
        self.content = content
        self.raw_bytes = None

    def __str__(self):
        if self.index_entry:
            return f'Section {self.index_entry}'
        if self.desc:
            return f'Section {self.desc.history.name}V{self.desc.version}'

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]

    def content_add(self, *instances):
        if not instances and not self.desc.history.primitive:
            self.content.append(instance := self.desc.instance())
            return instance
        self.content += instances

    def content_to_string(self):
        return ''.join(chr(c) for c in self.content if c != 0)

    def content_from_string(self, string):
        self.content = [ord(c) for c in string] + [0x00]


def section_list_load(filename):
    with open(filename, 'rb') as f:
        md_tag = f.read(4)[::-1].decode('ascii')
        md_version = int(md_tag[2:])
        f.seek(0)
        m3_header = structures[md_tag].get_version(11)
        header = m3_header.instance(f.read(m3_header.size))
        f.seek(header.index_offset)
        mdie = structures['MDIndexEntry'].get_version(md_version)

        for section in (sections := M3SectionList.from_index(mdie, [f.read(mdie.size) for ii in range(header.index_size)], md_version)):
            f.seek(section.index_entry.offset)
            section.raw_bytes = (buffer := f.read(section.index_entry.repetitions * section.desc.size))
            section.content = section.desc.instances(buffer=buffer, count=section.index_entry.repetitions)

    return sections


def section_list_save(sections: M3SectionList, filename):
    with open(filename, 'w+b') as f:
        index_buffer = bytearray(16 * len(sections))
        prev_section = None
        for ii, section in enumerate(sections):
            if section.index_entry.offset != f.tell():
                raise Exception(f'Section length: {prev_section.index_entry} with length {len(prev_section.raw_bytes)} followed by {section.index_entry}')
            section.index_entry.to_buffer(index_buffer, 16 * ii)
            f.write(section.raw_bytes)
            prev_section = section
        f.write(index_buffer)


structures = structures_from_tree()
