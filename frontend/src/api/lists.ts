import api from './index'
import type { ListModel, ListSchema, FormSchema } from '../types'

export const getLists = (appId: string): Promise<ListModel[]> => api.get(`/apps/${appId}/lists/`)
export const getList = (appId: string, id: string): Promise<ListModel> => api.get(`/apps/${appId}/lists/${id}/`)
export const createList = (appId: string, data: Partial<ListModel>): Promise<ListModel> => api.post(`/apps/${appId}/lists/`, data)
export const updateList = (appId: string, id: string, data: Partial<ListModel>): Promise<ListModel> => api.put(`/apps/${appId}/lists/${id}/`, data)
export const deleteList = (appId: string, id: string): Promise<void> => api.delete(`/apps/${appId}/lists/${id}/`)

// Schema — 统一读写字段 + 视图 + 表单布局
export const getListSchema = (appId: string, listId: string): Promise<ListSchema> =>
  api.get(`/apps/${appId}/lists/${listId}/schema/`)
export const updateListSchema = (appId: string, listId: string, data: ListSchema): Promise<void> =>
  api.put(`/apps/${appId}/lists/${listId}/schema/`, data)

export const getFormSchema = (appId: string, listId: string): Promise<FormSchema> => api.get(`/apps/${appId}/lists/${listId}/form_schema/`)
