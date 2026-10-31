# Система 1. Мероприятия и оценка — фронтенд

Стек: React 19, TypeScript, Vite, Tailwind v4, react-router-dom 7. Новые модули: `src/features/events/` (мероприятия, анонсы, акселератор) и `src/features/eval/` (оценочные листы, оценка, итоги). Имена полей совпадают с контрактами бэкенда ([backend.md](backend.md)). Перед началом выполнить список «Что сделать в существующем коде» из [../00-common/conventions.md](../00-common/conventions.md).

Визуальный эталон — работающий фронт и прототип v5 (`source/Прототип v5.dc.html`, `ТелефонV5.dc.html`): токены цвета primary `#006d30`, primary-container `#00ab4f`, кнопки `#0E9344`, tertiary `#5d3fe0`, фон `#f7fafc`; шрифты Manrope и Hanken Grotesk; предупреждение `#8a5a00` на `#fff4e0`. Кнопки «ВОЙТИ» и «СОХРАНИТЬ» — капсом, цвет success; активный пункт меню — primary-container. Новые экраны используют тот же стиль кнопок, что действующий фронт (ПР18). Брейкпоинты: десктоп 1440 px, телефон 390 px.

## 1. Типы

```ts
type Role = 'student' | 'expert' | 'organizer' | 'trainer' | 'mentor';
type EventType = 'predefense' | 'defense' | 'accelerator';
type PublicationStatus = 'draft' | 'published';
type EvaluationStatus = 'draft' | 'open' | 'closed';        // подписи: Не открыт / Активно / Завершён
type TemplateStatus = 'draft' | 'locked';
type EvalStatus = 'none' | 'draft' | 'submitted';
type OrderSource = 'manual' | 'excel' | 'predefense' | 'auto';
type RegistrationStatus = 'not_opened' | 'open' | 'closed';   // ○
type EnrollmentState = 'not_opened' | 'available' | 'enrolled' | 'closed'; // ○

// общий модуль
interface Material { id: number; track_id: number; title: string; file_name: string; size: number; uploaded_by: string; uploaded_at: string }
interface Trainer { id: number; user_id: number; full_name: string; position: string; company: string }
interface Track { id: number; role: string; room: string; description: string; capacity: number | null; seats_left?: number | null; trainers: Trainer[] }
interface Enrollment { state: EnrollmentState; track_id: number | null }
interface EventBase {
  id: number; title: string; type: EventType; event_date: string; start_time: string; end_time: string; place: string;
  description: string; publication_status: PublicationStatus; published_at: string | null;
}
interface Announcement extends EventBase { tracks?: Track[]; enrollment: Enrollment | null;
  registration_opens_at?: string | null }   // ○ только accelerator; эффективный статус записи приходит в enrollment.state

// модуль оценок
interface Level { score: number; description: string }
interface Criterion { id: number; title: string; description: string; position: number;
  max_score: number; /* только чтение */ levels: Level[] }
interface Template { id: number; name: string; description: string; status: TemplateStatus; criteria: Criterion[] }
interface EventEvaluation { template_id: number; status: EvaluationStatus;
  passing_score: number | null; /* только predefense */ source_event_id: number | null; /* только defense */ }
interface EventTeam { event_team_id: number; team_id: number; team_title: string;
  section_id: number | null; position: number | null; order_source: OrderSource; absent: boolean }
interface SectionTeam extends EventTeam { my_evaluation: EvalStatus; my_total: number | null }
interface Section { id: number; room: string; event: EventBase & { evaluation_status: EvaluationStatus };
  criteria: Criterion[]; teams: SectionTeam[] }
interface PassedTeam { team_id: number; team_title: string; total: number | null;
  submitted: number; experts: number; absent: boolean; passed: boolean }

interface ScoreInput { criterion_id: number; score: number }
interface EvaluationPayload { scores: ScoreInput[]; comment: string; status: 'draft' | 'submitted' }
interface Evaluation extends Omit<EvaluationPayload, 'status'> { status: EvalStatus; total: number | null; submitted_at: string | null }
interface ApiError { error: { code: string; message: string; details?: Record<string, unknown> } }
```

## 2. Функции API-клиента

