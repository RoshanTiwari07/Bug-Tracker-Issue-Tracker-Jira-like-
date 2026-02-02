import { create } from 'zustand';
import type {
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketSearchParams,
  TicketStatus,
} from '@/types';
import { ticketsApi } from '@/lib/api';

interface TicketState {
  tickets: Ticket[];
  currentTicket: Ticket | null;
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  searchTickets: (projectName: string, params?: TicketSearchParams) => Promise<void>;
  fetchTicket: (id: string) => Promise<void>;
  createTicket: (data: TicketCreate) => Promise<Ticket>;
  updateTicket: (id: string, data: TicketUpdate) => Promise<void>;
  changeTicketStatus: (id: string, status: TicketStatus, resolution?: string) => Promise<void>;
  assignTicket: (id: string, assigneeUsername: string) => Promise<void>;
  deleteTicket: (id: string) => Promise<void>;
  setCurrentTicket: (ticket: Ticket | null) => void;
  updateTicketInList: (ticket: Ticket) => void;
}

export const useTicketStore = create<TicketState>((set) => ({
  tickets: [],
  currentTicket: null,
  isLoading: false,
  error: null,
  totalCount: 0,

  searchTickets: async (projectName: string, params?: TicketSearchParams) => {
    set({ isLoading: true, error: null });
    try {
      const response = await ticketsApi.searchTickets(projectName, params);
      set({
        tickets: response.items,
        totalCount: response.total,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch tickets',
        isLoading: false,
      });
    }
  },

  fetchTicket: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const ticket = await ticketsApi.getTicket(id);
      set({ currentTicket: ticket, isLoading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch ticket',
        isLoading: false,
      });
    }
  },

  createTicket: async (data: TicketCreate) => {
    set({ isLoading: true, error: null });
    try {
      const ticket = await ticketsApi.createTicket(data);
      set((state) => ({
        tickets: [...state.tickets, ticket],
        isLoading: false,
      }));
      return ticket;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to create ticket',
        isLoading: false,
      });
      throw error;
    }
  },

  updateTicket: async (id: string, data: TicketUpdate) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTicket = await ticketsApi.updateTicket(id, data);
      set((state) => ({
        tickets: state.tickets.map((t) => (t.id === id ? updatedTicket : t)),
        currentTicket: state.currentTicket?.id === id ? updatedTicket : state.currentTicket,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to update ticket',
        isLoading: false,
      });
      throw error;
    }
  },

  changeTicketStatus: async (id: string, status: TicketStatus, resolution?: string) => {
    try {
      const updatedTicket = await ticketsApi.changeStatus(id, status, resolution);
      set((state) => ({
        tickets: state.tickets.map((t) => (t.id === id ? updatedTicket : t)),
        currentTicket: state.currentTicket?.id === id ? updatedTicket : state.currentTicket,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to change status',
      });
      throw error;
    }
  },

  assignTicket: async (id: string, assigneeUsername: string) => {
    try {
      const updatedTicket = await ticketsApi.assignTicket(id, assigneeUsername);
      set((state) => ({
        tickets: state.tickets.map((t) => (t.id === id ? updatedTicket : t)),
        currentTicket: state.currentTicket?.id === id ? updatedTicket : state.currentTicket,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to assign ticket',
      });
      throw error;
    }
  },

  deleteTicket: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await ticketsApi.deleteTicket(id);
      set((state) => ({
        tickets: state.tickets.filter((t) => t.id !== id),
        currentTicket: state.currentTicket?.id === id ? null : state.currentTicket,
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to delete ticket',
        isLoading: false,
      });
      throw error;
    }
  },

  setCurrentTicket: (ticket: Ticket | null) => {
    set({ currentTicket: ticket });
  },

  updateTicketInList: (ticket: Ticket) => {
    set((state) => ({
      tickets: state.tickets.map((t) => (t.id === ticket.id ? ticket : t)),
    }));
  },
}));
