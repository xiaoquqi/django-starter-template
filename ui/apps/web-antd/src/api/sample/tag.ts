import { requestClient } from '#/api/request';
import type { Tag } from './types';

/**
 * 获取标签列表
 */
export function getTagListApi() {
  return requestClient.get<Tag[]>('/api/v1/tags/');
}

/**
 * 获取标签详情
 */
export function getTagDetailApi(id: number) {
  return requestClient.get<Tag>(`/api/v1/tags/${id}/`);
}

/**
 * 创建标签
 */
export function createTagApi(data: Omit<Tag, 'id' | 'created_at'>) {
  return requestClient.post<Tag>('/api/v1/tags/', data);
}

/**
 * 更新标签
 */
export function updateTagApi(id: number, data: Partial<Tag>) {
  return requestClient.put<Tag>(`/api/v1/tags/${id}/`, data);
}

/**
 * 删除标签
 */
export function deleteTagApi(id: number) {
  return requestClient.delete(`/api/v1/tags/${id}/`);
}