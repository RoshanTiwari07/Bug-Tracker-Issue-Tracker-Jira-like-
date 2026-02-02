import { useState, FormEvent } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useTicketStore } from '@/stores/ticketStore';
import { IssueType, TicketPriority } from '@/types';
import { attachmentsApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { Paperclip, X } from 'lucide-react';

interface CreateTicketModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
}

export function CreateTicketModal({
  isOpen,
  onClose,
  projectName,
}: CreateTicketModalProps) {
  const { createTicket } = useTicketStore();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: IssueType.TASK,
    priority: TicketPriority.MEDIUM,
    due_date: '',
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const ticketData = {
        ...formData,
        project_name: projectName,
      };
      console.log('Creating ticket with data:', ticketData);
      const ticket = await createTicket(ticketData);

      // Upload attachments if any
      if (selectedFiles.length > 0) {
        const uploadPromises = selectedFiles.map(file => 
          attachmentsApi.uploadAttachment(ticket.id, file)
            .catch(err => {
              console.error(`Failed to upload ${file.name}:`, err);
              console.error('Error details:', JSON.stringify(err.response?.data, null, 2));
              console.error('Error status:', err.response?.status);
              return null;
            })
        );
        
        const results = await Promise.all(uploadPromises);
        const failedCount = results.filter(r => r === null).length;
        
        if (failedCount > 0) {
          toast.error(`Ticket created, but ${failedCount} attachment(s) failed to upload`);
        } else {
          toast.success(`Ticket created with ${selectedFiles.length} attachment(s)`);
        }
      } else {
        toast.success('Ticket created successfully');
      }

      onClose();
      setFormData({
        title: '',
        description: '',
        type: IssueType.TASK,
        priority: TicketPriority.MEDIUM,
        due_date: '',
      });
      setSelectedFiles([]);
    } catch (error: any) {
      console.error('Error creating ticket:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to create ticket');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Ticket" size="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Enter ticket title"
          required
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="Enter ticket description"
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={formData.type}
              onChange={(e) =>
                setFormData({ ...formData, type: e.target.value as IssueType })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
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
              onChange={(e) =>
                setFormData({
                  ...formData,
                  priority: e.target.value as TicketPriority,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={TicketPriority.LOW}>Low</option>
              <option value={TicketPriority.MEDIUM}>Medium</option>
              <option value={TicketPriority.HIGH}>High</option>
              <option value={TicketPriority.CRITICAL}>Critical</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Due Date (Optional)
          </label>
          <input
            type="date"
            value={formData.due_date}
            onChange={(e) =>
              setFormData({ ...formData, due_date: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attachments
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-gray-400 transition-colors">
            <label className="flex flex-col items-center cursor-pointer">
              <Paperclip className="w-8 h-8 text-gray-400 mb-2" />
              <span className="text-sm text-gray-600">Click to attach files</span>
              <span className="text-xs text-gray-500 mt-1">PDF, images, documents accepted</span>
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.gif,.xlsx,.xls"
              />
            </label>
          </div>
          
          {selectedFiles.length > 0 && (
            <div className="mt-3 space-y-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={`${file.name}-${index}`}
                  className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <Paperclip className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span className="text-sm text-gray-700 truncate">{file.name}</span>
                    <span className="text-xs text-gray-500 flex-shrink-0">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="ml-2 p-1 text-red-600 hover:text-red-700 hover:bg-red-50 rounded"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={isLoading}>
            Create Ticket
          </Button>
        </div>
      </form>
    </Modal>
  );
}
