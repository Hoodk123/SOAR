import React, { useEffect, useState } from 'react';
import { alertService } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { AlertCircle, Search, Filter, MoreVertical } from 'lucide-react';

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await alertService.getAlerts();
                setAlerts(response.data.alerts || []);
            } catch (error) {
                console.error('Failed to fetch alerts', error);
                // Mock data
                setAlerts([
                    { id: 1, title: 'Suspicious Login Attempt', severity: 'high', status: 'open', source: 'Auth Service', created_at: '2023-10-27T10:30:00Z' },
                    { id: 2, title: 'Port Scan Detected', severity: 'medium', status: 'investigating', source: 'Firewall', created_at: '2023-10-27T09:15:00Z' },
                    { id: 3, title: 'Malware Signature Match', severity: 'critical', status: 'open', source: 'EDR', created_at: '2023-10-27T08:45:00Z' },
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
    }, []);

    const getSeverityColor = (severity) => {
        switch (severity.toLowerCase()) {
            case 'critical': return 'text-danger bg-danger/10 border-danger/20';
            case 'high': return 'text-orange-400 bg-orange-400/10 border-orange-400/20';
            case 'medium': return 'text-warning bg-warning/10 border-warning/20';
            default: return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <h1 className="text-2xl font-bold text-white">Alerts Management</h1>
                <div className="flex gap-2">
                    <Button variant="secondary" className="flex items-center gap-2">
                        <Filter size={16} /> Filter
                    </Button>
                    <Button variant="accent" className="flex items-center gap-2">
                        <AlertCircle size={16} /> New Alert
                    </Button>
                </div>
            </div>

            <Card className="p-0 overflow-hidden">
                <div className="p-4 border-b border-border flex items-center gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" size={18} />
                        <input
                            type="text"
                            placeholder="Search alerts..."
                            className="w-full bg-surface-hover border border-border rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-accent transition-colors"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-border text-secondary text-sm">
                                <th className="p-4 font-medium">Severity</th>
                                <th className="p-4 font-medium">Title</th>
                                <th className="p-4 font-medium">Source</th>
                                <th className="p-4 font-medium">Status</th>
                                <th className="p-4 font-medium">Time</th>
                                <th className="p-4 font-medium"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {alerts.map((alert) => (
                                <tr key={alert.id} className="border-b border-border/50 hover:bg-white/5 transition-colors">
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityColor(alert.severity)} uppercase`}>
                                            {alert.severity}
                                        </span>
                                    </td>
                                    <td className="p-4 font-medium text-white">{alert.title}</td>
                                    <td className="p-4 text-secondary">{alert.source}</td>
                                    <td className="p-4">
                                        <span className="capitalize text-sm">{alert.status}</span>
                                    </td>
                                    <td className="p-4 text-secondary text-sm">
                                        {new Date(alert.created_at).toLocaleTimeString()}
                                    </td>
                                    <td className="p-4 text-right">
                                        <button className="text-secondary hover:text-white p-1">
                                            <MoreVertical size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
};

export default Alerts;
