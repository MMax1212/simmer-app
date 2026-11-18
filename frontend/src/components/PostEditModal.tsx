import { useEffect, useId, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { api, errorText } from "../services/api";
import { ErrorMessage } from "./ErrorMessage";

export interface EditablePost {
  id: number;
  caption: string;
  image_url: string;
  media_type: "image" | "video";
  recipe_id: number | null;
}
export interface PostEditModalProps {
  post: EditablePost;
  onCancel: () => void;
  onSaved: (post: EditablePost) => void;
}

export function PostEditModal(props: PostEditModalProps) {
  // Switching cards resets the draft instead of showing edits from the previous post.
  return <EditDraft key={props.post.id} {...props} />;
}

function EditDraft({ post, onCancel, onSaved }: PostEditModalProps) {
  const [caption, setCaption] = useState(post.caption);
  const [location, setLocation] = useState(post.image_url);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const panel = useRef<HTMLDivElement>(null);
  const captionInput = useRef<HTMLTextAreaElement>(null);
  const saving = useRef(false);
  const active = useRef(false);
  const titleId = useId();

  useEffect(() => {
    active.current = true;
    const trigger = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    captionInput.current?.focus();
    return () => {
      active.current = false;
      document.body.style.overflow = overflow;
      if (trigger?.isConnected) trigger.focus();
    };
  }, []);

  function keyboard(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Escape") {
      event.preventDefault();
      if (!saving.current) onCancel();
    }
    if (event.key !== "Tab") return;
    // Keep keyboard focus in the dialog; during saving all form controls are disabled.
    const controls = Array.from(panel.current?.querySelectorAll<HTMLElement>(
      "button:not(:disabled), textarea:not(:disabled), input:not(:disabled)",
    ) ?? []);
    if (!controls.length) { event.preventDefault(); panel.current?.focus(); }
    else if (event.shiftKey && document.activeElement === controls[0]) {
      event.preventDefault(); controls.at(-1)?.focus();
    } else if (!event.shiftKey && document.activeElement === controls.at(-1)) {
      event.preventDefault(); controls[0].focus();
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (saving.current) return;
    if (!caption.trim() || !location.trim()) {
      setError("Caption and media location must not be blank.");
      return;
    }
    // Check limits explicitly as well as HTML constraints for programmatic submission.
    if (caption.length > 2000 || location.length > 1000) {
      setError("Use at most 2000 caption characters and 1000 media-location characters.");
      return;
    }
    saving.current = true;
    setBusy(true);
    setError(null);
    panel.current?.focus();
    let updated: EditablePost;
    try {
      // Never omit these untouched fields: PUT defaults would otherwise detach the
      // linked recipe or convert a video post's media type back to image.
      updated = await api.updatePost(post.id, {
        caption, image_url: location, media_type: post.media_type, recipe_id: post.recipe_id,
      });
    } catch (failure) {
      if (active.current) { setError(errorText(failure)); setBusy(false); }
      saving.current = false;
      return;
    }
    if (active.current) {
      // The parent replaces its displayed card with the server response and closes
      // the modal. Callback errors must not be presented as failed network writes.
      onSaved(updated);
    }
  }

  return <div className="post-delete-backdrop">
    <div className="card post-delete-dialog" role="dialog" aria-modal="true" aria-labelledby={titleId} tabIndex={-1} ref={panel} onKeyDown={keyboard}>
      <h2 id={titleId}>Edit post</h2>
      <form className="post-edit-form" onSubmit={submit}>
        <label>Caption<textarea ref={captionInput} value={caption} onChange={(event) => setCaption(event.target.value)} required maxLength={2000} rows={4} disabled={busy} /></label>
        {/* The backend accepts URLs, paths and data strings, so this is not a URL-only input. */}
        <label>Image or video location<input value={location} onChange={(event) => setLocation(event.target.value)} required maxLength={1000} disabled={busy} /></label>
        <ErrorMessage error={error} />
        <div className="row">
          <button type="submit" disabled={busy}>Save changes</button>
          <button type="button" className="secondary" disabled={busy} onClick={onCancel}>Cancel</button>
        </div>
        {busy && <p role="status">Saving changes…</p>}
      </form>
    </div>
  </div>;
}
