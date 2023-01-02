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
import copy
from sys import stderr
from xml.etree import ElementTree as ET


primitive_struct_names = {'U8__', 'I16_', 'U16_', 'I32_', 'U32_', 'I64_', 'U64_', 'FLAG', 'REAL', 'CHAR'}
primitive_field_info = {
    'int8': {'size': 1, 'format': 'b', 'min': -1 << 7, 'max': (1 << 7) - 1},
    'uint8': {'size': 1, 'format': 'B', 'min': 0, 'max': (1 << 8) - 1},
    'int16': {'size': 2, 'format': 'h', 'min': -1 << 15, 'max': (1 << 15) - 1},
    'uint16': {'size': 2, 'format': 'H', 'min': 0, 'max': (1 << 16) - 1},
    'int32': {'size': 4, 'format': 'i', 'min': -1 << 31, 'max': (1 << 31) - 1},
    'uint32': {'size': 4, 'format': 'I', 'min': 0, 'max': (1 << 32) - 1},
    'int64': {'size': 8, 'format': 'q', 'min': -1 << 63, 'max': (1 << 63) - 1},
    'uint64': {'size': 8, 'format': 'Q', 'min': 0, 'max': (1 << 64) - 1},
    'fixed8': {'size': 1, 'format': 'B'},
    'float': {'size': 4, 'format': 'f'},
    'tag': {'size': 4, 'format': '4s'},
}


class M3StructureHistory:
    'Describes the history of a structure with a specific name'

    def __init__(self, name, version_to_size, field_versions):
        self.name = name
        self.primitive = self.name in primitive_struct_names
        self.field_versions = field_versions
        self.version_to_size = version_to_size
        self.version_to_description = {}
        # Create all to check sizes:
        for version in version_to_size:
            self.get_version(version)

    def get_version(self, version, md_version=34):
        struct_name = 'MD{}_{}'.format(md_version, version)
        structure = self.version_to_description.get(struct_name)
        if structure is None:
            used_fields = {}
            for field_versions in self.field_versions:
                field = field_versions.get(version)
                if field:
                    used_fields[field.name] = field

            final_fields = {}
            if md_version == 33:
                for field in used_fields.values():
                    new_field = copy.copy(field)
                    if type(new_field) == EmbeddedStructureField:
                        new_desc_name = field.struct_desc.struct_name
                        if new_desc_name == 'Reference':
                            new_desc_name = 'SmallReference'
                        new_desc = structures[new_desc_name].get_version(field.struct_desc.struct_version, md_version)
                        new_field.struct_desc = new_desc
                        new_field.size = new_desc.size
                    final_fields[new_field.name] = new_field
            else:
                final_fields = used_fields

            structure = M3StructureDescription(self, version, final_fields, self.version_to_size.get(version), md_version != 33)
            self.version_to_description[struct_name] = structure
        return structure


