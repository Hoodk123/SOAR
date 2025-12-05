import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Settings, Activity, Menu, ChevronLeft, ChevronRight } from 'lucide-react';

const SidebarItem = ({ icon: Icon, label, to, active, collapsed }) => (
    <Link
        to={to}
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${active
                ? 'bg-white/10 text-white border-l-2 border-accent'
                : 'text-secondary hover:text-white hover:bg-white/5'
            } ${collapsed ? 'justify-center px-2' : ''}`}
        title={collapsed ? label : ''}
    >
        <Icon size={20} />
        {!collapsed && <span className="font-medium">{label}</span>}
    </Link>
);

const MainLayout = ({ children }) => {
    const location = useLocation();
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className="min-h-screen bg-background text-white flex">
            {/* Sidebar */}
            <aside
                className={`border-r border-border bg-surface hidden md:flex flex-col transition-all duration-300 ${collapsed ? 'w-20' : 'w-64'
                    }`}
            >
                <div className={`p-6 border-b border-border flex items-center ${collapsed ? 'justify-center' : 'justify-between'}`}>
                    {!collapsed && (
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded bg-accent flex items-center justify-center">
                                <ShieldAlert className="text-black" size={20} />
                            </div>
                            <span className="text-xl font-bold tracking-tight">SOAR<span className="text-accent">.ai</span></span>
                        </div>
                    )}
                    {collapsed && (
                        <div className="w-8 h-8 rounded bg-accent flex items-center justify-center">
                            <ShieldAlert className="text-black" size={20} />
                        </div>
                    )}
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    <SidebarItem
                        icon={LayoutDashboard}
                        label="Dashboard"
                        to="/"
                        active={location.pathname === '/'}
                        collapsed={collapsed}
                    />
                    <SidebarItem
                        icon={ShieldAlert}
                        label="Alerts"
                        to="/alerts"
                        active={location.pathname.startsWith('/alerts')}
                        collapsed={collapsed}
                    />
                    <SidebarItem
                        icon={Activity}
                        label="Playbooks"
                        to="/playbooks"
                        active={location.pathname.startsWith('/playbooks')}
                        collapsed={collapsed}
                    />
                    <SidebarItem
                        icon={Settings}
                        label="Settings"
                        to="/settings"
                        active={location.pathname.startsWith('/settings')}
                        collapsed={collapsed}
                    />
                </nav>

                <div className="p-4 border-t border-border">
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="w-full flex items-center justify-center p-2 rounded hover:bg-white/5 text-secondary transition-colors mb-4"
                    >
                        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                    </button>

                    {!collapsed ? (
                        <div className="flex items-center gap-3 px-4 py-2">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-accent to-blue-500" />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium">Admin User</span>
                                <span className="text-xs text-secondary">Security Analyst</span>
                            </div>
                        </div>
                    ) : (
                        <div className="flex justify-center">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-accent to-blue-500" />
                        </div>
                    )}
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0">
                {/* Header */}
                <header className="h-16 border-b border-border bg-surface/50 backdrop-blur-md flex items-center justify-between px-6 sticky top-0 z-10">
                    <div className="md:hidden">
                        <Menu className="text-secondary" />
                    </div>
                    <div className="flex-1" /> {/* Spacer */}
                    <div className="flex items-center gap-4">
                        <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                        <span className="text-sm text-accent font-medium">System Operational</span>
                    </div>
                </header>

                {/* Page Content */}
                <div className="flex-1 p-6 overflow-auto grid-bg">
                    <div className="max-w-7xl mx-auto">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default MainLayout;
