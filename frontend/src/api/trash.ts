import api from './index'
import type { TrashItem } from '../types'

export const getTrash = (appId: string): Promise<TrashItem[]> => api.get(`/apps/${appId}/trash/`)
export const restoreItem = (appId: string, id: string, data: { type: string; list_id?: string }): Promise<{ status: string }> => api.post(`/apps/${appId}/trash/${id}/`, data)
export const permanentDelete = (appId: string, id: string, params: { type: string; list_id?: string }): Promise<void> => api.delete(`/apps/${appId}/trash/${id}/`, { params })
