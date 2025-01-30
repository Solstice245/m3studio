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

import struct
import copy
from os import path
from sys import stderr
from xml.etree import ElementTree as ET

primitive_field_info = {
    'uint8': {'format': 'B', 'min': 0, 'max': (1 << 8) - 1},
    'int16': {'format': 'h', 'min': -1 << 15, 'max': (1 << 15) - 1}, 'uint16': {'format': 'H', 'min': 0, 'max': (1 << 16) - 1},
    'int32': {'format': 'i', 'min': -1 << 31, 'max': (1 << 31) - 1}, 'uint32': {'format': 'I', 'min': 0, 'max': (1 << 32) - 1},
    'uint64': {'format': 'Q', 'min': 0, 'max': (1 << 64) - 1}, 'float': {'format': 'f'},
}


def structures_from_tree():

    def parse_hex_str(hex_string):
        return bytes([int(hex_string[x + 2:x + 4], 16) for x in range(0, len(hex_string) - 2, 2)]) if hex_string else None

    histories = {}
    for xml_structure in ET.parse(path.join(path.dirname(__file__), 'structures.xml')).getroot().findall('structure'):
        xml_structure_name = xml_structure.get('name')
        xml_versions = xml_structure.findall('versions')[0].findall('version')
        version_max = max(set([int(xml_version.get('number')) for xml_version in xml_versions]))
        version_to_size = {int(xml_version.get('number')): int(xml_version.get('size')) for xml_version in xml_versions}

        all_field_versions = []
        for xml_field in xml_structure.findall('fields')[0].findall('field'):
            str_name = xml_field.get('name')
            str_type = xml_field.get('type')
            str_ref_to = xml_field.get('ref_to')
            str_size = xml_field.get('size')
            str_since_version = xml_field.get('since_version', None)
            str_till_version = xml_field.get('till_version', None)
            str_default_val = xml_field.get('default_value', None)
            str_expected_val = xml_field.get('expected_value', None)
            since_version = int(str_since_version) if str_since_version is not None else None
            till_version = int(str_till_version) if str_till_version is not None else None

            if str_type in primitive_field_info and 'int' in str_type:
                default_val = int(str_default_val, 0) if str_default_val else None
                expected_val = int(str_expected_val, 0) if str_expected_val else None
                bitmasks = {}
                xml_bits = xml_field.findall('bits')
                if len(xml_bits):
                    bitmasks = {xml_bit.get('name'): int(xml_bit.get('mask'), 0) for xml_bit in xml_bits[0].findall('bit')}
                field = M3FieldInt(str_name, str_type, default_val or expected_val or 0, expected_val, bitmasks)

            elif str_type == 'float':
                default_val = float(str_default_val) if str_default_val else None
                expected_val = float(str_expected_val) if str_expected_val else None
                field = M3FieldFloat(str_name, str_type, default_val or expected_val or 0.0, expected_val)

            elif str_type is None:
                size = int(str_size)
                default_val = parse_hex_str(str_default_val)
                expected_val = parse_hex_str(str_expected_val)
                field = M3FieldBytes(str_name, size, default_val or expected_val or bytes(size), expected_val)
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
                field = M3FieldStructure(str_name, field_desc, str_ref_to)

            all_field_versions.append({ii: field for ii in range(since_version or 0, (till_version if till_version is not None else version_max) + 1)})

        histories[xml_structure_name] = M3StructureHistory(xml_structure_name, version_to_size, all_field_versions)

    return histories


class M3StructureHistory:
    ''' Container for information generally related to an M3 structure '''

    def __init__(self, name, version_to_size, field_versions):
        self.name = name
        self.primitive = self.name in {'U8__', 'I16_', 'U16_', 'I32_', 'U32_', 'I64_', 'U64_', 'FLAG', 'REAL', 'CHAR'}
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
                        fields[field.name] = M3FieldStructure(field.name, new_field_desc, field.ref_to)

            calc_size = sum(field.size for field in fields.values())
            spec_size = self.version_to_size.get(version)
            if calc_size != spec_size and md_version == 34:  # validate the specified size, but skip if model is not md34
                offset = 0
                stderr.write(f'Offsets of {self.name} in version {version}:\n')
                for field in fields:
                    stderr.write(f'{offset}: {fields[field].name}\n')
                    offset += fields[field].size
                raise Exception(f'Size mismatch: {self.name}V{version} specified={spec_size} calculated={calc_size}')
            self.version_to_description[desc_id] = (desc := M3StructureDescription(self, version, fields, calc_size))

        return desc


