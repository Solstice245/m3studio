"""Stage and send a model preview to an open SC2 Editor on Windows."""

import mmap
from pathlib import Path
import struct
import uuid
import xml.etree.ElementTree as ET


MAPPING_NAME = 'StarCraft II Editor File'
MAPPING_SIZE = 512


def write_cutscene(path, models, *, append=False):
    def guid():
        return str(uuid.uuid4().int & ((1 << 64) - 1))

    path = Path(path)
    if append and path.exists():
        root = ET.parse(path).getroot()
    else:
        root = ET.Element('CutsceneState', cutsceneVersion='1.200000')

    for model_path, model_name, animation in models:
        for actor in list(root.findall('CCutsceneNodeActor')):
            if actor.get('name') == model_name:
                root.remove(actor)

        actor = ET.SubElement(
            root, 'CCutsceneNodeActor', guid=guid(), name=model_name,
            position='0.0 ,0.0 ,0.0', modelPath=str(model_path),
            fromArchive='0', teamColorDiffuse='0.705800,0.078300,0.117600,1.000000',
            teamColorEmissive='0.545100,0.062700,0.086100,1.000000',
        )
        ET.SubElement(actor, 'CCutsceneElementObject', guid=guid(), duration='10000', lockedToEnd='1')
        if animation:
            layer = ET.SubElement(actor, 'CCutsceneNodeAnimLayer', guid=guid(), name='Animation Layer')
            ET.SubElement(
                layer, 'CCutsceneElementAnim', guid=guid(), duration='10000',
                lockedToEnd='1', anim=animation, originalDuration='10000',
            )

    path.write_bytes(b'\xef\xbb\xbf' + ET.tostring(root, encoding='utf-8', xml_declaration=True))

def send_preview(cutscene_path, *, add_to_scene=False):
    filename = str(Path(cutscene_path).resolve(strict=True)).encode('utf-8')
    if len(filename) > 259:
        raise ValueError('Preview cutscene path exceeds 259 UTF-8 bytes.')

    mode = 3 if add_to_scene else 2
    packet = struct.pack('<BI', 0x33, mode) + filename + b'\0\0' + struct.pack('<I', 0)
    mapping = mmap.mmap(-1, MAPPING_SIZE, tagname=MAPPING_NAME, access=mmap.ACCESS_WRITE)
    try:
        mapping[:len(packet)] = packet
    except Exception:
        mapping.close()
        raise
    return mapping
