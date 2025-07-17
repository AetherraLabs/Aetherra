import { motion } from 'framer-motion';

interface TransparencyNoticeProps {
    className?: string;
}

export default function TransparencyNotice({ className = '' }: TransparencyNoticeProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 ${className}`}
        >
            <div className="flex items-start space-x-3">
                <div className="text-blue-400 text-lg">ℹ️</div>
                <div>
                    <h4 className="text-blue-300 font-semibold mb-1">Transparency Notice</h4>
                    <p className="text-blue-200 text-sm leading-relaxed">
                        We believe in complete transparency. This website shows only real, implemented features of Aetherra.
                        Any placeholder content is clearly marked as "Coming Soon" or "TBD". We never inflate numbers or
                        promise features that don't exist yet.
                    </p>
                </div>
            </div>
        </motion.div>
    );
}

// Also export as named export for backward compatibility
export { TransparencyNotice };