class M3StructureDescription:
    ''' Container for information relating to a specific version of an M3 structure '''

    @classmethod
    def get_vertex_description(cls, vertex_flags):
        size = 0
        fields = []

        if vertex_flags & 0x1:
            fields.append({0: M3FieldStructure('pos', structures['VEC3'].get_version(0))})
            size += 12

        lookup_pairs = 0
        if vertex_flags & 0x20:
            lookup_pairs += 2
        if vertex_flags & 0x40:
            lookup_pairs += 2

        for ii in range(lookup_pairs):
            field_name = 'weight' + str(ii)
            fields.append({0: M3FieldInt(field_name, 'uint8')})
            size += 1

        for ii in range(lookup_pairs):
            field_name = 'lookup' + str(ii)
            fields.append({0: M3FieldInt(field_name, 'uint8')})
            size += 1

        if vertex_flags & 0x80:
            fields.append({0: M3FieldStructure('normalf', structures['VEC3'].get_version(0))})
            size += 12

        if vertex_flags & 0x0800000:
            fields.append({0: M3FieldStructure('normal', structures['Vector3As3uint8'].get_version(0))})
            fields.append({0: M3FieldInt('sign', 'uint8')})
            size += 4

        # must come before color component
        if vertex_flags & 0x100:
            fields.append({0: M3FieldInt('test100', 'uint32', 0)})
            size += 4

        if vertex_flags & 0x200:
            fields.append({0: M3FieldStructure('col', structures['COL'].get_version(0))})
            size += 4

        if vertex_flags & 0x400:
            fields.append({0: M3FieldInt('test400', 'uint32', 0x00000000)})
            size += 4

        if vertex_flags & 0x800:
            fields.append({0: M3FieldInt('test800', 'uint32', 0xFFFFFFFF)})
            size += 4

        if vertex_flags & 0x1000:
            fields.append({0: M3FieldInt('test1000', 'uint32', 0xFFFFFFFF)})
            size += 4

        uv_coords = 0
        if vertex_flags & 0x00020000:
            uv_coords += 1
        if vertex_flags & 0x00040000:
            uv_coords += 1
        if vertex_flags & 0x00080000:
            uv_coords += 1
        if vertex_flags & 0x00100000:
            uv_coords += 1
        if vertex_flags & 0x40000000:
            uv_coords += 1

        if vertex_flags & 0x2000:
            fields.append({0: M3FieldStructure('fuv0', structures['VEC2'].get_version(0))})
            size += 8

        if vertex_flags & 0x4000:
            fields.append({0: M3FieldStructure('fuv1', structures['VEC2'].get_version(0))})
            size += 8

        if vertex_flags & 0x8000:
            fields.append({0: M3FieldStructure('fuv2', structures['VEC2'].get_version(0))})
            size += 8

        if vertex_flags & 0x10000:
            fields.append({0: M3FieldStructure('fuv3', structures['VEC2'].get_version(0))})
            size += 8

        for ii in range(uv_coords):
            field_name = 'uv' + str(ii)
            fields.append({0: M3FieldStructure(field_name, structures['Vector2As2int16'].get_version(0))})
            size += 4

        if vertex_flags & 0x200000:
            fields.append({0: M3FieldStructure('normalf', structures['VEC3'].get_version(0))})
            size += 12

        if vertex_flags & 0x400000:
            fields.append({0: M3FieldStructure('tanf', structures['VEC3'].get_version(0))})
            size += 12

        if vertex_flags & 0x1000000:
            fields.append({0: M3FieldStructure('tan', structures['Vector3As3uint8'].get_version(0))})
            fields.append({0: M3FieldInt('unused', 'uint8')})
            size += 4

        if vertex_flags & 0x2000000:
            fields.append({0: M3FieldInt('test2000000', 'uint32', 10000)})
            size += 4

        if vertex_flags & 0x4000000:
            fields.append({0: M3FieldInt('test4000000', 'uint32', 10000)})
            fields.append({0: M3FieldInt('test4000001', 'uint32', 10000)})
            fields.append({0: M3FieldInt('test4000002', 'uint32', 10000)})
            size += 12

        if vertex_flags & 0x8000000:
            fields.append({0: M3FieldInt('test8000000', 'uint32', 10000)})
            fields.append({0: M3FieldInt('test8000001', 'uint32', 10000)})
            fields.append({0: M3FieldInt('test8000002', 'uint32', 10000)})
            size += 12

        if vertex_flags & 0x10000000:
            fields.append({0: M3FieldInt('test10000000', 'uint32', 10000)})
            size += 4

        if vertex_flags & 0x20000000:
            fields.append({0: M3FieldInt('test20000000', 'uint32', 10000)})
            size += 4

        return M3StructureHistory('VertexFormat'+hex(vertex_flags).zfill(8), {0: size}, fields).get_version(0)

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
        if self.history.primitive:
            return struct.unpack(f'<{count}' + self.fields['value'].struct_format.format[1:], buffer)
        else:
            vals = []
            instance_offset = 0
            for ii in range(count):
                vals.append(self.instance(buffer=buffer, offset=instance_offset))
                instance_offset += self.size
            return vals

    def instance_validate(self, instance, instance_name):
        if self.history.primitive:
            self.fields['value'].content_validate(instance, instance_name + '.value')
        else:

            if not self == instance.desc:
                raise TypeError(f'M3 description of {instance_name} {instance} {instance.desc} does not match {self}')

            for field in self.fields.values():
                field.content_validate(getattr(instance, field.name), instance_name + '.' + field.name)

    def instances_to_bytearray(self, instances):
        raw_bytes = bytearray(self.size * len(instances))
        if self.history.primitive:  # instances of numbers
            struct.pack_into(f'<{len(instances)}' + self.fields['value'].struct_format.format[1:], raw_bytes, 0, *instances)
        else:  # instances of M3StructureData
            offset = 0
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

    def __repr__(self):
        return f'{self.desc.history.name}V{self.desc.version}'

    def copy(self):
        data = copy.copy(self)

        for field in self.desc.fields.values():
            if type(field) == M3FieldStructure:
                setattr(data, field.name, getattr(self, field.name).copy())

        return data

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
    ''' Container for information relating to a specific field in an M3StructureHistory or M3StructureDescription instance '''

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.__class__.__name__

    def default_set(self, data: M3StructureData):
        setattr(data, self.name, getattr(self, 'default_value', ''))


