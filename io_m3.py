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

import xml.etree.ElementTree as ET
from sys import stderr
import struct
import copy
import sys


class SectionList(list):
    def __init__(self, sections=None):
        list.__init__(self, sections or [])

    def __getitem__(self, item):
        if type(item) == M3Structure:
            assert hasattr(item, 'index')
            return self[item.index] if item.index else []
        else:
            return super(SectionList, self).__getitem__(item)

    def __setitem__(self, item, val):
        assert type(val) == Section
        return super(SectionList, self).__setitem__(item, val)


def to_valid_section_size(size):
    incomplete_block_bytes = size % 16
    return size + (16 - (size % incomplete_block_bytes) if incomplete_block_bytes != 0 else 0)


class Section:
    """Has fields index_entry, struct_desc, content, buffer_size, raw_bytes"""

    def __init__(self):
        self.content = []
        self.index_entry = None
        self.struct_desc = None
        self.buffer_size = 0

    def __str__(self):
        result = 'Section'
        if self.index_entry:
            result += ' {}'.format(self.index_entry)
        if self.struct_desc:
            result += ' {}V{}'.format(self.struct_desc.structureName, self.struct_desc.structureVersion)
        return result

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)

    def __getitem__(self, item):
        return self.content[item]

    @classmethod
    def from_index_bytes(cls, buffer, header_version, checks=True):
        self = cls()
        index_entry_struct = structures['MDIndexEntry'].get_version(header_version)
        self.index_entry = index_entry_struct.createInstance(buffer, checks=checks)
        self.struct_desc = structures[self.index_entry.tag].get_version(self.index_entry.version)
        self.buffer_size = self.index_entry.repetitions * self.struct_desc.size

        return self

    @classmethod
    def for_reference(cls, section_list, structure, field, version=0):
        getattr(structure, field).index = len(section_list)
        self = cls()
        section_list.append(self)
        desc = structure.struct_desc
        history = desc.history
        ref_struct = history.allFields[field][desc.structureVersion].ref_to
        self.struct_desc = structures[ref_struct].get_version(version)

        return self

    def content_add(self, instance=None):
        instance = instance if instance else self.struct_desc.createInstance()
        self.content.append(instance)
        return instance

    def content_iter_add(self, instances=[]):
        if len(instances):
            self.content.extend(instances)
        return instances

    def bytes_from_buffer(self, buffer):
        self.raw_bytes = buffer

    def bytes_from_content(self):
        min_raw_bytes = self.struct_desc.instancesToBytes(self.content)
        section_size = to_valid_section_size(len(min_raw_bytes))
        if len(min_raw_bytes) == section_suze:
            self.raw_bytes = min_raw_bytes
        else:
            raw_bytes = bytearray(section_size)
            raw_bytes[0:len(min_raw_bytes)] = min_raw_bytes
            for ii in range(len(min_raw_bytes), section_size):
                raw_bytes[ii] = 0xaa
            self.raw_bytes = raw_bytes

    def content_from_bytes(self, checks):
        self.content = self.struct_desc.createInstances(buffer=self.raw_bytes, count=self.index_entry.repetitions, checks=checks)

    def content_from_instances(self, instances, tag=''):
        self.content = instances


primitiveFieldTypeSizes = {"uint32": 4, "int32": 4, "uint16": 2, "int16": 2, "uint8": 1, "int8": 1, "float": 4, "tag": 4, "fixed8": 1}
primitiveFieldTypeFormats = {"uint32": "I", "int32": "i", "uint16": "H", "int16": "h", "uint8": "B", "int8": "b", "float": "f", "tag": "4s", "fixed8": "B"}
int_types = {"uint32", "int32", "uint16", "int16", "uint8", "int8"}
structureNamesOfPrimitiveTypes = {"CHAR", "U8__", "REAL", "I16_", "U16_", "I32_", "U32_", "FLAG"}


