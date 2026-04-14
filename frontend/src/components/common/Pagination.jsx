import { ChevronLeft, ChevronRight } from 'lucide-react';

const range = (start, end) => Array.from({ length: end - start + 1 }, (_, i) => start + i);

const getPages = (page, totalPages) => {
  if (totalPages <= 7) return range(1, totalPages);

  if (page <= 3) return [...range(1, 4), '...', totalPages];
  if (page >= totalPages - 2) return [1, '...', ...range(totalPages - 3, totalPages)];
  return [1, '...', page - 1, page, page + 1, '...', totalPages];
};

const Pagination = ({ page, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  const pages = getPages(page, totalPages);

  const btnBase =
    'inline-flex items-center justify-center min-w-[36px] h-9 rounded-lg text-sm font-medium transition-colors';

  return (
    <nav className="flex items-center gap-1.5">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className={`${btnBase} px-2 text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed`}
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {pages.map((p, i) =>
        p === '...' ? (
          <span key={`ellipsis-${i}`} className="px-1 text-gray-400 select-none">
            …
          </span>
        ) : (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            className={`${btnBase} ${
              p === page
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {p}
          </button>
        )
      )}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className={`${btnBase} px-2 text-gray-500 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed`}
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </nav>
  );
};

export default Pagination;
