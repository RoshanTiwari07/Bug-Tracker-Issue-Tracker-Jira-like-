import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/stores/projectStore';
import { projectsApi } from '@/lib/api';
import { Layout } from '@/components/layout/Layout';
import { AdminStatsPanel } from '@/components/admin/AdminStatsPanel';
import { MemberManagement } from '@/components/admin/MemberManagement';
import { InviteMemberModal } from '@/components/invitation/InviteMemberModal';
import { DeleteProjectModal } from '@/components/project/DeleteProjectModal';
import { KanbanBoard } from '@/components/kanban/KanbanBoard';
import { ArrowLeft, Settings, Users, LayoutGrid, Trash2 } from 'lucide-react';
import { Loader } from 'lucide-react';

export function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { currentProject, fetchProject, fetchProjects, deleteProject, isLoading } = useProjectStore();
  const [activeTab, setActiveTab] = useState<'board' | 'members' | 'settings'>('board');
  const [userRole, setUserRole] = useState<string | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [roleLoading, setRoleLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
      fetchUserRole();
    }
  }, [projectId]);

  const fetchUserRole = async () => {
    if (!projectId) return;
    try {
      const role = await projectsApi.getUserRole(projectId);
      setUserRole(role.role);
    } catch (error) {
      console.error('Failed to fetch user role:', error);
      setUserRole('viewer');
    } finally {
      setRoleLoading(false);
    }
  };

  const isAdmin = userRole === 'admin' || userRole === 'owner';

  const handleDeleteProject = async () => {
    if (!projectId) return;
    try {
      await deleteProject(projectId);
      // Refetch projects after successful delete
      await fetchProjects();
      navigate('/projects');
    } catch (error) {
      console.error('Delete failed:', error);
      throw error; // Re-throw so DeleteProjectModal can show the error
    }
  };

  if (isLoading || roleLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-20">
          <Loader className="animate-spin text-blue-600" size={32} />
        </div>
      </Layout>
    );
  }

  if (!currentProject) {
    return (
      <Layout>
        <div className="text-center py-20">
          <h2 className="text-2xl font-bold text-gray-900">Project not found</h2>
          <button
            onClick={() => navigate('/projects')}
            className="mt-4 text-blue-600 hover:text-blue-700 font-semibold"
          >
            Back to projects
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/projects')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft size={24} />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{currentProject.name}</h1>
              <p className="text-gray-600">{currentProject.key} • {currentProject.is_private ? '🔒 Private' : '🌐 Public'}</p>
            </div>
          </div>
          <span className={`px-4 py-2 rounded-full font-semibold text-sm ${
            isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {isAdmin ? '👑 Admin' : '👤 Member'}
          </span>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex space-x-6">
            <button
              onClick={() => setActiveTab('board')}
              className={`py-4 px-2 border-b-2 font-semibold transition-colors ${
                activeTab === 'board'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <LayoutGrid size={18} className="inline mr-2" />
              Kanban Board
            </button>

            {isAdmin && (
              <>
                <button
                  onClick={() => setActiveTab('members')}
                  className={`py-4 px-2 border-b-2 font-semibold transition-colors ${
                    activeTab === 'members'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Users size={18} className="inline mr-2" />
                  Members
                </button>

                <button
                  onClick={() => setActiveTab('settings')}
                  className={`py-4 px-2 border-b-2 font-semibold transition-colors ${
                    activeTab === 'settings'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Settings size={18} className="inline mr-2" />
                  Settings
                </button>
              </>
            )}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'board' && (
          <div>
            <KanbanBoard projectName={currentProject.name} />
          </div>
        )}

        {activeTab === 'members' && isAdmin && (
          <MemberManagement
            projectId={projectId || ''}
            onInviteClick={() => setShowInviteModal(true)}
            userRole={userRole || 'viewer'}
          />
        )}

        {activeTab === 'settings' && isAdmin && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Project Settings</h3>
            
            {/* Delete Project Section */}
            <div className="border-t border-gray-200 pt-6">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-gray-900">Danger Zone</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    Delete this project permanently. This action cannot be undone.
                  </p>
                </div>
                <button
                  onClick={() => setShowDeleteModal(true)}
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors"
                >
                  <Trash2 size={18} />
                  <span>Delete Project</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Invite Modal */}
      <InviteMemberModal
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        projectId={projectId || ''}
        onSuccess={fetchUserRole}
      />

      {/* Delete Project Modal */}
      {currentProject && (
        <DeleteProjectModal
          isOpen={showDeleteModal}
          projectName={currentProject.name}
          projectKey={currentProject.key}
          onClose={() => setShowDeleteModal(false)}
          onConfirmDelete={handleDeleteProject}
        />
      )}
    </Layout>
  );
}
