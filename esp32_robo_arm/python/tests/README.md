# Tests

Папка содержит все тестовые файлы для системы робота-руки ESP32.

## Структура тестов

### Основные тесты
- `final_api_test.py` - Финальный тест API-only системы
- `test_api_only_system.py` - Тест системы без файлов
- `test_new_endpoints.py` - Тест новых API endpoints

### Тесты калибровки
- `test_calibration_api.py` - Тест API калибровки
- `test_calibration_saving.py` - Тест сохранения калибровки
- `test_calibration_start_position.py` - Тест стартовой позиции
- `test_simple_start_position.py` - Простой тест позиции

### Базовые тесты
- `test_1.py` - Базовый тест 1
- `test_2.py` - Базовый тест 2
- `test_duration.py` - Тест длительности

## Запуск тестов

```bash
# Из папки python
cd tests
python3 final_api_test.py

# Или из корня python
python3 tests/final_api_test.py
```

## Требования

- API сервер должен быть запущен
- ESP32 робот должен быть подключен (для некоторых тестов)
- Все зависимости установлены

## Примечания

Все тесты обновлены для работы из папки `tests` и автоматически находят модули проекта.
