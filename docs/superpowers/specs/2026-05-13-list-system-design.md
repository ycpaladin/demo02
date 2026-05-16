# 通用列表系统 需求设计文档

**日期**：2026-05-13
**状态**：设计定稿，待实现

---

## 一、概述

一个元数据驱动的动态列表系统，使用者无需编写代码即可完成以下闭环：

1. 定义字段类型（内置 + 自定义）
2. 将字段组合为"内容类型"（支持继承）
3. 创建"列表"，绑定内容类型或独立定义字段
4. 系统自动在 MSSQL 中创建物理数据表
5. 对列表数据进行增删改查、筛选排序分页、导入导出
6. 提交数据时根据字段定义执行前后端双重校验
7. 删除的数据进入回收站，可恢复或彻底删除

---

## 二、技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus |
| 后端 | Python(虚拟环境venv目录) + Django REST Framework |
| 数据库 | MSSQL（元数据：普通关系表；数据：每列表独立建表，JSON 列存储字段值） |
| 权限 | 后续添加 |

---

## 三、功能模块

### 3.1 应用空间

- 应用支持层级结构（parent 自引用），形成树形组织
- 每个应用有独立 `url_prefix`，子应用 URL 由父级前缀递归拼接
- 例：`/admin/cms/news` 表示 企业管理平台 → 内容管理 → 新闻中心
- 应用下所有列表、回收站、导航配置均归属该应用

### 3.2 字段类型管理

**内置字段类型**：

| 字段类型 | 存储格式 | 搜索方式 |
|----------|----------|----------|
| 文本 | string | fuzzy (LIKE) |
| 数字 | number | range |
| 日期 | string (ISO 8601) | range |
| 布尔 | boolean | exact |
| 长文本 | string | fuzzy |
| 下拉选项 | string | exact (IN) |
| 多选 | array of string | exact (IN) |
| 附件 | object {url, name, size} | — |
| 关联引用 | string (record id) | exact |

- 支持注册自定义字段类型，自定义字段与内置字段在表单渲染、校验、搜索等方面的处理机制一致

### 3.3 字段可搜索配置

- 每个字段可配置 `searchable`（是否作为搜索条件）
- `search_type` 根据字段类型自动映射，支持：fuzzy / range / exact
- 前端数据页面的搜索栏根据可搜索字段动态生成搜索输入控件

### 3.4 验证器管理

- 内置验证规则：required、max_length、min_length、pattern、min、max、min_date、max_date、allowed_types、max_size 等
- 唯一性校验（unique）作为字段级配置项
- 自定义验证器采用**声明式规则**，存储 `rule_type` + `rule_config`（JSON），一次定义，前后端各自解析：
  - 前端 RuleEngine 生成 Element Plus Form Rules
  - 后端 RuleEngine 生成 DRF Validator
- 复杂校验逻辑（跨字段等）使用 `expression` 类型，仅在后端执行，前端通过 `/records/validate/` 接口调用

### 3.5 内容类型

- 内容类型是由若干字段组成的"结构模板"
- 支持继承：子类型递归合并所有父级字段，同名字段子覆盖父
- 例：基础实体（名称、创建时间、状态）→ 文章（继承基础实体 + 正文、摘要、发布日期）→ 新闻稿（继承文章 + 新闻来源、记者）

### 3.6 列表管理

- 两种字段来源：
  - **绑定内容类型**：继承内容类型的字段定义，统一维护
  - **独立添加字段**：不绑定内容类型，列表自行管理字段
- 创建列表时自动生成物理数据表 `dyn_{list.key}`（id + JSON 数据列 + 时间戳）
- 对于标记唯一或常被查询的字段，可选自动创建计算列和索引
- 列表 URL：默认值为 `/list{n}`（n = 同应用下列表数 + 1），用户可自定义

### 3.7 列表视图

- 每个列表支持多个视图
- 每个视图有独立的 `url_key`，默认视图的 url_key 为 `"default"`
- 视图可配置：可见字段列表、默认排序、默认筛选条件、每页条数
- 前端数据页面顶部显示视图标签页，点击切换视图，可新建/编辑/删除视图

### 3.8 数据操作

