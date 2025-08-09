export function HeroVideo() {
    return (
        <div className="w-full h-[40vh] bg-black flex items-center justify-center overflow-hidden">
            <video autoPlay loop muted className="w-full h-full object-cover opacity-50">
                <source src="/media/hero-preview.mp4" type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
}