class M3StructureHistory:
    "Describes the history of a structure with a specific name"

    def __init__(self, name, versionToSizeMap, allFields):
        self.name = name
        self.versionToSizeMap = versionToSizeMap
        self.allFields = allFields
        self.versionToStructureDescriptionMap = {}
        self.isPrimitive = self.name in structureNamesOfPrimitiveTypes
        # Create all to check sizes:
        for version in versionToSizeMap:
            self.get_version(version)

    def createStructureDescription(self, version, usedFields, specifiedSize, fmagic):
        finalFields = []
        # dirty patching of all structures to make MD33 models work
        # - they use `SmallReference` instead of `Reference` across all structures
        if fmagic == 'MD33':
            for field in usedFields:
                if isinstance(field, ReferenceField):
                    field = copy.copy(field)
                    if field.referenceStructureDescription.structureName == 'Reference':
                        newStructureHistory = structures['SmallReference']
                        newDescription = newStructureHistory.get_version(0, fmagic)
                        field.referenceStructureDescription = newDescription
                        field.size = newDescription.size
                elif self.name == 'MODL' and field.name == 'tightHitTest':
                    field = copy.copy(field)
                    newStructureHistory = structures[field.struct_desc.structureName]
                    newDescription = newStructureHistory.get_version(1, fmagic)
                    field.struct_desc = newDescription
                    field.size = newDescription.size
                finalFields.append(field)
        else:
            finalFields = usedFields
        structure = M3StructureDescription(self.name, version, finalFields, specifiedSize, self, fmagic != 'MD33')
        return structure

    def get_version(self, version, fmagic='MD34', force=False):
        structure = self.versionToStructureDescriptionMap.get(fmagic + '_' + str(version))
        if structure is None:
            used_fields = []
            for field_versions in self.allFields.values():
                field = field_versions.get(version)
                if field:
                    used_fields.append(field)
            specifiedSize = self.versionToSizeMap.get(version)
            if not force and specifiedSize is None:
                return None
            structure = self.createStructureDescription(version, used_fields, specifiedSize, fmagic)
            self.versionToStructureDescriptionMap[fmagic + '_' + str(version)] = structure
        return structure

    def getNewestVersion(self):
        newestVersion = None
        for version in self.versionToSizeMap.keys():
            if newestVersion is None or version > newestVersion:
                newestVersion = version
        return self.get_version(newestVersion)

    def createEmptyArray(self):
        if self.name == "CHAR":
            return None  # even no terminating character
        elif self.name == "U8__":
            return bytearray(0)
        else:
            return []

        def __str__():
            return self.name