class M3FieldStructure(M3Field):

    def __init__(self, name, desc: M3StructureDescription, ref_to=''):
        M3Field.__init__(self, name)
        self.desc = desc
        self.size = desc.size
        self.ref_to = ref_to

    def __repr__(self):
        if self.ref_to:
            return self.__class__.__name__ + '_' + str(self.desc) + '->' + self.ref_to
        else:
            return self.__class__.__name__ + '_' + str(self.desc)

    def from_buffer(self, data: M3StructureData, buffer, offset):
        setattr(data, self.name, self.desc.instance(buffer, offset))

    def to_buffer(self, data: M3StructureData, buffer, offset):
        instance = getattr(data, self.name)
        instance_offset = offset
        for field in instance.desc.fields.values():
            field.to_buffer(instance, buffer, instance_offset)
            instance_offset += field.size

    def default_set(self, data: M3StructureData):
        setattr(data, self.name, self.desc.instance())

    def content_validate(self, field_content, field_path):
        self.desc.instance_validate(field_content, field_path)


class M3FieldPrimitive(M3Field):
    ''' Base class for M3FieldBytes, M3FieldInt, M3FieldFloat '''

    def __init__(self, name, type_str, default_value=0, expected_value=None):
        M3Field.__init__(self, name)
        self.struct_format = struct.Struct('<' + primitive_field_info[type_str]['format'])
        self.size = self.struct_format.size
        self.default_value = default_value
        self.expected_value = expected_value

    def from_buffer(self, data: M3StructureData, buffer, offset):
        value = self.struct_format.unpack_from(buffer, offset)[0]
        if self.expected_value is not None and value != self.expected_value:
            raise Exception(f'{data.desc.history.name}V{data.desc.version}.{self.name} expected to be {self.expected_value}, but it was {value}')
        setattr(data, self.name, value)

    def to_buffer(self, data: M3StructureData, buffer, offset):
        value = getattr(data, self.name)
        self.struct_format.pack_into(buffer, offset, value)


