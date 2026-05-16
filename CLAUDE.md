# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Django)

```bash
# Start dev server
cd backend && ./venv/bin/python manage.py runserver 8000

# Run migrations
cd backend && ./venv/bin/python manage.py makemigrations && ./venv/bin/python manage.py migrate

# Seed built-in field types and validators
cd backend && ./venv/bin/python manage.py seed_data

# Create default app
cd backend && ./venv/bin/python manage.py shell -c "
from applications.models import Application
app, created = Application.objects.get_or_create(
    key='default',
    defaults={'name': '通用列表存储', 'url_prefix': '/', 'description': '默认应用空间'}
)
"

# Verify DB connection
cd backend && python manage.py check --database default
```

### Frontend (Vue 3 + TypeScript)

```bash
# Dev server (proxies /api to localhost:8000)
cd frontend && npm run dev

# Type-check
cd frontend && npx vue-tsc --noEmit

# Build
cd frontend && npm run build
```

## Architecture

This is a **metadata-driven dynamic list system** — users define field types, content types, and lists through a UI; the system auto-generates MSSQL tables and provides CRUD with dual frontend+backend validation. No coding required to create new data collections.

### Backend (`backend/`)

Four Django apps, all mounted under `/api/`:

| App | Purpose |
|-----|---------|
| `core` | `BaseModel` (UUID PK + timestamps), `FieldType`, `FieldValidator` models; `FieldTypeRegistry` (cached singleton); `ValidationEngine` (generates DRF validators + frontend rules from field defs) |
| `applications` | `Application` (tree via `parent` self-FK, recursive URL prefix), `Navigation` (menu items linking to lists or custom URLs) |
| `metadata` | `ContentType` (field templates with inheritance via `parent`), `ContentTypeField`, `List`, `ListField`, `ListView`; `ContentTypeManager.resolve_fields()` recursively merges parent fields (child overrides parent by key) |
| `data` | `DynamicTableBuilder` (creates/drops `dyn_{key}` tables with id + JSON data column + timestamps), `QueryBuilder` (parses `key:op:value` filter strings into parameterized `JSON_VALUE` SQL), `SerializerFactory` (dynamically creates DRF Serializers with field validators and unique checks), `TrashView` (soft-delete + restore + permanent delete), `DynamicRecordView` (CRUD via `apps/{app_id}/lists/{list_url}/records/`) |

**Key design decisions:**
- **One dynamic table per list**: `dyn_{list.key}` with `id UNIQUEIDENTIFIER`, `data NVARCHAR(MAX)` (JSON), `created_at`, `updated_at`
- **JSON_VALUE queries**: all filtering/sorting done via `JSON_VALUE(data, '$.field_key')` — no DDL changes needed when fields change
- **Soft delete**: lists use `is_deleted` flag on metadata row; records use `_is_deleted: true` inside the JSON data column
- **Dual validation**: `ValidationEngine.build_field()` generates DRF validators; `ValidationEngine.build_frontend_rules()` generates Element Plus form rules — both from the same field definition
- **Content type inheritance**: `ContentTypeManager.resolve_fields()` recursively walks `parent` chain, child fields with same key override parent fields
- **DRF pagination unwrapped**: the frontend axios interceptor detects `{count, results}` DRF responses and returns just `results` to callers

### Frontend (`frontend/`)

Vue 3 + TypeScript + Element Plus + Vite. Vite proxies `/api` to `localhost:8000`.

#### Layout

AppLayout.vue provides the shell: header with site name + "设置" dropdown, left sidebar driven by navigation API, main content via `<slot>`.

Header dropdown items: 站点设置, 查看网站所有内容, 新建列表, 新建子站点.

#### File structure

