import axios, { AxiosError } from 'axios';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  Project,
  ProjectCreate,
  ProjectMember,
  ProjectMemberWithUser,
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketSearchParams,
  SearchResponse,
  Comment,
  CommentCreate,
  Attachment,
  TicketStatus,
  Resolution,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/v1/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/api/v1/users/me');
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/v1/auth/logout');
  },
};

// Users API
export const usersApi = {
  getUsers: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/api/v1/users');
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/api/v1/users/${id}`);
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/api/v1/users/me', data);
    return response.data;
  },

  deleteUser: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/users/${id}`);
  },
};

// Projects API
export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get<Project[]>('/api/v1/projects');
    return response.data;
  },

  getProject: async (id: string): Promise<Project> => {
    const response = await api.get<Project>(`/api/v1/projects/${id}`);
    return response.data;
  },

  createProject: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post<Project>('/api/v1/projects', data);
    return response.data;
  },

  updateProject: async (id: string, data: Partial<ProjectCreate>): Promise<Project> => {
    const response = await api.put<Project>(`/api/v1/projects/${id}`, data);
    return response.data;
  },

  deleteProject: async (id: string): Promise<{ message: string; project_id: string }> => {
    const response = await api.delete<{ message: string; project_id: string }>(`/api/v1/projects/${id}`);
    return response.data;
  },

  getMembers: async (projectId: string): Promise<ProjectMemberWithUser[]> => {
    const response = await api.get<ProjectMemberWithUser[]>(`/api/v1/projects/${projectId}/members`);
    return response.data;
  },

  addMember: async (projectId: string, userId: string, role: string): Promise<ProjectMember> => {
    const response = await api.post<ProjectMember>(`/api/v1/projects/${projectId}/members`, {
      user_id: userId,
      role,
    });
    return response.data;
  },

  removeMember: async (projectId: string, userId: string): Promise<void> => {
    await api.delete(`/api/v1/projects/${projectId}/members/${userId}`);
  },

  updateMemberRole: async (projectId: string, userId: string, role: string): Promise<ProjectMemberWithUser> => {
    const response = await api.put<ProjectMemberWithUser>(`/api/v1/projects/${projectId}/members/${userId}`, {
      role,
    });
    return response.data;
  },

  getUserRole: async (projectId: string): Promise<any> => {
    const response = await api.get(`/api/v1/projects/${projectId}/me/role`);
    return response.data;
  },

  getProjectStats: async (projectId: string): Promise<any> => {
    const response = await api.get(`/api/v1/projects/${projectId}/stats`);
    return response.data;
  },
};

// Tickets API
export const ticketsApi = {
  searchTickets: async (
    projectName: string,
    params?: TicketSearchParams
  ): Promise<SearchResponse<Ticket>> => {
    const response = await api.get<SearchResponse<Ticket>>(
      `/api/v1/tickets/${projectName}/search`,
      { params }
    );
    return response.data;
  },

  getTicket: async (id: string): Promise<Ticket> => {
    const response = await api.get<Ticket>(`/api/v1/tickets/ticket/${id}`);
    return response.data;
  },

  createTicket: async (data: TicketCreate): Promise<Ticket> => {
    const response = await api.post<Ticket>('/api/v1/tickets', data);
    return response.data;
  },

  updateTicket: async (id: string, data: TicketUpdate): Promise<Ticket> => {
    const response = await api.patch<Ticket>(`/api/v1/tickets/ticket/${id}`, data);
    return response.data;
  },

  changeStatus: async (id: string, status: TicketStatus, resolution?: Resolution | null): Promise<Ticket> => {
    const response = await api.patch<Ticket>(`/api/v1/tickets/ticket/${id}/status`, {
      status,
      resolution: resolution || null,
    });
    return response.data;
  },

  assignTicket: async (id: string, assigneeUsername: string): Promise<Ticket> => {
    const response = await api.patch<Ticket>(`/api/v1/tickets/ticket/${id}/assign`, {
      assignee_username: assigneeUsername,
    });
    return response.data;
  },

  deleteTicket: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/tickets/ticket/${id}`);
  },

  getProjectMembers: async (projectId: string): Promise<User[]> => {
    const response = await api.get<User[]>(`/api/v1/tickets/project/${projectId}/members`);
    return response.data;
  },
};

// Comments API
export const commentsApi = {
  getComments: async (ticketId: string): Promise<Comment[]> => {
    const response = await api.get<Comment[]>(`/api/v1/tickets/${ticketId}/comments`);
    return response.data;
  },

  createComment: async (ticketId: string, data: CommentCreate): Promise<Comment> => {
    const response = await api.post<Comment>(`/api/v1/tickets/${ticketId}/comments`, data);
    return response.data;
  },

  updateComment: async (ticketId: string, commentId: string, content: string): Promise<Comment> => {
    const response = await api.put<Comment>(`/api/v1/tickets/${ticketId}/comments/${commentId}`, { content });
    return response.data;
  },

  deleteComment: async (commentId: string): Promise<void> => {
    await api.delete(`/api/v1/tickets/comments/${commentId}`);
  },

  replyToComment: async (ticketId: string, parentId: string, content: string): Promise<Comment> => {
    const response = await api.post<Comment>(`/api/v1/tickets/${ticketId}/comments`, { 
      content,
      parent_id: parentId 
    });
    return response.data;
  },
};

// Attachments API
export const attachmentsApi = {
  getAttachments: async (ticketId: string): Promise<Attachment[]> => {
    const response = await api.get<Attachment[]>(
      `/api/v1/attachments/tickets/${ticketId}/attachments`
    );
    return response.data;
  },

  uploadAttachment: async (ticketId: string, file: File): Promise<Attachment> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<Attachment>(
      `/api/v1/attachments/tickets/${ticketId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  uploadAttachmentToComment: async (ticketId: string, commentId: string, file: File): Promise<Attachment> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<Attachment>(
      `/api/v1/attachments/tickets/${ticketId}/upload?comment_id=${commentId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  deleteAttachment: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/attachments/${id}`);
  },

  downloadAttachment: async (id: string): Promise<Blob> => {
    const response = await api.get(`/api/v1/attachments/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Invitations API
export const invitationsApi = {
  getInvitations: async (): Promise<any[]> => {
    const response = await api.get('/api/v1/me/invitations');
    return response.data;
  },

  acceptInvitation: async (id: string): Promise<void> => {
    await api.post(`/api/v1/me/invitations/${id}/accept`);
  },

  declineInvitation: async (id: string): Promise<void> => {
    await api.post(`/api/v1/me/invitations/${id}/decline`);
  },

  sendInvitation: async (projectId: string, userId: string, role: string): Promise<any> => {
    const response = await api.post(`/api/v1/projects/${projectId}/invitations`, {
      user_id: userId,
      role,
    });
    return response.data;
  },
};

export default api;