class M3FieldBytes(M3FieldPrimitive):
    ''' Inherits methods from M3FieldPrimitive, but is initialized as an M3Field '''

    def __init__(self, name, size, default_value, expected_value=None):
        M3Field.__init__(self, name)
        self.size = size
        self.struct_format = struct.Struct(f'<{size}s')
        self.default_value = default_value
        self.expected_value = expected_value

    def content_validate(self, field_content, field_path):
        if type(field_content) != bytes or len(field_content) != self.size:
            raise Exception(f'{field_path} is not a bytes object of size {self.size}')


class M3FieldInt(M3FieldPrimitive):

    def __init__(self, name, type_str, default_value=0, expected_value=None, bit_mask_map=None):
        M3FieldPrimitive.__init__(self, name, type_str, default_value, expected_value)
        self.min_val = primitive_field_info[type_str]['min']
        self.max_val = primitive_field_info[type_str]['max']
        self.bit_mask_map = bit_mask_map

    def content_validate(self, field_content, field_path):
        if type(field_content) != int:
            raise Exception(f'{field_path} {field_content} type is {type(field_content)}, not int')
        if field_content < self.min_val or field_content > self.max_val:
            raise Exception(f'{field_path} {field_content} not in range({self.min_val}, {self.max_val})')


class M3FieldFloat(M3FieldPrimitive):

    def __init__(self, name, type_str, default_value=0.0, expected_value=None):
        M3FieldPrimitive.__init__(self, name, type_str, default_value, expected_value)

    def content_validate(self, field_content, field_path):
        if type(field_content) != float:
            raise Exception(f'{field_path} {field_content} type is {type(field_content)}, not float')


