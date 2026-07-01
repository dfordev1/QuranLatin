# QuranLatin

QuranLatin is a public JSON library of Quran translation texts converted into Latin letters. It helps readers, students, and app builders browse translations from many languages even when the original writing system is hard for them to read or render.

This is transliteration of translation text. It is not Arabic recitation transliteration, and it is not a new Quran translation.

## Start Here

- Public catalog: [`index.json`](./index.json)
- Browse page: [`index.html`](./index.html)
- Language folders: [`data/languages`](./data/languages)
- Internal processing notes: [`data/internal`](./data/internal)

## What Is Inside

| Item | Count |
| --- | ---: |
| Languages | 44 |
| Translation JSON files | 89 |
| Verse rows per complete file | 6,236 |

Each language has its own folder:

```text
data/languages/
  arabic/
  bengali/
  hindi/
  persian/
  russian/
  urdu/
```

Each folder contains the ready-to-use JSON files for that language plus a small `index.json`.

## Use The Data

```js
const res = await fetch("data/languages/urdu/ur_mokhtasar.json");
const data = await res.json();
console.log(data.translations[0]);
```

Every translation file follows the same basic shape:

```json
{
  "source": {},
  "row_count": 6236,
  "transliteration": {},
  "translations": [
    {
      "sura": 1,
      "aya": 1,
      "translation": "..."
    }
  ]
}
```

## Quality Labels

The public catalog includes a `quality_status` for every JSON file.

| Status | Meaning |
| --- | --- |
| `reviewed-draft` | Best current machine transliteration set, still not a scholarly edition |
| `draft` | Readable draft output that should be sampled before production use |
| `needs-review` | Useful for experimentation, but needs language-aware review |

## Credits

Source data credits: QUL and QuranENC.