class M3StructureDescription:

    def __init__(self, structureName, structureVersion, fields, specifiedSize, history, validateSize=True):
        self.structureName = structureName
        self.structureVersion = structureVersion
        self.fields = fields
        self.isPrimitive = self.structureName in structureNamesOfPrimitiveTypes
        self.history = history

        calculatedSize = 0
        for field in fields:
            calculatedSize += field.size
        self.size = calculatedSize

        # Validate the specified size:
        if validateSize and calculatedSize != specifiedSize:
            self.dumpOffsets()
            raise Exception("Size mismatch: %s in version %d has been specified to have size %d, but the calculated size was %d" % (structureName, structureVersion, specifiedSize, calculatedSize))

        nameToFieldMap = {}
        for field in fields:
            if field.name in nameToFieldMap:
                raise Exception("%s contains in version %s multiple fields with the name %s" % (structureName, structureVersion, field.name))
            nameToFieldMap[field.name] = field
        self.nameToFieldMap = nameToFieldMap

    def createInstance(self, buffer=None, offset=0, checks=True):
        return M3Structure(self, buffer, offset, checks)

    def createInstances(self, buffer, count, checks=True):
        if self.isPrimitive:
            if self.structureName == "CHAR":
                return buffer[:count - 1].decode("ASCII", "replace")
            elif self.structureName == "U8__":
                return bytearray(buffer[:count])
            else:
                structFormat = self.fields[0].structFormat
                list = []
                for offset in range(0, count * self.size, self.size):
                    bytesOfOneEntry = buffer[offset:(offset + self.size)]
                    intValue = structFormat.unpack(bytesOfOneEntry)[0]
                    list.append(intValue)
                return list
        else:
            list = []
            instanceOffset = 0
            for i in range(count):
                list.append(self.createInstance(buffer=buffer, offset=instanceOffset, checks=checks))
                instanceOffset += self.size
            return list

    def dumpOffsets(self):
        offset = 0
        stderr.write("Offsets of %s in version %d:\n" % (self.structureName, self.structureVersion))
        for field in self.fields:
            stderr.write("%s: %s\n" % (offset, field.name))
            offset += field.size

    def countInstances(self, instances):
        if self.structureName == "CHAR":
            if instances is None:
                return 0
            return len(instances) + 1  # +1 terminating null character
        elif hasattr(instances, "__len__"):  # either a list or an array of bytes
            return len(instances)
        else:
            raise Exception("Can't measure the length of %s which is a %s" % (instances, self.structureName))

    def validateInstance(self, instance, instanceName):
        for field in self.fields:
            try:
                fieldContent = getattr(instance, field.name)
            except AttributeError:
                raise Exception("%s does not have a field called %s" % (instanceName, field.name))
                raise
            field.validateContent(fieldContent, instanceName + "." + field.name)

    def hasField(self, fieldName):
        return fieldName in self.nameToFieldMap

    def instancesToBytes(self, instances):
        if self.structureName == "CHAR":
            if type(instances) != str:
                raise Exception("Expected a string but it was a %s" % type(instances))
            return instances.encode("ASCII") + b'\x00'
        elif self.structureName == "U8__":
            if type(instances) != bytes and type(instances) != bytearray:
                raise Exception("Expected a byte array but it was a %s" % type(instances))
            return instances
        else:
            raw_bytes = bytearray(self.size * len(instances))
            offset = 0

            if self.isPrimitive:
                structFormat = self.fields[0].structFormat
                for value in instances:
                    structFormat.pack_into(raw_bytes, offset, value)
                    offset += self.size
            else:
                for value in instances:
                    value.writeToBuffer(raw_bytes, offset)
                    offset += self.size
            return raw_bytes

    def countBytesRequiredForInstances(self, instances):
        if self.structureName == "CHAR":
            return len(instances) + 1  # +1 for terminating character
        return self.size * self.countInstances(instances)


class M3Structure:

    def __init__(self, struct_desc: M3StructureDescription, buffer=None, offset=0, checks=True):
        self.struct_desc = struct_desc

        if buffer is not None:
            self.readFromBuffer(buffer, offset, checks)
        else:
            for field in self.struct_desc.fields:
                field.setToDefault(self)

    def introduceIndexReferences(self, indexMaker):
        for field in self.struct_desc.fields:
            field.introduceIndexReferences(self, indexMaker)

    def readFromBuffer(self, buffer, offset, checks):
        fieldOffset = offset
        for field in self.struct_desc.fields:
            try:
                field.readFromBuffer(self, buffer, fieldOffset, checks)
            except struct.error as e:
                raise Exception('failed to unpack %sV%s %s' % (self.struct_desc.structureName, self.struct_desc.structureVersion, field.name), e)
            fieldOffset += field.size
        assert fieldOffset - offset == self.struct_desc.size

    def writeToBuffer(self, buffer, offset):
        fieldOffset = offset
        for field in self.struct_desc.fields:
            field.writeToBuffer(self, buffer, fieldOffset)
            fieldOffset += field.size
        assert fieldOffset - offset == self.struct_desc.size

    def __str__(self):
        fieldValueMap = {}
        for field in self.struct_desc.fields:
            fieldValueMap[field.name] = str(getattr(self, field.name))
        return "%sV%s: {%s}" % (self.struct_desc.structureName, self.struct_desc.structureVersion, fieldValueMap)

    def getNamedBit(self, fieldName, bitName):
        field = self.struct_desc.nameToFieldMap[fieldName]
        return field.getNamedBit(self, bitName)

    def setNamedBit(self, fieldName, bitName, value):
        field = self.struct_desc.nameToFieldMap[fieldName]
        return field.setNamedBit(self, bitName, value)

    def getBitNameMaskPairs(self, fieldName):
        field = self.struct_desc.nameToFieldMap[fieldName]
        return field.getBitNameMaskPairs()


