import api from './index'

export const getFieldTypes = () => api.get('/field-types/')
export const createFieldType = (data) => api.post('/field-types/', data)
export const updateFieldType = (id, data) => api.put(`/field-types/${id}/`, data)
export const deleteFieldType = (id) => api.delete(`/field-types/${id}/`)
export const getValidators = () => api.get('/validators/')
export const createValidator = (data) => api.post('/validators/', data)
export const updateValidator = (id, data) => api.put(`/validators/${id}/`, data)
export const deleteValidator = (id) => api.delete(`/validators/${id}/`)