```
src/
├── api/index.ts          # axios instance, DRF pagination unwrapper, error flattener
├── api/{applications,fieldTypes,contentTypes,lists,records,trash}.ts
├── types/index.ts        # All TypeScript interfaces
├── utils/ruleEngine.ts   # Client-side validation rule builder from field definitions
├── router/index.ts       # All routes scoped under /apps/:appId
├── components/
│   ├── AppLayout.vue     # Shell: sidebar + header with settings dropdown + slot
│   ├── DynamicForm.vue   # Renders form fields from schema, applies validation rules
│   ├── DynamicSearchBar.vue  # Generates search inputs from searchable fields
│   └── ViewTabs.vue      # Tag-based view switcher
└── views/
    ├── SiteOverview.vue  # "查看网站所有内容" — lists + child sites sorted by created_at
    ├── applications/
    │   └── AppList.vue
    ├── lists/
    │   ├── ListManagement.vue  # Default landing page for a site
    │   ├── ListDesigner.vue    # List field designer
    │   ├── ListData.vue        # Record table with search/filter/pagination
    │   ├── RecordForm.vue      # Create / edit record (form-based)
    │   ├── ListSettings.vue    # Card page: info / fields / views
    │   └── ListInfoEdit.vue    # Edit list name, description, url
    └── settings/
        ├── SiteSettings.vue    # Card page: info / content-types / field-types / navigations / trash
        ├── SiteInfoEdit.vue    # Edit site name, key, url_prefix, description
        ├── ContentTypeList.vue
        ├── ContentTypeDesigner.vue
        ├── FieldTypeList.vue
        ├── NavigationConfig.vue
        └── TrashPage.vue
```

**Important frontend patterns:**
- `getFormSchema(appId, listId)` returns field definitions + pre-built validation rules — the single source of truth for both form rendering and client-side validation
- `RecordForm.vue` handles both create and edit (edit mode when `recordId` route param exists)
- API modules are thin wrappers around the axios instance; the interceptor handles DRF pagination unwrapping
- `FormSchema.rules[]` are Element Plus form rule objects, built server-side by `ValidationEngine.build_frontend_rules()`
- Sidebar menu items come from the navigation API (`/api/apps/:appId/navigations/`), filtered by `visible=true`

### Database

MSSQL via `mssql-django`. Two categories of tables:
1. **Metadata tables** (Django-managed): `applications`, `field_types`, `field_validators`, `content_types`, `content_type_fields`, `lists`, `list_fields`, `list_views`, `navigations`
2. **Dynamic data tables**: `dyn_{list.key}` — created/dropped by `DynamicTableBuilder`, queried via raw SQL with `JSON_VALUE`

Built-in seed data (`python manage.py seed_data`): 9 field types (text, number, date, boolean, long_text, select, multi_select, attachment, reference) and 4 validators (required, phone, email, id_card).


## gstack

### 1. 使用规则
- 所有网页浏览一律使用 **gstack 的 `/browse`**。
- **禁止**使用任何 `mcp__claude-in-chrome__*` 工具。
- 当需要浏览网页、抓取内容、分析页面时，始终执行：

### 2. 可用技能列表（gstack 提供）
- /office-hours  
- /plan-ceo-review  
- /plan-eng-review  
- /plan-design-review  
- /design-consultation  
- /design-shotgun  
- /design-html  
- /review  
- /ship  
- /land-and-deploy  
- /canary  
- /benchmark  
- /browse  
- /connect-chrome  
- /qa  
- /qa-only  
- /design-review  
- /setup-browser-cookies  
- /setup-deploy  
- /setup-gbrain  
- /retro  
- /investigate  
- /document-release  
- /document-generate  
- /codex  
- /cso  
- /autoplan  
- /plan-devex-review  
- /devex-review  
- /careful  
- /freeze  
- /guard  
- /unfreeze  
- /gstack-upgrade  
- /learn

### 3. 使用要求
- 在执行任何编码、审查、规划、QA、发布相关任务前，必须先：Load gstack
- 所有涉及浏览器、URL、页面内容的任务必须使用 `/browse`。
- 遇到需要规划的任务，优先使用 `/autoplan` 或相关 plan-* 技能。
- 遇到需要安全审计时使用 `/cso`。
- 遇到需要 QA 时使用 `/qa` 或 `/qa-only`。
- 遇到需要发布或上线时使用 `/ship`、`/land-and-deploy`、`/canary`。

### 4. 团队协作（可选）
如果你希望团队成员也能使用 gstack，请将 gstack 添加到项目的共享配置中（例如 `.claude/skills` 或项目级 CLAUDE.md）。
