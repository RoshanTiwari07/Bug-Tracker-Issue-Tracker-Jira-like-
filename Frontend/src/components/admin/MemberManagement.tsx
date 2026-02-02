import { useEffect, useState } from 'react';
import { projectsApi } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Users, Crown, Shield, Eye, Trash2, Edit2, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

interface Member {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
  joined_at: string;
}

interface MemberManagementProps {
  projectId: string;
  onInviteClick: () => void;
  userRole?: string;
}

export function MemberManagement({ projectId, onInviteClick, userRole = 'admin' }: MemberManagementProps) {
  const isAdmin = userRole === 'admin' || userRole === 'owner';
  const [members, setMembers] = useState<Member[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingMemberId, setEditingMemberId] = useState<string | null>(null);
  const [editingRole, setEditingRole] = useState<string>('developer');
  const [operationLoading, setOperationLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchMembers();
  }, [projectId]);

  const fetchMembers = async () => {
    try {
      const data = await projectsApi.getMembers(projectId);
      setMembers(data);
    } catch (error) {
      toast.error('Failed to load members');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateRole = async (memberId: string) => {
    if (!window.confirm('Are you sure you want to change this member\'s role?')) return;
    
    setOperationLoading(memberId);
    try {
      await projectsApi.updateMemberRole(projectId, memberId, editingRole);
      setMembers(
        members.map((m) => (m.id === memberId ? { ...m, role: editingRole } : m))
      );
      setEditingMemberId(null);
      toast.success('Member role updated');
    } catch (error) {
      toast.error('Failed to update member role');
    } finally {
      setOperationLoading(null);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!window.confirm('Remove this member from the project?')) return;

    setOperationLoading(memberId);
    try {
      await projectsApi.removeMember(projectId, memberId);
      setMembers(members.filter((m) => m.id !== memberId));
      toast.success('Member removed');
    } catch (error) {
      toast.error('Failed to remove member');
    } finally {
      setOperationLoading(null);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
      case 'admin':
        return <Crown size={16} className="text-yellow-500" />;
      case 'developer':
        return <Shield size={16} className="text-blue-500" />;
      case 'viewer':
        return <Eye size={16} className="text-gray-500" />;
      default:
        return null;
    }
  };

  const maskEmail = (email: string) => {
    if (!email || typeof email !== 'string') return '';
    const [username, domain] = email.split('@');
    if (!username || !domain) return email;
    const maskedUsername = username.length > 2
      ? username.slice(0, 2) + '*'.repeat(username.length - 2)
      : username;
    return `${maskedUsername}@${domain}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="animate-spin text-blue-600" size={24} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Users size={24} />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Team Members</h3>
            <p className="text-sm text-gray-600">{members.length}</p>
          </div>
        </div>
        {isAdmin && (
          <Button
            onClick={onInviteClick}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Add Member
          </Button>
        )}
      </div>

      {/* Members List */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Member</th>
              {isAdmin && (
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Email</th>
              )}
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Role</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Joined</th>
              {isAdmin && (
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
              )}
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id} className="border-b hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div>
                    <p className="font-semibold text-gray-900">
                      {member.full_name || member.username}
                    </p>
                    <p className="text-sm text-gray-600">@{member.username}</p>
                  </div>
                </td>
                {isAdmin && (
                  <td className="px-6 py-4 text-sm text-gray-600">{maskEmail(member.email)}</td>
                )}
                <td className="px-6 py-4">
                  {isAdmin && editingMemberId === member.id ? (
                    <select
                      value={editingRole}
                      onChange={(e) => setEditingRole(e.target.value)}
                      disabled={operationLoading === member.id}
                      className="border border-gray-300 rounded px-2 py-1 text-sm disabled:bg-gray-100"
                    >
                      <option value="admin">Admin</option>
                      <option value="developer">Developer</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  ) : (
                    <div className="flex items-center space-x-2">
                      {getRoleIcon(member.role)}
                      <span className="text-sm font-semibold capitalize text-gray-900">
                        {member.role}
                      </span>
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {new Date(member.joined_at).toLocaleDateString()}
                </td>
                {isAdmin && (
                  <td className="px-6 py-4">
                    {member.role !== 'owner' && (
                    <div className="flex items-center space-x-2">
                      {editingMemberId === member.id ? (
                        <>
                          <button
                            onClick={() => handleUpdateRole(member.id)}
                            disabled={operationLoading === member.id}
                            className="text-green-600 hover:text-green-700 font-semibold text-sm disabled:text-gray-400 disabled:cursor-not-allowed flex items-center space-x-1"
                          >
                            {operationLoading === member.id && <Loader size={14} className="animate-spin" />}
                            <span>Save</span>
                          </button>
                          <button
                            onClick={() => setEditingMemberId(null)}
                            disabled={operationLoading === member.id}
                            className="text-gray-600 hover:text-gray-700 text-sm disabled:text-gray-400 disabled:cursor-not-allowed"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => {
                              setEditingMemberId(member.id);
                              setEditingRole(member.role);
                            }}
                            disabled={operationLoading === member.id}
                            className="text-blue-600 hover:text-blue-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                            title="Edit role"
                          >
                            <Edit2 size={16} />
                          </button>
                          <button
                            onClick={() => handleRemoveMember(member.id)}
                            disabled={operationLoading === member.id}
                            className="text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
                            title="Remove member"
                          >
                            {operationLoading === member.id ? (
                              <Loader size={16} className="animate-spin" />
                            ) : (
                              <Trash2 size={16} />
                            )}
                          </button>
                        </>
                      )}
                    </div>
                  )}
                  {member.role === 'owner' && (
                    <span className="text-xs font-semibold text-yellow-600">Owner</span>
                  )}
                </td>
              )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
