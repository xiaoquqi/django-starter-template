export interface Post {
  id: number;
  title: string;
  content: string;
  author: number;
  created_at: string;
  updated_at: string;
  tags: number[];
  category: number;
}

export interface Tag {
  id: number;
  name: string;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  created_at: string;
}