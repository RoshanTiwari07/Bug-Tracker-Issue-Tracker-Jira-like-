import { useEffect, useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { useTicketStore } from '@/stores/ticketStore';
import { useAuthStore } from '@/stores/authStore';
import { commentsApi, attachmentsApi, ticketsApi } from '@/lib/api';
import type { Comment, Attachment, User as UserType } from '@/types';
import { TicketStatus, Resolution, UserRole } from '@/types';
import {
  formatDateTime,
  formatRelativeTime,
  getPriorityColor,
  getStatusColor,
  getIssueTypeIcon,
  getStatusLabel,
  formatFileSize,
} from '@/lib/utils';
import {
  Calendar,
  User,
  MessageSquare,
  Paperclip,
  Download,
  Send,
  CheckCircle2,
  XCircle,
  Edit2,
  Save,
  X,
  Trash2,
  UserPlus,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface TicketDetailsModalProps {
  ticketId: string;
  isOpen: boolean;
  onClose: () => void;
  startInEditMode?: boolean;
}

export function TicketDetailsModal({
  ticketId,
  isOpen,
  onClose,
  startInEditMode = false,
}: TicketDetailsModalProps) {
  const { currentTicket, fetchTicket, changeTicketStatus, updateTicket, deleteTicket, assignTicket } = useTicketStore();
  const { user } = useAuthStore();
  const [comments, setComments] = useState<Comment[]>([]);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [commentAttachment, setCommentAttachment] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<TicketStatus | null>(null);
  const [selectedResolution, setSelectedResolution] = useState<Resolution | null>(null);
  const [isEditing, setIsEditing] = useState(startInEditMode);
  const [projectMembers, setProjectMembers] = useState<UserType[]>([]);
  const [isAssigning, setIsAssigning] = useState(false);
  const [replyingTo, setReplyingTo] = useState<{ id: string; username: string } | null>(null);
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    priority: '',
    type: '',
    due_date: '',
  });

  useEffect(() => {
    if (ticketId) {
      fetchTicket(ticketId);
      loadComments();
      loadAttachments();
    }
  }, [ticketId]);

  useEffect(() => {
    if (currentTicket) {
      setEditForm({
        title: currentTicket.title,
        description: currentTicket.description || '',
        priority: currentTicket.priority,
        type: currentTicket.type,
        due_date: currentTicket.due_date ? new Date(currentTicket.due_date).toISOString().slice(0, 16) : '',
      });
      // Load project members for assignment
      loadProjectMembers();
    }
  }, [currentTicket]);

  const loadProjectMembers = async () => {
    if (!currentTicket?.project_id) return;
    try {
      const members = await ticketsApi.getProjectMembers(currentTicket.project_id);
      setProjectMembers(members);
    } catch (error) {
      console.error('Failed to load project members:', error);
    }
  };

  const handleAssignTicket = async (assigneeUsername: string | null) => {
    if (!currentTicket) return;
    setIsAssigning(true);
    try {
      if (assigneeUsername) {
        await assignTicket(currentTicket.id, assigneeUsername);
        toast.success('Ticket assigned successfully');
      } else {
        // Unassign - call backend with empty/null assignee
        await assignTicket(currentTicket.id, '');
        toast.success('Ticket unassigned');
      }
      await fetchTicket(ticketId);
    } catch (error) {
      toast.error('Failed to assign ticket');
    } finally {
      setIsAssigning(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!currentTicket) return;
    setIsSubmitting(true);
    try {
      await updateTicket(currentTicket.id, {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority as any,
        type: editForm.type as any,
        due_date: editForm.due_date ? new Date(editForm.due_date).toISOString() : null,
      });
      setIsEditing(false);
      toast.success('Ticket updated');
      await fetchTicket(ticketId);
    } catch (error) {
      toast.error('Failed to update ticket');
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadComments = async () => {
    try {
      const data = await commentsApi.getComments(ticketId);
      console.log('Loaded comments:', data);
      setComments(data);
    } catch (error) {
      console.error('Failed to load comments:', error);
      toast.error('Failed to load comments');
    }
  };

  const loadAttachments = async () => {
    try {
      const data = await attachmentsApi.getAttachments(ticketId);
      setAttachments(data);
    } catch (error) {
      console.error('Failed to load attachments');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    try {
      // First add the comment
      const newCommentData = await commentsApi.createComment(ticketId, { 
        content: newComment,
        parent_id: replyingTo?.id || undefined
      });
      
      // If there's an attachment, upload it linked to the comment
      if (commentAttachment) {
        await attachmentsApi.uploadAttachmentToComment(ticketId, newCommentData.id, commentAttachment);
      }
      
      setNewComment('');
      setReplyingTo(null);
      setCommentAttachment(null);
      loadComments();
      loadAttachments(); // Refresh attachments section
      toast.success(replyingTo ? 'Reply added' : 'Comment added');
    } catch (error) {
      toast.error('Failed to add comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReply = (commentId: string, username: string) => {
    setReplyingTo({ id: commentId, username });
  };

  const cancelReply = () => {
    setReplyingTo(null);
  };

  const handleCommentFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setCommentAttachment(file);
    }
  };

  const removeCommentAttachment = () => {
    setCommentAttachment(null);
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;

    try {
      await commentsApi.deleteComment(commentId);
      loadComments();
      toast.success('Comment deleted');
    } catch (error) {
      toast.error('Failed to delete comment');
    }
  };

  const isAdmin = user?.role === UserRole.ADMIN;
  const canEditTicket = isAdmin;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await attachmentsApi.uploadAttachment(ticketId, file);
      loadAttachments();
      toast.success('File uploaded');
    } catch (error) {
      toast.error('Failed to upload file');
    }
  };

  const handleDownload = async (attachment: Attachment) => {
    try {
      const blob = await attachmentsApi.downloadAttachment(attachment.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = attachment.original_filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Failed to download file');
    }
  };

  const handleStatusChange = async (newStatus: TicketStatus, resolution?: Resolution) => {
    if (!currentTicket) return;
    setIsUpdatingStatus(true);
    try {
      await changeTicketStatus(currentTicket.id, newStatus, resolution);
      setSelectedStatus(null);
      setSelectedResolution(null);
      toast.success('Ticket status updated');
      await fetchTicket(ticketId);
    } catch (error) {
      toast.error('Failed to update ticket status');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const getAvailableTransitions = (currentStatus: TicketStatus): TicketStatus[] => {
    switch (currentStatus) {
      case TicketStatus.IDEA:
        return [TicketStatus.TODO, TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED];
      case TicketStatus.TODO:
        return [TicketStatus.IDEA, TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED];
      case TicketStatus.IN_PROGRESS:
        return [TicketStatus.TODO, TicketStatus.IN_REVIEW, TicketStatus.CANCELLED];
      case TicketStatus.IN_REVIEW:
        return [TicketStatus.IN_PROGRESS, TicketStatus.DONE, TicketStatus.CANCELLED];
      case TicketStatus.DONE:
        return [TicketStatus.IDEA, TicketStatus.TODO, TicketStatus.IN_PROGRESS, TicketStatus.IN_REVIEW];
      case TicketStatus.CANCELLED:
        return [TicketStatus.IDEA, TicketStatus.TODO, TicketStatus.IN_PROGRESS];
      default:
        return [];
    }
  };

  const handleDelete = async () => {
    if (!currentTicket) return;
    
    if (!confirm(`Are you sure you want to delete ticket ${currentTicket.key}? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteTicket(currentTicket.id);
      toast.success('Ticket deleted successfully');
      onClose();
    } catch (error) {
      toast.error('Failed to delete ticket');
    }
  };

  if (!currentTicket) {
    return null;
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getIssueTypeIcon(currentTicket.type)}</span>
                <span className="text-sm font-medium text-gray-500">
                  {currentTicket.key}
                </span>
                <span className={`badge border ${getPriorityColor(currentTicket.priority)}`}>
                  {currentTicket.priority}
                </span>
                <span className={`badge ${getStatusColor(currentTicket.status)}`}>
                  {getStatusLabel(currentTicket.status)}
                </span>
              </div>
              {canEditTicket && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    if (isEditing) {
                      setIsEditing(false);
                      setEditForm({
                        title: currentTicket.title,
                        description: currentTicket.description || '',
                        priority: currentTicket.priority,
                        type: currentTicket.type,
                        due_date: currentTicket.due_date ? new Date(currentTicket.due_date).toISOString().slice(0, 16) : '',
                      });
                    } else {
                      setIsEditing(true);
                    }
                  }}
                >
                  {isEditing ? <X size={18} /> : <Edit2 size={18} />}
                  <span className="ml-2">{isEditing ? 'Cancel' : 'Edit'}</span>
                </Button>
              )}
            </div>
            {isEditing ? (
              <input
                type="text"
                value={editForm.title}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                className="text-2xl font-bold text-gray-900 w-full border-b-2 border-primary-500 focus:outline-none"
              />
            ) : (
              <h2 className="text-2xl font-bold text-gray-900">{currentTicket.title}</h2>
            )}
          </div>

          {/* Edit Form Fields - Admin Only */}
          {isEditing && canEditTicket && (
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg border-l-4 border-primary-500">
              <div className="col-span-2">
                <p className="text-xs text-gray-600 mb-3 flex items-center gap-1">
                  <span className="inline-block w-2 h-2 bg-primary-500 rounded-full"></span>
                  Admin editing mode - Type, Priority, Due Date, Description, and Assignee
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type
                </label>
                <select
                  value={editForm.type}
                  onChange={(e) => setEditForm({ ...editForm, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="bug">Bug</option>
                  <option value="feature">Feature</option>
                  <option value="task">Task</option>
                  <option value="improvement">Improvement</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  value={editForm.priority}
                  onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Due Date
                </label>
                <input
                  type="datetime-local"
                  value={editForm.due_date}
                  onChange={(e) => setEditForm({ ...editForm, due_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="col-span-2">
                <Button
                  onClick={handleSaveEdit}
                  isLoading={isSubmitting}
                  size="sm"
                  className="w-full"
                >
                  <Save size={16} className="mr-2" />
                  Save Changes
                </Button>
              </div>
            </div>
          )}

          {/* Description - Admin Editable */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
            {isEditing && canEditTicket ? (
              <textarea
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            ) : (
              <p className="text-gray-700 whitespace-pre-wrap">
                {currentTicket.description || 'No description provided'}
              </p>
            )}
          </div>

          {/* Attachments */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <Paperclip size={18} className="mr-2" />
                Attachments ({attachments.length})
              </h3>
              <label className="cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                />
                <span className="text-sm text-primary-600 hover:text-primary-700">
                  + Upload
                </span>
              </label>
            </div>
            <div className="space-y-2">
              {attachments.map((attachment) => (
                <div
                  key={attachment.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <Paperclip size={16} className="text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {attachment.original_filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(attachment.file_size)} •{' '}
                        {formatRelativeTime(attachment.created_at)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(attachment)}
                    className="text-primary-600 hover:text-primary-700"
                  >
                    <Download size={18} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Comments */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              <MessageSquare size={18} className="mr-2" />
              Comments ({comments?.length || 0})
            </h3>

            <div className="space-y-4 mb-4">
              {comments && comments.length > 0 ? (
                comments.map((comment) => (
                  <div key={comment.id} className="space-y-3">
                    {/* Main Comment */}
                    <div className="flex space-x-3">
                      <Avatar
                        src={comment.author?.avatar_url}
                        name={comment.author?.full_name || comment.author?.username || 'Unknown'}
                        size="sm"
                      />
                      <div className="flex-1">
                        <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-sm text-gray-900">
                              {comment.author?.full_name || comment.author?.username || 'Unknown User'}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500">
                                {formatRelativeTime(comment.created_at)}
                              </span>
                              {(isAdmin || comment.author_id === user?.id) && (
                                <button
                                  onClick={() => handleDeleteComment(comment.id)}
                                  className="text-red-600 hover:text-red-700"
                                  title="Delete comment"
                                >
                                  <Trash2 size={14} />
                                </button>
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-gray-700 mb-2">{comment.content}</p>
                          
                          {/* Comment Attachments */}
                          {comment.attachments && comment.attachments.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {comment.attachments.map((attachment) => (
                                <div
                                  key={attachment.id}
                                  className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded text-xs"
                                >
                                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                                    <Paperclip size={14} className="text-gray-400 flex-shrink-0" />
                                    <span className="text-gray-700 truncate">{attachment.original_filename}</span>
                                    <span className="text-gray-400">({formatFileSize(attachment.file_size)})</span>
                                  </div>
                                  <button
                                    onClick={() => handleDownload(attachment)}
                                    className="text-primary-600 hover:text-primary-700 ml-2"
                                  >
                                    <Download size={14} />
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {/* Reply Button */}
                          <button
                            onClick={() => handleReply(comment.id, comment.author?.username || 'user')}
                            className="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1 mt-2"
                          >
                            <MessageSquare size={12} />
                            Reply
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Replies */}
                    {comment.replies && comment.replies.length > 0 && (
                      <div className="ml-12 space-y-3">
                        {comment.replies.map((reply) => (
                          <div key={reply.id} className="flex space-x-3">
                            <Avatar
                              src={reply.author?.avatar_url}
                              name={reply.author?.full_name || reply.author?.username || 'Unknown'}
                              size="xs"
                            />
                            <div className="flex-1">
                              <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                                <div className="flex items-center justify-between mb-1">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium text-sm text-gray-900">
                                      {reply.author?.full_name || reply.author?.username || 'Unknown User'}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                      replied to {comment.author?.username || 'user'}
                                    </span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs text-gray-500">
                                      {formatRelativeTime(reply.created_at)}
                                    </span>
                                    {(isAdmin || reply.author_id === user?.id) && (
                                      <button
                                        onClick={() => handleDeleteComment(reply.id)}
                                        className="text-red-600 hover:text-red-700"
                                        title="Delete reply"
                                      >
                                        <Trash2 size={14} />
                                      </button>
                                    )}
                                  </div>
                                </div>
                                <p className="text-sm text-gray-700 mb-2">{reply.content}</p>
                                
                                {/* Reply Attachments */}
                                {reply.attachments && reply.attachments.length > 0 && (
                                  <div className="mt-2 space-y-1">
                                    {reply.attachments.map((attachment) => (
                                      <div
                                        key={attachment.id}
                                        className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded text-xs"
                                      >
                                        <div className="flex items-center space-x-2 flex-1 min-w-0">
                                          <Paperclip size={14} className="text-gray-400 flex-shrink-0" />
                                          <span className="text-gray-700 truncate">{attachment.original_filename}</span>
                                          <span className="text-gray-400">({formatFileSize(attachment.file_size)})</span>
                                        </div>
                                        <button
                                          onClick={() => handleDownload(attachment)}
                                          className="text-primary-600 hover:text-primary-700 ml-2"
                                        >
                                          <Download size={14} />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500 italic py-4">No comments yet. Be the first to comment!</p>
              )}
            </div>

            {/* Add Comment */}
            <div className="space-y-2">
              {/* Reply indicator */}
              {replyingTo && (
                <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2 text-sm">
                    <MessageSquare size={14} className="text-blue-600" />
                    <span className="text-gray-700">
                      Replying to <span className="font-medium text-blue-600">@{replyingTo.username}</span>
                    </span>
                  </div>
                  <button
                    onClick={cancelReply}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X size={16} />
                  </button>
                </div>
              )}

              {/* Attachment preview */}
              {commentAttachment && (
                <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Paperclip size={14} className="text-green-600" />
                    <span className="text-gray-700 font-medium">{commentAttachment.name}</span>
                    <span className="text-gray-500 text-xs">({formatFileSize(commentAttachment.size)})</span>
                  </div>
                  <button
                    onClick={removeCommentAttachment}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X size={16} />
                  </button>
                </div>
              )}
              
              <div className="flex space-x-2">
                <div className="flex-1">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder={replyingTo ? `Reply to @${replyingTo.username}...` : "Add a comment..."}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <div className="mt-1">
                    <label className="inline-flex items-center gap-1.5 text-xs text-gray-600 hover:text-primary-600 cursor-pointer">
                      <Paperclip size={14} />
                      <span>Attach file</span>
                      <input
                        type="file"
                        className="hidden"
                        onChange={handleCommentFileSelect}
                      />
                    </label>
                  </div>
                </div>
                <Button
                  onClick={handleAddComment}
                  isLoading={isSubmitting}
                  disabled={!newComment.trim()}
                >
                  <Send size={18} />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Permission Info */}
          {!canEditTicket && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-blue-800 mb-1 font-medium">Developer Mode</p>
              <p className="text-xs text-blue-700">
                You can change status, add comments/attachments. Ticket details can only be edited by admins.
              </p>
            </div>
          )}
          
          {/* Workflow Actions */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-3">Actions</h4>
            <div className="space-y-3">
              {/* Delete Button */}
              <Button
                onClick={handleDelete}
                variant="outline"
                size="sm"
                className="w-full border-red-300 text-red-600 hover:bg-red-50 hover:border-red-400"
              >
                <Trash2 size={16} className="mr-2" />
                Delete Ticket
              </Button>
              {/* Status Transitions - Available to all users */}
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Change Status <span className="text-green-600">(All users)</span>
                </label>
                <select
                  value={selectedStatus || currentTicket.status}
                  onChange={(e) => setSelectedStatus(e.target.value as TicketStatus)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value={currentTicket.status}>
                    Current: {getStatusLabel(currentTicket.status)}
                  </option>
                  {getAvailableTransitions(currentTicket.status).map((status) => (
                    <option key={status} value={status}>
                      → {getStatusLabel(status)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Resolution (if transitioning to DONE or CANCELLED) */}
              {selectedStatus && (selectedStatus === TicketStatus.DONE || selectedStatus === TicketStatus.CANCELLED) && (
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Resolution
                  </label>
                  <select
                    value={selectedResolution || ''}
                    onChange={(e) => setSelectedResolution(e.target.value as Resolution)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select resolution...</option>
                    <option value={Resolution.FIXED}>Fixed</option>
                    <option value={Resolution.WONT_FIX}>Won't Fix</option>
                    <option value={Resolution.DUPLICATE}>Duplicate</option>
                    <option value={Resolution.INCOMPLETE}>Incomplete</option>
                  </select>
                </div>
              )}

              {/* Apply Button */}
              {selectedStatus && selectedStatus !== currentTicket.status && (
                <Button
                  onClick={() => handleStatusChange(selectedStatus, selectedResolution || undefined)}
                  isLoading={isUpdatingStatus}
                  size="sm"
                  className="w-full"
                >
                  <CheckCircle2 size={16} className="mr-2" />
                  Apply Status Change
                </Button>
              )}
            </div>
          </div>

          {/* Details */}
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Details</h4>
            <div className="space-y-3">
              <div className="flex items-start space-x-2 text-sm">
                <UserPlus size={16} className="text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <span className="text-gray-600 block mb-2">
                    Assignee {canEditTicket && <span className="text-xs text-primary-600">(Admin editable)</span>}
                  </span>
                  {currentTicket.assignee ? (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2 mb-1">
                        <Avatar
                          src={currentTicket.assignee.avatar_url}
                          name={
                            currentTicket.assignee.full_name ||
                            currentTicket.assignee.username
                          }
                          size="sm"
                        />
                        <span className="font-medium text-gray-700">
                          {currentTicket.assignee.username}
                        </span>
                      </div>
                      {canEditTicket && (
                        <select
                          value={currentTicket.assignee?.username || ''}
                          onChange={(e) => handleAssignTicket(e.target.value || null)}
                          disabled={isAssigning}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900"
                        >
                          <option value="" className="text-gray-500">Unassign</option>
                          {projectMembers.map((member) => (
                            <option key={member.id} value={member.username} className="text-gray-900">
                              {member.username}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <span className="text-gray-500 block text-sm italic">No one assigned</span>
                      {canEditTicket && (
                        <select
                          value=""
                          onChange={(e) => handleAssignTicket(e.target.value || null)}
                          disabled={isAssigning}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-gray-900"
                        >
                          <option value="" className="text-gray-500">Select member to assign...</option>
                          {projectMembers.map((member) => (
                            <option key={member.id} value={member.username} className="text-gray-900">
                              {member.username}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-start space-x-2 text-sm">
                <User size={16} className="text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <span className="text-gray-600 block">Reporter <span className="text-xs text-gray-500">(Fixed)</span>:</span>
                  <span className="font-medium">{currentTicket.reporter.username}</span>
                </div>
              </div>

              {currentTicket.resolution && (
                <div className="flex items-start space-x-2 text-sm">
                  <CheckCircle2 size={16} className="text-gray-400 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-gray-600 block">Resolution:</span>
                    <span className="font-medium capitalize">
                      {currentTicket.resolution.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              )}

              {currentTicket.due_date && (
                <div className="flex items-start space-x-2 text-sm">
                  <Calendar size={16} className="text-gray-400 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-gray-600 block">Due Date:</span>
                    <span className="font-medium">
                      {formatDateTime(currentTicket.due_date)}
                    </span>
                  </div>
                </div>
              )}

              <div className="flex items-start space-x-2 text-sm">
                <Calendar size={16} className="text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <span className="text-gray-600 block">Created:</span>
                  <span className="font-medium">
                    {formatDateTime(currentTicket.created_at)}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-2 text-sm">
                <Calendar size={16} className="text-gray-400 mt-0.5" />
                <div className="flex-1">
                  <span className="text-gray-600 block">Updated:</span>
                  <span className="font-medium">
                    {formatRelativeTime(currentTicket.updated_at)}
                  </span>
                </div>
              </div>

              {currentTicket.resolved_at && (
                <div className="flex items-start space-x-2 text-sm">
                  <CheckCircle2 size={16} className="text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <span className="text-gray-600 block">Resolved:</span>
                    <span className="font-medium">
                      {formatDateTime(currentTicket.resolved_at)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Labels */}
          {currentTicket.labels && currentTicket.labels.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Labels</h4>
              <div className="flex flex-wrap gap-2">
                {currentTicket.labels.map((label) => (
                  <span
                    key={label.id}
                    className="badge"
                    style={{
                      backgroundColor: label.color + '20',
                      color: label.color,
                    }}
                  >
                    {label.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
