<div align="center">

# sv.autoclick

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/Core-OpenCV-5C3EE8?logo=opencv&logoColor=white)
![UI](https://img.shields.io/badge/GUI-CustomTkinter-2EA043?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-555555)

**sv.autoclick** — это терминально-стилизованный комплекс автоматизации, базирующийся на алгоритмах компьютерного зрения (OpenCV). Программа предоставляет мощный движок сканирования экрана с поддержкой скрытого внедрения инпутов (Background Protocol) и модулями обхода эвристического анализа.

[Скачать релиз](https://github.com/KrekerDM/sv.autoclick/releases) • [Сообщить об ошибке](https://github.com/KrekerDM/sv.autoclick/issues)

<br/>

<img width="541" height="831" alt="image" src="https://github.com/user-attachments/assets/aa43b5c5-8b6a-4ac8-aa2a-1ad01e7e6513" />

</div>

---

## Описание проекта

**sv.autoclick** спроектирован для надежной работы в агрессивных средах. Вместо тривиального кликера по координатам, утилита использует метод `Template Matching` для точного оптического распознавания целей. 

Проект выделяется современным интерфейсом в стиле **Google Material Design 3** (Dark Theme) и набором защитных механизмов, позволяющих использовать его для скрытой автоматизации процессов.


---

## Технические возможности

* **Computer Vision Engine:** Оптическое распознавание через `cv2.matchTemplate`. Поддержка гибкой настройки чувствительности (Sensitivity) для нахождения точных или приблизительных совпадений.
* **INPUT_PROTOCOL:** Два режима работы ввода:
  * `physical` — прямой перехват курсора ОС через PyAutoGUI.
  * `background` — скрытая инъекция событий мыши через `Win32API` (`PostMessage`), позволяющая взаимодействовать с окнами в фоновом режиме.
* **ARIRAL_STEALTH:** Модуль анти-детекта. Рандомизирует координаты смещения клика (в пределах габаритов цели) и вносит микрозадержки в тайминги исполнения для обхода анти-чит систем.
* **TARGET_DB:** Встроенная база целей с горячим переключением. Поддерживает импорт внешних изображений и встроенный `SNIP`-инструмент для быстрого захвата фрагментов экрана.
* **VISION_DEBUG:** Режим отладки, выводящий отдельное окно с визуализацией алгоритмов CV (отрисовка bounding boxes и центров захвата в реальном времени).
* **Scan Region Optimizer:** Возможность ручного ограничения зоны сканирования для кратного повышения FPS обработки.

---

### Требования
* Python 3.10 или выше
* Операционная система Windows

### Установка зависимостей

pip install opencv-python numpy pyautogui customtkinter pywin32 keyboard

### Горячие клавиши (Hotkeys)
F7 — Инициализация ядра сканирования (SYS: ACTIVE).
F8 — Экстренная остановка всех потоков (SYS: STANDBY).


### Дисклеймер ⚠️⚠️
Программное обеспечение предоставляется "как есть". Интегрированные модули обхода блокировок (ARIRAL_STEALTH) предназначены для исследовательских целей. Автор не несет ответственности за блокировки или санкции со стороны сторонних платформ.
