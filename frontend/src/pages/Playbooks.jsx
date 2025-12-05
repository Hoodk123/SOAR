import React, { useEffect, useState } from 'react';
import { playbookService } from '../services/api';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { Play, FileText, Clock, CheckCircle, XCircle, ChevronRight } from 'lucide-react';

const Playbooks = () => {
    const [playbooks, setPlaybooks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPlaybook, setSelectedPlaybook] = useState(null);

    useEffect(() => {
        const fetchPlaybooks = async () => {
            try {
                const response = await playbookService.getPlaybooks();
                setPlaybooks(response.data.playbooks || []);
            } catch (error) {
                console.error('Failed to fetch playbooks', error);
            } finally {
                setLoading(false);
            }
        };

        fetchPlaybooks();
    }, []);

    const handleRunPlaybook = async (e, id) => {
        e.stopPropagation();
        try {
            await playbookService.runPlaybook(id);
            alert('Playbook execution started');
        } catch (error) {
            console.error('Failed to run playbook', error);
            alert('Failed to start playbook');
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Security Playbooks</h1>
                <Button variant="accent" className="flex items-center gap-2">
                    <FileText size={16} /> Create Playbook
                </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {playbooks.map((playbook) => (
                    <Card
                        key={playbook.id}
                        className="group cursor-pointer hover:border-accent/50 transition-all duration-300"
                        onClick={() => setSelectedPlaybook(playbook)}
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 rounded-lg bg-white/5 group-hover:bg-accent/10 text-accent transition-colors">
                                <FileText size={24} />
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-medium border ${playbook.active ? 'text-success border-success/20 bg-success/10' : 'text-secondary border-secondary/20 bg-secondary/10'
                                }`}>
                                {playbook.active ? 'ACTIVE' : 'INACTIVE'}
                            </span>
                        </div>

                        <h3 className="text-lg font-bold text-white mb-2">{playbook.name}</h3>
                        <p className="text-secondary text-sm mb-4 line-clamp-2">{playbook.description}</p>

                        <div className="flex items-center justify-between mt-auto pt-4 border-t border-border">
                            <div className="flex items-center gap-2 text-xs text-secondary">
                                <Clock size={14} />
                                <span>Last run: {playbook.last_executed_at ? new Date(playbook.last_executed_at).toLocaleDateString() : 'Never'}</span>
                            </div>
                            <Button
                                variant="primary"
                                className="!py-1 !px-3 text-xs flex items-center gap-1"
                                onClick={(e) => handleRunPlaybook(e, playbook.id)}
                            >
                                <Play size={12} /> Run
                            </Button>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Playbook Details Modal (Simplified as an overlay for now) */}
            {selectedPlaybook && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={() => setSelectedPlaybook(null)}>
                    <Card className="w-full max-w-2xl max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h2 className="text-2xl font-bold text-white">{selectedPlaybook.name}</h2>
                                <p className="text-secondary mt-1">{selectedPlaybook.description}</p>
                            </div>
                            <button onClick={() => setSelectedPlaybook(null)} className="text-secondary hover:text-white">
                                <XCircle size={24} />
                            </button>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-medium text-secondary uppercase tracking-wider mb-3">Trigger Condition</h3>
                                <div className="p-3 rounded bg-white/5 font-mono text-sm text-accent">
                                    {selectedPlaybook.trigger_condition || 'Manual Trigger Only'}
                                </div>
                            </div>

                            <div>
                                <h3 className="text-sm font-medium text-secondary uppercase tracking-wider mb-3">Execution Steps</h3>
                                <div className="space-y-3">
                                    {selectedPlaybook.steps.map((step, index) => (
                                        <div key={index} className="flex gap-4 p-3 rounded border border-border bg-white/5">
                                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/20 text-accent flex items-center justify-center text-xs font-bold">
                                                {step.order}
                                            </div>
                                            <div>
                                                <h4 className="font-medium text-white">{step.action}</h4>
                                                <p className="text-sm text-secondary">{step.description}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <Button variant="secondary" onClick={() => setSelectedPlaybook(null)}>Close</Button>
                            <Button variant="accent" onClick={(e) => handleRunPlaybook(e, selectedPlaybook.id)}>Execute Playbook</Button>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default Playbooks;
