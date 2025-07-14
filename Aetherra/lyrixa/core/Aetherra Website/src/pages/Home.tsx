import { AnimatedBanner } from "../components/AnimatedBanner";
import { HeroVideo } from "../components/HeroVideo";
import { IntroText } from "../components/IntroText";

export default function Home() {
  return (
    <div className="min-h-screen bg-aetherra-dark text-white overflow-hidden neural-bg">
      <AnimatedBanner />
      <HeroVideo />
      <IntroText />
    </div>
  );
}