| Функция | Запрос |
|---|---|
| `getAnnouncements()`, `getAnnouncement(id)` | `GET /api/events/announcements/`, `/announcements/{id}/` |
| `listEvents(filters)`, `createEvent(e)`, `getEvent(id)`, `updateEvent(id, patch)`, `deleteEvent(id)`, `publishEvent(id)` | `/api/events/`, `/api/events/{id}/`, `POST …/publish/` |
| `saveTrack()`, `deleteTrack()`, `saveTrainer()`, `deleteTrainer()` | `/api/events/{id}/tracks/`, `/tracks/{tid}/`, `/trainers/{id}/` |
| `getEvaluationSettings(id)`, `saveEvaluationSettings(id, s)` | `GET, PUT /api/eval/events/{id}/evaluation/` |
| `openEvaluation(id)`, `closeEvaluation(id)`, `reopenEvaluation(id)` | `POST /api/eval/events/{id}/open/`, `/close/`, `/reopen/` |
| `getPassedTeams(predefenseId)` | `GET /api/eval/events/{id}/passed-teams/` |
| `listEventTeams(id)`, `addEventTeam(id, teamId)`, `removeEventTeam(etId)`, `setAbsent(etId, absent, confirm?)` | `/api/eval/events/{id}/teams/`, `/event-teams/{id}/` |
| `createSection()`, `updateSection()`, `deleteSection()`, `saveSectionTeams(sid, teamIds)`, `saveSectionExperts(sid, userIds)`, `searchExperts(q)` | `/api/eval/events/{id}/sections/`, `/sections/{sid}/`, `/sections/{sid}/teams/`, `/sections/{sid}/experts/`, `/experts/` |
| `importTeams(eventId, file, dryRun)` | `POST /api/eval/events/{id}/teams/import/` |
| `listTemplates()`, `getTemplate(id)`, `saveTemplate(t)`, `deleteTemplate(id)`, `duplicateTemplate(id)` | `/api/eval/templates/` |
| `getMyEvents()`, `getMySection(sid)`, `getEvaluation(etId)`, `saveEvaluation(etId, payload)` | `/api/eval/my/events/`, `/my/sections/{sid}/`, `/my/event-teams/{id}/evaluation/` |
| `getResults(eventId)`, `getPrintData(sid)` | `GET /api/eval/events/{id}/results/`, `/sections/{sid}/print/` |
| `searchUsers(q)`, `getMyTrainings()` | `GET /api/events/users/`, `/api/events/my/trainings/` |
| `uploadMaterial(tid, file, title)`, `deleteMaterial(id)`, `listMaterials(eventId)`, `getMaterialUrl(id)` | `/api/events/tracks/{tid}/materials/`, `/materials/{id}/`, `/{id}/materials/`, `/materials/{id}/download/` |
| ○ `openRegistration(id)`, `closeRegistration(id)` | `POST /api/events/{id}/registration/open/`, `/close/` |
| ○ `enroll(eventId, trackId)`, `switchTrack(eventId, trackId)`, `cancelEnrollment(eventId)` | `POST, PUT, DELETE /api/events/{id}/enrollment/` |
| ○ `listEnrollments(trackId)` | `GET /api/events/tracks/{tid}/enrollments/` |

## 3. Маршруты и меню

| Путь | Роль | Экран |
|---|---|---|
| `/profile` (существующий) | любой | Новый блок «Ближайшие мероприятия»: карточки анонсов |
| `/events/:id` | любой | Карточка анонса. У акселератора кнопка «Записаться»; у записавшегося после мероприятия блок «Материалы направления» |
| `/expert`, `/expert/sections/:sid`, `/expert/sections/:sid/teams/:etId` | expert | Мои предзащиты, команды аудитории, форма оценки |
| `/organizer/templates`, `/organizer/templates/:id` | organizer | Список и конструктор оценочных листов |
| `/organizer/events` | organizer | Список мероприятий всех типов |
| `/organizer/events/new` | organizer | Создание: выбор типа, поля по типу; для защиты — выбор предзащиты и предпросмотр прошедших |
| `/organizer/events/:id` | organizer | Карточка: публикация; акселератор — направления, тренеры, запись; предзащита и защита — команды, аудитории, эксперты, приём оценок |
| `/organizer/events/:id/results` | organizer | Итоги; у предзащиты порог и «прошла / не прошла» |
| `/organizer/sections/:sid/print` | organizer | Печатная матрица без Sidebar, `window.print()` |
| `/trainer` | trainer | «Мои мероприятия»: направление, аудитория, время; после окончания «Выложить презентацию» |

Маршруты расписания — в [../02-schedule/frontend.md](../02-schedule/frontend.md).
Гард маршрута: если в `roles` нет нужной роли, редирект на `/` (удобство интерфейса; доступ проверяет бэкенд). Экран «Нет доступа»: заголовок «Нет доступа», для организаторского раздела «Этот раздел открыт только организаторам мероприятия.», кнопка «Вернуться в личный кабинет».
Пункты Sidebar по ролям: «Мои предзащиты» — expert; «Оценочные листы» и «Мероприятия» — organizer; «Мои мероприятия» — trainer; «Расписание» — mentor. Меню — объединение пунктов всех ролей человека.

