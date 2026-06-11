import request from './request'

export const login = (data) => {
  return request.post('/login', data)
}

export const getArticleList = (params) => {
  return request.get('/article/list', { params })
}

export const getArticleById = (id) => {
  return request.get(`/article/${id}`)
}

export const createArticle = (data) => {
  return request.post('/article', data)
}

export const updateArticle = (id, data) => {
  return request.put(`/article/${id}`, data)
}

export const deleteArticle = (id) => {
  return request.delete(`/article/${id}`)
}

export const getCategoryList = () => {
  return request.get('/category')
}

export const createCategory = (data) => {
  return request.post('/category', data)
}

export const updateCategory = (id, data) => {
  return request.put(`/category/${id}`, data)
}

export const deleteCategory = (id) => {
  return request.delete(`/category/${id}`)
}

export const getTagList = () => {
  return request.get('/tag')
}

export const getProfile = () => {
  return request.get('/profile')
}

export const updateProfile = (data) => {
  return request.put('/profile', data)
}

export const createTag = (data) => {
  return request.post('/tag', data)
}

export const updateTag = (id, data) => {
  return request.put(`/tag/${id}`, data)
}

export const deleteTag = (id) => {
  return request.delete(`/tag/${id}`)
}

export const batchDeleteArticle = (ids) => {
  return request.post('/article/batch-delete', { ids })
}

export const batchDeleteCategory = (ids) => {
  return request.post('/category/batch-delete', { ids })
}

export const batchDeleteTag = (ids) => {
  return request.post('/tag/batch-delete', { ids })
}
