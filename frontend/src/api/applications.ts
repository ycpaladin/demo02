import api from './index'
import type { Application, Navigation } from '../types'

export const getApps = (): Promise<Application[]> => api.get('/apps/')
export const getApp = (id: string): Promise<Application> => api.get(`/apps/${id}/`)
export const createApp = (data: Partial<Application>): Promise<Application> => api.post('/apps/', data)
export const updateApp = (id: string, data: Partial<Application>): Promise<Application> => api.put(`/apps/${id}/`, data)
export const deleteApp = (id: string): Promise<void> => api.delete(`/apps/${id}/`)
export const getNavigations = (appId: string): Promise<Navigation[]> => api.get(`/apps/${appId}/navigations/`)
export const createNavigation = (appId: string, data: Partial<Navigation>): Promise<Navigation> => api.post(`/apps/${appId}/navigations/`, data)
export const updateNavigation = (appId: string, id: string, data: Partial<Navigation>): Promise<Navigation> => api.put(`/apps/${appId}/navigations/${id}/`, data)
export const deleteNavigation = (appId: string, id: string): Promise<void> => api.delete(`/apps/${appId}/navigations/${id}/`)