## 4. Общие состояния экранов

| Состояние | Вид | Поведение |
|---|---|---|
| Загрузка | Скелетоны | Кнопки действий неактивны |
| Пусто | Иконка, заголовок, пояснение, основное действие | — |
| Ошибка сервера | Плашка с текстом и «Повторить» | Повторный запрос |
| Нет связи | Баннер «Нет связи. Показаны последние сохранённые данные, изменения не сохранятся.» | Действия, меняющие данные, неактивны или падают с «не удалось сохранить» |

Организатор на ширине < 1024 px: заглушка «Экран организатора рассчитан на компьютер».

## 5. Организатор

**Список мероприятий.** Заголовок «Мероприятия», кнопка «Создать мероприятие» **всегда видна** (и в пустом состоянии тоже). Фильтры: тип (Предзащита, Защита, Акселератор), статус публикации, статус приёма оценок, год. Значения фильтров хранятся в параметрах адреса (`?type=…&year=…`), чтобы ссылку можно было переслать (ПР18). Фильтра «Требует внимания» нет. Карточка: тип, название, дата и время, место, бейджи (публикация, приём оценок, расписание или запись).

**Создание** (все типы сохраняются черновиком; «Опубликовать» открывает подтверждение «Анонс увидят все пользователи лидерборда»).
1. Тип выбирается тремя карточками и после создания не меняется. Защита отдельно не создаётся — карточка защиты ведёт к пояснению.
2. Общие поля: название (placeholder зависит от типа), дата, начало, конец, место, описание.
3. Предзащита: шаблон (выбор или «Новый лист в конструкторе»), проходной балл (обязателен, подсказка «из N возможных»), способ добавления команд: «Через расписание» или «Вручную или из Excel». После публикации шаблон и порог неактивны.
4. Защита: шаблон, выбор завершённой и ещё не использованной предзащиты; после выбора — таблица из `passed-teams` с чекбоксами (прошедшие отмечены), счётчик «В защиту перейдут N команд», название. Способ составления очерёдности — как у предзащиты.
5. Акселератор: необязательное поле «Запись откроется автоматически» (дата и время, `registration_opens_at`); направления (роль свободным текстом, аудитория, описание, лимит мест) и тренеры (`+ тренер`, поиск пользователя от 2 символов, должность, компания). Повтор роли или аудитории подсвечивается.

**Карточка предзащиты и защиты.** Шапка: название, бейджи, «Опубликовать», «Открыть приём оценок» / «Завершить приём», «Итоги», «Расписание» (если есть), «Создать защиту» (когда приём завершён). Красная плашка причин, пока приём открыть нельзя: «Нельзя открыть приём оценок: сначала опубликуйте мероприятие» / «…сначала опубликуйте расписание» / «…{N команд без аудитории, в ауд. X нет экспертов}». Подпись под неактивной кнопкой: «Сначала опубликуйте» / «Сначала опубликуйте расписание» / «Причины — на красной плашке ниже». Блоки: «Команды без аудитории» (с выбором аудитории) сверху; аудитории аккордеоном — эксперты (поиск, удаление), команды (порядок, меню ⋮: переместить, «Не явилась», «Убрать из мероприятия»); «Добавить команду», «Импорт из Excel» (только без расписания и до открытия приёма), «Добавить аудиторию». При расписании перетаскивание порядка и импорт недоступны, подсказка у кнопки удаления: «Состав команд задаёт расписание». Текст блока для мероприятия с расписанием: «Порядок и время выступления задаёт расписание. Аудитории назначьте на шаге «Команды и аудитории»» (в прототипе устаревшая формулировка «Состав команд, аудитории и порядок выступления задаёт расписание» — заменить).
Если вернуть предзащиту в работу нельзя: «Предзащиту нельзя вернуть в работу: из неё создана защита».

**Итоги.** Таблица по командам: аудитория, оценок N из M, средний балл, вердикт «Прошла / Не прошла», «Не явилась», предупреждение «Неполные оценки: итог по N оценкам из M». Сводка по аудиториям.

**Конструктор оценочного листа.** Название, описание, критерии (название, описание, уровни «балл + описание»), добавление, удаление, порядок. Максимум листа считается автоматически; предпросмотр бланка; «Печать бланка» (пустая матрица, `/organizer/sections/:sid/print`).