class M3StructureDescription:

    def __init__(self, struct_history: M3StructureHistory, struct_version, fields, specific_size, validate_size=True):
        self.history = struct_history
        self.struct_name = struct_history.name
        self.struct_version = struct_version
        self.fields = fields
        self.primitive = self.struct_name in primitive_struct_names
        self.size = 0

        for field in fields.values():
            self.size += field.size

        # Validate the specified size:
        if validate_size and self.size != specific_size:

            offset = 0
            stderr.write('Offsets of {} in version {}:\n'.format(self.struct_name, self.struct_version))
            for field in self.fields:
                stderr.write('{}: {}\n'.format(offset, field.name))
                offset += field.size

            args = self.struct_name, self.struct_version, specific_size, self.size
            raise Exception('Size mismatch: {} in version {} has been specified to have size {}, but the calculated size was {}'.format(*args))

    def instance(self, buffer=None, offset=0, checks=True):
        return M3Structure(self, buffer, offset, checks)

    def instances(self, buffer, count, checks=True):
        if self.primitive:
            if self.struct_name == 'CHAR':
                if type(buffer) == str:
                    return buffer
                else:
                    return buffer[:count - 1].decode('ASCII', 'replace')
            elif self.struct_name == 'U8__':
                return bytearray(buffer[:count])
            else:
                struct_format = list(self.fields.values())[0].struct_format
                vals = []
                for offset in range(0, count * self.size, self.size):
                    entry_bytes = buffer[offset:(offset + self.size)]
                    int_val = struct_format.unpack(entry_bytes)[0]
                    vals.append(int_val)
                return vals
        else:
            vals = []
            instance_offset = 0
            for i in range(count):
                vals.append(self.instance(buffer=buffer, offset=instance_offset, checks=checks))
                instance_offset += self.size
            return vals

    def instances_count(self, instances):
        if self.struct_name == 'CHAR':
            if instances is None:
                return 0
            return len(instances) + 1  # +1 terminating null character
        elif hasattr(instances, '__len__'):  # either a list or an array of bytes
            return len(instances)
        else:
            raise Exception('Can\'t measure the length of %s which is a %s' % (instances, self.struct_name))

    def instance_validate(self, instance, instance_name):
        if self.struct_name in primitive_struct_names:
            if self.struct_name == 'CHAR':
                if type(instance) != str:
                    raise Exception('%s is not a string character' % (field_path))
            # TODO validate other primitive structure tags
        else:
            for field in self.fields.values():
                try:
                    field_content = getattr(instance, field.name)
                except AttributeError:
                    raise Exception('%s does not have a field called %s' % (instance_name, field.name))
                    raise
                field.content_validate(field_content, instance_name + '.' + field.name)

    def instances_to_bytes(self, instances):
        if self.struct_name == 'CHAR':
            instances = ''.join(instances)
            if type(instances) != str:
                raise Exception('Expected a string but it was a %s' % type(instances))
            return instances.encode('ASCII') + b'\x00'
        elif self.struct_name == 'U8__':
            if type(instances) != bytes and type(instances) != bytearray:
                raise Exception('{}: Expected a byte array but it was a {}'.format(self.struct_name, type(instances)))
            return instances
        else:
            raw_bytes = bytearray(self.size * len(instances))
            offset = 0

            if self.primitive:
                struct_format = list(self.fields.values())[0].struct_format
                for value in instances:
                    struct_format.pack_into(raw_bytes, offset, value)
                    offset += self.size
            else:
                for value in instances:
                    value.to_buffer(raw_bytes, offset)
                    offset += self.size
            return raw_bytes

    def count_bytes_required_for_instances(self, instances):
        if self.struct_name == 'CHAR':
            return len(instances) + 1  # +1 for terminating character
        elif self.struct_name == 'U8__':
            return len(instances)
        else:
            return self.size * self.instances_count(instances)


class M3Structure:

    def __init__(self, struct_desc: M3StructureDescription, buffer=None, offset=0, checks=True):
        self.struct_desc = struct_desc

        if buffer is not None:
            self.from_buffer(buffer, offset, checks)
        else:
            for field in self.struct_desc.fields.values():
                field.default_set(self)

    def __str__(self):
        return '%sV%s: {%s}' % (self.struct_desc.struct_name, self.struct_desc.struct_version, self.struct_desc.fields)

    def from_buffer(self, buffer, offset, checks):
        field_offset = offset
        for field in self.struct_desc.fields.values():
            try:
                field.from_buffer(self, buffer, field_offset, checks)
            except struct.error as e:
                raise Exception('Failed to unpack %sV%s %s' % (self.struct_desc.struct_name, self.struct_desc.struct_version, field.name), e)
            field_offset += field.size
        assert field_offset - offset == self.struct_desc.size

    def to_buffer(self, buffer, offset):
        field_offset = offset
        for field in self.struct_desc.fields.values():
            field.to_buffer(self, buffer, field_offset)
            field_offset += field.size
        assert field_offset - offset == self.struct_desc.size

    def bit_get(self, field_name, bit_name):
        field = self.struct_desc.fields[field_name]
        return field.bit_get(self, bit_name)

    def bit_set(self, field_name, bit_name, value):
        field = self.struct_desc.fields[field_name]
        return field.bit_set(self, bit_name, value)


class Field:
    def __init__(self, name, since_version, till_version):
        self.name = name
        self.since_version = since_version
        self.till_version = till_version


