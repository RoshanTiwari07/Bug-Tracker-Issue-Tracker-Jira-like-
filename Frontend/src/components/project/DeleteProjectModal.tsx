import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import toast from 'react-hot-toast';

interface DeleteProjectModalProps {
  isOpen: boolean;
  projectName: string;
  projectKey: string;
  onClose: () => void;
  onConfirmDelete: () => Promise<void>;
}

export function DeleteProjectModal({
  isOpen,
  projectName,
  projectKey,
  onClose,
  onConfirmDelete,
}: DeleteProjectModalProps) {
  const [inputValue, setInputValue] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [showSuggestion, setShowSuggestion] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    setShowSuggestion(value.length > 0 && value !== projectName);
  };

  const isNameCorrect = inputValue === projectName;

  const handleDelete = async () => {
    if (!isNameCorrect) {
      toast.error('Project name does not match');
      return;
    }

    setIsDeleting(true);
    try {
      await onConfirmDelete();
      toast.success(`Project "${projectName}" deleted successfully`);
      setInputValue('');
      onClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete project';
      toast.error(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClickSuggestion = () => {
    setInputValue(projectName);
    setShowSuggestion(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="text-red-600" size={24} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Delete Project</h2>
              <p className="text-sm text-gray-600">This action cannot be undone</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Project Info Card */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
            <div>
              <p className="text-sm font-semibold text-gray-600">Project Name</p>
              <p className="text-base font-bold text-gray-900">{projectName}</p>
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-600">Project Key</p>
              <p className="text-base font-mono text-gray-900">{projectKey}</p>
            </div>
          </div>

          {/* Warning Message */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">
              <strong>Warning:</strong> Deleting this project will permanently remove all associated tickets, comments, and attachments.
            </p>
          </div>

          {/* Input Field */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-gray-700">
              Type project name to confirm deletion
            </label>
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                placeholder={`Type "${projectName}" to confirm`}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
              
              {/* Suggestion */}
              {showSuggestion && (
                <button
                  onClick={handleClickSuggestion}
                  className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm rounded transition-colors"
                >
                  {projectName}
                </button>
              )}
            </div>
          </div>

          {/* Info Text */}
          <p className="text-xs text-gray-600">
            Enter the exact project name "{projectName}" above to enable the delete button.
          </p>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          <button
            onClick={onClose}
            disabled={isDeleting}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={!isNameCorrect || isDeleting}
            className={`flex-1 px-4 py-2 rounded-lg font-semibold text-white transition-colors ${
              isNameCorrect && !isDeleting
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isDeleting ? 'Deleting...' : 'Delete Project'}
          </button>
        </div>
      </div>
    </div>
  );
}
