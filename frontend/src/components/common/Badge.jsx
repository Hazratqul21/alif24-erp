const variantMap = {
  success: 'bg-green-50 text-green-700 ring-green-600/20',
  warning: 'bg-yellow-50 text-yellow-700 ring-yellow-600/20',
  danger:  'bg-red-50 text-red-700 ring-red-600/20',
  info:    'bg-blue-50 text-blue-700 ring-blue-600/20',
};

const Badge = ({ text, variant = 'info' }) => (
  <span
    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${
      variantMap[variant] ?? variantMap.info
    }`}
  >
    {text}
  </span>
);

export default Badge;