class TagField(Field):

    def __init__(self, name, since_version, till_version):
        Field.__init__(self, name, since_version, till_version)
        self.struct_format = struct.Struct('<4B')
        self.size = 4

    def from_buffer(self, owner, buffer, offset, checks):
        b = self.struct_format.unpack_from(buffer, offset)
        if b[3] == 0:
            s = chr(b[2]) + chr(b[1]) + chr(b[0])
        else:
            s = chr(b[3]) + chr(b[2]) + chr(b[1]) + chr(b[0])

        setattr(owner, self.name, s)

    def to_buffer(self, owner, buffer, offset):
        s = getattr(owner, self.name)
        if len(s) == 4:
            b = (s[3] + s[2] + s[1] + s[0]).encode('ascii')
        else:
            b = (s[2] + s[1] + s[0]).encode('ascii') + b'\x00'
        return self.struct_format.pack_into(buffer, offset, b[0], b[1], b[2], b[3])

    def default_set(self, owner):
        setattr(owner, self.name, '')

    def content_validate(self, field_content, field_path):
        if (type(field_content) != str) or (len(field_content) != 4):
            raise Exception('%s is not a string with 4 characters' % (field_path))


class EmbeddedStructureField(Field):

    def __init__(self, name, struct_desc, since_version, till_version, ref_to):
        Field.__init__(self, name, since_version, till_version)
        self.struct_desc = struct_desc
        self.size = struct_desc.size
        self.ref_to = ref_to

    def from_buffer(self, owner, buffer, offset, checks):
        instance = self.struct_desc.instance(buffer, offset, checks)
        setattr(owner, self.name, instance)

    def to_buffer(self, owner, buffer, offset):
        instance = getattr(owner, self.name)
        instance_offset = offset
        for field in instance.struct_desc.fields.values():
            field.to_buffer(instance, buffer, instance_offset)
            instance_offset += field.size

    def default_set(self, owner):
        instance = self.struct_desc.instance()
        setattr(owner, self.name, instance)

    def content_validate(self, field_content, field_path):
        self.struct_desc.instance_validate(field_content, field_path)


class PrimitiveField(Field):
    ' Base class for IntField and FloatField '

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        Field.__init__(self, name, since_version, till_version)
        self.size = primitive_field_info[type_str]['size']
        self.struct_format = struct.Struct('<' + primitive_field_info[type_str]['format'])
        self.type_str = type_str
        self.default_value = default_value
        self.expected_value = expected_value

    def from_buffer(self, owner, buffer, offset, checks):
        value = self.struct_format.unpack_from(buffer, offset)[0]
        if self.expected_value is not None and value != self.expected_value:
            args = (self.name, owner.struct_desc.struct_name, owner.struct_desc.struct_version, self.expected_value, value)
            raise Exception('Expected that field {} of {}V{} always has the value {}, but it was {}'.format(*args))
        setattr(owner, self.name, value)

    def to_buffer(self, owner, buffer, offset):
        value = getattr(owner, self.name)
        self.struct_format.pack_into(buffer, offset, value)

    def default_set(self, owner):
        setattr(owner, self.name, self.default_value)


class IntField(PrimitiveField):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value, bit_mask_map):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)
        self.min_val = primitive_field_info[type_str]['min']
        self.max_val = primitive_field_info[type_str]['max']
        self.bit_mask_map = bit_mask_map

    def content_validate(self, field_content, field_path):
        if (type(field_content) != int):
            raise Exception('%s is not an int but a %s!' % (field_path, type(field_content)))
        if (field_content < self.min_val) or (field_content > self.max_val):
            raise Exception('%s has value %d which is not in range [%d, %d]' % (field_path, field_content, self.min_val, self.max_val))

    def bit_get(self, owner, bit_name):
        mask = self.bit_mask_map[bit_name]
        int_val = getattr(owner, self.name)
        return ((int_val & mask) != 0)

    def bit_set(self, owner, bit_name, value):
        mask = self.bit_mask_map[bit_name]
        int_val = getattr(owner, self.name)
        if value:
            setattr(owner, self.name, int_val | mask)
        else:
            if (int_val & mask) != 0:
                setattr(owner, self.name, int_val ^ mask)


class FloatField(PrimitiveField):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)

    def content_validate(self, field_content, field_path):
        if (type(field_content) != float):
            raise Exception('%s is not a float but a %s!' % (field_path, type(field_content)))


