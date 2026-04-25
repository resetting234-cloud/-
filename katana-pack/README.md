# MeetionRC Resource Pack — База

Скелет ресурспака для Minecraft. Сюда можно класть свои JSON-модели и
PNG-текстуры — `pack.mcmeta` и структура папок уже готовы, остаётся положить
файлы и упаковать в zip.

Поддерживаемые версии: **1.20.1, 1.21.4, 1.21.5, 1.21.8, 1.21.11**
(через `supported_formats: 15..64` в `pack.mcmeta`).

## Структура

```
katana-pack/
├── pack.mcmeta          # формат пака + supported_formats
├── pack.png             # иконка пака (можно заменить)
└── assets/minecraft/
    ├── models/item/     # ← клади сюда: wooden_sword.json, iron_sword.json, ...
    ├── textures/item/   # ← клади сюда: wooden_sword.png, iron_sword.png, ...
    └── items/           # ← (только 1.21.4+) item definitions, если нужны
```

## Как добавить свой меч/предмет

1. **Модель** — JSON-файл в `assets/minecraft/models/item/<имя_предмета>.json`.
   Пример имён: `wooden_sword`, `iron_sword`, `diamond_sword`, `netherite_sword`,
   `stick`, `bow`, и т.д. — это ванильные ID предметов.
2. **Текстура** — PNG-файл в `assets/minecraft/textures/item/<имя>.png`.
   Если используешь UV-атлас, не забудь прописать в JSON-модели
   `"texture_size": [width, height]`.
3. **На 1.21.4+** — дополнительно положить `assets/minecraft/items/<имя>.json`
   с редиректом на твою модель (на 1.20.1/1.21 предыдущих этот файл
   игнорируется).

## Установка пака в Minecraft

1. Заархивируй содержимое этой папки в zip (на верхнем уровне zip должны быть
   `pack.mcmeta` и `assets/`, а не папка `katana-pack/`).
2. Кинь zip в `%APPDATA%\.minecraft\resourcepacks\` (Windows) или
   `~/.minecraft/resourcepacks/` (Linux/macOS).
3. В игре: Esc → Options → Resource Packs → активировать.

## Заметка про pack.mcmeta

`pack_format: 15` — базовое значение для 1.20+. `supported_formats: {15..64}`
говорит Minecraft что пак совместим с диапазоном версий. На 1.20.x — игра
смотрит `pack_format`; на 1.21.x — `supported_formats`. Один пак работает
на всех целевых версиях без копий.
