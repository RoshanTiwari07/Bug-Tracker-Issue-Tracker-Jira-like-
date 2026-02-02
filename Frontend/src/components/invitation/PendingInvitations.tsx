import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInvitationStore } from '@/stores/invitationStore';
import { useProjectStore } from '@/stores/projectStore';
import { Mail, CheckCircle, XCircle, MapPin, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';
import { formatDate } from '@/lib/utils';

export function PendingInvitations() {
  const navigate = useNavigate();
  const { invitations, acceptInvitation, declineInvitation, isLoading } = useInvitationStore();
  const { fetchProjects, projects } = useProjectStore();
  const [processing, setProcessing] = useState<string | null>(null);

  if (invitations.length === 0) {
    return null;
  }

  const handleAccept = async (id: string, projectId: string) => {
    setProcessing(id);
    try {
      await acceptInvitation(id);
      await fetchProjects();
      toast.success('Invitation accepted! Redirecting to board...');
      // Redirect to the kanban board
      setTimeout(() => {
        navigate(`/board/${projectId}`);
      }, 500);
    } catch (error) {
      toast.error('Failed to accept invitation');
    } finally {
      setProcessing(null);
    }
  };

  const handleDecline = async (id: string) => {
    setProcessing(id);
    try {
      await declineInvitation(id);
      toast.success('Invitation declined');
    } catch (error) {
      toast.error('Failed to decline invitation');
    } finally {
      setProcessing(null);
    }
  };

  return (
    <div className="space-y-4 mb-8">
      <div className="flex items-center space-x-2 mb-4">
        <Mail className="text-amber-500" size={24} />
        <h2 className="text-2xl font-bold text-gray-900">Pending Invitations</h2>
        <span className="bg-amber-100 text-amber-800 px-2 py-1 rounded-full text-sm font-semibold">
          {invitations.length}
        </span>
      </div>

      {invitations.map((invitation) => (
        <div
          key={invitation.id}
          className="bg-gradient-to-r from-amber-50 to-transparent border-l-4 border-amber-400 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900">{invitation.project_name}</h3>
              <p className="text-sm text-gray-600">You've been invited to join this project</p>
            </div>
            <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold uppercase">
              {invitation.role}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Calendar size={16} />
              <span>Invited {formatDate(invitation.created_at)}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold">By:</span>
              <span>{invitation.invited_by}</span>
            </div>
          </div>

          <div className="flex items-center space-x-3 pt-4 border-t border-amber-200">
            <button
              onClick={() => handleAccept(invitation.id, invitation.project_id)}
              disabled={processing === invitation.id || isLoading}
              className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              <CheckCircle size={18} />
              <span>Accept</span>
            </button>
            <button
              onClick={() => handleDecline(invitation.id)}
              disabled={processing === invitation.id || isLoading}
              className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              <XCircle size={18} />
              <span>Decline</span>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
