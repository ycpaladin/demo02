import api from './index'
import type { ContentType, ContentTypeField } from '../types'

export const getContentTypes = (): Promise<ContentType[]> => api.get('/content-types/')
export const getContentType = (id: string): Promise<ContentType> => api.get(`/content-types/${id}/`)
export const createContentType = (data: Partial<ContentType>): Promise<ContentType> => api.post('/content-types/', data)
export const updateContentType = (id: string, data: Partial<ContentType>): Promise<ContentType> => api.put(`/content-types/${id}/`, data)
export const deleteContentType = (id: string): Promise<void> => api.delete(`/content-types/${id}/`)
export const getCTFields = (ctId: string): Promise<ContentTypeField[]> => api.get(`/content-types/${ctId}/fields/`)
export const createCTField = (ctId: string, data: Partial<ContentTypeField>): Promise<ContentTypeField> => api.post(`/content-types/${ctId}/fields/`, data)
export const updateCTField = (ctId: string, id: string, data: Partial<ContentTypeField>): Promise<ContentTypeField> => api.put(`/content-types/${ctId}/fields/${id}/`, data)
export const deleteCTField = (ctId: string, id: string): Promise<void> => api.delete(`/content-types/${ctId}/fields/${id}/`)
