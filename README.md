# Инструменты для набросков сайтов (ветка tools)

Не публикуется на сайте. Используется ежедневным поиском клиентов.

```
bash setup.sh                                   # шрифты
LEADS_DIR=leads OUT_DIR=out TMP_DIR=tmp python3 make_concepts.py
```
`leads/<id>.json` — документы из коллекции leads (поля name, city, addr, cat, sit, rating, reviews, services…).
Результат: `out/<id>.jpg`.
