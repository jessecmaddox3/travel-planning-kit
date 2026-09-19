import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from travel_kit.cli import main,SAMPLE
from travel_kit.demo import make_demo

class CliTests(unittest.TestCase):
    def test_every_renderer_runs_from_an_arbitrary_working_folder_and_preserves_outputs(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.chdir(folder):
            for kind in ['packing','plan','compare','table']:
                output=Path(folder)/(kind+'.html')
                with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main([kind,'--config',str(SAMPLE),'--output',str(output)]),0)
                    content=output.read_bytes();self.assertEqual(main([kind,'--config',str(SAMPLE),'--output',str(output)]),2)
                self.assertEqual(output.read_bytes(),content)
    def test_demo_has_no_network_and_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as folder,patch('socket.socket',side_effect=AssertionError('Demo must be offline')):
            output=Path(folder)/'demo';make_demo(output)
            self.assertEqual(len(list(output.glob('*.html'))),5)
            self.assertTrue((output/'LICENSE.txt').exists() and (output/'ASSETS.txt').exists())
            before=(output/'Start.html').read_bytes()
            with self.assertRaises(FileExistsError):make_demo(output)
            self.assertEqual((output/'Start.html').read_bytes(),before)

if __name__=='__main__':unittest.main()
