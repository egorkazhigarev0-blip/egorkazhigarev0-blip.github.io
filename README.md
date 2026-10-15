# Инструменты для набросков сайтов (ветка tools)

Не публикуется на сайте. Используется ежедневным поиском клиентов.

```
bash setup.sh                                   # шрифты Google
LEADS_DIR=leads OUT_DIR=out TMP_DIR=tmp python3 make_concepts.py
```
- `leads/<id>.json` — документы из коллекции leads (name, city, addr, cat, niche, rating, reviews, services…).
- Результат: `out/<id>.jpg`.
- Ниши, палитры, тексты и примерные цены — в `niches.py`. Ниша определяется по полю `niche` и названию.
- 3D-иллюстрации: Microsoft Fluent Emoji (лицензия MIT), папка `assets3d/`.
