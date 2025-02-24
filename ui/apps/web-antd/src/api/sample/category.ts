import { requestClient } from '#/api/request';
import type { Category } from './types';

/**
 * 获取分类列表
 */
export function getCategoryListApi() {
  return requestClient.get<Category[]>('/categories/');
}

/**
 * 获取分类详情
 */
export function getCategoryDetailApi(id: number) {
  return requestClient.get<Category>(`/categories/${id}/`);
}

/**
 * 创建分类
 */
export function createCategoryApi(data: Omit<Category, 'id' | 'created_at'>) {
  return requestClient.post<Category>('/categories/', data);
}

/**
 * 更新分类
 */
export function updateCategoryApi(id: number, data: Partial<Category>) {
  return requestClient.put<Category>(`/categories/${id}/`, data);
}

/**
 * 删除分类
 */
export function deleteCategoryApi(id: number) {
  return requestClient.delete(`/categories/${id}/`);
}