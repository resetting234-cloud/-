# MeetionMC BoxPvP / Doombox Modpack

Сборка модов и ресурспаков для **Minecraft Fabric** под BoxPvP/Doombox на серверах
типа `Meetionmc.net` (и любом другом BoxPvP-сервере).

Поддерживаемые версии: **1.20.1**, **1.21.5**, **1.21.8**.

Главное: **тебе НЕ нужно вручную скачивать моды и паки**. Запускаешь один скрипт —
он сам тянет всё свежее с [Modrinth](https://modrinth.com) в нужные папки.

---

## Быстрый старт

### Windows
1. Установи [Fabric Loader](https://fabricmc.net/use/installer/) под нужную версию MC.
2. Двойной клик по `install.bat` (или `install.bat 1.21.8` чтобы скачать только одну версию).
3. Заходишь в папку `1.21.8/mods/` и `1.21.8/resourcepacks/` — там лежат все моды и паки.
4. Копируешь содержимое в `%APPDATA%\.minecraft\mods` и `%APPDATA%\.minecraft\resourcepacks`.

### Linux / macOS
```bash
chmod +x install.sh
./install.sh                 # все версии
./install.sh 1.21.8          # одна версия
./install.sh 1.20.1 1.21.5   # несколько
```

Затем мoды → `~/.minecraft/mods` (Linux) или `~/Library/Application Support/minecraft/mods` (macOS).

### Зависимости
- `install.sh`: `bash`, `curl`, `jq` (на Ubuntu: `sudo apt install jq`).
- `install.bat`: ничего, использует встроенный PowerShell 5+.

---

## Что внутри сборки

Состав определяется в [`modpack.json`](./modpack.json). Скрипт умеет автоматически
**пропускать** моды/паки, у которых нет совместимого билда под выбранную MC-версию,
поэтому одна и та же конфигурация работает для всех трёх версий.

### Моды — FPS / производительность

| Мод | Что делает |
|-----|------------|
| **Sodium** | Полностью переписанный рендер. Главный буст FPS. |
| **Sodium Extra** + **Reese's Sodium Options** | Доп. настройки Sodium (отключить дождь/облака/туман и т.д.) |
| **Lithium** | Оптимизация серверного тика, физики, AI, redstone. |
| **FerriteCore** | -30…40% потребления RAM. |
| **EntityCulling** | Не рендерит сущности за стенами. Огромный буст в полных боксах. |
| **ImmediatelyFast** | Быстрый рендер HUD/чата/инвентаря. |
| **Dynamic FPS** | Урезает FPS, когда окно неактивно — экономит CPU/GPU. |
| **Krypton** | Оптимизация сетевого стека, меньше пиков пинга. |
| **FastQuit** | Возврат в меню без зависания при выходе с сервера. |
| **Debugify** | Чинит сотни мелких ванильных багов. |
| **ModernFix** *(только 1.20.1)* | Большой пакет фиксов и оптимизаций. |
| **MemoryLeakFix** *(только 1.20.1)* | Патчит утечки памяти. |
| **Starlight** *(только 1.20.1)* | Быстрый движок света. |
| **Indium** *(только 1.20.1)* | FRAPI-совместимость для Sodium 0.5. |
| **ScalableLux** *(1.21+)* | Многопоточный движок света (замена Starlight). |
| **Noisium** | Быстрая генерация чанков. |
| **Exordium** | Кеширует фреймы HUD — меньше работы GPU. |

### Моды — PvP / QoL

| Мод | Что делает |
|-----|------------|
| **Raised** | Поднимает хотбар над иконками зелий — must-have для PvP. |
| **Zoomify** | Плавный настраиваемый зум (Ctrl, по умолчанию C). |
| **Mouse Tweaks** | Тяни-перетаскивание в инвентаре. Быстрее свапать тотемы/перлы. |
| **AppleSkin** | Показывает голод и насыщение. |
| **Chat Heads** | Головы игроков рядом с сообщениями в чате — видно кто кого убил. |
| **BetterF3** | Кастомизируемый F3-экран. |
| **Mod Menu** | Список модов и доступ к их настройкам. |
| **No Chat Reports** | Отключает Mojang chat reporting. |

### Ресурспаки

В сборку входит подборка популярных PvP-паков и «no-particles»-паков. Какие из них
реально установятся — зависит от того, что автор пака зарелизил под твою версию MC:
скрипт пропустит несовместимые. После установки ты сам решаешь, какие включить
(в Minecraft → Options → Resource Packs).

Ядро на все версии:
- **Better PvP Fire** — почти прозрачный огонь, видно врага.
- **No Explosion Particles**, **No Crystal Particles**, **No Block Particles**, **No Particles Essential** — убирают визуальный шум во время боя.
- **Block Hitbox Indicator** — точные хитбоксы блоков.

Полные PvP-паки (16x):
- **Yeahlow's PvP Pack** — 1.21.x
- **Haze PvP** — 1.21.5/1.21.6
- **Master's PvP Pack** — 1.21.5+
- **Candy PvP Pack** — 1.21.5
- **Clean PvP Pack** — 1.20.x

---

## Как добавить свой мод

Открой `modpack.json` и допиши объект в массив `mods` или `resourcepacks`. Нужен
только slug проекта на Modrinth (то, что в URL: `modrinth.com/mod/<SLUG>`).

```json
{ "slug": "iris", "category": "fps", "desc": "Шейдеры (опционально)" }
```

Запусти скрипт ещё раз — он скачает только новые / отсутствующие файлы.

---

## Структура репозитория

```
.
├── install.sh           # Linux/macOS установщик
├── install.bat          # Windows-обёртка над install.ps1
├── install.ps1          # Windows установщик (PowerShell)
├── modpack.json         # список модов и паков
├── 1.20.1/
│   ├── mods/            # сюда падают .jar
│   └── resourcepacks/   # сюда падают .zip
├── 1.21.5/{mods,resourcepacks}/
└── 1.21.8/{mods,resourcepacks}/
```

`*.jar` и `*.zip` игнорятся гитом (см. `.gitignore`) — репо не пухнет от загрузок,
только хранит конфиг и установщики.

---

## Где брать Fabric

https://fabricmc.net/use/installer/ — выбираешь версию MC (1.20.1 / 1.21.5 / 1.21.8),
ставишь, в лаунчере появляется профиль `fabric-loader-...`. Запускай его — и моды из
`.minecraft/mods` подхватятся.
