import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export function IntroText() {
  return (
    <motion.div
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.5, duration: 1 }}
      className="text-center p-6 text-lg max-w-2xl mx-auto"
    >
      <p className="text-shadow leading-relaxed">
        An operating system that thinks. A companion that learns.
        <br />
        <span className="gradient-text font-semibold">
          Lyrixa is your gateway to conscious technology.
        </span>
      </p>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 0.5 }}
        className="mt-8"
      >
        <Link 
          to="/demo"
          className="inline-block px-8 py-3 bg-aetherra-green text-aetherra-dark font-semibold rounded-lg hover:bg-aetherra-green/90 transition-colors glow-effect"
        >
          Enter Aetherra
        </Link>
      </motion.div>
    </motion.div>
  );
}
