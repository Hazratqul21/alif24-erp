import { useCallback, useRef, useState } from 'react';
import { UploadCloud, File, X, CheckCircle } from 'lucide-react';

const formatSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
};

const FileUpload = ({
  onUpload,
  accept,
  maxSize = 10 * 1024 * 1024,
  label = 'Перетащите файл сюда или нажмите для выбора',
}) => {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  const processFile = useCallback(
    (f) => {
      setError('');
      setDone(false);
      if (maxSize && f.size > maxSize) {
        setError(`Файл превышает ${formatSize(maxSize)}`);
        return;
      }
      setFile(f);
      setProgress(0);

      let pct = 0;
      const interval = setInterval(() => {
        pct += Math.random() * 30;
        if (pct >= 100) {
          pct = 100;
          clearInterval(interval);
          setDone(true);
          onUpload?.(f);
        }
        setProgress(Math.min(pct, 100));
      }, 200);
    },
    [maxSize, onUpload],
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      const f = e.dataTransfer.files?.[0];
      if (f) processFile(f);
    },
    [processFile],
  );

  const handleChange = (e) => {
    const f = e.target.files?.[0];
    if (f) processFile(f);
  };

  const reset = () => {
    setFile(null);
    setProgress(0);
    setError('');
    setDone(false);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !file && inputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-8 text-center transition-colors cursor-pointer ${
          dragActive
            ? 'border-blue-400 bg-blue-50/60'
            : file
              ? 'border-gray-200 bg-gray-50 cursor-default'
              : 'border-gray-300 bg-white hover:border-blue-300 hover:bg-blue-50/30'
        }`}
      >
        <input ref={inputRef} type="file" accept={accept} onChange={handleChange} className="hidden" />

        {!file ? (
          <>
            <UploadCloud className={`w-10 h-10 ${dragActive ? 'text-blue-500' : 'text-gray-400'}`} />
            <p className="text-sm text-gray-500">{label}</p>
            <p className="text-xs text-gray-400">Макс. размер: {formatSize(maxSize)}</p>
          </>
        ) : (
          <div className="w-full space-y-3">
            <div className="flex items-center gap-3">
              {done ? (
                <CheckCircle className="w-8 h-8 text-green-500 shrink-0" />
              ) : (
                <File className="w-8 h-8 text-blue-500 shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-700 truncate">{file.name}</p>
                <p className="text-xs text-gray-400">{formatSize(file.size)}</p>
              </div>
              <button onClick={reset} className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${done ? 'bg-green-500' : 'bg-blue-500'}`}
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
      {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
    </div>
  );
};

export default FileUpload;
