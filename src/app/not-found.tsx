export default function NotFound() {
  return (
    <div className="flex h-screen items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-slate-100 mb-2">404 - Page Not Found</h2>
        <p className="text-slate-400 mb-4">The page you are looking for does not exist.</p>
        <a
          href="/"
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 inline-block"
        >
          Go Home
        </a>
      </div>
    </div>
  );
}
