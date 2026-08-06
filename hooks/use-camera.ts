import { useRef, useState, useCallback, useEffect } from 'react';

const MAX_CAPTURE_WIDTH = 1000;

type CameraState = {
  isStreaming: boolean;
  error: string | null;
};

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [state, setState] = useState<CameraState>({
    isStreaming: false,
    error: null,
  });

  const startCamera = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setState((s) => ({ ...s, error: 'Kamera wird nicht unterstützt.' }));
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setState((s) => ({ ...s, isStreaming: true, error: null }));
    } catch {
      setState((s) => ({ ...s, error: 'Kamerazugriff verweigert.' }));
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setState((s) => ({ ...s, isStreaming: false }));
  }, []);

  // Returns both the Blob (for OCR) and photoUrl (for ScanningView preview).
  // Downscales to MAX_CAPTURE_WIDTH to keep OCR fast on high-res cameras.
  const capturePhoto = useCallback((): Promise<{ blob: Blob; photoUrl: string }> => {
    return new Promise((resolve, reject) => {
      const video = videoRef.current;
      if (!video || video.videoWidth === 0) {
        reject(new Error('Camera not ready'));
        return;
      }
      const scale = Math.min(1, MAX_CAPTURE_WIDTH / video.videoWidth);
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(video.videoWidth * scale);
      canvas.height = Math.round(video.videoHeight * scale);
      canvas.getContext('2d')?.drawImage(video, 0, 0, canvas.width, canvas.height);
      const photoUrl = canvas.toDataURL('image/jpeg');
      canvas.toBlob(
        (blob) => {
          if (blob) resolve({ blob, photoUrl });
          else reject(new Error('Blob capture failed'));
        },
        'image/jpeg',
        0.92,
      );
    });
  }, []);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    videoRef,
    ...state,
    startCamera,
    stopCamera,
    capturePhoto,
  };
}