class Field:
    def __init__(self, name, since_version, till_version):
        self.name = name
        self.since_version = since_version
        self.till_version = till_version

    def introduceIndexReferences(self, owner, indexMaker):
        pass


class TagField(Field):

    def __init__(self, name, since_version, till_version):
        Field.__init__(self, name, since_version, till_version)
        self.structFormat = struct.Struct("<4B")
        self.size = 4

    def readFromBuffer(self, owner, buffer, offset, checks):
        b = self.structFormat.unpack_from(buffer, offset)
        if b[3] == 0:
            s = chr(b[2]) + chr(b[1]) + chr(b[0])
        else:
            s = chr(b[3]) + chr(b[2]) + chr(b[1]) + chr(b[0])

        setattr(owner, self.name, s)

    def writeToBuffer(self, owner, buffer, offset):
        s = getattr(owner, self.name)
        if len(s) == 4:
            b = (s[3] + s[2] + s[1] + s[0]).encode("ascii")
        else:
            b = (s[2] + s[1] + s[0]).encode("ascii") + b"\x00"
        return self.structFormat.pack_into(buffer, offset, b[0], b[1], b[2], b[3])

    def setToDefault(self, owner):
        pass

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != str) or (len(fieldContent) != 4):
            raise Exception("%s is not a string with 4 characters" % (fieldPath))


class ReferenceField(Field):
    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        Field.__init__(self, name, since_version, till_version)
        self.referenceStructureDescription = referenceStructureDescription
        self.historyOfReferencedStructures = historyOfReferencedStructures
        self.size = referenceStructureDescription.size

    def introduceIndexReferences(self, owner, indexMaker):
        referencedObjects = getattr(owner, self.name)
        struct_desc = self.getListContentStructureDefinition(referencedObjects, "while adding index ref")

        indexReference = indexMaker.getIndexReferenceTo(referencedObjects, self.referenceStructureDescription, struct_desc)
        isPrimitive = self.historyOfReferencedStructures is not None and self.historyOfReferencedStructures.isPrimitive
        if not isPrimitive:
            for referencedObject in referencedObjects:
                referencedObject.introduceIndexReferences(indexMaker)
        setattr(owner, self.name, indexReference)

    def getListContentStructureDefinition(self, li, contextString):

        if self.historyOfReferencedStructures is None:
            if len(li) == 0:
                return None
            else:
                variable = "%(fieldName)s" % {"fieldName": self.name}
                raise Exception("%s: %s must be an empty list but wasn't" % (contextString, variable))
        if self.historyOfReferencedStructures.isPrimitive:
            return self.historyOfReferencedStructures.get_version(0)

        if type(li) != list:
            raise Exception("%s: Expected a list, but was a %s" % (contextString, type(li)))
        if len(li) == 0:
            return None

        firstElement = li[0]
        contentClass = type(firstElement)
        if contentClass != M3Structure:
            raise Exception("%s: Expected a list to contain an M3Structure object and not a %s" % (contextString, contentClass))
        # Optional: Enable check:
        # if not contentClass.tagName == tagName:
        #     raise Exception("Expected a list to contain a object of a class with tagName %s, but it contained a object of class %s with tagName %s" % (tagName, contentClass, contentClass.tagName))
        return firstElement.struct_desc

    def readFromBuffer(self, owner, buffer, offset, checks):
        referenceObject = self.referenceStructureDescription.createInstance(buffer, offset, checks)
        setattr(owner, self.name, referenceObject)

    def writeToBuffer(self, owner, buffer, offset):
        referenceObject = getattr(owner, self.name)
        referenceObject.writeToBuffer(buffer, offset)

    def setToDefault(self, owner):

        if self.historyOfReferencedStructures is not None:
            default_value = self.historyOfReferencedStructures.createEmptyArray()
        else:
            default_value = []
        setattr(owner, self.name, default_value)

    # The method validateContent is defined in subclasses


