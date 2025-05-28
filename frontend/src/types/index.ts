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
  text_content?: string;
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
  completed_at: string | null;
}

export interface ReadingSession {
  id: number;
  file_id: number;
  start_time: string;
  end_time: string | null;
  duration: number | null;
}

export interface Stats {
  total_time: number;
  by_type: Array<{
    type: string;
    seconds: number;
  }>;
  by_file: Array<{
    id: number;
    name: string;
    seconds: number;
  }>;
  daily_activity: Array<{
    date: string;
    seconds: number;
  }>;
} 