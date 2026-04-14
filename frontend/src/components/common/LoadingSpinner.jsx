const sizeMap = {
  sm: 'w-5 h-5 border-2',
  md: 'w-8 h-8 border-[3px]',
  lg: 'w-12 h-12 border-4',
};

const LoadingSpinner = ({ size = 'md', text }) => (
  <div className="flex flex-col items-center justify-center gap-3">
    <div
      className={`${sizeMap[size]} rounded-full border-gray-200 border-t-blue-600 animate-spin`}
    />
    {text && <p className="text-sm text-gray-500 animate-pulse">{text}</p>}
  </div>
);

export default LoadingSpinner;