**Акселератор.** Направления: роль, аудитория, тренеры, поле «Лимит мест», счётчик «N из M» / «Без лимита · N». «Записавшиеся» — раскрывающийся список по направлению (ФИО, группа, дата). Кнопка «Открыть запись» / «Закрыть запись» (вручную; запись закрывается автоматически в момент начала мероприятия). При лимите меньше числа записавшихся: «Лимит меньше числа записавшихся: записи сохранены, новых не будет.»

## 6. Эксперт (телефон 390 px, основной сценарий)

- «Мои предзащиты»: мероприятие, аудитория, прогресс «оценено N из M», статус приёма.
- Команды аудитории по порядку (`position`), поиск по названию, бейджи «Оценена», «Не явилась».
- Экран оценки: критерии, уровни кнопками-чипами (цель касания не меньше 44 px), описание выбранного уровня, «Сумма баллов N из max», комментарий, кнопки «Отправить», «Отправить и далее», «Не явилась» / «Снять отметку».
- Приём закрыт — плашка «Приём оценок закрыт», все поля только для чтения.

**Поведение формы оценки.**
- При каждом изменении баллы и комментарий пишутся в `localStorage` под ключом `eval:{etId}` (в `try/catch`); через 800 мс после последнего ввода уходит `PUT` со `status = draft`. Отправленная оценка автоматически не пересохраняется.
- При ошибке сети данные остаются локально, индикатор «Не сохранено», повтор с нарастающей паузой. После успешного ответа локальная копия удаляется.
- «Далее» ведёт к следующей команде по `position`, пропуская отмеченные как не явившиеся; на последней — «К списку».
- «Не явилась» отмечается прямо из формы; при ответе `team_has_evaluations` показать диалог подтверждения с числом оценок и повторить с `confirm: true`.
- Коды ошибок: `event_closed` и `event_not_open` переводят форму в режим чтения; `invalid_score` и `incomplete_evaluation` подсвечивают критерии из `details`; `team_absent` показывает баннер «Команда отмечена как не явившаяся»; `not_assigned` — экран «Нет доступа». Подсказка при незаполненных критериях: «Выберите уровень, чтобы отправить».

## 7. Тренер

- «Мои мероприятия»: направление, аудитория, дата, бейдж «Предстоит» / «Состоялся».
- Материалы: «Выложить» неактивна до окончания мероприятия, подпись «Выложить можно после окончания мероприятия»; список файлов, удаление, «Выложено: N файлов» / «Файлов пока нет».
- Диалог загрузки: название, файл, прогресс, ошибки размера (> 50 МБ) и формата (не PDF/PPTX), проверка на фронте до отправки.

## 8. Студент

- ЛК → «Ближайшие мероприятия»: карточки анонсов всех типов.
- Предзащита и защита: кнопки «Записаться» нет. Члену команды после публикации расписания — блок «Расписание вашей команды» (аудитория, время, номер); подробности — в системе 2.
- Акселератор: направления, тренеры, места. Состояния по `enrollment.state`:
  - `not_opened` — бейдж «Запись не открыта»; если у мероприятия задано `registration_opens_at`, текст «Запись откроется {дата} в {время}.», иначе «Запись откроет организатор.» (строка «Запись откроется 1 ноября в 10:00» в прототипе — демо-данные; ПР10);
  - `available` — кнопка «Записаться»; диалог «Записаться на «{роль}»» с остатком мест («Мест без ограничений.» / «Осталось N») и кнопкой «Записаться» / «Записываем…»;
  - `enrolled` — бейдж «Вы записаны», «Направление «X», ауд. Y. Сменить направление можно, пока открыта запись.»; диалог смены: «Перейти» / «Переводим…» с упоминанием старого направления;
  - `closed` — «Запись закрыта» (записанный студент видит своё направление; сменить или отменить запись нельзя, ПР10).
- Ошибка: «Места закончились, пока вы выбирали»; остаток в диалоге обновить из ответа.
- «Материалы направления» — только записанному и только после загрузки тренером.

## 9. Что не переносить из прототипа

Демо-панель (роль, «Сегодня в прототипе», «Сеть», «Ширина окна», «Открыть чужой раздел», «Сбросить демо», «Имитировать: место заняли»), данные в памяти вкладки, фиксированный список команд, один демо-файл Excel, телефон с единственным экспертом, заглушки блоков ЛК («Карточка профиля», «Метрика», «Проекты», «График»). Устаревшие тексты прототипа заменить: «Аудитории и время назначит система записи» (экран создания защиты) → «Аудитории назначает организатор; время и порядок задаёт расписание» (при расписании) или «Аудитории и порядок задаёт организатор» (без расписания).
