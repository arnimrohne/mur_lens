import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-black flex flex-col items-center justify-center p-8 gap-8">
      <div className="text-center space-y-4">
        <h1 className="text-white text-5xl font-bold tracking-tight">MUR Lens</h1>
        <p className="text-gray-400 text-xl">Mauritius-Preise sofort in Euro</p>
      </div>
      <Link
        href="/scan"
        className="w-full max-w-sm py-6 bg-white text-black text-2xl font-bold rounded-2xl text-center active:scale-95 transition-transform"
      >
        Kamera öffnen
      </Link>
    </main>
  );
}
