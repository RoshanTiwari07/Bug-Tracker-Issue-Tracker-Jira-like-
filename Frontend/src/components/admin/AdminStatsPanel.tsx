import { useEffect, useState } from 'react';
import { projectsApi } from '@/lib/api';
import { Users, CheckCircle2, AlertCircle, TrendingUp, Activity } from 'lucide-react';
import { Loader } from 'lucide-react';

interface ProjectStats {
  total_tickets: number;
  tickets_by_status: Record<string, number>;
  tickets_by_priority: Record<string, number>;
  overdue_tickets: number;
  team_members: number;
  completion_rate: number;
}

interface AdminStatsPanelProps {
  projectId: string;
}

export function AdminStatsPanel({ projectId }: AdminStatsPanelProps) {
  const [stats, setStats] = useState<ProjectStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await projectsApi.getProjectStats(projectId);
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [projectId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="animate-spin text-blue-600" size={24} />
      </div>
    );
  }

  if (!stats || !stats.tickets_by_status || !stats.tickets_by_priority) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <p className="text-gray-500">No statistics available yet.</p>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Tickets',
      value: stats.total_tickets,
      icon: TrendingUp,
      color: 'bg-blue-500',
      lightColor: 'bg-blue-100 text-blue-800',
    },
    {
      label: 'Team Members',
      value: stats.team_members,
      icon: Users,
      color: 'bg-purple-500',
      lightColor: 'bg-purple-100 text-purple-800',
    },
    {
      label: 'Completed',
      value: stats.completion_rate,
      icon: CheckCircle2,
      color: 'bg-green-500',
      lightColor: 'bg-green-100 text-green-800',
      suffix: '%',
    },
    {
      label: 'Overdue',
      value: stats.overdue_tickets,
      icon: AlertCircle,
      color: 'bg-red-500',
      lightColor: 'bg-red-100 text-red-800',
    },
  ];

  return (
    <div className="space-y-6 mb-8">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stat.value}
                  {stat.suffix && <span className="text-lg">{stat.suffix}</span>}
                </p>
              </div>
              <div className={`${stat.color} p-3 rounded-lg`}>
                <stat.icon className="text-white" size={24} />
              </div>
            </div>
            {stat.label === 'Completed' && (
              <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${stat.value}%` }}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Status Breakdown */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <Activity size={20} />
          <span>Status Breakdown</span>
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(stats.tickets_by_status).map(([status, count]) => (
            <div key={status} className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-xs font-semibold text-gray-600 uppercase mb-2">{status.replace('_', ' ')}</p>
              <p className="text-2xl font-bold text-gray-900">{count}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Priority Breakdown */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Priority Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(stats.tickets_by_priority).map(([priority, count]) => {
            const priorityColors: Record<string, string> = {
              critical: 'bg-red-100 text-red-800 border-red-300',
              high: 'bg-orange-100 text-orange-800 border-orange-300',
              medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
              low: 'bg-green-100 text-green-800 border-green-300',
            };
            return (
              <div key={priority} className={`border rounded-lg p-3 text-center ${priorityColors[priority] || 'bg-gray-100'}`}>
                <p className="text-sm font-semibold uppercase mb-1">{priority}</p>
                <p className="text-2xl font-bold">{count}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
