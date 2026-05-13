const { useMemo, useState, useCallback } = React;

// ─── Helpers ──────────────────────────────────────────────────────────────────
function scoreColor(score) {
  if (!score) return "#64748b";
  if (score >= 0.6) return "#22c55e";
  if (score >= 0.4) return "#f59e0b";
  return "#ef4444";
}

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [docId, setDocId] = useState("");
  const [query, setQuery] = useState("Summarize key facts and parties involved");
  const [topK, setTopK] = useState(5);
  const [documents, setDocuments] = useState([]);
  const [docDetails, setDocDetails] = useState(null);
  const [originalDraft, setOriginalDraft] = useState("");
  const [editedDraft, setEditedDraft] = useState("");
  const [result, setResult] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [toasts, setToasts] = useState([]);
  const [errorBanner, setErrorBanner] = useState("");
  const [loading, setLoading] = useState({ docs: false, details: false, draft: false, save: false, patterns: false });

  const selectedDoc = useMemo(() => documents.find((d) => d.doc_id === docId) || null, [documents, docId]);

  // ─── Toast ──────────────────────────────────────────────────────────────────
  const showToast = useCallback((message, error = false) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, error }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  }, []);

  const setFlag = useCallback((key, val) => setLoading((p) => ({ ...p, [key]: val })), []);

  function validateDocId() {
    if (!docId.trim()) { setErrorBanner("Please select or enter a valid doc_id."); return false; }
    setErrorBanner(""); return true;
  }

  // ─── API calls ──────────────────────────────────────────────────────────────
  async function loadDocuments() {
    setFlag("docs", true);
    try {
      const res = await fetch("/documents");
      const data = await res.json();
      setDocuments(data.documents || []);
      showToast(`Loaded ${(data.documents || []).length} document(s)`);
    } catch (e) {
      showToast("Failed to load documents", true);
    } finally { setFlag("docs", false); }
  }

  async function loadDocDetails() {
    if (!validateDocId()) return;
    setFlag("details", true);
    try {
      const res = await fetch(`/documents/${docId}`);
      const data = await res.json();
      if (!res.ok) { setErrorBanner(data.detail || "Failed to load document"); showToast(data.detail, true); return; }
      setDocDetails(data); showToast("Document details loaded");
    } finally { setFlag("details", false); }
  }

  async function loadPatterns() {
    setFlag("patterns", true);
    try {
      const res = await fetch("/patterns");
      const data = await res.json();
      setPatterns(data); showToast("Patterns loaded");
    } finally { setFlag("patterns", false); }
  }

  async function generateDraft() {
    if (!validateDocId()) return;
    if (!query.trim()) { setErrorBanner("Query cannot be empty."); return; }
    setFlag("draft", true);
    try {
      const res = await fetch(`/draft/${docId}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ query, top_k: Number(topK) }),
      });
      const data = await res.json();
      if (!res.ok) { setErrorBanner(data.detail || "Draft generation failed"); showToast(data.detail, true); return; }
      setErrorBanner("");
      setOriginalDraft(data.draft || "");
      setEditedDraft(data.draft || "");
      setResult(data);
      showToast(`Draft generated — ${data.evidence_count} evidence chunks, grounding: ${data.grounding_ok ? "OK" : "WARN"}`);
    } finally { setFlag("draft", false); }
  }

  async function saveEdit(e) {
    e.preventDefault();
    if (!validateDocId()) return;
    setFlag("save", true);
    try {
      const res = await fetch(`/edit/${docId}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ original_draft: originalDraft, edited_draft: editedDraft }),
      });
      const data = await res.json();
      if (!res.ok) { setErrorBanner(data.detail || "Save failed"); showToast(data.detail, true); return; }
      setErrorBanner("");
      setPatterns(data.patterns);
      showToast(`Edit saved — ${data.patterns_added} new pattern(s) learned`);
    } finally { setFlag("save", false); }
  }

  async function copyDraft() {
    if (!editedDraft.trim()) { showToast("No draft to copy", true); return; }
    await navigator.clipboard.writeText(editedDraft);
    showToast("Draft copied to clipboard");
  }

  function exportDraft() {
    if (!editedDraft.trim()) { showToast("No draft to export", true); return; }
    const blob = new Blob([editedDraft], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${docId || "draft"}-edited.txt`;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
    showToast("Draft exported");
  }

  // ─── Render ─────────────────────────────────────────────────────────────────
  const evidenceMap = result?.evidence_map || [];
  const totalPatterns = patterns
    ? (patterns.style_notes?.length || 0) + (patterns.content_corrections?.length || 0) + (patterns.structural_preferences?.length || 0)
    : 0;

  return (
    <div>
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo">AI</div>
          <div>
            <div className="header-title">Legal AI — Operator Review</div>
            <div className="header-sub">Pearson Specter Litt Internal System</div>
          </div>
        </div>
        <div className="header-badge">
          {totalPatterns > 0 ? `${totalPatterns} patterns learned` : "No patterns yet"}
        </div>
      </header>

      <div className="layout">
        {errorBanner && <div className="banner">{errorBanner}</div>}

        {/* ── Document Selection ── */}
        <div className="card">
          <div className="card-title">1 — Select Document</div>
          <div className="row">
            <button className="btn btn-ghost" disabled={loading.docs} onClick={loadDocuments}>
              {loading.docs ? <span className="spinner" /> : "↻"} Load Documents
            </button>
            <select className="select" style={{flex:1}} value={docId} onChange={(e) => setDocId(e.target.value)}>
              <option value="">— Select a document —</option>
              {documents.map((d) => (
                <option key={d.doc_id} value={d.doc_id}>
                  {d.doc_id.slice(0, 8)}… ({d.total_pages}p, {d.pages_with_text} w/ text, conf: {d.avg_confidence})
                </option>
              ))}
            </select>
          </div>
          <div className="row" style={{marginTop:10}}>
            <input className="input" placeholder="Or paste doc_id manually" value={docId} onChange={(e) => setDocId(e.target.value)} />
            <button className="btn btn-ghost" disabled={loading.details || !docId} onClick={loadDocDetails}>
              {loading.details ? <span className="spinner" /> : "Inspect"}
            </button>
          </div>

          {selectedDoc && (
            <div className="doc-meta">
              <div><div className="meta-label">Pages</div><div className="meta-value">{selectedDoc.total_pages}</div></div>
              <div><div className="meta-label">With Text</div><div className="meta-value">{selectedDoc.pages_with_text}</div></div>
              <div><div className="meta-label">Avg Confidence</div><div className="meta-value">{selectedDoc.avg_confidence}</div></div>
              <div><div className="meta-label">Warnings</div><div className="meta-value">{selectedDoc.warning_count}</div></div>
            </div>
          )}

          {docDetails && (
            <>
              <hr className="divider" />
              <div className="card-title" style={{marginBottom:6}}>Structured Fields</div>
              <pre className="json-pre">{JSON.stringify(docDetails.structured_fields, null, 2)}</pre>
            </>
          )}
        </div>

        {/* ── Generate Draft ── */}
        <div className="card">
          <div className="card-title">2 — Generate Grounded Draft</div>
          <div className="row">
            <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter drafting query..." />
            <input className="input input-sm" type="number" min="1" max="20" value={topK} onChange={(e) => setTopK(e.target.value)} title="Top-K chunks" />
            <button className="btn" disabled={loading.draft || !docId} onClick={generateDraft}>
              {loading.draft ? <><span className="spinner" /> Generating…</> : "Generate Draft"}
            </button>
          </div>

          {result && (
            <>
              <hr className="divider" />
              <div className="row" style={{gap:10, marginBottom:10}}>
                {result.grounding_ok
                  ? <span className="grounding-ok">✓ Grounding OK</span>
                  : <span className="grounding-warn">⚠ Grounding issues</span>
                }
                <span style={{fontSize:11, color:"var(--text-dim)"}}>
                  {result.evidence_count} chunks · {result.grounding_attempts} attempt(s)
                </span>
                {result.invalid_citations?.length > 0 && (
                  <span style={{fontSize:11, color:"var(--red)"}}>Invalid cites: {result.invalid_citations.join(", ")}</span>
                )}
              </div>

              {evidenceMap.length > 0 && (
                <>
                  <div className="card-title" style={{marginBottom:6}}>Evidence Map</div>
                  <div className="evidence-map">
                    {evidenceMap.map((ev, i) => (
                      <div className="evidence-item" key={i}>
                        <span className="evidence-id">{ev.evidence_id}</span>
                        <span className="evidence-page">Page {ev.page_number || ev.page_hint || "?"} · Chunk {ev.chunk_index}</span>
                        {ev.score != null && (
                          <span className="evidence-score" style={{color: scoreColor(ev.score)}}>
                            {(ev.score * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </div>

        {/* ── Edit Draft ── */}
        <form className="card" onSubmit={saveEdit}>
          <div className="card-title">3 — Review & Edit Draft</div>
          <div className="draft-grid">
            <div>
              <label className="textarea-label">Original Draft</label>
              <textarea className="textarea" value={originalDraft} onChange={(e) => setOriginalDraft(e.target.value)} placeholder="Draft will appear here after generation…" />
            </div>
            <div>
              <label className="textarea-label">Your Edited Version</label>
              <textarea className="textarea" value={editedDraft} onChange={(e) => setEditedDraft(e.target.value)} placeholder="Edit the draft here, then save to teach the system…" />
            </div>
          </div>
          <div className="row" style={{marginTop:14}}>
            <button className="btn" disabled={loading.save || !docId} type="submit">
              {loading.save ? <><span className="spinner" /> Saving…</> : "Save Edit & Learn"}
            </button>
            <button className="btn btn-ghost" type="button" onClick={copyDraft}>Copy Edited</button>
            <button className="btn btn-ghost" type="button" onClick={exportDraft}>Export .txt</button>
          </div>
        </form>

        {/* ── Learned Patterns ── */}
        <div className="card">
          <div className="card-title" style={{justifyContent:"space-between", display:"flex"}}>
            <span>4 — Learned Writing Patterns</span>
            <button className="btn btn-ghost" style={{fontSize:11,padding:"3px 10px"}} disabled={loading.patterns} onClick={loadPatterns}>
              {loading.patterns ? <span className="spinner" /> : "Refresh"}
            </button>
          </div>
          {patterns ? (
            <div className="patterns-grid">
              {["style_notes","content_corrections","structural_preferences"].map((key) => (
                <div key={key}>
                  <div className="pattern-group-title">{key.replace(/_/g," ")}</div>
                  {(patterns[key] || []).length === 0
                    ? <span className="pattern-empty">None yet</span>
                    : (patterns[key] || []).map((n, i) => <span key={i} className="pattern-tag">{n}</span>)
                  }
                </div>
              ))}
            </div>
          ) : (
            <p style={{fontSize:13, color:"var(--text-dim)"}}>
              Submit an edit to learn patterns, or click Refresh to view current patterns.
            </p>
          )}
        </div>
      </div>

      {/* Toast stack */}
      <div className="toast-wrap">
        {toasts.map((t) => (
          <div key={t.id} className={`toast${t.error ? " error" : ""}`}>{t.message}</div>
        ))}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("app")).render(<App />);
