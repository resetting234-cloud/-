# Сборка для Minecraft 1.21.8 (Fabric)

Эту папку наполняет автоматически `install.sh` / `install.bat` из корня репо.

```
mods/            <- скачанные .jar моды
resourcepacks/   <- скачанные .zip ресурспаки
```

После `install.bat 1.21.8` копируй содержимое в:
- `%APPDATA%\.minecraft\mods` и `%APPDATA%\.minecraft\resourcepacks` (Windows)
- `~/.minecraft/mods` и `~/.minecraft/resourcepacks` (Linux)

Состав — в `../modpack.json`. Скрипт сам отфильтрует моды без билда под 1.21.8.

На 1.21.8 актуальные оптимизации: **Sodium 0.6+ / ScalableLux / Exordium**. Часть
ресурспаков, которые делались под более старые/новые версии, могут быть пропущены —
это нормально, скрипт явно об этом скажет.
