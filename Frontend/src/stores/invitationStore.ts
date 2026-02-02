import { create } from 'zustand';
import { invitationsApi } from '@/lib/api';

export interface ProjectInvitation {
  id: string;
  project_id: string;
  project_name: string;
  role: string;
  invited_by: string;
  created_at: string;
  expires_at: string;
  status: string;
}

interface InvitationState {
  invitations: ProjectInvitation[];
  isLoading: boolean;
  error: string | null;
  fetchInvitations: () => Promise<void>;
  acceptInvitation: (id: string) => Promise<void>;
  declineInvitation: (id: string) => Promise<void>;
  clearError: () => void;
}

export const useInvitationStore = create<InvitationState>((set) => ({
  invitations: [],
  isLoading: false,
  error: null,

  fetchInvitations: async () => {
    set({ isLoading: true, error: null });
    try {
      const invitations = await invitationsApi.getInvitations();
      set({ invitations, isLoading: false });
    } catch (error: any) {
      // If endpoint doesn't exist (404), just set empty invitations
      if (error.response?.status === 404) {
        set({ invitations: [], isLoading: false });
      } else {
        set({
          error: error.response?.data?.detail || 'Failed to fetch invitations',
          isLoading: false,
        });
      }
    }
  },

  acceptInvitation: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await invitationsApi.acceptInvitation(id);
      set((state) => ({
        invitations: state.invitations.filter((inv) => inv.id !== id),
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to accept invitation',
        isLoading: false,
      });
      throw error;
    }
  },

  declineInvitation: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await invitationsApi.declineInvitation(id);
      set((state) => ({
        invitations: state.invitations.filter((inv) => inv.id !== id),
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to decline invitation',
        isLoading: false,
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));
