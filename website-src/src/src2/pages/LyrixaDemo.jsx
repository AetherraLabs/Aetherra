import { DashboardStats } from "../components/DashboardStats";
import { LyrixaChat } from "../components/LyrixaChat";
import { ReflectionPanel } from "../components/ReflectionPanel";
import { SelfImprovementFeed } from "../components/SelfImprovementFeed";
import { ThoughtLog } from "../components/ThoughtLog";

export default function LyrixaDemo() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
            <div className="space-y-4">
                <LyrixaChat />
                <ReflectionPanel />
            </div>
            <div className="space-y-4">
                <DashboardStats />
                <ThoughtLog />
                <SelfImprovementFeed />
            </div>
        </div>
    );
}
