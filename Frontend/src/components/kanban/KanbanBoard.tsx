import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, DropResult, DroppableProvided, DroppableStateSnapshot } from '@hello-pangea/dnd';
import { useTicketStore } from '@/stores/ticketStore';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';
import { TicketStatus, TicketPriority, UserRole } from '@/types';
import { KanbanColumn } from './KanbanColumn';
import { TicketDetailsModal } from './TicketDetailsModal';
import { CreateTicketModal } from './CreateTicketModal';
import { Button } from '@/components/ui/Button';
import { Plus, Search, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const COLUMNS = [
  { 
    id: TicketStatus.IDEA, 
    title: 'IDEA', 
    color: 'bg-purple-400',
    wipLimit: 5,
    showCommitmentPoint: true
  },
  { 
    id: TicketStatus.TODO, 
    title: 'TODO', 
    color: 'bg-cyan-400',
    wipLimit: 5,
    showCommitmentPoint: false
  },
  { 
    id: TicketStatus.IN_PROGRESS, 
    title: 'IN PROGRESS', 
    color: 'bg-orange-400',
    wipLimit: 4,
    showDeliveryPoint: true
  },
  { 
    id: TicketStatus.IN_REVIEW, 
    title: 'TESTING', 
    color: 'bg-yellow-400',
    wipLimit: 3
  },
  { 
    id: TicketStatus.DONE, 
    title: 'DONE', 
    color: 'bg-teal-400',
    wipLimit: null
  },
];

export function KanbanBoard({ projectName }: { projectName?: string }) {
  const navigate = useNavigate();
  const { currentProject } = useProjectStore();
  const { user } = useAuthStore();
  const { tickets, searchTickets, changeTicketStatus } = useTicketStore();
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [editingTicketId, setEditingTicketId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const isAdmin = user?.role === UserRole.ADMIN;

  const handleEditTicket = (ticket: any) => {
    setEditingTicketId(ticket.id);
  };

  useEffect(() => {
    if (currentProject && currentProject.id) {
      searchTickets(currentProject.name);
    }
  }, [currentProject, searchTickets]);

  const handleDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const newStatus = destination.droppableId as TicketStatus;
    
    try {
      await changeTicketStatus(draggableId, newStatus);
      // Refresh tickets to ensure UI is in sync with backend
      if (currentProject) {
        await searchTickets(currentProject.name);
      }
      toast.success('Ticket status updated');
    } catch (error) {
      toast.error('Failed to update ticket status');
      // Refresh on error too to reset UI to actual backend state
      if (currentProject) {
        await searchTickets(currentProject.name);
      }
    }
  };

  const handleSearch = () => {
    if (currentProject) {
      searchTickets(currentProject.name, { keyword: searchQuery });
    }
  };

  const getTicketsByStatus = (status: TicketStatus) => {
    return tickets.filter((ticket) => ticket.status === status);
  };

  const getExpediteTickets = () => {
    return tickets.filter((ticket) => ticket.priority === TicketPriority.CRITICAL);
  };

  const isOverWipLimit = (status: TicketStatus, wipLimit: number | null) => {
    if (!wipLimit) return false;
    return getTicketsByStatus(status).length > wipLimit;
  };

  if (!currentProject) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please select a project to view the board</p>
      </div>
    );
  }

  return (
    <div className="h-full">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          {/* Project Name & Key Badge */}
          <div className="flex items-center space-x-3">
            <div className="flex items-baseline space-x-3">
              {isAdmin && (
                <span className="inline-flex items-center px-4 py-2 rounded-lg bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold text-sm shadow-md">
                  {currentProject.key}
                </span>
              )}
              <h1 className="text-2xl font-bold text-gray-900">
                {currentProject.name}
              </h1>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus size={20} className="mr-2" />
              Create Ticket
            </Button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex items-center space-x-4">
          <div className="flex-1 flex items-center space-x-2">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <Button variant="secondary" onClick={handleSearch}>
              Search
            </Button>
          </div>
        </div>
      </div>

      {/* Kanban Board with Labels */}
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 shadow-lg border border-gray-200">
        {/* Commitment and Delivery Point Markers */}
        <div className="flex justify-between mb-4 px-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow"></div>
            <span className="text-sm font-semibold text-blue-700 uppercase">Commitment Point</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow"></div>
            <span className="text-sm font-semibold text-blue-700 uppercase">Delivery Point</span>
          </div>
        </div>

        <DragDropContext onDragEnd={handleDragEnd}>
          {/* Regular Swimlane */}
          <div className="mb-6">
            <div className="grid grid-cols-5 gap-3">
              {/* Kanban Columns */}
              {COLUMNS.map((column) => {
                const columnTickets = getTicketsByStatus(column.id);
                const isOverLimit = isOverWipLimit(column.id, column.wipLimit);
                
                return (
                  <div key={column.id} className="relative">
                    {/* Commitment/Delivery Point Indicator */}
                    {column.showCommitmentPoint && (
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center">
                        <div className="w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow"></div>
                        <div className="h-4 w-0.5 bg-blue-600 border-l-2 border-dashed border-blue-400"></div>
                      </div>
                    )}
                    {column.showDeliveryPoint && (
                      <div className="absolute -top-8 right-0 flex flex-col items-center">
                        <div className="w-4 h-4 rounded-full bg-blue-600 border-2 border-white shadow"></div>
                        <div className="h-4 w-0.5 bg-blue-600 border-l-2 border-dashed border-blue-400"></div>
                      </div>
                    )}

                    {/* Column Header */}
                    <div className={`${column.color} text-white px-4 py-3 rounded-t-lg font-bold text-center text-sm shadow-md`}>
                      <div>{column.title}</div>
                      {column.wipLimit && (
                        <div className="text-xs mt-1 flex items-center justify-center space-x-1">
                          <span>{columnTickets.length}/{column.wipLimit}</span>
                          {isOverLimit && <AlertCircle size={14} className="text-red-200" />}
                        </div>
                      )}
                    </div>

                    {/* Column Content */}
                    <Droppable droppableId={column.id}>
                      {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className={`bg-white rounded-b-lg p-2 min-h-[500px] border-2 transition-colors ${
                            snapshot.isDraggingOver ? 'border-primary-400 bg-primary-50' : 'border-gray-200'
                          } ${isOverLimit ? 'border-red-400' : ''}`}
                        >
                          <KanbanColumn
                            title=""
                            tickets={columnTickets}
                            provided={provided}
                            isDraggingOver={snapshot.isDraggingOver}
                            onTicketClick={setSelectedTicketId}
                            onTicketEdit={handleEditTicket}
                          />
                        </div>
                      )}
                    </Droppable>
                  </div>
                );
              })}
            </div>
          </div>
        </DragDropContext>
      </div>

      {/* Modals */}
      {selectedTicketId && (
        <TicketDetailsModal
          ticketId={selectedTicketId}
          isOpen={!!selectedTicketId}
          onClose={() => setSelectedTicketId(null)}
        />
      )}

      {editingTicketId && (
        <TicketDetailsModal
          ticketId={editingTicketId}
          isOpen={!!editingTicketId}
          startInEditMode={true}
          onClose={() => {
            setEditingTicketId(null);
            // Refresh tickets after editing
            if (currentProject) {
              searchTickets(currentProject.name);
            }
          }}
        />
      )}

      {showCreateModal && (
        <CreateTicketModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          projectName={currentProject.name}
        />
      )}
    </div>
  );
}
