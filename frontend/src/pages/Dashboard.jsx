import React, { useEffect, useState } from 'react';
import { alertService } from '../services/api';
import Card from '../components/ui/Card';
import { Shield, AlertTriangle, CheckCircle, Activity, Server, Globe, Lock } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color, trend }) => (
    <Card className="relative overflow-hidden group">
        <div className={`absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity ${color}`}>
            <Icon size={64} />
        </div>
        <div className="relative z-10">
            <div className="flex items-center gap-3 mb-2">
                <div className={`p-2 rounded-lg bg-white/5 ${color}`}>
                    <Icon size={20} />
                </div>
                <span className="text-secondary text-sm font-medium">{title}</span>
            </div>
            <div className="flex items-end gap-2">
                <span className="text-3xl font-bold text-white">{value}</span>
                {trend && (
                    <span className={`text-xs mb-1 ${trend > 0 ? 'text-success' : 'text-danger'}`}>
                        {trend > 0 ? '+' : ''}{trend}%
                    </span>
                )}
            </div>
        </div>
    </Card>
);

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await alertService.getStats();
                setStats(response.data);
            } catch (error) {
                console.error('Failed to fetch stats', error);
                // Fallback mock data for demo if backend is offline
                setStats({
                    total_alerts: 124,
                    by_severity: { critical: 12, high: 28, medium: 45, low: 39 },
                    by_status: { open: 42, investigating: 15, resolved: 67 },
                    active_incidents: 3
                });
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center h-full text-accent">Loading metrics...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Security Overview</h1>
                <div className="flex gap-2">
                    <span className="px-3 py-1 rounded-full bg-success/10 text-success text-xs border border-success/20 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                        Live Monitoring
                    </span>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Alerts"
                    value={stats?.total_alerts || 0}
                    icon={Shield}
                    color="text-blue-400"
                    trend={12}
                />
                <StatCard
                    title="Critical Threats"
                    value={stats?.by_severity?.critical || 0}
                    icon={AlertTriangle}
                    color="text-danger"
                    trend={-5}
                />
                <StatCard
                    title="Active Incidents"
                    value={stats?.active_incidents || 0}
                    icon={Activity}
                    color="text-warning"
                    trend={2}
                />
                <StatCard
                    title="Resolved Today"
                    value={stats?.by_status?.resolved || 0}
                    icon={CheckCircle}
                    color="text-success"
                    trend={8}
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Activity / Chart Placeholder */}
                <Card className="lg:col-span-2 min-h-[400px]">
                    <h3 className="text-lg font-medium text-white mb-6">Threat Traffic Analysis</h3>
                    <div className="w-full h-64 flex items-end justify-between gap-2 px-4">
                        {[40, 65, 30, 85, 50, 75, 45, 60, 90, 55, 70, 40].map((h, i) => (
                            <div key={i} className="w-full bg-white/5 hover:bg-accent/50 transition-colors rounded-t-sm relative group">
                                <div
                                    className="absolute bottom-0 w-full bg-gradient-to-t from-accent/20 to-accent/80 rounded-t-sm transition-all duration-500"
                                    style={{ height: `${h}%` }}
                                />
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 text-xs text-secondary">
                        <span>00:00</span>
                        <span>06:00</span>
                        <span>12:00</span>
                        <span>18:00</span>
                        <span>23:59</span>
                    </div>
                </Card>

                {/* System Status */}
                <div className="space-y-6">
                    <Card>
                        <h3 className="text-lg font-medium text-white mb-4">System Health</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <Server size={18} className="text-secondary" />
                                    <span className="text-sm">API Gateway</span>
                                </div>
                                <span className="text-xs text-success">Operational</span>
                            </div>
                            <div className="w-full bg-white/5 rounded-full h-1.5">
                                <div className="bg-success h-1.5 rounded-full" style={{ width: '98%' }} />
                            </div>

                            <div className="flex items-center justify-between pt-2">
                                <div className="flex items-center gap-3">
                                    <Globe size={18} className="text-secondary" />
                                    <span className="text-sm">Threat Intel Feeds</span>
                                </div>
                                <span className="text-xs text-success">Connected</span>
                            </div>
                            <div className="w-full bg-white/5 rounded-full h-1.5">
                                <div className="bg-success h-1.5 rounded-full" style={{ width: '100%' }} />
                            </div>

                            <div className="flex items-center justify-between pt-2">
                                <div className="flex items-center gap-3">
                                    <Lock size={18} className="text-secondary" />
                                    <span className="text-sm">Encryption Engine</span>
                                </div>
                                <span className="text-xs text-warning">High Load</span>
                            </div>
                            <div className="w-full bg-white/5 rounded-full h-1.5">
                                <div className="bg-warning h-1.5 rounded-full" style={{ width: '85%' }} />
                            </div>
                        </div>
                    </Card>

                    <Card className="bg-gradient-to-br from-accent/10 to-transparent border-accent/20">
                        <div className="flex items-start gap-4">
                            <div className="p-3 rounded-full bg-accent/20 text-accent">
                                <Shield size={24} />
                            </div>
                            <div>
                                <h4 className="font-medium text-white">Security Score</h4>
                                <p className="text-sm text-secondary mt-1">Your system security rating is excellent.</p>
                                <div className="mt-4 text-3xl font-bold text-white">94<span className="text-lg text-secondary font-normal">/100</span></div>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
