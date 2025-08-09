import { AnimatedBanner } from "../components/AnimatedBanner";
import { HeroVideo } from "../components/HeroVideo";
import { IntroText } from "../components/IntroText";

export default function Home() {
    return (
        <div className="min-h-screen bg-black text-white overflow-hidden">
            <AnimatedBanner />
            <HeroVideo />
            <IntroText />
        </div>
    );
}
