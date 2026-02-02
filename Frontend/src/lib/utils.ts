import { type ClassValue, clsx } from 'clsx';
import { format, formatDistanceToNow } from 'date-fns';
import { TicketPriority, TicketStatus, IssueType } from '@/types';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy');
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy h:mm a');
}

export function formatRelativeTime(date: string | Date): string {
  // If date is a string, append 'Z' to treat it as UTC if it doesn't already have timezone info
  if (typeof date === 'string' && !date.endsWith('Z') && !date.includes('+')) {
    date = date + 'Z';
  }
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function getPriorityColor(priority: TicketPriority): string {
  const colors = {
    [TicketPriority.LOW]: 'bg-gray-100 text-gray-700 border-gray-300',
    [TicketPriority.MEDIUM]: 'bg-blue-100 text-blue-700 border-blue-300',
    [TicketPriority.HIGH]: 'bg-orange-100 text-orange-700 border-orange-300',
    [TicketPriority.CRITICAL]: 'bg-red-100 text-red-700 border-red-300',
  };
  return colors[priority] || colors[TicketPriority.MEDIUM];
}

export function getStatusColor(status: TicketStatus): string {
  const colors = {
    [TicketStatus.IDEA]: 'bg-purple-100 text-purple-700',
    [TicketStatus.TODO]: 'bg-gray-100 text-gray-700',
    [TicketStatus.IN_PROGRESS]: 'bg-blue-100 text-blue-700',
    [TicketStatus.IN_REVIEW]: 'bg-yellow-100 text-yellow-700',
    [TicketStatus.DONE]: 'bg-green-100 text-green-700',
    [TicketStatus.CANCELLED]: 'bg-red-100 text-red-700',
  };
  return colors[status] || colors[TicketStatus.TODO];
}

export function getIssueTypeIcon(type: IssueType): string {
  const icons = {
    [IssueType.BUG]: '🐛',
    [IssueType.FEATURE]: '✨',
    [IssueType.TASK]: '📋',
    [IssueType.IMPROVEMENT]: '🚀',
  };
  return icons[type] || icons[IssueType.TASK];
}

export function getStatusLabel(status: TicketStatus): string {
  const labels = {
    [TicketStatus.IDEA]: 'Idea',
    [TicketStatus.TODO]: 'To Do',
    [TicketStatus.IN_PROGRESS]: 'In Progress',
    [TicketStatus.IN_REVIEW]: 'In Review',
    [TicketStatus.DONE]: 'Done',
    [TicketStatus.CANCELLED]: 'Cancelled',
  };
  return labels[status] || status;
}

export function getPriorityLabel(priority: TicketPriority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

export function getIssueTypeLabel(type: IssueType): string {
  return type.charAt(0).toUpperCase() + type.slice(1);
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.substring(0, length) + '...' : str;
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
