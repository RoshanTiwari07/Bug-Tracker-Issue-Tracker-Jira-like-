import { useState, useEffect } from 'react';
import { X, Loader2, Trash2 } from 'lucide-react';
import { useTicketStore } from '../../stores/ticketStore';
import { TicketStatus, TicketPriority, IssueType } from '../../types';
import toast from 'react-hot-toast';

interface EditTicketModalProps {
  ticketId: string;
  onClose: () => void;
}

export function EditTicketModal({ ticketId, onClose }: EditTicketModalProps) {
  const { tickets, updateTicket, changeTicketStatus, deleteTicket } = useTicketStore();
  
  const ticket = tickets.find(t => t.id === ticketId);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: IssueType.BUG,
    priority: TicketPriority.MEDIUM,
    status: TicketStatus.TODO,
    due_date: '',
    resolution: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ticket) {
      setFormData({
        title: ticket.title,
        description: ticket.description || '',
        type: ticket.type,
        priority: ticket.priority,
        status: ticket.status,
        due_date: ticket.due_date ? ticket.due_date.split('T')[0] : '',
        resolution: ticket.resolution || '',
      });
    }
  }, [ticket]);

  if (!ticket) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Update basic ticket fields
      const updateData: any = {
        title: formData.title,
        description: formData.description,
        type: formData.type,
        priority: formData.priority,
        due_date: formData.due_date || null,
      };

      await updateTicket(ticketId, updateData);

      // Update status if changed
      if (formData.status !== ticket.status) {
        await changeTicketStatus(
          ticketId, 
          formData.status, 
          (formData.status === TicketStatus.DONE || formData.status === TicketStatus.CANCELLED) ? formData.resolution : undefined
        );
      }

      onClose();
    } catch (err: any) {
      console.error('Failed to update ticket:', err);
      setError(err.response?.data?.detail || 'Failed to update ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete ticket ${ticket.key}? This action cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await deleteTicket(ticketId);
      toast.success('Ticket deleted successfully');
      onClose();
    } catch (err: any) {
      console.error('Failed to delete ticket:', err);
      setError(err.response?.data?.detail || 'Failed to delete ticket');
      toast.error('Failed to delete ticket');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Edit Ticket: {ticket.key}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Type and Priority Row */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value as IssueType })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={IssueType.BUG}>Bug</option>
                <option value={IssueType.FEATURE}>Feature</option>
                <option value={IssueType.TASK}>Task</option>
                <option value={IssueType.IMPROVEMENT}>Improvement</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as TicketPriority })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={TicketPriority.LOW}>Low</option>
                <option value={TicketPriority.MEDIUM}>Medium</option>
                <option value={TicketPriority.HIGH}>High</option>
                <option value={TicketPriority.CRITICAL}>Critical</option>
              </select>
            </div>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as TicketStatus })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={TicketStatus.IDEA}>Idea</option>
              <option value={TicketStatus.TODO}>To Do</option>
              <option value={TicketStatus.IN_PROGRESS}>In Progress</option>
              <option value={TicketStatus.IN_REVIEW}>In Review</option>
              <option value={TicketStatus.DONE}>Done</option>
              <option value={TicketStatus.CANCELLED}>Cancelled</option>
            </select>
          </div>

          {/* Resolution (show only for DONE/CANCELLED) */}
          {(formData.status === TicketStatus.DONE || formData.status === TicketStatus.CANCELLED) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Resolution
              </label>
              <select
                value={formData.resolution}
                onChange={(e) => setFormData({ ...formData, resolution: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select resolution...</option>
                <option value="FIXED">Fixed</option>
                <option value="WONT_FIX">Won't Fix</option>
                <option value="DUPLICATE">Duplicate</option>
                <option value="INCOMPLETE">Incomplete</option>
              </select>
            </div>
          )}

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={handleDelete}
              className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              disabled={loading}
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.title.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
