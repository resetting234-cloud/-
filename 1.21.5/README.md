# Сборка для Minecraft 1.21.5 (Fabric)

Эту папку наполняет автоматически `install.sh` / `install.bat` из корня репо.

```
mods/            <- скачанные .jar моды
resourcepacks/   <- скачанные .zip ресурспаки
```

После `install.bat 1.21.5` копируй содержимое в:
- `%APPDATA%\.minecraft\mods` и `%APPDATA%\.minecraft\resourcepacks` (Windows)
- `~/.minecraft/mods` и `~/.minecraft/resourcepacks` (Linux)

Состав — в `../modpack.json`. Скрипт сам отфильтрует моды без билда под 1.21.5.

Для 1.21.5 используется **Sodium 0.6+** + **ScalableLux** вместо Starlight, и
**Noisium** для ускорения чанков. ModernFix/MemoryLeakFix больше не нужны.
