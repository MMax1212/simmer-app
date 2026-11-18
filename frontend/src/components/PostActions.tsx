import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { api, errorText } from "../services/api";
import { ErrorMessage } from "./ErrorMessage";

export interface PostActionsProps {
  postId: number;
  authorId: number;
  currentUserId: number | null;
  // Editing belongs to Task 3.2.3; the host opens its editing modal via this callback.
  onEdit: (postId: number) => void;
  // The host removes the deleted card from its feed only after server confirmation.
  onDeleted: (postId: number) => void;
}

export function PostActions(props: PostActionsProps) {
  // Key per post/viewer so reused cards cannot inherit a different user's open dialog.
  return <AuthorPostActions key={`${props.postId}:${props.authorId}:${props.currentUserId}`} {...props} />;
}

function AuthorPostActions({ postId, authorId, currentUserId, onEdit, onDeleted }: PostActionsProps) {
  const [open, setOpen] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [deleted, setDeleted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const cancel = useRef<HTMLButtonElement>(null);
  const dialog = useRef<HTMLDivElement>(null);
  const deleting = useRef(false);
  const active = useRef(false);
  const titleId = useId();
  const descriptionId = useId();
  const isAuthor = currentUserId !== null && currentUserId === authorId;

  useEffect(() => {
    active.current = true;
    return () => { active.current = false; };
  }, []);

  useEffect(() => {
    if (!open) return;
    const dismiss = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", dismiss);
    return () => document.removeEventListener("pointerdown", dismiss);
  }, [open]);

  useEffect(() => {
    if (!confirming || !isAuthor) return;
    // Cancel receives initial focus to avoid accidentally confirming a destructive action.
    cancel.current?.focus();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = overflow;
      trigger.current?.focus();
    };
  }, [confirming, isAuthor]);

  function closeConfirmation() {
    // Do not let a pending DELETE be mistaken for a canceled request.
    if (!deleting.current) setConfirming(false);
  }

  function handleDialogKeys(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeConfirmation();
    }
    if (event.key !== "Tab") return;
    const buttons = Array.from(dialog.current?.querySelectorAll<HTMLButtonElement>("button:not(:disabled)") ?? []);
    if (!buttons.length) {
      event.preventDefault(); dialog.current?.focus();
    } else if (event.shiftKey && document.activeElement === buttons[0]) {
      event.preventDefault(); buttons.at(-1)?.focus();
    } else if (!event.shiftKey && document.activeElement === buttons.at(-1)) {
      event.preventDefault(); buttons[0].focus();
    }
  }

  async function removePost() {
    // React renders asynchronously: lock synchronously to guard repeated clicks.
    if (deleting.current || !isAuthor) return;
    deleting.current = true;
    setBusy(true);
    setError(null);
    dialog.current?.focus();
    try {
      await api.deletePost(postId);
    } catch (failure) {
      if (active.current) {
        setError(errorText(failure));
        setBusy(false);
      }
      deleting.current = false;
      return;
    }
    // Do not update a different page if the user navigated away during the request.
    // Keep parent callbacks outside the API error handler: a UI error is not a failed DELETE.
    if (active.current) {
      setConfirming(false);
      setDeleted(true);
      onDeleted(postId);
    }
  }

  // Visibility is a convenience, not authorization: the backend still enforces ownership.
  if (!isAuthor || deleted) return null;

  return (
    <div className="post-actions" ref={root} onKeyDown={(event) => {
      if (open && event.key === "Escape") { setOpen(false); trigger.current?.focus(); }
    }}>
      <button type="button" className="secondary" ref={trigger} aria-expanded={open} onClick={() => setOpen(!open)}>Post actions</button>
      {open && <div className="card post-actions-list" role="group" aria-label="Post actions">
        <button type="button" className="secondary" onClick={() => { setOpen(false); trigger.current?.focus(); onEdit(postId); }}>Edit post</button>
        <button type="button" className="danger" onClick={() => { setOpen(false); setError(null); setConfirming(true); }}>Delete post</button>
      </div>}
      {confirming && <div className="post-delete-backdrop">
        <div className="card post-delete-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} aria-describedby={descriptionId} tabIndex={-1} ref={dialog} onKeyDown={handleDialogKeys}>
          <h2 id={titleId}>Delete post?</h2>
          <p id={descriptionId}>This permanently removes the post and its likes, comments, and bookmarks. Your linked recipe will stay.</p>
          <ErrorMessage error={error} />
          <div className="row">
            <button type="button" className="secondary" ref={cancel} disabled={busy} onClick={closeConfirmation}>Cancel</button>
            <button type="button" className="danger" disabled={busy} onClick={removePost}>Delete permanently</button>
          </div>
          {busy && <p role="status">Deleting post…</p>}
        </div>
      </div>}
    </div>
  );
}