- 完整 CRUD
- 分页列表，支持多条件组合筛选（eq/neq/contains/startswith/gt/gte/lt/lte/in/nin/isnull）
- 排序（支持多字段）
- 新增和编辑使用独立页面路由（`/lists/:id/data/add` 和 `/lists/:id/data/:recordId/edit`）
- 批量编辑在当前列表页面内完成（勾选记录 → 选择字段 → 设置新值 → 执行）
- 导出：Excel / CSV / JSON
- 导入：上传 Excel / CSV，含字段校验

### 3.9 回收站

- 列表删除 → 软删除（lists.is_deleted = true），动态表保留
- 记录删除 → JSON 内标记 `_is_deleted: true`，正常查询自动过滤
- 应用级回收站页面，分"已删除列表"和"已删除记录"两个标签
- 操作：恢复（取消标记）/ 彻底删除（物理删除，列表则同时删除动态表）

### 3.10 菜单导航

- 每个应用可配置导航菜单
- 菜单项类型：列表（关联已有列表）/ 自定义链接
- 支持二级菜单分组（parent 自引用）
- 菜单项可排序、可隐藏

---

## 四、数据模型

### 4.1 元数据表（MSSQL 普通关系表）

#### applications
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| name | nvarchar | 应用名称 |
| key | nvarchar | 唯一标识 |
| description | nvarchar | |
| url_prefix | nvarchar | URL 前缀 |
| parent | FK → self, nullable | 父应用 |
| order | int | 排序 |
| created_at / updated_at | datetime2 | |

#### field_types
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| name | nvarchar | 显示名称 |
| key | nvarchar (唯一) | 标识符 |
| description | nvarchar | |
| icon | nvarchar | 图标 |
| builtin | bool | 是否内置 |
| config_schema | JSON | 该字段类型支持的配置项定义 |
| created_at / updated_at | datetime2 | |

#### field_validators
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| name | nvarchar | 显示名称 |
| key | nvarchar (唯一) | 标识符 |
| description | nvarchar | |
| builtin | bool | 是否内置 |
| rule_type | nvarchar | regex / range / expression |
| rule_config | JSON | 规则参数 |
| error_message | nvarchar | 校验失败提示 |
| created_at | datetime2 | |

#### content_types
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| name | nvarchar | 显示名称 |
| key | nvarchar (唯一) | 标识符 |
| description | nvarchar | |
| parent | FK → self, nullable | 父内容类型 |
| created_at / updated_at | datetime2 | |

#### content_type_fields
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| content_type | FK → content_types | 所属内容类型 |
| field_type | FK → field_types | 字段类型 |
| name | nvarchar | 字段显示名 |
| key | nvarchar | 字段标识 |
| required | bool | 是否必填 |
| unique | bool | 是否唯一 |
| searchable | bool | 是否可搜索 |
| search_type | nvarchar | fuzzy / range / exact |
| order | int | 排序 |
| config | JSON | 字段配置（如选项列表、最大长度等） |
| validators | JSON | 关联的验证器 key 列表 |
| created_at / updated_at | datetime2 | |

#### lists
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| application | FK → applications | 所属应用 |
| name | nvarchar | 列表名称 |
| key | nvarchar (唯一) | 标识符 |
| description | nvarchar | |
| content_type | FK → content_types, nullable | 绑定的内容类型 |
| url | nvarchar | 访问路径标识，默认 /list{n} |
| table_name | nvarchar | 动态表名 dyn_{key} |
| is_deleted | bool (default false) | 软删除标记 |
| deleted_at | datetime2, nullable | 删除时间 |
| created_at / updated_at | datetime2 | |

#### list_fields
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| list | FK → lists | 所属列表 |
| field_type | FK → field_types | 字段类型 |
| name | nvarchar | 字段显示名 |
| key | nvarchar | 字段标识 |
| required / unique / searchable / search_type | | 同 content_type_fields |
| order / config / validators | | 同 content_type_fields |

#### list_views
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| list | FK → lists | 所属列表 |
| name | nvarchar | 视图名称 |
| url_key | nvarchar | URL 标识，默认 "default" |
| is_default | bool | 是否默认视图 |
| config | JSON | 视图配置（visible_fields, default_sort, default_filter, page_size） |
| order | int | |
| created_at | datetime2 | |

