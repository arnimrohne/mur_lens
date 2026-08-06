interface ScanningViewProps {
  photoUrl: string;
}

export default function ScanningView({ photoUrl }: ScanningViewProps) {
  return (
    <div className="flex flex-col items-center gap-4 p-4 pb-12">
      <div className="w-full max-w-lg rounded-2xl overflow-hidden aspect-[3/4] relative bg-black">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={photoUrl}
          alt=""
          aria-hidden="true"
          className="w-full h-full object-cover opacity-40"
        />

        <div className="absolute inset-0 flex flex-col items-center justify-center gap-8">
          <div className="flex gap-4" aria-hidden="true">
            <span className="w-4 h-4 bg-green-400 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-4 h-4 bg-green-400 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-4 h-4 bg-green-400 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
          <div className="text-center space-y-2 px-6">
            <h2 className="text-white text-2xl font-bold">Text wird erkannt</h2>
            <p className="text-gray-400 text-base">Dauert meist 2–4 Sekunden</p>
          </div>
        </div>
      </div>
    </div>
  );
}
