import { DroppableProvided } from '@hello-pangea/dnd';
import { Ticket } from '@/types';
import { TicketCard } from './TicketCard';

interface KanbanColumnProps {
  title: string;
  tickets: Ticket[];
  provided: DroppableProvided;
  isDraggingOver: boolean;
  onTicketClick: (ticketId: string) => void;
  onTicketEdit: (ticket: Ticket) => void;
}

export function KanbanColumn({
  title,
  tickets,
  provided,
  isDraggingOver,
  onTicketClick,
  onTicketEdit,
}: KanbanColumnProps) {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className="bg-gray-200 text-gray-700 text-xs font-medium px-2 py-1 rounded-full">
          {tickets.length}
        </span>
      </div>

      <div
        ref={provided.innerRef}
        {...provided.droppableProps}
        className={`flex-1 space-y-3 p-2 rounded-lg transition-colors ${
          isDraggingOver ? 'bg-primary-50' : 'bg-gray-50'
        }`}
        style={{ minHeight: '500px' }}
      >
        {tickets.map((ticket, index) => (
          <TicketCard
            key={ticket.id}
            ticket={ticket}
            index={index}
            onClick={() => onTicketClick(ticket.id)}
            onEdit={onTicketEdit}
          />
        ))}
        {provided.placeholder}
      </div>
    </div>
  );
}
