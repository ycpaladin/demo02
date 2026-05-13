import api from './index'
import type { RecordsResponse, RecordItem } from '../types'

export const getRecords = (appId: string, listUrl: string, params?: Record<string, unknown>): Promise<RecordsResponse> => api.get(`/apps/${appId}/lists/${listUrl}/records/`, { params })
export const getRecord = (appId: string, listUrl: string, id: string): Promise<RecordItem> => api.get(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const createRecord = (appId: string, listUrl: string, data: Record<string, unknown>): Promise<RecordItem> => api.post(`/apps/${appId}/lists/${listUrl}/records/`, data)
export const updateRecord = (appId: string, listUrl: string, id: string, data: Record<string, unknown>): Promise<RecordItem> => api.put(`/apps/${appId}/lists/${listUrl}/records/${id}/`, data)
export const deleteRecord = (appId: string, listUrl: string, id: string): Promise<void> => api.delete(`/apps/${appId}/lists/${listUrl}/records/${id}/`)
export const batchUpdate = (appId: string, listUrl: string, data: Record<string, unknown>): Promise<{ updated: number }> => api.patch(`/apps/${appId}/lists/${listUrl}/records/batch/`, data)
