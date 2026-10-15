# Инструменты для набросков сайтов (ветка tools)

Не публикуется на сайте. Используется ежедневным поиском клиентов.

```
bash setup.sh                                   # шрифты Google
LEADS_DIR=leads OUT_DIR=out TMP_DIR=tmp python3 make_concepts.py
```
- `leads/<id>.json` — документы из коллекции leads (name, city, addr, cat, niche, rating, reviews, services…).
- Результат: `out/<id>.jpg`.
- Ниши, палитры, тексты и примерные цены — в `niches.py`. Ниша определяется по полю `niche` и названию.
- 3D-иллюстрации (`assets3d/`) и плоские 2D (`assets2d/`): Microsoft Fluent Emoji, лицензия MIT.
- `VARIANT=2` — второй вариант для повторного касания (другая палитра, раскладка, заголовок, 2D-иконки), файл `out/<id>-2.jpg`.
- Поля лида, которые делают набросок личным: `motto` (девиз бизнеса → заголовок), `services` (реальные цены), `rating`, `reviews`.
