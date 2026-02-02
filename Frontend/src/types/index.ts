// User Types
export enum UserRole {
  ADMIN = 'admin',
  DEVELOPER = 'developer',
  VIEWER = 'viewer',
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  avatar_url: string | null;
  role: UserRole;
  timezone: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username_or_email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  timezone?: string;
}

// Project Types
export enum ProjectRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  DEVELOPER = 'developer',
  VIEWER = 'viewer',
}

export interface Project {
  id: string;
  name: string;
  key: string;
  description: string | null;
  is_private: boolean;
  is_archived: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectMember {
  id: string;
  project_id: string;
  user_id: string;
  role: ProjectRole;
  joined_at: string;
  added_by: string;
}

export interface ProjectMemberWithUser extends ProjectMember {
  username: string;
  email: string;
  full_name: string | null;
  avatar_url?: string | null;
}

export interface ProjectCreate {
  name: string;
  key: string;
  description?: string;
  is_private?: boolean;
}

// Ticket Types
export enum TicketStatus {
  IDEA = 'idea',
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  IN_REVIEW = 'in_review',
  DONE = 'done',
  CANCELLED = 'cancelled',
}

export enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum IssueType {
  BUG = 'bug',
  FEATURE = 'feature',
  TASK = 'task',
  IMPROVEMENT = 'improvement',
}

export enum Resolution {
  FIXED = 'fixed',
  WONT_FIX = 'wont_fix',
  DUPLICATE = 'duplicate',
  INCOMPLETE = 'incomplete',
}

export interface Label {
  id: string;
  name: string;
  color: string;
  project_id: string;
}

export interface Ticket {
  id: string;
  key: string;
  title: string;
  description: string | null;
  type: IssueType;
  priority: TicketPriority;
  status: TicketStatus;
  resolution: Resolution | null;
  project_id: string;
  assignee_id: string | null;
  reporter_id: string;
  order_index: number;
  due_date: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  assignee: User | null;
  reporter: User;
  comments_count: number;
  attachments_count: number;
  labels: Label[];
}

export interface TicketCreate {
  title: string;
  description?: string;
  project_name: string;
  type?: IssueType;
  priority?: TicketPriority;
  due_date?: string;
}

export interface TicketUpdate {
  title?: string;
  description?: string;
  type?: IssueType;
  priority?: TicketPriority;
  assignee_id?: string | null;
  status?: TicketStatus;
  resolution?: Resolution | null;
  due_date?: string | null;
}

// Comment Types
export interface Comment {
  id: string;
  ticket_id: string;
  author_id: string;
  parent_id: string | null;
  content: string;
  created_at: string;
  updated_at: string;
  is_edited: boolean;
  author: User;
  replies: Comment[];
  attachments: Attachment[];
}

export interface CommentCreate {
  content: string;
  parent_id?: string;
}

// Attachment Types
export interface Attachment {
  id: string;
  ticket_id: string;
  uploaded_by: string;
  comment_id?: string | null;
  filename: string;
  original_filename: string;
  file_size: number;
  file_url: string;
  mime_type: string;
  created_at: string;
  uploader: User;
}

// Search & Filter Types
export interface TicketSearchParams {
  keyword?: string;
  status?: TicketStatus;
  priority?: TicketPriority;
  issue_type?: IssueType;
  assignee_id?: string;
  reporter_id?: string;
  skip?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SearchResponse<T> {
  total: number;
  count: number;
  items: T[];
  skip: number;
  limit: number;
}
