"""Explicit bounded reads and atomic writes, independent of the working directory."""
from pathlib import Path
import os
import tempfile
from .model import ValidationError
from .schema import loads_document


def read_document(path):
    path=Path(path)
    if path.stat().st_size>2_000_000:raise ValidationError('Choose a JSON document smaller than 2 MB.')
    return loads_document(path.read_text(encoding='utf-8'))


def write_file(path,content,overwrite=False):
    path=Path(path)
    if path.exists() and not overwrite:raise FileExistsError('Output already exists. Choose a new filename, or explicitly allow replacement.')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    temp=Path(name)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(content.encode('utf-8') if isinstance(content,str) else content);stream.flush();os.fsync(stream.fileno())
        if overwrite:os.replace(temp,path)
        else:
            # Creating a hard link is atomic and refuses even a late-arriving file.
            os.link(temp,path)
            temp.unlink()
    finally:
        temp.unlink(missing_ok=True)
