# Ollama Setup Guide

Это руководство по установке и настройке Ollama для локального AI в Sulpak HelpDesk.

## Что такое Ollama?

Ollama - это локальный AI сервер, который позволяет запускать большие языковые модели (LLM) на вашем компьютере без необходимости облачных API. Это дешевле и приватнее чем использование Anthropic Claude API.

## Установка Ollama

### Windows

1. Скачайте Ollama для Windows:
   - Перейдите на https://ollama.com/download
   - Скачайте `OllamaSetup.exe`
   - Запустите установщик

2. После установки Ollama автоматически запустится как сервис Windows

3. Проверьте установку:
   ```powershell
   ollama --version
   ```

### macOS / Linux

```bash
# macOS
curl -fsSL https://ollama.com/install.sh | sh

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

## Установка модели

После установки Ollama нужно скачать модель. Рекомендуемые модели:

### Llama 3.2 (рекомендуется, ~2GB)

```bash
ollama pull llama3.2:latest
```

Преимущества:
- ✅ Быстрая
- ✅ Хорошее качество ответов
- ✅ Небольшой размер
- ✅ Поддержка русского языка

### Qwen 2.5 (альтернатива, ~4.7GB)

```bash
ollama pull qwen2.5:latest
```

Преимущества:
- ✅ Отличное качество
- ✅ Лучше работает с инструкциями
- ✅ Отличная поддержка русского языка

### Mistral (опционально, ~4.1GB)

```bash
ollama pull mistral:latest
```

## Проверка работы Ollama

### 1. Проверьте, что сервис запущен

```bash
# Windows PowerShell
Get-Service Ollama

# Linux/macOS
systemctl status ollama
```

### 2. Проверьте список моделей

```bash
ollama list
```

Должны увидеть установленные модели, например:
```
NAME                ID              SIZE    MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB  5 minutes ago
```

### 3. Проверьте API

```bash
curl http://localhost:11434/api/tags
```

Должен вернуть JSON со списком моделей.

### 4. Тестовый запрос

```bash
ollama run llama3.2 "Привет! Как дела?"
```

## Конфигурация для Sulpak HelpDesk

После установки Ollama обновите `backend/.env`:

```bash
# Включите Ollama
USE_OLLAMA=true

# URL Ollama сервера (по умолчанию локально)
OLLAMA_URL=http://localhost:11434

# Модель (используйте ту, которую установили)
AI_MODEL=llama3.2:latest
```

## Запуск проекта с Ollama

1. Убедитесь, что Ollama запущена:
   ```bash
   ollama ps  # Показать запущенные модели
   ```

2. Запустите backend:
   ```bash
   cd backend
   python run_all.py
   ```

3. Бот автоматически начнет использовать Ollama для ответов

## Переключение на Anthropic Claude

Если хотите использовать Anthropic API вместо Ollama:

```bash
# backend/.env
USE_OLLAMA=false
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
```

## Производительность

### Системные требования

**Минимум:**
- CPU: 4 cores
- RAM: 8 GB
- Диск: 5 GB (для llama3.2)

**Рекомендуется:**
- CPU: 8 cores
- RAM: 16 GB
- GPU: NVIDIA с 6GB+ VRAM (опционально, для ускорения)
- Диск: 20 GB (для нескольких моделей)

### Скорость генерации

На среднем ПК (без GPU):
- Llama 3.2: ~20-30 tokens/sec
- Qwen 2.5: ~15-25 tokens/sec

С GPU (NVIDIA):
- Llama 3.2: ~50-100 tokens/sec
- Qwen 2.5: ~40-80 tokens/sec

## GPU Acceleration (опционально)

Если у вас есть NVIDIA GPU, Ollama автоматически использует CUDA для ускорения.

Проверка GPU:
```bash
nvidia-smi
```

Ollama автоматически определит GPU и использует его.

## Troubleshooting

### Ollama не запускается

**Windows:**
```powershell
# Перезапустите сервис
Restart-Service Ollama
```

**Linux/macOS:**
```bash
sudo systemctl restart ollama
```

### Порт 11434 занят

Измените порт в `backend/.env`:
```bash
OLLAMA_URL=http://localhost:12434
```

И настройте Ollama:
```bash
# Linux/macOS
export OLLAMA_HOST=0.0.0.0:12434
ollama serve

# Windows - измените в настройках сервиса
```

### Модель работает медленно

1. Используйте меньшую модель:
   ```bash
   ollama pull llama3.2:1b  # Самая быстрая (1GB)
   ```

2. Закройте другие приложения

3. Увеличьте RAM если возможно

### AI отвечает на английском

Убедитесь, что system prompt в `ai_service.py` содержит инструкцию отвечать на русском:
```python
def _build_system_prompt(self) -> str:
    return """Ты — AI-ассистент службы поддержки Sulpak...
    Отвечай дружелюбно, профессионально и по существу на русском языке
    ...
    """
```

### Connection refused

Проверьте, что Ollama запущена:
```bash
curl http://localhost:11434/api/tags
```

Если не работает:
```bash
ollama serve  # Запустить вручную
```

## Альтернативные модели

### Для русского языка:

```bash
# Qwen 2.5 - лучшая для русского
ollama pull qwen2.5:latest

# Saiga (специально для русского)
ollama pull saiga:latest

# Vikhr (русская модель от Сбера)
ollama pull vikhr:latest
```

### Для низких ресурсов:

```bash
# Llama 3.2 1B - очень быстрая
ollama pull llama3.2:1b

# Phi 3 Mini - хорошее качество/скорость
ollama pull phi3:mini
```

## Мониторинг

Посмотреть использование ресурсов:
```bash
# Запущенные модели
ollama ps

# Логи
journalctl -u ollama -f  # Linux
Get-WinEvent -LogName Application -Source Ollama  # Windows
```

## Полезные ссылки

- Official website: https://ollama.com/
- Model library: https://ollama.com/library
- GitHub: https://github.com/ollama/ollama
- Discord: https://discord.gg/ollama

## Сравнение: Ollama vs Anthropic Claude

| Параметр | Ollama (локально) | Anthropic Claude API |
|----------|------------------|----------------------|
| **Стоимость** | Бесплатно | $3-15 за 1M tokens |
| **Скорость** | 20-100 tok/sec | 50-200 tok/sec |
| **Качество** | Хорошее | Отличное |
| **Приватность** | ✅ 100% локально | ❌ Данные уходят в облако |
| **Setup** | Требует установки | Только API key |
| **Требования** | 8GB RAM, 5GB диск | Интернет |
| **Надежность** | Зависит от ПК | 99.9% SLA |

**Рекомендация:**
- Разработка/тест: Ollama (быстрее, бесплатно)
- Production: Anthropic Claude (качественнее, надежнее)