class CharReferenceField(ReferenceField):

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)

    def validateContent(self, fieldContent, fieldPath):
        if (fieldContent is not None) and (type(fieldContent) != str):
            raise Exception("%s is not a string but a %s" % (fieldPath, type(fieldContent)))


class ByteReferenceField(ReferenceField):

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != bytearray):
            raise Exception("%s is not a bytearray but a %s" % (fieldPath, type(fieldContent)))


class RealReferenceField(ReferenceField):

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != list):
            raise Exception("%s is not a list of float" % (fieldPath))
        for itemIndex, item in enumerate(fieldContent):
            if type(item) != float:
                itemPath = "%s[%d]" % (fieldPath, itemIndex)
                raise Exception("%s is not an float" % (itemPath))


class IntReferenceField(ReferenceField):
    intRefToMinValue = {"I16_": (-(1 << 15)), "U16_": 0, "I32_": (-(1 << 31)), "U32_": 0, "FLAG": 0}
    intRefToMaxValue = {"I16_": ((1 << 15) - 1), "U16_": ((1 << 16) - 1), "I32_": ((1 << 31) - 1), "U32_": ((1 << 32) - 1), "FLAG": ((1 << 32) - 1)}

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)
        self.minValue = IntReferenceField.intRefToMinValue[historyOfReferencedStructures.name]
        self.maxValue = IntReferenceField.intRefToMaxValue[historyOfReferencedStructures.name]

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != list):
            raise Exception("%s is not a list of integers" % (fieldPath))
        for itemIndex, item in enumerate(fieldContent):
            itemPath = "%s[%d]" % (fieldPath, itemIndex)
            if type(item) != int:
                raise Exception("%s is not an integer" % (itemPath))
            if (item < self.minValue) or (item > self.maxValue):
                raise Exception("%s has value %d which is not in range [%s, %s]" % (itemPath, item, self.minValue, self.maxValue))


class StructureReferenceField(ReferenceField):

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != list):
            raise Exception("%s is not a list, but a %s" % (fieldPath, type(fieldContent)))
        if len(fieldContent) > 0:
            struct_desc = self.getListContentStructureDefinition(fieldContent, fieldPath)
            if struct_desc.history != self.historyOfReferencedStructures:
                raise Exception("Expected that %s is a list of %s and not %s" % (fieldPath, self.historyOfReferencedStructures.name, struct_desc.history.name))
            for itemIndex, item in enumerate(fieldContent):
                struct_desc.validateInstance(item, "%s[%d]" % (fieldPath, itemIndex))


class UnknownReferenceField(ReferenceField):

    def __init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version):
        ReferenceField.__init__(self, name, referenceStructureDescription, historyOfReferencedStructures, since_version, till_version)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != list) or (len(fieldContent) != 0):
            raise Exception("%s is not an empty list" % (fieldPath))


class EmbeddedStructureField(Field):

    def __init__(self, name, struct_desc, since_version, till_version, ref_to):
        Field.__init__(self, name, since_version, till_version)
        self.struct_desc = struct_desc
        self.size = struct_desc.size
        self.ref_to = ref_to

    def introduceIndexReferences(self, owner, indexMaker):
        embeddedStructure = getattr(owner, self.name)
        embeddedStructure.introduceIndexReferences(indexMaker)

    def toBytes(self, owner):
        embeddedStructure = getattr(owner, self.name)
        return embeddedStructure.toBytes()

    def readFromBuffer(self, owner, buffer, offset, checks):

        referenceObject = self.struct_desc.createInstance(buffer, offset, checks)
        setattr(owner, self.name, referenceObject)

    def writeToBuffer(self, owner, buffer, offset):
        embeddedStructure = getattr(owner, self.name)
        embeddedStructure.writeToBuffer(buffer, offset)

    def setToDefault(self, owner):
        v = self.struct_desc.createInstance()
        setattr(owner, self.name, v)

    def validateContent(self, fieldContent, fieldPath):
        self.struct_desc.validateInstance(fieldContent, fieldPath)


