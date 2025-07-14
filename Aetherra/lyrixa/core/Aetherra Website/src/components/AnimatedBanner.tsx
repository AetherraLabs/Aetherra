import { motion } from "framer-motion";

export function AnimatedBanner() {
  return (
    <div className="h-[60vh] flex items-center justify-center relative z-10">
      <motion.h1
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.2 }}
        className="text-5xl font-bold tracking-wide gradient-text glow-effect"
      >
        Welcome to Aetherra
      </motion.h1>
    </div>
  );
}
