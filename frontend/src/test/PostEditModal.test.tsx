import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { PostEditModal } from "../components/PostEditModal";

const original = { id: 7, caption: 'Original caption', image_url: '/images/dinner.jpg', media_type: 'video' as const, recipe_id: 22 };
const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => { vi.stubGlobal('fetch', fetchMock); fetchMock.mockReset(); });
function setup() {
  const onSaved = vi.fn(); const onCancel = vi.fn();
  render(<PostEditModal post={original} onSaved={onSaved} onCancel={onCancel} />);
  return { actor: userEvent.setup(), onSaved, onCancel };
}

it('prefills caption and media location and cancels without writing', async () => {
  const { actor, onCancel } = setup();
  expect(screen.getByRole('dialog', { name: 'Edit post' })).toBeInTheDocument();
  expect(screen.getByLabelText('Caption')).toHaveValue(original.caption);
  expect(screen.getByLabelText('Image or video location')).toHaveValue(original.image_url);
  await actor.click(screen.getByRole('button', { name: 'Cancel' }));
  expect(onCancel).toHaveBeenCalledTimes(1);
  expect(fetchMock).not.toHaveBeenCalled();
});

it('saves edited fields while retaining the existing media type and recipe link', async () => {
  const { actor, onSaved } = setup();
  localStorage.setItem('simmer_token', 'valid');
  const updated = { ...original, caption: 'New caption', image_url: '/images/new.jpg' };
  fetchMock.mockResolvedValue(new Response(JSON.stringify(updated), { status: 200 }));
  await actor.clear(screen.getByLabelText('Caption'));
  await actor.type(screen.getByLabelText('Caption'), updated.caption);
  await actor.clear(screen.getByLabelText('Image or video location'));
  await actor.type(screen.getByLabelText('Image or video location'), updated.image_url);
  await actor.click(screen.getByRole('button', { name: 'Save changes' }));
  await waitFor(() => expect(onSaved).toHaveBeenCalledWith(updated));
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe('/api/v1/posts/7');
  expect(init?.method).toBe('PUT');
  expect(new Headers(init?.headers).get('Authorization')).toBe('Bearer valid');
  expect(JSON.parse(init!.body as string)).toEqual({ caption: updated.caption, image_url: updated.image_url, media_type: 'video', recipe_id: 22 });
});

it.each(['Caption', 'Image or video location'])('rejects blank %s before issuing a request', async (label) => {
  const { actor } = setup();
  await actor.clear(screen.getByLabelText(label));
  await actor.type(screen.getByLabelText(label), '   ');
  fireEvent.submit(screen.getByRole('button', { name: 'Save changes' }).closest('form')!);
  expect(screen.getByRole('alert')).toHaveTextContent(/must not be blank/i);
  expect(fetchMock).not.toHaveBeenCalled();
});

it('keeps edits on server error and permits retry', async () => {
  const { actor, onSaved } = setup();
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Save failed' }), { status: 500 }))
    .mockResolvedValueOnce(new Response(JSON.stringify(original), { status: 200 }));
  await actor.type(screen.getByLabelText('Caption'), ' changed');
  await actor.click(screen.getByRole('button', { name: 'Save changes' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Save failed');
  expect(screen.getByLabelText('Caption')).toHaveValue('Original caption changed');
  expect(onSaved).not.toHaveBeenCalled();
  await actor.click(screen.getByRole('button', { name: 'Save changes' }));
  await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1));
});

it('blocks duplicate submissions during a pending save', async () => {
  const { actor, onSaved } = setup();
  let finish!: (response: Response) => void;
  fetchMock.mockReturnValueOnce(new Promise<Response>((resolve) => { finish = resolve; }));
  try {
    const save = screen.getByRole('button', { name: 'Save changes' });
    await actor.dblClick(save);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(save).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeDisabled();
  } finally { finish(new Response(JSON.stringify(original), { status: 200 })); }
  await waitFor(() => expect(onSaved).toHaveBeenCalledTimes(1));
});

it('contains keyboard focus and supports Escape cancellation', async () => {
  const { actor, onCancel } = setup();
  const dialog = screen.getByRole('dialog', { name: 'Edit post' });
  expect(within(dialog).getByLabelText('Caption')).toHaveFocus();
  await actor.tab({ shift: true });
  expect(within(dialog).getByRole('button', { name: 'Cancel' })).toHaveFocus();
  await actor.keyboard('{Escape}');
  expect(onCancel).toHaveBeenCalledTimes(1);
  expect(fetchMock).not.toHaveBeenCalled();
});