#### navigations
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| application | FK → applications | 所属应用 |
| name | nvarchar | 菜单项名称 |
| link_type | nvarchar | list / custom_url |
| list | FK → lists, nullable | 关联的列表 |
| custom_url | nvarchar, nullable | 自定义链接 |
| icon | nvarchar, nullable | 图标 |
| parent | FK → self, nullable | 父菜单项（二级菜单） |
| order | int | |
| visible | bool | |

### 4.2 动态数据表

每个列表在创建时自动生成一张物理表：

```sql
CREATE TABLE dyn_{list.key} (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWSEQUENTIALID(),
    data NVARCHAR(MAX) NOT NULL,  -- JSON 存储所有字段值
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

**JSON 数据格式**：
```json
{
  "title": "产品发布v2",
  "body": "正文内容...",
  "status": "已发布",
  "published_date": "2026-05-01",
  "_is_deleted": false,
  "_deleted_at": null
}
```

**可选优化**：对唯一字段或常被筛选/排序的字段，创建计算列并建索引：
```sql
ALTER TABLE dyn_blog ADD title_c AS JSON_VALUE(data, '$.title');
CREATE UNIQUE INDEX IX_title ON dyn_blog(title_c) WHERE JSON_VALUE(data, '$._is_deleted') IS NULL OR JSON_VALUE(data, '$._is_deleted') = 'false';
```

---

## 五、API 设计

### 5.1 元数据管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/apps/` | 应用管理 |
| CRUD | `/api/apps/{id}/navigations/` | 导航菜单 |
| CRUD | `/api/field-types/` | 字段类型（内置不可删） |
| CRUD | `/api/validators/` | 自定义验证器 |
| CRUD | `/api/content-types/` | 内容类型 |
| CRUD | `/api/content-types/{id}/fields/` | 内容类型字段 |
| CRUD | `/api/apps/{app_id}/lists/` | 列表（已删除的不返回） |
| CRUD | `/api/lists/{id}/fields/` | 列表独立字段 |
| CRUD | `/api/lists/{id}/views/` | 列表视图 |
| GET | `/api/lists/{id}/form-schema/` | 返回字段+校验规则（前端渲染用） |

### 5.2 数据操作 API

基路径：`/{app_path}/lists/{list_url}/records/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/?page=&size=&sort=&order=&filter=` | 分页列表（自动过滤已删除） |
| GET | `/{id}/` | 单条详情 |
| POST | `/` | 创建记录（含校验） |
| PUT | `/{id}/` | 更新记录（含校验） |
| DELETE | `/{id}/` | 删除记录（软删除） |
| PATCH | `/batch/` | 批量编辑 |
| POST | `/validate/` | 仅校验不入库（前端调用） |
| GET | `/export/?format=xlsx` | 导出 |
| POST | `/import/` | 导入 |

**视图参数**：`/{app_path}/lists/{list_url}/records/?view={view_url_key}`

**筛选参数格式**：
```
?filter=title:contains:关键词,status:eq:已发布,created_at:gte:2026-01-01
```
支持操作符：`eq` `neq` `contains` `startswith` `gt` `gte` `lt` `lte` `in` `nin` `isnull`

### 5.3 回收站 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/apps/{app_id}/trash/` | 回收站列表（列表+记录） |
| POST | `/api/apps/{app_id}/trash/{item_id}/restore/` | 恢复 |
| DELETE | `/api/apps/{app_id}/trash/{item_id}/` | 彻底删除 |
| GET | `/lists/{list_url}/records/trash/` | 某列表下已删除的记录 |

---

## 六、前端页面

### 6.1 整体布局

```
┌──────────────────────────────────────────────────────────┐
│  [站点名称]                            [设置 ▾]          │
│                                       ├ 站点设置          │
│                                       ├ 查看网站所有内容   │
│                                       ├ 新建列表          │
│                                       └ 新建子站点         │
├───────────┬──────────────────────────────────────────────┤
│ 侧边栏     │  主内容区                                     │
│ (导航菜单)  │                                              │
│           │                                              │
│ 首页       │                                              │
│ 博客列表    │                                              │
│ ...       │                                              │
└───────────┴──────────────────────────────────────────────┘
```

- 侧边栏数据来源：菜单配置（`/api/apps/:appId/navigations/`），仅渲染 `visible=true` 的项
- 设置下拉菜单提供 4 个入口：站点设置、查看网站所有内容、新建列表（跳转列表页并弹窗）、新建子站点（对话框）

### 6.2 页面路由

