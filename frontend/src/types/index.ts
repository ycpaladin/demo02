export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}

export interface Application extends BaseEntity {
  name: string
  key: string
  description: string
  parent: string | null
  order: number
  children?: Application[]
}

export interface FieldType extends BaseEntity {
  name: string
  key: string
  description: string
  icon: string
  builtin: boolean
  config_schema: Record<string, unknown>
}

export interface FieldValidator extends BaseEntity {
  name: string
  key: string
  description: string
  builtin: boolean
  rule_type: 'regex' | 'range' | 'required' | 'expression'
  rule_config: Record<string, unknown>
  error_message: string
}

export interface ContentType extends BaseEntity {
  name: string
  key: string
  description: string
  parent: string | null
  fields?: ContentTypeField[]
}

export interface ContentTypeField extends BaseEntity {
  content_type: string
  field_type: string
  field_type__key?: string
  field_type__name?: string
  name: string
  key: string
  required: boolean
  unique: boolean
  searchable: boolean
  search_type: string
  order: number
  config: Record<string, unknown>
  validators: string[]
}

export interface ListModel extends BaseEntity {
  application: string
  name: string
  key: string
  description: string
  content_type: string | null
  table_name: string
  schema: ListSchema
  is_deleted: boolean
  deleted_at: string | null
}

export interface ListSchema {
  fields: SchemaField[]
  views: SchemaView[]
  form: SchemaForm
}

export interface SchemaField {
  id?: string
  key: string
  name: string
  field_type: string
  required: boolean
  unique: boolean
  searchable: boolean
  search_type: string
  order: number
  config: Record<string, unknown>
  validators: string[]
  is_extension?: boolean // GET 时标记是否为扩展字段
}

export interface SchemaView {
  id?: string
  url_key: string
  name: string
  is_default: boolean
  page_size_options: number[]
  default_page_size: number
  fields: { key: string; visible: boolean }[]
  where?: WhereNode
  orderBy: { field: string; sort: 'ASC' | 'DESC' }[]
}

export type WhereNode = WhereBranch | WhereLeaf

export interface WhereBranch {
  logic: 'AND' | 'OR'
  left: WhereNode
  right?: WhereNode
}

export interface WhereLeaf {
  field: string
  comparison: string
  value: string
}

export interface SchemaForm {
  groups: FormGroup[]
}

export interface FormGroup {
  name: string
  columns: number
  fields: { key: string; col_span: number }[]
}

export interface Navigation extends BaseEntity {
  application: string
  name: string
  link_type: 'list' | 'custom_url'
  list: string | null
  custom_url: string
  icon: string
  parent: string | null
  order: number
  visible: boolean
}

export interface FormField {
  key: string
  name: string
  field_type: string
  required: boolean
  unique: boolean
  searchable: boolean
  search_type: string
  config: Record<string, unknown>
  rules: FormRule[]
  validators?: FormRule[]
  options?: string[]
}

export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string
  type?: string
  min?: number
  max?: number
  pattern?: string | RegExp
}

export interface FormSchema {
  list_id: string
  list_name: string
  fields: FormField[]
}

export interface RecordsResponse {
  total: number
  page: number
  page_size: number
  results: RecordItem[]
}

export interface RecordItem {
  id: string
  data: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface TrashItem {
  id: string
  type: 'list' | 'record'
  name: string
  list_id?: string
  list_url?: string
  deleted_at: string | null
}
