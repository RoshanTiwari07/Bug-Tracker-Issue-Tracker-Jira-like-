import { useState, useCallback, useEffect } from 'react';
import { projectsApi, invitationsApi, usersApi } from '@/lib/api';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Search, UserPlus, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
}

interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  onSuccess?: () => void;
}

export function InviteMemberModal({ isOpen, onClose, projectId, onSuccess }: InviteMemberModalProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [role, setRole] = useState('developer');
  const [isSearching, setIsSearching] = useState(false);
  const [isInviting, setIsInviting] = useState(false);

  // Load all users when modal opens
  useEffect(() => {
    if (!isOpen) return;
    
    const loadUsers = async () => {
      try {
        const users = await usersApi.getUsers();
        setAllUsers(users as any);
      } catch (error) {
        toast.error('Failed to load users');
      }
    };
    
    loadUsers();
  }, [isOpen]);

  const handleSearch = useCallback((query: string) => {
    if (query.length < 1) {
      setSearchResults([]);
      return;
    }

    // Filter users locally based on query
    const filtered = allUsers.filter(
      (user) =>
        user.username.toLowerCase().includes(query.toLowerCase()) ||
        user.email.toLowerCase().includes(query.toLowerCase()) ||
        (user.full_name && user.full_name.toLowerCase().includes(query.toLowerCase()))
    );
    setSearchResults(filtered);
  }, [allUsers]);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setSelectedUser(null);
    handleSearch(value);
  };

  const handleSelectUser = (user: User) => {
    setSelectedUser(user);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleInvite = async () => {
    if (!selectedUser) {
      toast.error('Please select a user');
      return;
    }

    setIsInviting(true);
    try {
      await invitationsApi.sendInvitation(projectId, selectedUser.id, role);
      toast.success('Invitation sent successfully!');
      setSelectedUser(null);
      setRole('developer');
      onSuccess?.();
      onClose();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setIsInviting(false);
    }
  };

  const handleRemoveSelected = () => {
    setSelectedUser(null);
    setSearchQuery('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Member to Project" size="md">
      <div className="space-y-6">
        {/* Search User */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            <Search size={16} className="inline mr-2" />
            Search by username or email
          </label>
          <div className="relative z-20">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              placeholder="john_doe or john@example.com"
              disabled={!!selectedUser}
            />
            {isSearching && <Loader className="absolute right-3 top-3 animate-spin text-gray-400" size={18} />}

            {/* Search Results */}
            {searchResults.length > 0 && !selectedUser && (
              <div className="absolute z-30 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {searchResults.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => handleSelectUser(user)}
                    className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b last:border-b-0 transition-colors"
                  >
                    <div className="font-semibold text-gray-900">{user.full_name || user.username}</div>
                    <div className="text-sm text-gray-600">@{user.username}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </button>
                ))}
              </div>
            )}
            {searchQuery.length >= 2 && searchResults.length === 0 && !isSearching && !selectedUser && (
              <div className="absolute z-30 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-center">
                <p className="text-gray-600 text-sm">No users found matching "{searchQuery}"</p>
              </div>
            )}
          </div>
        </div>

        {/* Selected User */}
        {selectedUser && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-900">{selectedUser.full_name || selectedUser.username}</h4>
                <p className="text-sm text-gray-600">@{selectedUser.username}</p>
                <p className="text-xs text-gray-500">{selectedUser.email}</p>
              </div>
              <button
                onClick={handleRemoveSelected}
                className="text-blue-600 hover:text-blue-700 font-semibold text-sm"
              >
                Change
              </button>
            </div>
          </div>
        )}

        {/* Role Selection */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">Role</label>
          <div className="space-y-2">
            <label className="flex items-center space-x-3 cursor-pointer p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="role"
                value="viewer"
                checked={role === 'viewer'}
                onChange={(e) => setRole(e.target.value)}
                className="w-4 h-4"
              />
              <div>
                <span className="font-semibold text-gray-900">Viewer</span>
                <p className="text-xs text-gray-600">Read-only access</p>
              </div>
            </label>
            <label className="flex items-center space-x-3 cursor-pointer p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="role"
                value="developer"
                checked={role === 'developer'}
                onChange={(e) => setRole(e.target.value)}
                className="w-4 h-4"
              />
              <div>
                <span className="font-semibold text-gray-900">Developer</span>
                <p className="text-xs text-gray-600">Can create & edit tickets</p>
              </div>
            </label>
            <label className="flex items-center space-x-3 cursor-pointer p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <input
                type="radio"
                name="role"
                value="admin"
                checked={role === 'admin'}
                onChange={(e) => setRole(e.target.value)}
                className="w-4 h-4"
              />
              <div>
                <span className="font-semibold text-gray-900">Admin</span>
                <p className="text-xs text-gray-600">Can manage project & members</p>
              </div>
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="secondary" onClick={onClose} disabled={isInviting}>
            Cancel
          </Button>
          <Button
            onClick={handleInvite}
            disabled={!selectedUser || isInviting}
            className="bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-400"
          >
            {isInviting ? (
              <>
                <Loader size={16} className="animate-spin mr-2" />
                Sending...
              </>
            ) : (
              <>
                <UserPlus size={16} className="mr-2" />
                Send Invitation
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
