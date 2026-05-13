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

  const selectedDoc = useMemo(
    () => documents.find((d) => d.doc_id === docId) || null,
    [documents, docId]
  );

  function showToast(message, error = false) {
    setToast({ show: true, message, error });
    window.setTimeout(() => setToast({ show: false, message: "", error: false }), 3000);
  }

  async function loadDocuments() {
    const res = await fetch("/documents");
    const data = await res.json();
    setDocuments(data.documents || []);
    showToast("Documents loaded");
  }

  async function loadDocDetails() {
    if (!docId) {
      showToast("Select or enter a doc_id first", true);
      return;
    }
    const res = await fetch(`/documents/${docId}`);
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Failed to load document", true);
      return;
    }
    setDocDetails(data);
    showToast("Document details loaded");
  }

  async function generateDraft() {
    if (!docId) {
      showToast("Select or enter a doc_id first", true);
      return;
    }
    const res = await fetch(`/draft/${docId}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ query, top_k: Number(topK) }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Draft generation failed", true);
      return;
    }
    setOriginalDraft(data.draft || "");
    setEditedDraft(data.draft || "");
    setResult(data);
    showToast("Draft generated");
  }

  async function saveEdit(e) {
    e.preventDefault();
    if (!docId) {
      showToast("Select or enter a doc_id first", true);
      return;
    }
    const res = await fetch(`/edit/${docId}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ original_draft: originalDraft, edited_draft: editedDraft }),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Save failed", true);
      return;
    }
    setResult(data);
    showToast("Edit saved successfully");
  }

  return (
    <div>
      <h2>Operator Draft Review</h2>
      <p>Load a document, generate a grounded draft, edit it, then save feedback.</p>

      <div className="card">
        <div className="row">
          <button className="btn" onClick={loadDocuments}>Load Documents</button>
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
          <button className="btn" onClick={loadDocDetails}>Load Details</button>
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
          <button className="btn" onClick={generateDraft}>Generate Draft</button>
        </div>
      </div>

      <form className="card" onSubmit={saveEdit}>
        <div className="row"><strong>Original Draft</strong></div>
        <textarea value={originalDraft} onChange={(e) => setOriginalDraft(e.target.value)} />
        <div className="row"><strong>Edited Draft</strong></div>
        <textarea value={editedDraft} onChange={(e) => setEditedDraft(e.target.value)} />
        <div className="row">
          <button className="btn" type="submit">Save Edit</button>
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