class PrimitiveField(Field):
    """ Base class for IntField and FloatField """

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        Field.__init__(self, name, since_version, till_version)
        self.size = primitiveFieldTypeSizes[type_str]
        self.structFormat = struct.Struct("<" + primitiveFieldTypeFormats[type_str])
        self.type_str = type_str
        self.default_value = default_value
        self.expected_value = expected_value

    def readFromBuffer(self, owner, buffer, offset, checks):
        value = self.structFormat.unpack_from(buffer, offset)[0]
        if self.expected_value is not None and value != self.expected_value:
            structureName = owner.struct_desc.structureName
            structureVersion = owner.struct_desc.structureVersion
            raise Exception("Expected that field %s of %s (V. %d) has always the value %s, but it was %s" % (self.name, structureName, structureVersion, self.expected_value, value))
        setattr(owner, self.name, value)

    def writeToBuffer(self, owner, buffer, offset):
        value = getattr(owner, self.name)
        return self.structFormat.pack_into(buffer, offset, value)

    def setToDefault(self, owner):
        setattr(owner, self.name, self.default_value)


class IntField(PrimitiveField):
    intTypeToMinValue = {"int16": (-(1 << 15)), "uint16": 0, "int32": (-(1 << 31)), "uint32": 0, "int8": -(1 << 7), "uint8": 0}
    intTypeToMaxValue = {"int16": ((1 << 15) - 1), "uint16": ((1 << 16) - 1), "int32": ((1 << 31) - 1), "uint32": ((1 << 32) - 1), "int8": ((1 << 7) - 1), "uint8": ((1 << 8) - 1)}

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value, bitMaskMap):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)
        self.minValue = IntField.intTypeToMinValue[type_str]
        self.maxValue = IntField.intTypeToMaxValue[type_str]
        self.bitMaskMap = bitMaskMap

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != int):
            raise Exception("%s is not an int but a %s!" % (fieldPath, type(fieldContent)))
        if (fieldContent < self.minValue) or (fieldContent > self.maxValue):
            raise Exception("%s has value %d which is not in range [%d, %d]" % (fieldPath, fieldContent, self.minValue, self.maxValue))

    def getNamedBit(self, owner, bitName):
        mask = self.bitMaskMap[bitName]
        intValue = getattr(owner, self.name)
        return ((intValue & mask) != 0)

    def setNamedBit(self, owner, bitName, value):
        mask = self.bitMaskMap[bitName]
        intValue = getattr(owner, self.name)
        if value:
            setattr(owner, self.name, intValue | mask)
        else:
            if (intValue & mask) != 0:
                setattr(owner, self.name, intValue ^ mask)

    def getBitNameMaskPairs(self):
        return self.bitMaskMap.items()


class FloatField(PrimitiveField):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != float):
            raise Exception("%s is not a float but a %s!" % (fieldPath, type(fieldContent)))


class Fixed8Field(PrimitiveField):

    def __init__(self, name, type_str, since_version, till_version, default_value, expected_value):
        PrimitiveField.__init__(self, name, type_str, since_version, till_version, default_value, expected_value)

    def readFromBuffer(self, owner, buffer, offset, checks):
        intValue = self.structFormat.unpack_from(buffer, offset)[0]
        floatValue = ((intValue / 255.0 * 2.0) - 1)

        if checks and self.expected_value is not None and floatValue != self.expected_value:
            structureName = owner.struct_desc.structureName
            structureVersion = owner.struct_desc.structureVersion
            raise Exception("Expected that field %s of %s (V. %d) has always the value %s, but it was %s" % (self.name, structureName, structureVersion, self.expected_value, intValue))
        setattr(owner, self.name, floatValue)

    def writeToBuffer(self, owner, buffer, offset):
        floatValue = getattr(owner, self.name)
        intValue = round((floatValue + 1) / 2.0 * 255.0)
        return self.structFormat.pack_into(buffer, offset, intValue)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != float):
            raise Exception("%s is not a float but a %s!" % (fieldPath, type(fieldContent)))


