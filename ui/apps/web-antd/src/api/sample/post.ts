import { requestClient } from '#/api/request';
import type { Post } from './types';

/**
 * 获取文章列表
 */
export async function getPostListApi(params?: { page?: number; page_size?: number }) {
  return requestClient.get<{ results: Post[]; count: number }>('/posts/', { params });
}

/**
 * 获取文章详情
 */
export function getPostDetailApi(id: number) {
  return requestClient.get<Post>(`/posts/${id}/`);
}

/**
 * 创建文章
 */
export function createPostApi(data: Omit<Post, 'id' | 'created_at' | 'updated_at'>) {
  return requestClient.post<Post>('/posts/', data);
}

/**
 * 更新文章
 */
export function updatePostApi(id: number, data: Partial<Post>) {
  return requestClient.put<Post>(`/posts/${id}/`, data);
}

/**
 * 删除文章
 */
export function deletePostApi(id: number) {
  return requestClient.delete(`/posts/${id}/`);
}