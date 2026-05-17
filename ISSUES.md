# 项目审查问题清单

**审查日期**: 2026-05-17
**分支**: main
**综合评分**: N/A — 缺少 linter、测试、死代码检测工具

---

## 自动化健康检查

| 类别 | 工具 | 评分 | 状态 |
|------|------|------|------|
| TypeScript 类型检查 | vue-tsc --noEmit | 10/10 | CLEAN — 0 错误 |
| 代码检查 | — | N/A | 未配置 linter |
| 测试 | — | N/A | 无测试脚本 |
| 死代码 | — | N/A | 未配置 |
| Shell 脚本 | — | N/A | 无 shell 脚本 |

---

## CRITICAL（必须修复）

### C1. SQL 注入 — QueryBuilder
**文件**: `backend/data/query_builder.py:30,52,70`

用户传入的筛选器 `key` 和排序 `sort` 直接拼接到 SQL 字符串中。攻击者可构造特殊参数执行任意 SQL。

### C2. SQL 注入 — DynamicTableBuilder
**文件**: `backend/data/table_builder.py:8,24,36,38`

`table_name` 来源于用户创建的 List `key` 字段，直接拼接到 CREATE/DROP TABLE 语句中。

### C3. SQL 注入 — SerializerFactory 唯一性校验
**文件**: `backend/data/serializer_factory.py:58-61`

唯一性校验中的字段 key 直接拼接到 SQL 中。

### C4. 无认证/授权机制
**文件**: `backend/config/settings.py:86-92`

所有 API 端点均未配置 `DEFAULT_AUTHENTICATION_CLASSES` 和 `DEFAULT_PERMISSION_CLASSES`。任何能访问服务的人都可以读写所有数据。

### C5. NameError Bug — `list_url` 未定义
**文件**: `backend/data/views.py:115`

```python
lst = List.objects.get(application_id=app_id, url=list_url, is_deleted=False)
```
`list_url` 在该作用域中不存在（URL kwarg 是 `list_id`）。`DynamicRecordBatchView.patch()` 完全不可用。

### C6. SECRET_KEY 硬编码
**文件**: `backend/config/settings.py:6`

```python
SECRET_KEY = 'django-insecure-dev-key-change-in-production-xxx'
```
公开占位密钥，攻击者可利用其伪造会话 cookie。

### C7. DEBUG=True + ALLOWED_HOSTS=['*']
**文件**: `backend/config/settings.py:8,10`

错误页面会泄露完整堆栈跟踪、环境变量和源代码。未限制 Host 头部。

### C8. 数据库密码明文
**文件**: `backend/config/settings.py:59-67`

```python
'USER': 'user',
'PASSWORD': '@1Qazxsw2',
'HOST': '192.168.11.219',
```
数据库密码明文存储在版本控制中。已从 MSSQL 迁移至 PostgreSQL。

### C9. CORS 全开
**文件**: `backend/config/settings.py:84`

```python
CORS_ALLOW_ALL_ORIGINS = True
```

### C10. 依赖版本不存在于 npm 官方仓库
**文件**: `frontend/package.json`

| 包名 | 声明版本 | npm 官方最新 |
|------|----------|-------------|
| typescript | `^6.0.3` | 5.8.x |
| vite | `^8.0.12` | 6.x |
| vue-router | `^5.0.6` | 4.5.x |
| vue-tsc | `^3.2.8` | 2.2.x |

这些版本号在 npm 官方仓库不存在。项目依赖 npmmirror.com 镜像。新开发者使用默认 registry 将无法安装。

---

## HIGH

| # | 描述 | 位置 |
|---|------|------|
| H1 | 静默异常吞没 `except Exception: pass` | `data/trash.py:31` |
| H2 | CSRF 中间件开启但无认证，行为不一致 | `settings.py:32` |
| H3 | 多步操作无事务保护（reorder、batch update） | `metadata/views.py:31-33`, `data/views.py:123-133` |
| H4 | 无 CI/CD / Docker 部署配置 | 项目根目录 |
| H5 | `.gitignore` 未忽略 `.playwright-mcp/`（70+ 自动生成文件） | `.gitignore` |

---

## MEDIUM

| # | 描述 | 位置 |
|---|------|------|
| M1 | `UniqueValidator.__call__` 是空操作（no-op），实际校验在别处 | `core/validation.py:120-126` |
| M2 | `Navigation.list` 字段名遮蔽 Python 内置 `list` 类型 | `applications/models.py:24` |
| M3 | TrashView N+1 查询 + 无分页 — 数据量大时性能问题 | `data/trash.py:15-52` |
| M4 | `DynamicForm.vue` 的 `initialData` prop 变更时不更新表单 | `components/DynamicForm.vue:62` |
| M5 | 字段移除后 formRules 不清除（幽灵验证规则残留） | `components/DynamicForm.vue:65-71` |
| M6 | `batchUpdate` 已导入但从未调用 — 批量编辑按钮是空操作 | `views/lists/ListData.vue:32` |
| M7 | 5 个重复的死代码视图目录（与 `views/settings/` 重复） | `views/content-types/`, `views/field-types/`, `views/navigations/`, `views/trash/` |
| M8 | 空 `backend/package-lock.json` 应删除 | `backend/package-lock.json` |
| M9 | 缺少 `lint`/`test`/`typecheck` npm scripts | `frontend/package.json` |
| M10 | `openpyxl` 依赖已声明但未使用 | `backend/requirements.txt:5` |
| M11 | 无 `.env.example` 说明必需环境变量 | 项目根目录 |
| M12 | 未使用 Pinia/Vuex — 每个视图重复请求相同数据 | 全局架构 |
| M13 | 无 404 回退路由，未匹配路径白屏 | `frontend/src/router/index.ts` |

---

## LOW

| # | 描述 | 位置 |
|---|------|------|
| L1 | `formRules` 类型 `Record<string, unknown>` 应改为 `Record<string, FormRule[]>` | `components/DynamicForm.vue:63` |
| L2 | `formRef` 未参数化 `ref<FormInstance>()` | `components/FieldDesigner.vue:173` |
| L3 | `.claude/settings.local.json` 权限过于宽泛 | `.claude/` |
| L4 | 路由器重定向可能产生 `/apps/undefined/lists` | `router/index.ts:6` |
| L5 | 缺少 `.editorconfig`、`.gitattributes` | 项目根目录 |

---

## 修复优先级建议

1. **立即（安全）**: C1-C3 SQL 注入、C4 认证、C5 NameError、C6-C9 安全配置
2. **本周**: H1-H3 异常处理/事务、C10 依赖版本、H5 gitignore
3. **下次迭代**: M3 性能、M4-M7 前端 bug、M8-M13 配置补充