class Fixed8Field(PrimitiveField):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)

    def from_buffer(self, owner, buffer, offset, checks):
        int_val = self.struct_format.unpack_from(buffer, offset)[0]
        float_val = ((int_val / 255.0 * 2.0) - 1)

        if checks and self.expected_value is not None and float_val != self.expected_value:
            args = (self.name, owner.struct_desc.struct_name, owner.struct_desc.struct_version, self.expected_value, value)
            raise Exception('Expected that field {} of {}V{} always has the value {}, but it was {}'.format(*args))
        setattr(owner, self.name, float_val)

    def to_buffer(self, owner, buffer, offset):
        floatValue = getattr(owner, self.name)
        int_val = round((floatValue + 1) / 2.0 * 255.0)
        return self.struct_format.pack_into(buffer, offset, int_val)

    def content_validate(self, field_content, field_path):
        if (type(field_content) != float):
            raise Exception('%s is not a float but a %s!' % (field_path, type(field_content)))


class UnknownBytesField(Field):

    def __init__(self, name, size, since_version, till_version, default_value, expected_value):
        Field.__init__(self, name, since_version, till_version)
        self.size = size
        self.struct_format = struct.Struct('<%ss' % size)
        self.default_value = default_value
        self.expected_value = expected_value
        assert self.struct_format.size == self.size

    def from_buffer(self, owner, buffer, offset, checks):
        value = self.struct_format.unpack_from(buffer, offset)[0]
        if checks and self.expected_value is not None and value != self.expected_value:
            args = (self.name, owner.struct_desc.struct_name, owner.struct_desc.struct_version, self.expected_value, value)
            raise Exception('Expected that field {} of {}V{} always has the value {}, but it was {}'.format(*args))
        setattr(owner, self.name, value)

    def to_buffer(self, owner, buffer, offset):
        value = getattr(owner, self.name)
        return self.struct_format.pack_into(buffer, offset, value)

    def default_set(self, owner):
        setattr(owner, self.name, self.default_value)

    def content_validate(self, field_content, field_path):
        if (type(field_content) != bytes) or (len(field_content) != self.size):
            raise Exception('%s is not an bytes object of size %s' % (field_path, self.size))


class SectionList(list):
    def __init__(self, init_header=False):
        list.__init__(self, [])

        if init_header:
            section = Section(index_entry=None, struct_desc=structures['MD34'].get_version(11), references=[], content=[])
            md34 = section.content_add()
            md34.tag = 'MD34'
            self.append(section)

    def __getitem__(self, item):
        if type(item) == M3Structure:
            assert hasattr(item, 'index')
            return self[item.index] if item.index else []
        else:
            return super(SectionList, self).__getitem__(item)

    def __setitem__(self, item, val):
        assert type(val) == Section
        assert type(val.struct_desc) == M3StructureDescription
        return super(SectionList, self).__setitem__(item, val)

    @classmethod
    def from_index(cls, entry_desc, entry_buffers):
        self = cls()

        for entry_buffer in entry_buffers:
            index_entry = entry_desc.instance(entry_buffer)
            struct_desc = structures[index_entry.tag].get_version(index_entry.version, entry_desc.struct_version)
            section = Section(index_entry=index_entry, struct_desc=struct_desc, references=[], content=[])

            if section.struct_desc is None:
                format_args = index_entry.offset, index_entry.tag, index_entry.version, index_entry.repetitions
                stderr.write('ERROR: Unknown section at offset {} with tag={} version={} repetitions={} '.format(*format_args))

            self.append(section)

        return self

    def section_for_reference(self, structure, field, version=0, pos=-1):
        desc = structure.struct_desc
        ref = getattr(structure, field)
        ref_struct_name = desc.fields[field].ref_to
        ref_struct_desc = structures[ref_struct_name].get_version(version)

        section = Section(index_entry=None, struct_desc=ref_struct_desc, references=[ref], content=[])

        if type(pos) is int:
            if pos < 0:
                self.append(section)
            else:
                self.insert(pos, section)

        return section

    def resolve(self):
        aggregate_references = set()
        for ii, section in enumerate(self):
            for reference in section.references:
                assert reference not in aggregate_references  # reference must be unique to section
                aggregate_references.add(reference)
                reference.index = ii
                reference.entries = section.struct_desc.instances_count(section.content)

    def validate(self):
        for ii, section in enumerate(self):
            for instance in section:
                section.struct_desc.instance_validate(instance, section.struct_desc.struct_name)

    def to_index(self):
        header_section = self[0]
        header_desc = header_section.struct_desc
        header = header_section[0]

        buffer_offset = header_desc.size + 16
        for section in self[1:]:
            section.content_to_bytes()
            section.index_entry = structures['MDIndexEntry'].get_version(34).instance()
            section.index_entry.tag = section.struct_desc.struct_name
            section.index_entry.offset = buffer_offset
            section.index_entry.repetitions = section.struct_desc.instances_count(section)
            section.index_entry.version = section.struct_desc.struct_version
            buffer_offset += len(section.raw_bytes)

        header.index_offset = buffer_offset
        header.index_size = len(self)
        header_section.content_to_bytes()

        header_section.index_entry = structures['MDIndexEntry'].get_version(34).instance()
        header_section.index_entry.tag = header_desc.struct_name
        header_section.index_entry.offset = 0
        header_section.index_entry.repetitions = 1
        header_section.index_entry.version = header_desc.struct_version