class UnknownBytesField(Field):

    def __init__(self, name, size, since_version, till_version, default_value, expected_value):
        Field.__init__(self, name, since_version, till_version)
        self.size = size
        self.structFormat = struct.Struct("<%ss" % size)
        self.default_value = default_value
        self.expected_value = expected_value
        assert self.structFormat.size == self.size

    def readFromBuffer(self, owner, buffer, offset, checks):
        value = self.structFormat.unpack_from(buffer, offset)[0]
        if checks and self.expected_value is not None and value != self.expected_value:
            raise Exception("Expected that %sV%s.%s has always the value %s, but it was %s" % (owner.struct_desc.structureName, owner.struct_desc.structureVersion, self.name, self.expected_value, value))

        setattr(owner, self.name, value)

    def writeToBuffer(self, owner, buffer, offset):
        value = getattr(owner, self.name)
        return self.structFormat.pack_into(buffer, offset, value)

    def setToDefault(self, owner):
        setattr(owner, self.name, self.default_value)

    def validateContent(self, fieldContent, fieldPath):
        if (type(fieldContent) != bytes) or (len(fieldContent) != self.size):
            raise Exception("%s is not an bytes object of size %s" % (fieldPath, self.size))


def load_sections(filename, checks=True):
    source = open(filename, "rb")
    try:
        fmagic = source.read(4)[::-1].decode('ascii')
        source.seek(0)

        m3Header = structures[fmagic].get_version(11)
        headerBytes = source.read(m3Header.size)
        header = m3Header.createInstance(headerBytes, checks=checks)

        source.seek(header.index_offset)
        mdie = structures["MDIndexEntry"].get_version(fmagic[2:])
        sections = [Section.from_index_bytes(source.read(mdie.size), fmagic[2:], checks) for ii in range(header.index_size)]
        offsets = [section.index_entry.offset for section in sections]
        offsets.sort()

        unknown_sections = set()
        for section in sections:
            source.seek(section.index_entry.offset)
            section.bytes_from_buffer(source.read(section.buffer_size))

            if section.struct_desc is not None:
                section.content_from_bytes(checks)
            else:
                guessed_bytes = 0
                for i in range(1, 16):
                    if section.raw_bytes[len(section.raw_bytes) - i] == 0xaa:
                        guessed_bytes += 1
                    else:
                        break
                guessedBytesPerEntry = float(len(section.raw_bytes) - guessed_bytes) / section.index_entry.repetitions
                message = "ERROR: Unknown section at offset %s with tag=%s version=%s repetitions=%s sectionLengthInBytes=%s guessed_bytes=%s guessedBytesPerEntry=%s\n" % (index_entry.offset, index_entry.tag, index_entry.version, index_entry.repetitions, len(section.raw_bytes), guessed_bytes, guessedBytesPerEntry)
                stderr.write(message)
                if sys.stderr.isatty():
                    for entryNum in range(section.index_entry.repetitions):
                        stderr.write('Entry %d\n' % entryNum)
                        offset = 0
                        while offset < int(guessedBytesPerEntry):
                            val_u32 = struct.unpack_from('<I', section.raw_bytes, int(guessedBytesPerEntry) * entryNum + offset)[0]
                            val_float = struct.unpack_from('<f', section.raw_bytes, int(guessedBytesPerEntry) * entryNum + offset)[0]
                            stderr.write('%sV%d @%02d -> %04X:%04d = 0x%08X  %15d  %20.5f\n' % (
                                section.index_entry.tag,
                                section.index_entry.version,
                                entryNum,
                                offset,
                                offset,
                                val_u32,
                                val_u32,
                                val_float,
                            ))
                            offset += 4
                unknown_sections.add("%sV%s" % (section.index_entry.tag, section.index_entry.version))
        if len(unknown_sections) != 0:
            raise Exception("There were %s unknown sections: %s (see console log for more details)" % (len(unknown_sections), unknown_sections))
    finally:
        source.close()
    return SectionList(sections)


