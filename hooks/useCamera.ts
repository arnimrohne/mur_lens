import { useRef, useState, useCallback, useEffect } from 'react';

type CameraState = {
  isStreaming: boolean;
  capturedPhoto: string | null;
  error: string | null;
};

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [state, setState] = useState<CameraState>({
    isStreaming: false,
    capturedPhoto: null,
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

  const capturePhoto = useCallback(() => {
    const video = videoRef.current;
    if (!video || video.videoWidth === 0) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d')?.drawImage(video, 0, 0);
    setState((s) => ({ ...s, capturedPhoto: canvas.toDataURL('image/jpeg') }));
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
