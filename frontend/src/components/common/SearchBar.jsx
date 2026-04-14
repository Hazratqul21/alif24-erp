import { useEffect, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';

const SearchBar = ({ value = '', onChange, placeholder = 'Поиск...' }) => {
  const [internal, setInternal] = useState(value);
  const timerRef = useRef(null);

  useEffect(() => {
    setInternal(value);
  }, [value]);

  const handleChange = (e) => {
    const val = e.target.value;
    setInternal(val);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => onChange?.(val), 300);
  };

  const handleClear = () => {
    setInternal('');
    clearTimeout(timerRef.current);
    onChange?.('');
  };

  useEffect(() => () => clearTimeout(timerRef.current), []);

  return (
    <div className="relative w-full max-w-md">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-gray-400 pointer-events-none" />
      <input
        type="text"
        value={internal}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-10 pr-9 py-2.5 rounded-xl border border-gray-200 bg-white text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30 focus:border-blue-400 transition-shadow"
      />
      {internal && (
        <button
          onClick={handleClear}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 p-0.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

export default SearchBar;