class IndexReferenceSourceAndSectionListMaker:
    """ Creates a list of sections which are needed to store the objects for which index references are requested"""
    def __init__(self):
        self.objectsIdToIndexReferenceMap = {}
        self.offset = 0
        self.nextFreeIndexPosition = 0
        self.sections = []
        self.MD34IndexEntry = structures["MDIndexEntry"].get_version(34)

    def getIndexReferenceTo(self, objectsToSave, referenceStructureDescription, struct_desc):
        if id(objectsToSave) in self.objectsIdToIndexReferenceMap.keys():
            return self.objectsIdToIndexReferenceMap[id(objectsToSave)]

        if struct_desc is None:
            repetitions = 0
        else:
            repetitions = struct_desc.countInstances(objectsToSave)

        indexReference = referenceStructureDescription.createInstance()
        if repetitions > 0:
            indexReference.entries = repetitions
            indexReference.index = self.nextFreeIndexPosition

        if (repetitions > 0):
            index_entry = self.MD34IndexEntry.createInstance()
            index_entry.tag = struct_desc.structureName
            index_entry.offset = self.offset
            index_entry.repetitions = repetitions
            index_entry.version = struct_desc.structureVersion

            section = Section()
            section.index_entry = index_entry
            section.content = objectsToSave
            section.struct_desc = struct_desc
            self.sections.append(section)
            self.objectsIdToIndexReferenceMap[id(objectsToSave)] = indexReference
            totalBytes = section.bytesRequiredForContent()
            totalBytes = to_valid_section_size(totalBytes)
            self.offset += totalBytes
            self.nextFreeIndexPosition += 1
        return indexReference


def modelToSections(model):
    MD34V11 = structures["MD34"].get_version(11)
    header = MD34V11.createInstance()
    header.tag = "MD34"
    header.model = [model]
    ReferenceV0 = structures["Reference"].get_version(0)
    indexMaker = IndexReferenceSourceAndSectionListMaker()
    indexMaker.getIndexReferenceTo([header], ReferenceV0, MD34V11)
    header.introduceIndexReferences(indexMaker)
    sections = indexMaker.sections
    header.index_offset = indexMaker.offset
    header.index_size = len(sections)

    # WIP
    return sections


def saveSections(sections, filename):
    fileObject = open(filename, "w+b")
    try:
        previous_section = None
        for section in sections:
            if section.index_entry.offset != fileObject.tell():
                raise Exception("Section length problem: Section with index entry %(previousIndexEntry)s has length %(previousLength)s and gets followed by section with index entry %(currentIndexEntry)s" % {"previousIndexEntry": previous_section.index_entry, "previousLength": len(previous_section.raw_bytes), "currentIndexEntry": section.index_entry})
            fileObject.write(section.raw_bytes)
            previous_section = section
        header = sections[0].content[0]
        if fileObject.tell() != header.index_offset:
            raise Exception("Not at expected write position %s after writing sections, but %s" % (header.index_offset, fileObject.tell()))
        for section in sections:
            index_entryBytesBuffer = bytearray(section.index_entry.struct_desc.size)
            section.index_entry.writeToBuffer(index_entryBytesBuffer, 0)
            fileObject.write(index_entryBytesBuffer)
    finally:
        fileObject.close()


def saveAndInvalidateModel(model, filename):
    '''Do not use the model object after calling this method since it gets modified'''
    model.struct_desc.validateInstance(model, "model")
    sections = modelToSections(model)
    saveSections(sections, filename)


def parse_hex_str(hex_string):
    if not hex_string:
        return None
    hex_string = hex_string[2:]
    return bytes([int(hex_string[x:x + 2], 16) for x in range(0, len(hex_string), 2)])


def structures_from_tree():
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

        field_versions = {xml_field.get('name'): {} for xml_field in xml_fields}
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

            elif str_type in int_types:
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

            for ii in range(since_version or 0, (till_version or sorted(version_nums)[-1]) + 1):
                field_versions[str_name][ii] = field

        histories[xml_structure_name] = M3StructureHistory(xml_structure_name, version_to_size, field_versions)

    return histories


structures = structures_from_tree()
