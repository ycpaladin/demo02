import api from './index'
import type { ListModel, ListField, ListView, FormSchema } from '../types'

export const getLists = (appId: string): Promise<ListModel[]> => api.get(`/apps/${appId}/lists/`)
export const getList = (appId: string, id: string): Promise<ListModel> => api.get(`/apps/${appId}/lists/${id}/`)
export const createList = (appId: string, data: Partial<ListModel>): Promise<ListModel> => api.post(`/apps/${appId}/lists/`, data)
export const updateList = (appId: string, id: string, data: Partial<ListModel>): Promise<ListModel> => api.put(`/apps/${appId}/lists/${id}/`, data)
export const deleteList = (appId: string, id: string): Promise<void> => api.delete(`/apps/${appId}/lists/${id}/`)
export const getListFields = (listId: string): Promise<ListField[]> => api.get(`/lists/${listId}/fields/`)
export const createListField = (listId: string, data: Partial<ListField>): Promise<ListField> => api.post(`/lists/${listId}/fields/`, data)
export const updateListField = (listId: string, id: string, data: Partial<ListField>): Promise<ListField> => api.put(`/lists/${listId}/fields/${id}/`, data)
export const deleteListField = (listId: string, id: string): Promise<void> => api.delete(`/lists/${listId}/fields/${id}/`)
export const reorderListFields = (listId: string, orderedIds: string[]): Promise<void> => api.post(`/lists/${listId}/fields/reorder/`, { ordered_ids: orderedIds })
export const getListViews = (listId: string): Promise<ListView[]> => api.get(`/lists/${listId}/views/`)
export const createListView = (listId: string, data: Partial<ListView>): Promise<ListView> => api.post(`/lists/${listId}/views/`, data)
export const updateListView = (listId: string, id: string, data: Partial<ListView>): Promise<ListView> => api.put(`/lists/${listId}/views/${id}/`, data)
export const deleteListView = (listId: string, id: string): Promise<void> => api.delete(`/lists/${listId}/views/${id}/`)
export const getFormSchema = (appId: string, listId: string): Promise<FormSchema> => api.get(`/apps/${appId}/lists/${listId}/form_schema/`)
