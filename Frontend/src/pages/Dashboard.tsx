import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/stores/projectStore';
import { useAuthStore } from '@/stores/authStore';
import { useInvitationStore } from '@/stores/invitationStore';
import { Layout } from '@/components/layout/Layout';
import { PendingInvitations } from '@/components/invitation/PendingInvitations';
import { FolderOpen, CheckCircle, Clock, AlertCircle, Plus, Loader } from 'lucide-react';
import { projectsApi } from '@/lib/api';
import { UserRole } from '@/types';

export function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { projects, fetchProjects } = useProjectStore();
  const { invitations, fetchInvitations } = useInvitationStore();
  const [checkingRoles, setCheckingRoles] = useState(true);
  
  const isAdmin = user?.role === UserRole.ADMIN;

  useEffect(() => {
    const initializeData = async () => {
      await fetchProjects();
      await fetchInvitations();
      setCheckingRoles(false);
    };
    initializeData();
  }, [fetchProjects, fetchInvitations]);

  // Auto-redirect regular members to kanban board
  useEffect(() => {
    const checkAndRedirect = async () => {
      if (projects.length === 0 || checkingRoles || invitations.length > 0) {
        return;
      }

      try {
        const roles: { [key: string]: string } = {};
        for (const project of projects) {
          try {
            const roleData = await projectsApi.getUserRole(project.id);
            roles[project.id] = roleData.role;
          } catch (error) {
            roles[project.id] = 'viewer';
          }
        }

        // Check if user is only a regular member (no owner/admin role)
        const isOwnerOrAdmin = Object.values(roles).some(role => role === 'owner' || role === 'admin');
        
        if (!isOwnerOrAdmin && projects.length > 0) {
          // Redirect to first project's board
          navigate(`/board/${projects[0].id}`, { replace: true });
        }
      } catch (error) {
        console.error('Error checking roles:', error);
      }
    };

    if (!checkingRoles) {
      checkAndRedirect();
    }
  }, [projects, checkingRoles, invitations.length, navigate]);

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
      <div className="space-y-8">
        {/* Welcome Section */}
        <div>
          <h1 className="text-4xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.username}! 👋
          </h1>
          <p className="text-gray-600 mt-2">
            {projects.length === 0 
              ? "Get started by creating your first project"
              : "Here's what's happening with your projects today"}
          </p>
        </div>

        {/* Pending Invitations */}
        {invitations.length > 0 && <PendingInvitations />}

        {/* Empty State */}
        {projects.length === 0 ? (
          <div className="text-center py-20 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl">
            <FolderOpen size={64} className="mx-auto text-blue-400 mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Projects Yet</h2>
            <p className="text-gray-600 mb-6">Create your first project to get started</p>
            <Link
              to="/projects"
              className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              <Plus size={20} />
              <span>Create Project</span>
            </Link>
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  name: 'Total Projects',
                  value: projects.length,
                  icon: FolderOpen,
                  color: 'bg-blue-500',
                },
                {
                  name: 'Active Tickets',
                  value: '0',
                  icon: Clock,
                  color: 'bg-yellow-500',
                },
                {
                  name: 'Completed',
                  value: '0',
                  icon: CheckCircle,
                  color: 'bg-green-500',
                },
                {
                  name: 'High Priority',
                  value: '0',
                  icon: AlertCircle,
                  color: 'bg-red-500',
                },
              ].map((stat) => (
                <div key={stat.name} className="card p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stat.value}
                      </p>
                    </div>
                    <div className={`${stat.color} p-3 rounded-lg`}>
                      <stat.icon className="text-white" size={24} />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Projects */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">Your Projects</h2>
                <Link
                  to="/projects"
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  View all
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.slice(0, 3).map((project) => (
                  <Link
                    key={project.id}
                    to={`/project/${project.id}`}
                    className="card p-6 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FolderOpen className="text-blue-600" size={20} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{project.name}</h3>
                        {isAdmin && <p className="text-sm text-gray-500">{project.key}</p>}
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                      {project.description || 'No description'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {project.is_private ? '🔒 Private' : '🌐 Public'}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
