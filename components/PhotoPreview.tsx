/* eslint-disable @next/next/no-img-element */

interface PhotoPreviewProps {
  src: string;
}

export default function PhotoPreview({ src }: PhotoPreviewProps) {
  return (
    <div className="w-full max-w-lg">
      <p className="text-white text-lg font-medium mb-3">Aufnahme</p>
      <img src={src} alt="Aufnahme" className="w-full rounded-2xl" />
    </div>
  );
}
