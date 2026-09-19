# Setup and everyday use

> **TL;DR:** The example HTML files open without installing anything. Editing your own trip needs Python 3.11+, the full source folder, and a web browser. There are no extra runtime packages.

## If the launcher does not open

Install a current stable Python from [the official download page](https://www.python.org/downloads/), then try again. The launcher explains if Python is missing or too old. The kit needs the actual files from the ZIP extracted into a folder; it cannot run inside Windows' ZIP preview.

On a Mac, open Terminal from Applications → Utilities. Type `cd `, including the space, drag the unzipped kit folder onto the Terminal window, and press Return. Then run:

```sh
python3 -m travel_kit start
```

On Windows, open the unzipped kit folder in File Explorer, click the address bar, type `cmd`, and press Enter. In the window that opens, run:

```bat
py -m travel_kit start
```

If `py` is unavailable, try `python -m travel_kit start`. If neither works, finish the [official Windows Python setup](https://docs.python.org/3/using/windows.html) and open a new command window.

The command prints an address beginning `http://127.0.0.1:` and opens it in your browser. If the browser does not open, copy that exact address into its address bar. The number after the colon can change each time. Keep the command window running. Stop it with Ctrl+C when finished.

On Linux, open a terminal in the kit folder and use `python3 -m travel_kit start`. Install Python 3.11+ through your distribution if needed.

## Saving and reopening

**Save my trip** downloads JSON through your browser. The editor does not choose a permanent save location or overwrite a file on disk. Browsers may add a number to repeated downloads, so keep the newest copy and give it a useful name. A saved copy can contain personal plans. Store it in a private folder.

Choose **Open saved trip** to reopen a JSON file. An incompatible or malformed file is rejected without discarding the current draft. Unsaved changes remain only in the tab. Save before refreshing, closing, or starting another trip.

HTML downloads are separate finished documents. Open them in a browser and print with Cmd+P on Mac or Ctrl+P on Windows/Linux. The packing list uses two columns. The full comparison prints in landscape groups. Enable background graphics if you want the colored section bars. Print dialog settings and printer margins vary, so check the preview.

## Using your own photo folder

Create a private trip folder, put your saved JSON inside it, and add an `images` subfolder for PNG/JPEG/WebP files. Start with that exact saved configuration:

```sh
python3 -m travel_kit start --config "/full/path/to/my-trip/trip.json"
```

In the editor, enter `images/cottage.jpg` as a photo path. Save later JSON downloads back beside the original file so those paths still work. Opening another JSON through the browser does not change the server's permitted photo folder; restart with `--config` when switching photo folders. This prevents an imported document from choosing arbitrary files on your computer.

## Optional installed command

Developers may install the release wheel into a virtual environment and use `travel-kit` from any directory. The wheel includes the example JSON, fictional images and editor assets. No dependency installation is needed at runtime. Templates and the optional assistant skill are in the full source download.
