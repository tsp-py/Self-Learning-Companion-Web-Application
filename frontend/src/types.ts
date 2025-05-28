export interface User {
  id: number;
  email: string;
  name: string;
}

export interface File {
  id: number;
  name: string;
  type: string;
  tags: string[];
  upload_date: string;
}

export interface ReadingSession {
  id: number;
  start_time: string;
  end_time?: string;
  duration?: number;
}

export interface LearningPath {
  id: number;
  title: string;
  description: string;
  created_at: string;
  resources: PathResource[];
}

export interface PathResource {
  id: number;
  file_id: number;
  file_name: string;
  order: number;
  completed: boolean;
  completed_at?: string;
}

export interface Stats {
  total_time: number;
  by_type: { type: string; seconds: number }[];
  by_file: { id: number; name: string; seconds: number }[];
  daily_activity: { date: string; seconds: number }[];
} 