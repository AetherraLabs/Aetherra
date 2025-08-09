import DashboardStats from '../components/DashboardStats';
import LyrixaChat from '../components/LyrixaChat';
import ReflectionPanel from '../components/ReflectionPanel';
import SelfImprovementFeed from '../components/SelfImprovementFeed';
import ThoughtLog from '../components/ThoughtLog';

export default function LyrixaDemo() {
    return (
        <div className="p-6 space-y-4">
            <h1 className="text-3xl font-bold">Lyrixa Sandbox Demo</h1>
            <DashboardStats />
            <ThoughtLog />
            <ReflectionPanel />
            <SelfImprovementFeed />
            <LyrixaChat />
        </div>
    );
}
