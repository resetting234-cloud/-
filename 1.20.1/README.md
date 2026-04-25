# Сборка для Minecraft 1.20.1 (Fabric)

Эту папку наполняет автоматически `install.sh` / `install.bat` из корня репо.

```
mods/            <- скачанные .jar моды
resourcepacks/   <- скачанные .zip ресурспаки
```

После `install.bat 1.20.1` копируй содержимое в:
- `%APPDATA%\.minecraft\mods` и `%APPDATA%\.minecraft\resourcepacks` (Windows)
- `~/.minecraft/mods` и `~/.minecraft/resourcepacks` (Linux)

Список того, что войдёт в эту версию, — в `../modpack.json`. Скрипт сам отфильтрует
моды, у которых нет билда под 1.20.1.

Для 1.20.1 действует особый набор оптимизаций (актуальный для Sodium 0.5):
**Starlight, Indium, ModernFix, MemoryLeakFix, Smooth Boot Reloaded** — на 1.21+ они
не нужны, их роль играет встроенный код Sodium 0.6 и `ScalableLux`.
