# Photos and listing research

> **TL;DR:** Use your own local pictures for a fully offline gallery. The optional fetch command discovers URLs from explicitly supplied public listing pages. It does not download photo bytes or grant permission to redistribute them.

## Local images

Put images in a folder beside your saved JSON, for example `images/cottage.jpg`. Start the editor with `--config` pointing to that JSON, then enter relative paths in **Places to stay**. PNG, JPEG and WebP files up to 8 MB each are supported. A missing photo gives a designed placeholder. Absolute paths, parent traversal and symlinks outside the selected folder are rejected.

The exported gallery embeds local photo bytes. This makes it portable, but also means a photo's metadata can travel with the document. Review your own images before sharing. All shipped example images are generated illustrations of invented properties.

## Collect public listing photo URLs

This is an optional command-line workflow. Create a CSV with exactly `id,url` as its headers. Use the property IDs in your saved trip, for example:

```csv
id,url
blue-shutter,https://example.invalid/replace-with-your-listing
```

The example address is deliberately nonfunctional. Replace it with a public listing you choose to inspect. Then run:

```sh
python3 -m travel_kit fetch-photos --csv private/listings.csv --output private/photos.json
python3 -m travel_kit apply-photos --config private/trip.json --photos private/photos.json --output private/trip-with-photos.json
python3 -m travel_kit compare --config private/trip-with-photos.json --output private/gallery.html
```

The fetcher recognizes listing photo feeds used by Airbnb and Vrbo/related lodging hosts before falling back to image metadata and ordinary image URLs. It deduplicates URLs and keeps at most 24 per listing. Websites can block automated access, require login/JavaScript or change their markup. A failed page or a page without images is reported as a failure. It is not treated as a new empty gallery.

Use `fetch-photos --update` to merge successful fetches into an existing photo collection. Previous entries for failed listings remain. If every fetch fails, the existing file is not rewritten. `apply-photos` appends new URLs to matching property IDs, preserves other fields, and rejects unknown property IDs. Use `--replace` only when you want to replace the matching properties' existing photos. Existing output JSON files need a new filename or explicit `--overwrite`.

Keep the new JSON beside the original so relative local photos still resolve. Applying photos does not fetch image bytes or change the hero selection. Add helpful alt descriptions and credits in the editor afterward.

## External image loading

By default, HTTP(S) images are links in the gallery. Opening or printing it makes no remote image requests. To deliberately make a connected gallery, add `--remote-images` to `compare`. Everyone who opens that HTML may then contact the image hosts, revealing the usual browser network information. The browser editor always uses the offline setting.

Check that you have permission before publishing someone else's photos or listing text. A listing being publicly viewable does not make its assets part of this kit's MIT license.
