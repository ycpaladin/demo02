import api from './index'
import type { RecordsResponse, RecordItem } from '../types'

export const getRecords = (appId: string, listId: string, params?: Record<string, unknown>): Promise<RecordsResponse> => api.get(`/apps/${appId}/lists/${listId}/records/`, { params })
export const getRecord = (appId: string, listId: string, id: string): Promise<RecordItem> => api.get(`/apps/${appId}/lists/${listId}/records/${id}/`)
export const createRecord = (appId: string, listId: string, data: Record<string, unknown>): Promise<RecordItem> => api.post(`/apps/${appId}/lists/${listId}/records/`, data)
export const updateRecord = (appId: string, listId: string, id: string, data: Record<string, unknown>): Promise<RecordItem> => api.put(`/apps/${appId}/lists/${listId}/records/${id}/`, data)
export const deleteRecord = (appId: string, listId: string, id: string): Promise<void> => api.delete(`/apps/${appId}/lists/${listId}/records/${id}/`)
export const batchUpdate = (appId: string, listId: string, data: Record<string, unknown>): Promise<{ updated: number }> => api.patch(`/apps/${appId}/lists/${listId}/records/batch/`, data)
