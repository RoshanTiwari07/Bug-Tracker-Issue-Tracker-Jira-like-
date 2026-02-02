import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/stores/projectStore';
import { useInvitationStore } from '@/stores/invitationStore';
import { useAuthStore } from '@/stores/authStore';
import { Layout } from '@/components/layout/Layout';
import { PendingInvitations } from '@/components/invitation/PendingInvitations';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Plus, FolderOpen, Calendar, Users, Loader } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';
import type { ProjectCreate } from '@/types';
import { projectsApi } from '@/lib/api';

export function Projects() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { projects, fetchProjects, createProject, setCurrentProject } = useProjectStore();
  const { invitations, fetchInvitations } = useInvitationStore();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [checkingRoles, setCheckingRoles] = useState(true);
  const [userRoles, setUserRoles] = useState<{ [key: string]: string }>({});
  const [formData, setFormData] = useState<ProjectCreate>({
    name: '',
    key: '',
    description: '',
    is_private: true,
  });

  useEffect(() => {
    const initializeAndCheckRedirect = async () => {
      await fetchProjects();
      await fetchInvitations();
      setCheckingRoles(false);
    };
    initializeAndCheckRedirect();
  }, [fetchProjects, fetchInvitations]);

  // Fetch user roles for each project
  useEffect(() => {
    const fetchUserRoles = async () => {
      const roles: { [key: string]: string } = {};
      for (const project of projects) {
        try {
          const roleData = await projectsApi.getUserRole(project.id);
          roles[project.id] = roleData.role;
        } catch (error) {
          roles[project.id] = 'viewer';
        }
      }
      setUserRoles(roles);
      
      // Auto-redirect regular members to the first project's board
      const isOwnerOrAdmin = Object.values(roles).some(role => role === 'owner' || role === 'admin');
      if (!isOwnerOrAdmin && projects.length > 0 && invitations.length === 0) {
        const firstProject = projects[0];
        navigate(`/board/${firstProject.id}`);
      }
    };

    if (projects.length > 0 && !checkingRoles) {
      fetchUserRoles();
    }
  }, [projects, checkingRoles, invitations.length, navigate]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const project = await createProject(formData);
      toast.success('Project created successfully');
      setShowCreateModal(false);
      setFormData({ name: '', key: '', description: '', is_private: true });
      setCurrentProject(project);
      navigate(`/project/${project.id}`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectClick = (project: any) => {
    setCurrentProject(project);
    navigate(`/project/${project.id}`);
  };

  // Check if user can create projects (is owner or admin of at least one project, or has no projects)
  const canCreateProjects = projects.length === 0 || Object.values(userRoles).some(role => role === 'owner' || role === 'admin');

  if (checkingRoles && projects.length > 0) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-20">
          <Loader className="animate-spin text-blue-600" size={32} />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
            <p className="text-gray-600 mt-1">Manage your projects and teams</p>
          </div>
          {canCreateProjects && (
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus size={20} className="mr-2" />
              New Project
            </Button>
          )}
        </div>

        {/* Pending Invitations */}
        {invitations.length > 0 && <PendingInvitations />}

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{projects.map((project) => (
            <div
              key={project.id}
              onClick={() => handleProjectClick(project)}
              className="card p-6 hover:shadow-lg transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <FolderOpen className="text-primary-600" size={24} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{project.name}</h3>
                    <p className="text-sm text-gray-500">{project.key}</p>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {project.description || 'No description'}
              </p>

              <div className="flex items-center justify-between text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <Calendar size={14} />
                  <span>{formatDate(project.created_at)}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users size={14} />
                  <span>Team</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {projects.length === 0 && (
          <div className="text-center py-12">
            <FolderOpen size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No projects yet
            </h3>
            <p className="text-gray-600 mb-4">
              Get started by creating your first project
            </p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus size={20} className="mr-2" />
              Create Project
            </Button>
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Project"
        size="md"
      >
        <form onSubmit={handleCreateProject} className="space-y-4">
          <Input
            label="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Bug Tracker"
            required
          />

          <Input
            label="Project Key"
            value={formData.key}
            onChange={(e) =>
              setFormData({ ...formData, key: e.target.value.toUpperCase() })
            }
            placeholder="e.g., BUG"
            pattern="[A-Z0-9]{2,10}"
            maxLength={10}
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
              placeholder="Project description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_private"
              checked={formData.is_private}
              onChange={(e) =>
                setFormData({ ...formData, is_private: e.target.checked })
              }
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label htmlFor="is_private" className="text-sm text-gray-700">
              Private project
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setShowCreateModal(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isLoading}>
              Create Project
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}
