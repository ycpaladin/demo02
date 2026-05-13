import api from './index'

export const getContentTypes = () => api.get('/content-types/')
export const getContentType = (id) => api.get(`/content-types/${id}/`)
export const createContentType = (data) => api.post('/content-types/', data)
export const updateContentType = (id, data) => api.put(`/content-types/${id}/`, data)
export const deleteContentType = (id) => api.delete(`/content-types/${id}/`)
export const getCTFields = (ctId) => api.get(`/content-types/${ctId}/fields/`)
export const createCTField = (ctId, data) => api.post(`/content-types/${ctId}/fields/`, data)
export const updateCTField = (ctId, id, data) => api.put(`/content-types/${ctId}/fields/${id}/`, data)
export const deleteCTField = (ctId, id) => api.delete(`/content-types/${ctId}/fields/${id}/`)
