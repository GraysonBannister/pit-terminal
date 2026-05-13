"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="bg-slate-950 text-slate-100">
        <div className="flex h-screen items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-bold mb-4">Something went wrong</h2>
            <button
              onClick={reset}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
