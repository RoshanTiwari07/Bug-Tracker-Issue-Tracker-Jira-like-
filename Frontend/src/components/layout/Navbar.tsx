import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { useProjectStore } from '@/stores/projectStore';
import { Avatar } from '@/components/ui/Avatar';
import { LogOut, Settings, User } from 'lucide-react';
import { useState, useEffect } from 'react';
import { projectsApi } from '@/lib/api';

export function Navbar() {
  const { user, logout } = useAuthStore();
  const { projects } = useProjectStore();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isAdminOrOwner, setIsAdminOrOwner] = useState(false);
  const [rolesChecked, setRolesChecked] = useState(false);

  useEffect(() => {
    const checkUserRoles = async () => {
      if (projects.length === 0) {
        setIsAdminOrOwner(true); // Show dashboard if no projects
        setRolesChecked(true);
        return;
      }

      try {
        const roles: string[] = [];
        for (const project of projects) {
          try {
            const roleData = await projectsApi.getUserRole(project.id);
            roles.push(roleData.role);
          } catch (error: any) {
            // Silently default to viewer if can't get role (403, 404, etc.)
            roles.push('viewer');
          }
        }
        
        // User is admin/owner if they have that role in ANY project
        const hasAdminRole = roles.some(role => role === 'owner' || role === 'admin');
        setIsAdminOrOwner(hasAdminRole);
        setRolesChecked(true);
      } catch (error: any) {
        // Silently default to non-admin if overall check fails
        setIsAdminOrOwner(false);
        setRolesChecked(true);
      }
    };

    if (projects.length >= 0) {
      checkUserRoles();
    }
  }, [projects]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-primary-600">🐛</span>
              <span className="text-xl font-bold text-gray-900">Bug Tracker</span>
            </Link>

            <div className="hidden md:flex ml-10 space-x-8">
              {rolesChecked && isAdminOrOwner && (
                <Link
                  to="/"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
                >
                  Dashboard
                </Link>
              )}
              <Link
                to="/projects"
                className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium"
              >
                Projects
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {user && (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="flex items-center space-x-2 focus:outline-none"
                >
                  <Avatar
                    src={user.avatar_url}
                    name={user.full_name || user.username}
                    size="sm"
                  />
                  <span className="hidden md:block text-sm font-medium text-gray-700">
                    {user.username}
                  </span>
                </button>

                {showDropdown && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={() => setShowDropdown(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 z-20 border border-gray-200">
                      <Link
                        to="/profile"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowDropdown(false)}
                      >
                        <User size={16} className="mr-2" />
                        Profile
                      </Link>
                      <Link
                        to="/settings"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowDropdown(false)}
                      >
                        <Settings size={16} className="mr-2" />
                        Settings
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                      >
                        <LogOut size={16} className="mr-2" />
                        Logout
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
