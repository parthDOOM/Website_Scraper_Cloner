import React, { useState } from 'react';

const Icon = ({ path, className = "w-5 h-5" }: { path: string, className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d={path} />
  </svg>
);

const ClipboardIcon = () => <Icon path="M15.66,4.34,13.66,2.34a2,2,0,0,0-2.83,0L8.17,5H6A2,2,0,0,0,4,7V19a2,2,0,0,0,2,2H18a2,2,0,0,0,2-2V7a2,2,0,0,0-2-2H15.83l2.83-2.83A2,2,0,0,0,15.66,4.34ZM18,19H6V7h3.17l3.5-3.5a.29.29,0,0,1,.41,0l2,2a.29.29,0,0,1,0,.41L12.83,8H18Z" />;
const DesktopIcon = () => <Icon path="M20,16H4a2,2,0,0,1-2-2V4A2,2,0,0,1,4,2H20a2,2,0,0,1,2,2v10A2,2,0,0,1,20,16Zm-7-2h2V6H13ZM9,6H7v8H9Zm-4,0H3v8H5ZM19,4H5V14H19ZM16,22H8a1,1,0,0,1,0-2h8a1,1,0,0,1,0,2Z" />;
const MobileIcon = () => <Icon path="M17,2H7A3,3,0,0,0,4,5V19a3,3,0,0,0,3,3H17a3,3,0,0,0,3-3V5A3,3,0,0,0,17,2Zm1,17a1,1,0,0,1-1,1H7a1,1,0,0,1-1-1V5A1,1,0,0,1,7,4H17a1,1,0,0,1,1,1Z" />;

export default function Home() {
  const [url, setUrl] = useState("");
  const [responseHtml, setResponseHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [view, setView] = useState<'preview' | 'code'>('preview');
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'mobile'>('desktop');
  const [copied, setCopied] = useState(false);

  const handleClone = async () => {
    setLoading(true);
    setResponseHtml(null);
    setError(null);
    setView('preview');

    if (!url || !url.startsWith('http')) {
      setError("Please enter a full and valid URL (e.g., https://example.com).");
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || `An error occurred: ${res.statusText}`);
      } else {
        setResponseHtml(data.html); 
      }
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(`Failed to connect to the backend or other network error: ${e.message}`);
      } else {
        setError(`An unknown network error occurred.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopyToClipboard = () => {
    if (responseHtml) {
      navigator.clipboard.writeText(responseHtml);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); 
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 md:p-8 font-sans">
      <main className="w-full max-w-4xl">
        <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
            Website Cloner
            </h1>
            <p className="text-gray-400 mt-2">
            Enter a public URL to generate a visual clone using AI.
            </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://info.cern.ch"
            className="flex-grow p-3 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none transition-all"
          />
          <button
            onClick={handleClone}
            disabled={loading}
            className="p-3 px-6 bg-purple-600 hover:bg-purple-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 font-semibold"
          >
            {loading ? (
                <>
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Cloning...
                </>
            ) : "Clone Website"}
          </button>
        </div>

        {error && (
          <div className="w-full bg-red-900/50 border border-red-700 text-red-200 p-4 rounded-lg mb-6">
            <h3 className="font-bold mb-1">Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {responseHtml && !error && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg shadow-2xl">
            <div className="flex items-center justify-between p-2 border-b border-gray-700">
              <div className="flex gap-1">
                <button onClick={() => setView('preview')} className={`px-4 py-1 rounded-md text-sm font-medium transition-colors ${view === 'preview' ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'}`}>Preview</button>
                <button onClick={() => setView('code')} className={`px-4 py-1 rounded-md text-sm font-medium transition-colors ${view === 'code' ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'}`}>Code</button>
              </div>

              <div>
                {view === 'preview' && (
                  <div className="flex items-center gap-2">
                    <button onClick={() => setPreviewDevice('desktop')} className={`p-2 rounded-md transition-colors ${previewDevice === 'desktop' ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'}`} title="Desktop View"><DesktopIcon /></button>
                    <button onClick={() => setPreviewDevice('mobile')} className={`p-2 rounded-md transition-colors ${previewDevice === 'mobile' ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'}`} title="Mobile View"><MobileIcon /></button>
                  </div>
                )}
                {view === 'code' && (
                  <button onClick={handleCopyToClipboard} className="flex items-center gap-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-md text-sm font-medium transition-colors">
                    <ClipboardIcon />
                    {copied ? 'Copied!' : 'Copy Code'}
                  </button>
                )}
              </div>
            </div>

            <div className="p-1">
              {view === 'preview' ? (
                <div className="bg-white rounded-b-md overflow-hidden">
                  <iframe
                    srcDoc={responseHtml}
                    title="Cloned Website Preview"
                    className={`w-full transition-all duration-300 ease-in-out border-0 ${previewDevice === 'desktop' ? 'h-[70vh]' : 'h-[60vh] max-w-sm mx-auto'}`}
                    sandbox="allow-same-origin" 
                  />
                </div>
              ) : (
                <div className="relative">
                  <pre className="whitespace-pre-wrap break-all text-sm text-gray-300 overflow-auto max-h-[70vh] p-4">
                    <code>
                        {responseHtml}
                    </code>
                  </pre>
                </div>
              )}
            </div>
          </div>
        )}
        
        {!responseHtml && !error && (
             <div className="w-full mt-8 p-5 bg-gray-800/50 border border-gray-700 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-purple-300">How to Use & Considerations</h3>
                <ul className="list-disc list-inside text-sm text-gray-400 space-y-2">
                <li>Enter a full, valid URL (e.g., <code>https://example.com</code>).</li>
                <li>This tool works best on simpler, primarily static web pages.</li>
                <li>Complex interactive sites or those behind logins may not be cloned accurately.</li>
                <li>The clone&apos;s quality depends on the AI&apos;s interpretation of the scraped content.</li>
                <li>Please respect website terms of service and copyrights.</li>
                </ul>
            </div>
        )}
      </main>
    </div>
  );
} 