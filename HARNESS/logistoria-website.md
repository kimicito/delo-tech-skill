# HARNESS.md — Logistoria Website

## Назначение

Основной сайт компании Logistoria:
- Презентация игр (KADENA, Krossdok, Beer Game)
- AI-курс
- Контакты, кейсы, клиенты

## Архитектура

```
logistoria-website/ (отдельный репозиторий)
├── index.html          # Главная
├── games/              # Страницы игр
│   ├── kadena/
│   ├── krossdok/
│   ├── beer-game/
│   └── storewars/
├── ai-course/          # AI-курс (отдельный submodule)
│   └── ...
├── cases/              # Кейсы клиентов
├── contact/            # Контакты
└── assets/             # Изображения, CSS, JS
```

## Технологии

- **Frontend:** Vanilla HTML/CSS/JS
- **Хостинг:** GitHub Pages
- **Домен:** logistoria.com
- **AI-курс:** Submodule → github.com/kimicito/ai-nontechnical-course

## Правила обновления

### Добавить игру
1. Создать `games/<название>/index.html`
2. Добавить в навигацию
3. Обновить главную (блок игр)

### Обновить кейс
1. Создать `cases/<клиент>.html`
2. Добавить логотип клиента
3. Обновить список клиентов

### AI-курс
- Разрабатывается в отдельном репо
- Обновляется через submodule
- Не редактировать напрямую в этом проекте!

## Параметры

| Параметр | Значение |
|----------|----------|
| Дизайн | Тёмная тема, фиолетовый акцент |
| Адаптив | Да, mobile-first |
| SEO | Оптимизировать title, meta, alt |

## Ограничения

- ❌ Не добавлять тяжёлые видео (>10MB)
- ❌ Не менять структуру URL (ломаются ссылки)
- ✅ Всё через GitHub Pages (бесплатно, надёжно)

## Чеклист обновления

- [ ] Изменения в отдельной ветке
- [ ] Проверить на мобильном
- [ ] Проверить все ссылки
- [ ] Merge → деплой автоматический

## Связанные проекты

- **ai-nontechnical-course** → submodule
- **instagram-automation** → контент для соцсетей
- **supplychains-bot** → Telegram канал

## Контакты

- **Владелец:** Artur A. (tagartur)
- **Репозиторий:** github.com/kimicito/logistoria-website