```
/apps                                                   — 应用列表
/apps/:appId                                            — 重定向到 /apps/:appId/lists
/apps/:appId/lists                                      — 列表管理（默认首页）
/apps/:appId/lists/:listId/data                         — 数据表格视图（默认视图）
/apps/:appId/lists/:listId/data/add                     — 新增记录
/apps/:appId/lists/:listId/data/:recordId/edit          — 编辑记录
/apps/:appId/lists/:listId/design                       — 列表字段设计器
/apps/:appId/lists/:listId/settings                     — 列表设置（卡片页）
/apps/:appId/lists/:listId/settings/info                — 列表基本信息编辑
/apps/:appId/lists/:listId/settings/fields              — 列表字段管理
/apps/:appId/lists/:listId/settings/views               — 列表视图管理
/apps/:appId/overview                                   — 查看网站所有内容
/apps/:appId/settings                                   — 站点设置（卡片页）
/apps/:appId/settings/info                               — 站点基本信息编辑
/apps/:appId/settings/content-types                      — 内容类型管理
/apps/:appId/settings/content-types/:ctId                — 内容类型设计器
/apps/:appId/settings/field-types                        — 字段类型管理
/apps/:appId/settings/navigations                        — 菜单导航配置
/apps/:appId/settings/trash                              — 回收站
```

### 6.3 站点设置页

分类卡片从左往右排列，点击跳转到对应的独立设置页面：

| 卡片 | 路由 | 说明 |
|------|------|------|
| 站点信息 | `settings/info` | 编辑名称、标识、URL 前缀、描述 |
| 内容类型 | `settings/content-types` | 内容类型 CRUD + 设计器 |
| 字段管理 | `settings/field-types` | 内置/自定义字段类型管理 |
| 菜单配置 | `settings/navigations` | 侧边栏导航菜单配置 |
| 回收站 | `settings/trash` | 已删除列表 + 已删除记录 |

### 6.4 列表设置页

分类卡片 + 独立路由子页面：

| 卡片 | 路由 | 说明 |
|------|------|------|
| 基本信息 | `settings/info` | 编辑名称、描述、URL |
| 字段管理 | `settings/fields` | 列表字段定义（复用 ListDesigner） |
| 视图管理 | `settings/views` | 列表视图配置 |

### 6.5 查看网站所有内容

按创建时间倒序排列，分组显示：
- **列表**：当前站点下所有列表，以卡片形式展示名称/标识/URL/记录数
- **子站点**：当前站点的子站点，以卡片形式展示

### 6.6 核心交互

- **内容类型设计器**：选择父级 → 添加/拖拽字段 → 配置每个字段的校验、搜索等
- **数据表格页**：顶部视图标签切换 → 搜索栏（可搜索字段动态生成）→ 表格 → 分页 → 批量编辑栏
- **新增/编辑页**：独立页面，根据字段定义渲染表单，前端即时校验，提交时后端双重校验
- **回收站**：已删除列表 + 已删除记录两个标签，每项旁有恢复和彻底删除按钮

---

## 七、核心引擎模块（后端）

| 模块 | 职责 |
|------|------|
| `FieldTypeRegistry` | 注册/管理字段类型，内置 + 可扩展 |
| `ContentTypeManager` | 内容类型 CRUD + 字段继承解析 |
| `DynamicTableBuilder` | 创建/删除动态表，管理计算列和索引 |
| `ValidationEngine` | 根据字段+验证器定义生成校验规则 |
| `SerializerFactory` | 动态生成 DRF Serializer，注入校验 |
| `QueryBuilder` | 构建 JSON_VALUE 筛选查询、排序、分页 |
| `ViewResolver` | 根据视图配置解析可见字段和默认参数 |
| `TrashManager` | 软删除/恢复/真删除操作 |

---

## 八、关键设计决策

1. **每列表独立建表**（而非统一数据表），数据隔离、查询性能好、运维灵活
2. **JSON 列存储字段值**（而非动态 DDL 改表结构），字段变更零成本
3. **验证器声明式定义**，一次配置前后端各自解析，无需分别编写校验代码
4. **软删除 + 回收站**，删除安全可恢复，真删除需在回收站二次确认
5. **内容类型支持继承**，减少重复字段定义，子类型可覆盖父级字段配置
6. **应用层级 URL 拼接**，天然支持多租户/多模块空间隔离
