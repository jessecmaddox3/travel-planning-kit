from pathlib import Path
import tempfile,unittest
from travel_kit.files import write_file

class FileTests(unittest.TestCase):
 def test_existing_file_is_preserved_unless_replacement_is_explicit(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'plan.html';write_file(p,'original')
   with self.assertRaises(FileExistsError):write_file(p,'replacement')
   self.assertEqual(p.read_text(),'original');write_file(p,'replacement',overwrite=True);self.assertEqual(p.read_text(),'replacement');self.assertEqual(list(Path(directory).iterdir()),[p])
 def test_non_ascii_paths_and_binary_content(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory)/'Trip notes'/'plan-été.html';write_file(p,b'\x00\xff');self.assertEqual(p.read_bytes(),b'\x00\xff')
