import api from './index'
import type { FieldType, FieldValidator } from '../types'

export const getFieldTypes = (): Promise<FieldType[]> => api.get('/field-types/')
export const createFieldType = (data: Partial<FieldType>): Promise<FieldType> => api.post('/field-types/', data)
export const updateFieldType = (id: string, data: Partial<FieldType>): Promise<FieldType> => api.put(`/field-types/${id}/`, data)
export const deleteFieldType = (id: string): Promise<void> => api.delete(`/field-types/${id}/`)
export const getValidators = (): Promise<FieldValidator[]> => api.get('/validators/')
export const createValidator = (data: Partial<FieldValidator>): Promise<FieldValidator> => api.post('/validators/', data)
export const updateValidator = (id: string, data: Partial<FieldValidator>): Promise<FieldValidator> => api.put(`/validators/${id}/`, data)
export const deleteValidator = (id: string): Promise<void> => api.delete(`/validators/${id}/`)