class Section:
    'Has fields index_entry, struct_desc, content, references and sometimes raw_bytes'

    def __init__(self, index_entry: M3Structure, struct_desc: M3StructureDescription, references: list, content: list):
        self.index_entry = index_entry
        self.struct_desc = struct_desc
        self.references = references
        self.content = content

    def __str__(self):
        result = 'Section'
        if self.index_entry:
            result += ' {}'.format(self.index_entry)
        if self.struct_desc:
            result += ' {}V{}'.format(self.struct_desc.struct_name, self.struct_desc.struct_version)
        return result

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]

    def content_from_bytes(self, buffer, count=None, checks=True):
        assert type(self.struct_desc) == M3StructureDescription
        count = count if count is not None else len(buffer)
        self.content = self.struct_desc.instances(buffer=buffer, count=count, checks=checks)

    def content_add(self, instance=None):
        if instance is not None:
            if type(instance) in [str, bytes]:
                raise Exception('Type of instance is {}. Use content_from_bytes instead'.format(type(instance)))
        instance = instance if instance is not None else self.struct_desc.instance()
        self.content.append(instance)
        return instance

    def content_iter_add(self, instances=[]):
        return [self.content_add(instance) for instance in instances]

    def content_to_bytes(self):
        min_raw_bytes = self.struct_desc.instances_to_bytes(self.content)

        section_size = len(min_raw_bytes)
        incomplete_block_bytes = section_size % 16
        section_size += 16 - (section_size % incomplete_block_bytes) if incomplete_block_bytes != 0 else 0

        if len(min_raw_bytes) == section_size:
            self.raw_bytes = min_raw_bytes
        else:
            raw_bytes = bytearray(section_size)
            raw_bytes[0:len(min_raw_bytes)] = min_raw_bytes
            for ii in range(len(min_raw_bytes), section_size):
                raw_bytes[ii] = 0xaa
            self.raw_bytes = raw_bytes


def section_list_load(filename, checks=True):
    with open(filename, 'rb') as source:
        md_tag = source.read(4)[::-1].decode('ascii')
        source.seek(0)

        m3_header = structures[md_tag].get_version(11)
        header = m3_header.instance(source.read(m3_header.size), checks=checks)

        source.seek(header.index_offset)
        mdie = structures['MDIndexEntry'].get_version(int(md_tag[2:]))
        sections = SectionList.from_index(mdie, [source.read(mdie.size) for ii in range(header.index_size)])

        for section in sections:
            source.seek(section.index_entry.offset)
            buffer = source.read(section.index_entry.repetitions * section.struct_desc.size)
            section.content_from_bytes(buffer=buffer, count=section.index_entry.repetitions, checks=checks)

    return sections


