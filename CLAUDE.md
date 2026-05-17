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
    defaults={'name': '通用列表存储', 'description': '默认应用空间'}
)
"

# Verify DB connection
cd backend && python manage.py check --database default

# Generate test data (100 fields + 100K records)
cd backend && ./venv/bin/python load_test_data.py [list_id]
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

This is a **metadata-driven dynamic list system** — users define field types, content types, and lists through a UI; the system auto-generates PostgreSQL tables and provides CRUD with dual frontend+backend validation. No coding required to create new data collections.

### Backend (`backend/`)

Four Django apps, all mounted under `/api/`:

| App | Purpose |
|-----|---------|
| `core` | `BaseModel` (UUID PK + timestamps), `FieldType`, `FieldValidator` models; `FieldTypeRegistry` (cached singleton); `ValidationEngine` (generates DRF validators + frontend rules from field defs) |
| `applications` | `Application` (tree via `parent` self-FK), `Navigation` (menu items linking to lists or custom URLs) |
| `metadata` | `ContentType` (field templates with inheritance via `parent`), `ContentTypeField`, `List`; `ContentTypeManager.resolve_fields()` recursively merges parent fields (child overrides parent by key). `List.schema` JSON field stores extension fields, views, and form layout |
| `data` | `QueryBuilder` (parses `key:op:value` filter strings + JSON `where` with nested AND/OR; top-level OR auto-splits into UNION ALL), `SerializerFactory` (dynamically creates DRF Serializers with field validators and unique checks), `TrashView` (soft-delete + restore + permanent delete), `DynamicRecordView` (CRUD via `apps/{app_id}/lists/{list_id}/records/`) |

**Key design decisions:**
- **One dynamic table per list**: `dyn_{list.key}` with `id UUID`, `data JSONB`, `is_deleted BOOLEAN NOT NULL DEFAULT FALSE`, `created_at`, `updated_at`
- **JSONB queries**: all filtering/sorting done via `data->>'field_key'`; top-level OR conditions use UNION ALL to leverage per-field indexes
- **Automatic field indexes**: when a field is added to a list, an index is auto-created on `(data->>'key')` (GIN trigram for text fields, btree for others); dropped when field is removed. Inherited fields indexed on list creation
- **Soft delete**: lists use `is_deleted` flag on metadata row; records use `is_deleted = TRUE` real column (not JSONB), with partial index `WHERE is_deleted = FALSE`
- **Dual validation**: `ValidationEngine.build_field()` generates DRF validators; `ValidationEngine.build_frontend_rules()` generates Element Plus form rules — both from the same field definition
- **Content type inheritance**: `ContentTypeManager.resolve_fields()` recursively walks `parent` chain, child fields with same key override parent fields
- **Schema-based config**: extension fields, views, and form layout stored in `List.schema` JSONField (no separate `list_fields`/`list_views` tables). GET returns merged inherited+extension fields; PUT accepts extension fields only and diffs by ID
- **DRF pagination unwrapped**: the frontend axios interceptor detects `{count, results}` DRF responses and returns just `results` to callers

### Frontend (`frontend/`)

Vue 3 + TypeScript + Element Plus + Vite + vxe-table. Vite proxies `/api` to `localhost:8000`.

#### Layout

AppLayout.vue provides the shell: header with site name + "设置" dropdown, left sidebar driven by navigation API, main content via `<slot>`.

Header dropdown items: 列表设置 (when on a list page), 站点设置, 查看网站所有内容, 新建列表, 新建子站点.

#### File structure

```
src/
├── api/index.ts          # axios instance, DRF pagination unwrapper, error flattener
├── api/{applications,fieldTypes,contentTypes,lists,records,trash}.ts
├── types/index.ts        # All TypeScript interfaces (ListSchema, SchemaField, SchemaView, WhereNode, etc.)
├── utils/ruleEngine.ts   # Client-side validation rule builder from field definitions
├── router/index.ts       # All routes scoped under /apps/:appId
├── components/
│   ├── AppLayout.vue     # Shell: sidebar + header with settings dropdown + slot
│   ├── DynamicForm.vue   # Renders form fields from schema + layout groups (el-row/el-col)
│   ├── DynamicSearchBar.vue  # Generates search inputs from searchable fields
│   ├── FieldControl.vue  # Single field input (text/number/date/boolean/select), used by DynamicForm
│   ├── FieldDesigner.vue # Reusable field CRUD table with type-specific config panels
│   ├── WhereNodeEditor.vue   # Recursive WHERE condition editor (nested AND/OR groups)
│   └── fields/           # Per-field-type config components (TextConfig, NumberConfig, etc.)
└── views/
    ├── SiteOverview.vue  # "查看网站所有内容" — lists + child sites sorted by created_at
    ├── applications/
    │   └── AppList.vue
    ├── lists/
    │   ├── ListManagement.vue  # Default landing page for a site
    │   ├── ListDesigner.vue    # List field designer (unified save to schema)
    │   ├── ListData.vue        # Record table (vxe-table) with view switcher + pagination
    │   ├── RecordForm.vue      # Create / edit / view record (form-based, supports readonly mode)
    │   ├── ListSettings.vue    # Card page: info / fields / views / form
    │   ├── ListInfoEdit.vue    # Edit list name, description
    │   ├── ListViewManager.vue # View CRUD with WHERE condition editor
    │   └── FormLayoutEditor.vue # Form layout: groups, columns, field assignment
    └── settings/
        ├── SiteSettings.vue    # Card page: info / content-types / field-types / navigations / trash
        ├── SiteInfoEdit.vue
        ├── ContentTypeList.vue
        ├── ContentTypeDesigner.vue
        ├── FieldTypeList.vue
        ├── NavigationConfig.vue
        └── TrashPage.vue
```

**Important frontend patterns:**
- `getFormSchema(appId, listId)` returns field definitions + pre-built validation rules — the single source of truth for both form rendering and client-side validation
- `getListSchema(appId, listId)` / `updateListSchema(appId, listId, data)` — unified read/write for extension fields, views, and form layout
- `RecordForm.vue` handles create, edit, and view modes (via route name: `recordAdd`/`recordEdit`/`recordView`)
- API modules are thin wrappers around the axios instance; the interceptor handles DRF pagination unwrapping
- `FormSchema.rules[]` are Element Plus form rule objects, built server-side by `ValidationEngine.build_frontend_rules()`
- Sidebar menu items come from the navigation API (`/api/apps/:appId/navigations/`), filtered by `visible=true`
- View switching uses a dropdown in the action bar (last option: "编辑当前视图")
- Pagination uses standard OFFSET/LIMIT; `is_deleted = FALSE` partial index keeps deep pages fast

### Database

PostgreSQL via `psycopg2-binary`. Two categories of tables:
1. **Metadata tables** (Django-managed): `applications`, `field_types`, `field_validators`, `content_types`, `content_type_fields`, `lists` (with `schema` JSONField), `navigations`
2. **Dynamic data tables**: `dyn_{list.key}` — created on list creation, queried via raw SQL with `data->>'key'` JSONB operator. Each has `is_deleted BOOLEAN` real column with partial index

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
