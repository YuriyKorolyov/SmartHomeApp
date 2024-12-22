# SmartHomeApp

## Участники

### Юрий Королев  РИС-21-1б

## Тема: Умная система мониторинга и управления домом

## Структура

- [ ] Подсистема мониторинга и сбора данных: Сбор данных с различных сенсоров (температуры, влажности, освещенности, движения)
- [ ] Подсистема управления устройствами: Управление устройствами, которые подключены к контроллеру через розетку 220 в (реле, свет, вентиляторы, сигнализация).
- [ ] Подсистема сценариев автоматизации: Обработка сценариев (например, включение света при движении, контроль температуры). 
- [ ] Подсистема обмена данными (связь между Raspberry Pi и Android): через API
- [ ] Мобильное приложение (Android): Интерфейс для отображения данных, управления устройствами и настройки сценариев.

## Используемые технологии

Python, GPIO Raspberry Pi для контроллера\
Java для Android приложения\
HTTP для связи с котроллером

## План работы

Разработка API\
Разработка Android-приложения\
Интеграция сценариев автоматизации\
CI/CD