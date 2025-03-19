[app]
# Название приложения
title = VoiceDiaryApp

# Имя пакета (должно быть уникальным)
package.name = voicediaryapp

# Домен (например, com.example)
package.domain = org.example

# Путь к основному файлу Python
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = assets/*,images/*,fonts/*
source.exclude_patterns = tests/*

# Версия приложения
version = 1.0

# Требуемые разрешения для Android
android.permissions = INTERNET, RECORD_AUDIO

# Зависимости
requirements = python3,kivy==2.1.0,kivymd,speechrecognition

# Ориентация экрана
orientation = portrait

# Логотип приложения (необязательно)
icon.filename = %(source.dir)s/assets/icon.png