class M3SectionList(list):
    ''' List object for M3Section instances '''

    def __init__(self):
        list.__init__(self, [])
        self.filepath = None
        self.file = None
        self.model = None
        self.md_version = 34

    def __getitem__(self, key):
        if type(key) == M3StructureData:
            item = self[key.index] if key.index and key.entries else []
        else:
            item = super(M3SectionList, self).__getitem__(key)

            if item is None:
                self[key] = self.section_from_index_entry(self.index_entries[key])
                item = self[key]

        return item

    def __setitem__(self, item, val):
        assert type(val.desc) == M3StructureDescription
        return super(M3SectionList, self).__setitem__(item, val)

    @classmethod
    def new(cls, name, version):
        self = cls()

        section = M3Section(desc=structures['MD34'].get_version(11), index_entry=None, references=[], content=[])
        section.content_add().tag = int.from_bytes(b'43DM', 'little')
        self.append(section)

        model_section = self.section_for_reference(self[0][0], 'model', version=version)
        self.model = model_section.content_add()

        model_name_section = self.section_for_reference(self.model, 'model_name')
        model_name_section.content_from_string(name)

        return self

    @classmethod
    def load(cls, filepath, lazy=False):
        self = cls()
        self.filepath = filepath
        self.index_entries = []

        f = open(filepath, 'rb')
        md_tag = f.read(4)[::-1].decode('ascii')
        self.md_version = int(md_tag[2:])
        f.seek(0)
        m3_header = structures[md_tag].get_version(11)
        header = m3_header.instance(f.read(m3_header.size))
        f.seek(header.index_offset)
        mdie = structures['MDIndexEntry'].get_version(self.md_version)

        self.file = f

        for entry_buffer in [f.read(mdie.size) for ii in range(header.index_size)]:
            index_entry = mdie.instance(entry_buffer)
            tag_str = index_entry.tag.to_bytes(4, 'little').decode('ascii').replace('\x00', '')[::-1]
            desc = structures[tag_str].get_version(index_entry.version, self.md_version)

            if desc is None:
                stderr.write(f'Unknown section: {tag_str}V{index_entry.version} at offset {index_entry.offset}')

            self.index_entries.append(index_entry)
            self.append(self.section_from_index_entry(index_entry) if not lazy else None)

        if not lazy:
            f.close()
            self.file = None

        self.model = self[self[0][0].model][0]

        return self

    def save(self, filepath=None):
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

        if filepath is None:
            filepath = self.filepath

        with open(filepath, 'w+b') as f:
            index_buffer = bytearray(16 * len(self))
            prev_section = None
            for ii, section in enumerate(self):
                if section.index_entry.offset != f.tell():
                    raise Exception(f'Section length: {prev_section.index_entry} with length {len(prev_section.raw_bytes)} followed by {section.index_entry}')
                section.index_entry.to_buffer(index_buffer, 16 * ii)
                f.write(section.raw_bytes)
                prev_section = section
            f.write(index_buffer)

    def section_from_index_entry(self, index_entry):
        tag_str = index_entry.tag.to_bytes(4, 'little').decode('ascii').replace('\x00', '')[::-1]
        desc = structures[tag_str].get_version(index_entry.version, self.md_version)
        self.file.seek(index_entry.offset)
        section_buffer = self.file.read(index_entry.repetitions * desc.size)
        section = M3Section(desc=desc, index_entry=index_entry, references=[], content=desc.instances(buffer=section_buffer, count=index_entry.repetitions))
        section.raw_bytes = section_buffer
        return section

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

    def data_eq(self, data, other):
        if type(data) != M3StructureData:
            return data == other

        for field in data.desc.fields.values():

            if type(field) == M3FieldStructure:
                if field.desc.history.name == 'Reference':
                    data_index = getattr(data, field.name).index
                    other_index = getattr(other, field.name).index

                    if data_index == other_index:
                        continue

                    if data_index == 0 ^ other_index == 0:
                        continue

                    if not self.section_eq(self[data_index], self[other_index]):
                        return False
                else:
                    if not self.data_eq(getattr(data, field.name), getattr(other, field.name)):
                        return False
            else:
                if getattr(data, field.name, 'not attr 0') != getattr(other, field.name, 'not attr 1'):
                    return False

        return True

    def section_eq(self, section, other):
        if type(other) != M3Section:
            return False
        if section.desc != other.desc:
            return False
        if len(section.content) != len(other.content):
            return False
        for ii in range(len(section.content)):
            if not self.data_eq(section.content[ii], other.content[ii]):
                return False
        return True

    def factor_sections(self):
        excluded_sections = []

        if self.model and self.model.desc.version >= 23:  # using the same section for both of these breaks attachment volumes
            excluded_sections.append(self[self.model.attachment_volumes_addon0])
            excluded_sections.append(self[self.model.attachment_volumes_addon1])

        matched_sections = []
        matched_sections_map = {}
        for ii, section in enumerate(self):

            if section in matched_sections:
                continue

            matched_sections.append(section)
            matched_sections_map[ii] = ii

            if section in excluded_sections:
                continue

            for jj, section_comp in enumerate(self):
                if section_comp in matched_sections:
                    continue
                if self.section_eq(section, section_comp):
                    matched_sections.append(section_comp)
                    matched_sections_map[jj] = ii

        remaining_sections = sorted([key for key, val in matched_sections_map.items() if val == key])
        sections_to_delete = sorted([key for key, val in matched_sections_map.items() if val != key], reverse=True)

        if not len(sections_to_delete):
            return

        # resolve reference indexes again after determining the adjusted indexes
        aggregate_references = set()
        for ii, section in enumerate(self):
            for reference in section.references:
                if reference in aggregate_references:
                    raise Exception('Cannot have reference index referenced by more than one section', reference, section.references)
                aggregate_references.add(reference)
                reference.index = remaining_sections.index(matched_sections_map[ii])
                reference.entries = len(section)

        for ii in sections_to_delete:
            del self[ii]


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
            return f'Section {self.desc.history.name}V{self.desc.version} ({len(self.content)})'

    def __repr__(self):
        return self.__str__()

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


structures = structures_from_tree()
