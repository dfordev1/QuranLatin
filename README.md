# QuranLatin

Latin-script Quran translation datasets, organized for publishing and reuse.

This repository currently contains two packages:

## 1. Bengali Package

Legacy Bengali Latin transliteration data.

- Location: `data/bengali`
- Sources: 5 verse-translation packs plus 1 word-by-word pack
- Combined verse rows: `31,180`
- Word-by-word entries: `83,664`

See `data/bengali/manifest.json` for the full package manifest.

## 2. Transliteration Bundle

Publish-ready Latin transliterations for the broader translation set.

- Location: `data/transliterations`
- Total JSON files: `89`
- Wave 1: `62`
- Wave 2: `21`
- Wave 3: `6`

The bundle is organized by wave:

- `data/transliterations/wave-1`
- `data/transliterations/wave-2`
- `data/transliterations/wave-3`

See `data/transliterations/manifest.json` for the full bundle manifest.

## Quality Notes

- JSON files in this repository are cleaned of URLs and web-link fields.
- A few draft files were excluded after review because the transliteration quality was not fit for publishing.
- The transliteration bundle is designed to be readable and reusable, but some files may still benefit from expert linguistic review.

## Credits

QUL and QuranENC.

