import { Draggable } from '@hello-pangea/dnd';
import { Ticket } from '@/types';
import { Avatar } from '@/components/ui/Avatar';
import {
  getPriorityColor,
  getIssueTypeIcon,
  truncate,
} from '@/lib/utils';
import { MessageSquare, Paperclip, Edit2 } from 'lucide-react';

interface TicketCardProps {
  ticket: Ticket;
  index: number;
  onClick: () => void;
  onEdit?: (ticket: Ticket) => void;
}

export function TicketCard({ ticket, index, onClick, onEdit }: TicketCardProps) {
  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onEdit) {
      onEdit(ticket);
    }
  };

  return (
    <Draggable draggableId={ticket.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={onClick}
          className={`bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
            snapshot.isDragging ? 'shadow-lg ring-2 ring-primary-500' : ''
          }`}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getIssueTypeIcon(ticket.type)}</span>
              <span className="text-xs font-medium text-gray-500">{ticket.key}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleEditClick}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Edit ticket"
              >
                <Edit2 size={14} className="text-gray-600 hover:text-primary-600" />
              </button>
              <span
                className={`badge border ${getPriorityColor(ticket.priority)}`}
              >
                {ticket.priority}
              </span>
            </div>
          </div>

          {/* Title */}
          <h4 className="font-medium text-gray-900 mb-2 line-clamp-2">
            {ticket.title}
          </h4>

          {/* Description */}
          {ticket.description && (
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {truncate(ticket.description, 80)}
            </p>
          )}

          {/* Labels */}
          {ticket.labels && ticket.labels.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {ticket.labels.slice(0, 3).map((label) => (
                <span
                  key={label.id}
                  className="badge text-xs"
                  style={{
                    backgroundColor: label.color + '20',
                    color: label.color,
                  }}
                >
                  {label.name}
                </span>
              ))}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center space-x-3 text-gray-500">
              {ticket.comments_count > 0 && (
                <div className="flex items-center space-x-1 text-xs">
                  <MessageSquare size={14} />
                  <span>{ticket.comments_count}</span>
                </div>
              )}
              {ticket.attachments_count > 0 && (
                <div className="flex items-center space-x-1 text-xs">
                  <Paperclip size={14} />
                  <span>{ticket.attachments_count}</span>
                </div>
              )}
            </div>

            {ticket.assignee && (
              <Avatar
                src={ticket.assignee.avatar_url}
                name={ticket.assignee.full_name || ticket.assignee.username}
                size="sm"
              />
            )}
          </div>
        </div>
      )}
    </Draggable>
  );
}
