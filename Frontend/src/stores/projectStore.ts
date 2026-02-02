import { create } from 'zustand';
import type { Project, ProjectCreate } from '@/types';
import { projectsApi } from '@/lib/api';

interface ProjectState {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<Project>;
  updateProject: (id: string, data: Partial<ProjectCreate>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  setCurrentProject: (project: Project | null) => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  error: null,

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const projects = await projectsApi.getProjects();
      set({ projects, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch projects',
        isLoading: false,
      });
    }
  },

  fetchProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const project = await projectsApi.getProject(id);
      set({ currentProject: project, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch project',
        isLoading: false,
      });
    }
  },

  createProject: async (data: ProjectCreate) => {
    set({ isLoading: true, error: null });
    try {
      const project = await projectsApi.createProject(data);
      set((state) => ({
        projects: [...state.projects, project],
        isLoading: false,
      }));
      return project;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create project',
        isLoading: false,
      });
      throw error;
    }
  },

  updateProject: async (id: string, data: Partial<ProjectCreate>) => {
    set({ isLoading: true, error: null });
    try {
      const updatedProject = await projectsApi.updateProject(id, data);
      set((state) => ({
        projects: state.projects.map((p) => (p.id === id ? updatedProject : p)),
        currentProject:
          state.currentProject?.id === id ? updatedProject : state.currentProject,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update project',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteProject: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const result = await projectsApi.deleteProject(id);
      console.log('Delete API response:', result);
      // Remove from local state immediately
      set((state) => ({
        projects: state.projects.filter((p) => p.id !== id),
        currentProject: state.currentProject?.id === id ? null : state.currentProject,
        isLoading: false,
        error: null,
      }));
    } catch (error: any) {
      console.error('Delete project error:', error);
      set({
        error: error.response?.data?.detail || 'Failed to delete project',
        isLoading: false,
      });
      throw error;
    }
  },

  setCurrentProject: (project: Project | null) => {
    set({ currentProject: project });
  },
}));
