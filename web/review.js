const { useMemo, useState } = React;

function App() {
  const [docId, setDocId] = useState("");
  const [query, setQuery] = useState("Summarize key facts");
  const [topK, setTopK] = useState(5);
  const [documents, setDocuments] = useState([]);
  const [docDetails, setDocDetails] = useState(null);
  const [originalDraft, setOriginalDraft] = useState("");
  const [editedDraft, setEditedDraft] = useState("");
  const [result, setResult] = useState(null);
  const [toast, setToast] = useState({ show: false, message: "", error: false });
  const [errorBanner, setErrorBanner] = useState("");
  const [loading, setLoading] = useState({ docs: false, details: false, draft: false, save: false });

  const selectedDoc = useMemo(
    () => documents.find((d) => d.doc_id === docId) || null,
    [documents, docId]
  );

  function showToast(message, error = false) {
    setToast({ show: true, message, error });
    window.setTimeout(() => setToast({ show: false, message: "", error: false }), 3000);
  }

  function setLoadingFlag(key, value) {
    setLoading((prev) => ({ ...prev, [key]: value }));
  }

  function validateDocId() {
    if (!docId || !docId.trim()) {
      setErrorBanner("Please select or enter a valid doc_id.");
      return false;
    }
    setErrorBanner("");
    return true;
  }

  async function loadDocuments() {
    setLoadingFlag("docs", true);
    try {
      const res = await fetch("/documents");
      const data = await res.json();
      setDocuments(data.documents || []);
      showToast("Documents loaded");
    } finally {
      setLoadingFlag("docs", false);
    }
  }

  async function loadDocDetails() {
    if (!validateDocId()) {
      return;
    }
    setLoadingFlag("details", true);
    try {
      const res = await fetch(`/documents/${docId}`);
      const data = await res.json();
      if (!res.ok) {
        setErrorBanner(data.detail || "Failed to load document");
        showToast(data.detail || "Failed to load document", true);
        return;
      }
      setDocDetails(data);
      showToast("Document details loaded");
    } finally {
      setLoadingFlag("details", false);
    }
  }

  async function generateDraft() {
    if (!validateDocId()) {
      return;
    }
    if (!query.trim()) {
      setErrorBanner("Query cannot be empty.");
      return;
    }
    setLoadingFlag("draft", true);
    try {
      const res = await fetch(`/draft/${docId}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query, top_k: Number(topK) }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorBanner(data.detail || "Draft generation failed");
        showToast(data.detail || "Draft generation failed", true);
        return;
      }
      setErrorBanner("");
      setOriginalDraft(data.draft || "");
      setEditedDraft(data.draft || "");
      setResult(data);
      showToast("Draft generated");
    } finally {
      setLoadingFlag("draft", false);
    }
  }

  async function saveEdit(e) {
    e.preventDefault();
    if (!validateDocId()) {
      return;
    }
    setLoadingFlag("save", true);
    try {
      const res = await fetch(`/edit/${docId}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ original_draft: originalDraft, edited_draft: editedDraft }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorBanner(data.detail || "Save failed");
        showToast(data.detail || "Save failed", true);
        return;
      }
      setErrorBanner("");
      setResult(data);
      showToast("Edit saved successfully");
    } finally {
      setLoadingFlag("save", false);
    }
  }

  async function copyDraft() {
    if (!editedDraft.trim()) {
      showToast("No edited draft to copy", true);
      return;
    }
    await navigator.clipboard.writeText(editedDraft);
    showToast("Edited draft copied");
  }

  function exportDraft() {
    if (!editedDraft.trim()) {
      showToast("No edited draft to export", true);
      return;
    }
    const blob = new Blob([editedDraft], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${docId || "draft"}-edited.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    showToast("Edited draft exported");
  }

  return (
    <div>
      <h2>Operator Draft Review</h2>
      <p>Load a document, generate a grounded draft, edit it, then save feedback.</p>
      {errorBanner && <div className="banner">{errorBanner}</div>}

      <div className="card">
        <div className="row">
          <button className="btn" disabled={loading.docs} onClick={loadDocuments}>
            {loading.docs ? "Loading..." : "Load Documents"}
          </button>
          <select className="input" value={docId} onChange={(e) => setDocId(e.target.value)}>
            <option value="">-- Select doc_id --</option>
            {documents.map((d) => (
              <option key={d.doc_id} value={d.doc_id}>{d.doc_id}</option>
            ))}
          </select>
        </div>
        <div className="row">
          <input
            className="input"
            placeholder="or type doc_id manually"
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
          />
          <button className="btn" disabled={loading.details} onClick={loadDocDetails}>
            {loading.details ? "Loading..." : "Load Details"}
          </button>
        </div>
        {selectedDoc && (
          <div className="row">
            <small>
              Pages: {selectedDoc.total_pages}, Text Pages: {selectedDoc.pages_with_text}, Warnings: {selectedDoc.warning_count}
            </small>
          </div>
        )}
      </div>

      <div className="card">
        <div className="row">
          <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} />
          <input
            className="input"
            style={{ width: "80px", marginLeft: "8px" }}
            type="number"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(e.target.value)}
          />
          <button className="btn" disabled={loading.draft} onClick={generateDraft}>
            {loading.draft ? "Generating..." : "Generate Draft"}
          </button>
        </div>
      </div>

      <form className="card" onSubmit={saveEdit}>
        <div className="row"><strong>Original Draft</strong></div>
        <textarea value={originalDraft} onChange={(e) => setOriginalDraft(e.target.value)} />
        <div className="row"><strong>Edited Draft</strong></div>
        <textarea value={editedDraft} onChange={(e) => setEditedDraft(e.target.value)} />
        <div className="row">
          <button className="btn" disabled={loading.save} type="submit">
            {loading.save ? "Saving..." : "Save Edit"}
          </button>
          <button className="btn" type="button" onClick={copyDraft}>Copy Edited Draft</button>
          <button className="btn" type="button" onClick={exportDraft}>Export Edited Draft</button>
        </div>
      </form>

      {docDetails && (
        <div className="card">
          <h4>Document Details</h4>
          <pre>{JSON.stringify(docDetails, null, 2)}</pre>
        </div>
      )}

      {result && (
        <div className="card">
          <h4>Latest API Result</h4>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      {toast.show && (
        <div className={`toast ${toast.error ? "error" : ""}`}>{toast.message}</div>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("app")).render(<App />);
