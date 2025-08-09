import { motion } from "framer-motion";

export function IntroText() {
    return (
        <motion.div
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 1 }}
            className="text-center p-6 text-lg max-w-2xl mx-auto"
        >
            <p>
                An operating system that thinks. A companion that learns.
                <br />
                Lyrixa is your gateway to conscious technology.
            </p>
        </motion.div>
    );
}
