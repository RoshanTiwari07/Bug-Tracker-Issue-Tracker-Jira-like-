import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/stores/projectStore';
import { Layout } from '@/components/layout/Layout';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Avatar } from '@/components/ui/Avatar';
import { projectsApi, usersApi } from '@/lib/api';
import { User, ProjectMember, ProjectRole } from '@/types';
import { ArrowLeft, UserPlus, Trash2, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

export function ProjectSettings() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { currentProject, fetchProject } = useProjectStore();
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedRole, setSelectedRole] = useState<ProjectRole>(ProjectRole.DEVELOPER);
  const [isLoading, setIsLoading] = useState(false);
  const [operationLoading, setOperationLoading] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
      loadMembers();
      loadUsers();
    }
  }, [projectId]);

  const loadMembers = async () => {
    if (!projectId) return;
    try {
      const data = await projectsApi.getMembers(projectId);
      setMembers(data);
    } catch (error) {
      toast.error('Failed to load members');
    }
  };

  const loadUsers = async () => {
    try {
      const data = await usersApi.getUsers();
      setUsers(data);
    } catch (error) {
      toast.error('Failed to load users');
    }
  };

  const handleAddMember = async () => {
    if (!projectId || !selectedUserId) return;
    
    setIsLoading(true);
    try {
      await projectsApi.addMember(projectId, selectedUserId, selectedRole);
      toast.success('Member added successfully');
      setShowAddModal(false);
      setSelectedUserId('');
      setSelectedRole(ProjectRole.DEVELOPER);
      loadMembers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add member');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!projectId) return;
    
    if (!confirm('Are you sure you want to remove this member?')) return;

    setOperationLoading(userId);
    try {
      await projectsApi.removeMember(projectId, userId);
      toast.success('Member removed successfully');
      loadMembers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to remove member');
    } finally {
      setOperationLoading(null);
    }
  };

  const getUserById = (userId: string) => {
    return users.find(u => u.id === userId);
  };

  const availableUsers = users.filter(
    user => !members.some(member => member.user_id === user.id)
  );

  if (!currentProject) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600">Loading project...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate(`/board/${projectId}`)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Back to Board"
            >
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Project Settings</h1>
              <p className="text-gray-600 mt-1">{currentProject.name}</p>
            </div>
          </div>
        </div>

        {/* Project Info Card */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
            <h2 className="text-xl font-semibold text-white">Project Information</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Project Name</label>
                <p className="text-lg text-gray-900 mt-1">{currentProject.name}</p>
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Project Key</label>
                <p className="text-lg text-gray-900 mt-1 font-mono bg-gray-100 px-3 py-1 rounded inline-block">
                  {currentProject.key}
                </p>
              </div>
              <div className="md:col-span-2">
                <label className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Description</label>
                <p className="text-gray-900 mt-1">{currentProject.description || 'No description provided'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Team Members Card */}
        <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <h2 className="text-xl font-semibold text-white">Team Members</h2>
              <span className="bg-white text-purple-600 text-sm font-bold px-3 py-1 rounded-full">
                {members.length}
              </span>
            </div>
            <Button 
              onClick={() => setShowAddModal(true)}
              className="bg-white text-purple-600 hover:bg-purple-50"
            >
              <UserPlus size={20} className="mr-2" />
              Add Member
            </Button>
          </div>
          <div className="p-6">
            {members.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                  <UserPlus size={32} className="text-gray-400" />
                </div>
                <p className="text-gray-500 text-lg mb-2">No team members yet</p>
                <p className="text-gray-400 text-sm mb-4">Add members to collaborate on this project</p>
                <Button onClick={() => setShowAddModal(true)}>
                  <UserPlus size={20} className="mr-2" />
                  Add Your First Member
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {members.map((member) => {
                  const user = getUserById(member.user_id);
                  if (!user) return null;

                  const roleColors = {
                    [ProjectRole.OWNER]: 'bg-yellow-100 text-yellow-800 border-yellow-200',
                    [ProjectRole.ADMIN]: 'bg-red-100 text-red-800 border-red-200',
                    [ProjectRole.DEVELOPER]: 'bg-blue-100 text-blue-800 border-blue-200',
                    [ProjectRole.VIEWER]: 'bg-gray-100 text-gray-800 border-gray-200',
                  };

                  return (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center space-x-4">
                        <Avatar
                          src={user.avatar_url}
                          name={user.full_name || user.username}
                          size="lg"
                        />
                        <div>
                          <p className="font-semibold text-gray-900 text-lg">
                            {user.full_name || user.username}
                          </p>
                          <p className="text-sm text-gray-600">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`px-4 py-2 rounded-full text-sm font-semibold border ${roleColors[member.role as ProjectRole] || roleColors[ProjectRole.VIEWER]}`}>
                          {member.role}
                        </span>
                        {member.role !== ProjectRole.OWNER && (
                          <button
                            onClick={() => handleRemoveMember(member.user_id)}
                            disabled={operationLoading === member.user_id}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:text-gray-400 disabled:hover:bg-white disabled:cursor-not-allowed"
                            title="Remove member"
                          >
                            {operationLoading === member.user_id ? (
                              <Loader size={20} className="animate-spin" />
                            ) : (
                              <Trash2 size={20} />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Member Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add Team Member"
        size="md"
      >
        <div className="space-y-6">
          {/* User Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Select User *
            </label>
            {availableUsers.length === 0 ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
                <p className="text-yellow-800 text-sm">
                  All users are already members of this project
                </p>
              </div>
            ) : (
              <select
                value={selectedUserId}
                onChange={(e) => setSelectedUserId(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              >
                <option value="">Choose a user...</option>
                {availableUsers.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.full_name || user.username} • {user.email}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Assign Role *
            </label>
            <div className="grid grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setSelectedRole(ProjectRole.VIEWER)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedRole === ProjectRole.VIEWER
                    ? 'border-purple-500 bg-purple-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-1">👁️</div>
                  <div className="font-semibold text-sm">Viewer</div>
                </div>
              </button>
              <button
                type="button"
                onClick={() => setSelectedRole(ProjectRole.DEVELOPER)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedRole === ProjectRole.DEVELOPER
                    ? 'border-purple-500 bg-purple-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-1">💻</div>
                  <div className="font-semibold text-sm">Developer</div>
                </div>
              </button>
              <button
                type="button"
                onClick={() => setSelectedRole(ProjectRole.ADMIN)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedRole === ProjectRole.ADMIN
                    ? 'border-purple-500 bg-purple-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-center">
                  <div className="text-2xl mb-1">⚙️</div>
                  <div className="font-semibold text-sm">Admin</div>
                </div>
              </button>
            </div>
          </div>

          {/* Role Descriptions */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2 text-sm">Role Permissions:</h4>
            <div className="space-y-2 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <span className="font-semibold min-w-[80px]">👁️ Viewer:</span>
                <span>Can view tickets and project details</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-semibold min-w-[80px]">💻 Developer:</span>
                <span>Can create, edit, and manage tickets</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-semibold min-w-[80px]">⚙️ Admin:</span>
                <span>Full access to project and member management</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setShowAddModal(false);
                setSelectedUserId('');
                setSelectedRole(ProjectRole.DEVELOPER);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddMember}
              isLoading={isLoading}
              disabled={!selectedUserId || availableUsers.length === 0}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <UserPlus size={18} className="mr-2" />
              Add Member
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}
