"""The only hashing implementation (D9)."""
import hashlib
from . import canonical, material

GENESIS='0'*64


def file_sha256(data):
    return hashlib.sha256(data).hexdigest()


def document_id(document):
    return file_sha256(canonical.dumps(document))


def material_id(value):
    return document_id(material.normalize(value))


def sequence_id(sequence,topology):
    return file_sha256((sequence.upper()+'|'+str(topology)).encode('utf-8'))


def event_hash(event):
    body={k:v for k,v in event.items() if k!='hash'}
    return file_sha256(canonical.dumps(body)+body['prev'].encode('ascii'))


def run_id(created_at,random_value):
    return file_sha256((created_at+random_value).encode('utf-8'))[:16]
