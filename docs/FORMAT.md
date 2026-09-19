# Saved trip format

> **TL;DR:** One versioned JSON document holds the trip, catalog, selections, plan and rental comparison. Prefer the editor for routine changes. Unknown fields or incompatible versions are rejected rather than silently lost.

`travel_kit/example/cedar-bay.json` is a complete, invented example. `travel_kit/schema.py` is the authoritative field validator. Supported fields are preserved during import/export, even if you do not edit their section. Text is plain text, not executable HTML.

## The six top-level fields

The format is intentionally explicit. It keeps facts separate from decisions and uncertain estimates separate from exact quotes.

| Field | Contents |
| --- | --- |
| `formatVersion` | Integer `1`. |
| `trip` | Title, optional subtitle/destination/origin/party, arrival `start` and departure `end`. Dates use `YYYY-MM-DD`. |
| `catalog` | Categories with stable IDs and print columns, plus items with category ID, tags, quantity, assignee and note. |
| `packing` | Trip tags, explicitly `selected`, `excluded` and `morning` item IDs, plus a note. |
| `plan` | Summary, status, days, decisions, activities, preferences, sources, notes and optional review. |
| `rentals` | Summary, criteria, optional hero image, household split scenarios and property records. |

## Selection and IDs

Item, category and property IDs begin with a lowercase letter and contain lowercase letters, digits or hyphens, up to 64 characters. IDs must be unique within each collection. Items must refer to existing categories; packing selections must refer to existing items.

Universal items are suggested on every trip. Other supported tags are `beach`, `camping` and `road-trip`. Explicit inclusion adds an item regardless of tags. Exclusion takes priority over both. Morning-of selection highlights an already included item; it does not silently add an excluded item.

## Quotes

A quote has `kind` (`exact`, `range` or `unknown`) and `currency`. Exact totals use a decimal string `amount`, such as `"1843.25"`. Ranges use `min` and `max`. Do not include commas or currency symbols inside these strings. USD, EUR, GBP, CAD and AUD use two decimal places; JPY uses zero; KWD uses three. The maximum integer portion is nine digits. Ranges and unknowns never become exact household splits.

Optional `stayStart`, `stayEnd`, `checked`, `scope` and `note` preserve the basis of a quote. Supply both stay dates or neither. Differing trip and quote dates are flagged in the documents. The kit does not silently scale a price to a different number of nights. Unused exact/range fields can remain when changing quote type; only the active type drives calculation.

## Rental detail

Every property has ID, name, tier, rank, quote and photos. Tiers are `shortlist`, `alternative` and `rejected`. The full table retains name, platform, listing URL, area, drive, sleeps, bedrooms, bathrooms, square feet, acreage, theater, waterfront, pool, hot tub, game room, amenities, quote, split, rating, cancellation, availability and notes. Gallery detail also retains bed layout, practical details for children, sauna and the ranking rationale.

Availability is `available`, `unavailable` or `unknown`. Theater, hot tub, game room and sauna are `yes`, `no` or `unknown`; other descriptions remain text so you can record qualifications. A photo or hero is `{ "src": "images/house.jpg", "alt": "A description", "credit": "Your credit" }`. Relative local paths stay within the configuration folder. HTTP(S) references remain optional links unless explicitly enabled. See [photos](PHOTOS.md).

## Limits and backups

JSON is limited to 2 MB, each text field to 10,000 characters, catalog items to 1,000, categories to 60, properties to 100, and each property's photos to 24. A local image is limited to 8 MB. These are working document limits, not storage quotas. Duplicate JSON keys, nonfinite numbers, unsafe URLs and unsupported fields are rejected. Keep a saved JSON copy before making large changes.