def section_list_save(sections: SectionList, filename):
    with open(filename, 'w+b') as file_object:
        previous_section = None
        for section in sections:
            if section.index_entry.offset != file_object.tell():
                args = previous_section.index_entry, len(previous_section.raw_bytes), section.index_entry
                raise Exception('Section length problem: Section (index entry {}) has length {} and gets followed by section with index entry {}'.format(*args))
            file_object.write(section.raw_bytes)
            previous_section = section

        header = sections[0][0]

        if file_object.tell() != header.index_offset:
            raise Exception('Not at expected write position %s after writing sections, but %s' % (header.index_offset, file_object.tell()))

        for section in sections:
            index_entry_buffer = bytearray(section.index_entry.struct_desc.size)
            section.index_entry.to_buffer(index_entry_buffer, 0)
            file_object.write(index_entry_buffer)


def structures_from_tree():

    def parse_hex_str(hex_string):
        if not hex_string:
            return None
        hex_string = hex_string[2:]
        return bytes([int(hex_string[x:x + 2], 16) for x in range(0, len(hex_string), 2)])

    from os import path
    filename = path.join(path.dirname(__file__), 'structures.xml')
    root = ET.parse(filename).getroot()
    xml_structures = root.findall('structure')

    histories = {}

    for xml_structure in xml_structures:
        xml_structure_name = xml_structure.get('name')
        xml_versions = xml_structure.findall('versions')[0].findall('version')
        xml_fields = xml_structure.findall('fields')[0].findall('field')
        version_nums = set([int(xml_version.get('number')) for xml_version in xml_versions])

        version_to_size = {}
        for xml_version in xml_versions:
            num = int(xml_version.get('number'))
            if num not in version_to_size.keys():
                version_to_size[num] = int(xml_version.get('size'))

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

            if str_type == 'tag':
                field = TagField(str_name, since_version, till_version)

            elif str_type in primitive_field_info and 'int' in str_type:
                default_val = int(str_default_val, 0) if str_default_val else None
                expected_val = int(str_expected_val, 0) if str_expected_val else None
                if default_val is None:
                    default_val = expected_val or 0

                bitmasks = {}
                xml_bits = xml_field.findall('bits')
                if len(xml_bits):
                    bitmasks = {xml_bit.get('name'): int(xml_bit.get('mask'), 0) for xml_bit in xml_bits[0].findall('bit')}

                field = IntField(str_name, str_type, since_version, till_version, default_val, expected_val, bitmasks)

            elif str_type == 'float':
                default_val = float(str_default_val) if str_default_val else None
                expected_val = float(str_expected_val) if str_expected_val else None
                if default_val is None:
                    default_val = expected_val or 0.0
                field = FloatField(str_name, str_type, since_version, till_version, default_val, expected_val)

            elif str_type == 'fixed8':
                default_val = float(str_default_val) if str_default_val else None
                expected_val = float(str_expected_val) if str_expected_val else None
                if default_val is None:
                    default_val = expected_val or 0.0
                field = Fixed8Field(str_name, str_type, since_version, till_version, default_val, expected_val)
            elif str_type is None:
                size = int(str_size) if str_size else None
                default_val = parse_hex_str(str_default_val)
                expected_val = parse_hex_str(str_expected_val)
                if default_val is None:
                    default_val = expected_val or bytes(size)
                field = UnknownBytesField(str_name, size, since_version, till_version, default_val, expected_val)
            else:
                v_pos = str_type.rfind('V')
                if v_pos != -1:
                    field_struct_name = str_type[:v_pos]
                    field_struct_version = int(str_type[v_pos + 1:])
                else:
                    field_struct_name = str_type
                    field_struct_version = 0

                field_struct_history = histories.get(field_struct_name)
                if field_struct_history is None:
                    raise Exception('%s must be defined before %s' % (field_struct_name, xml_structure_name))
                field_struct_desc = field_struct_history.get_version(field_struct_version)
                field = EmbeddedStructureField(str_name, field_struct_desc, since_version, till_version, str_ref_to)

            field_versions = {}
            for ii in range(since_version or 0, (till_version or sorted(version_nums)[-1]) + 1):
                field_versions[ii] = field

            all_field_versions.append(field_versions)

        histories[xml_structure_name] = M3StructureHistory(xml_structure_name, version_to_size, all_field_versions)

    return histories


structures = structures_from_tree()
