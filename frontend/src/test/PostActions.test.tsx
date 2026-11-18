import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { PostActions } from "../components/PostActions";

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => { vi.stubGlobal('fetch', fetchMock); fetchMock.mockReset(); });
const props = { postId: 7, authorId: 1, currentUserId: 1, onEdit: vi.fn(), onDeleted: vi.fn() };

it.each([null, 2])('hides actions from visitors and other users (%s)', (currentUserId) => {
  render(<PostActions {...props} currentUserId={currentUserId} />);
  expect(screen.queryByRole('button', { name: 'Post actions' })).not.toBeInTheDocument();
});

it('opens author actions and hands Edit to the parent without a network request', async () => {
  const onEdit = vi.fn();
  const actor = userEvent.setup();
  render(<PostActions {...props} onEdit={onEdit} />);
  await actor.click(screen.getByRole('button', { name: 'Post actions' }));
  await actor.click(screen.getByRole('button', { name: 'Edit post' }));
  expect(onEdit).toHaveBeenCalledWith(7);
  expect(fetchMock).not.toHaveBeenCalled();
  expect(screen.queryByRole('button', { name: 'Delete post' })).not.toBeInTheDocument();
});

async function confirmDialog(extra = {}) {
  const actor = userEvent.setup();
  render(<PostActions {...props} {...extra} />);
  await actor.click(screen.getByRole('button', { name: 'Post actions' }));
  await actor.click(screen.getByRole('button', { name: 'Delete post' }));
  return { actor, dialog: screen.getByRole('dialog', { name: 'Delete post?' }) };
}

it('requires confirmation and allows cancellation without deletion', async () => {
  const { actor, dialog } = await confirmDialog();
  expect(within(dialog).getByRole('button', { name: 'Cancel' })).toHaveFocus();
  await actor.click(within(dialog).getByRole('button', { name: 'Cancel' }));
  expect(fetchMock).not.toHaveBeenCalled();
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Post actions' })).toHaveFocus();
});

it('deletes with authentication only after confirmation and notifies the parent', async () => {
  const onDeleted = vi.fn();
  localStorage.setItem('simmer_token', 'test-token');
  fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
  const { actor, dialog } = await confirmDialog({ onDeleted });
  await actor.click(within(dialog).getByRole('button', { name: 'Delete permanently' }));
  await waitFor(() => expect(onDeleted).toHaveBeenCalledWith(7));
  const [url, init] = fetchMock.mock.calls[0];
  expect(url).toBe('/api/v1/posts/7');
  expect(init?.method).toBe('DELETE');
  expect(new Headers(init?.headers).get('Authorization')).toBe('Bearer test-token');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

it('shows API errors and permits retry without notifying the parent prematurely', async () => {
  const onDeleted = vi.fn();
  fetchMock.mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Could not delete' }), { status: 500 }))
    .mockResolvedValueOnce(new Response(null, { status: 204 }));
  const { actor, dialog } = await confirmDialog({ onDeleted });
  await actor.click(within(dialog).getByRole('button', { name: 'Delete permanently' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Could not delete');
  expect(onDeleted).not.toHaveBeenCalled();
  await actor.click(within(dialog).getByRole('button', { name: 'Delete permanently' }));
  await waitFor(() => expect(onDeleted).toHaveBeenCalledTimes(1));
});

it('locks duplicate clicks until the deletion response arrives', async () => {
  let finish!: (response: Response) => void;
  fetchMock.mockReturnValueOnce(new Promise<Response>((resolve) => { finish = resolve; }));
  const onDeleted = vi.fn();
  const { actor, dialog } = await confirmDialog({ onDeleted });
  try {
    const button = within(dialog).getByRole('button', { name: 'Delete permanently' });
    await actor.dblClick(button);
    expect(button).toBeDisabled();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  } finally {
    finish(new Response(null, { status: 204 }));
  }
  await waitFor(() => expect(onDeleted).toHaveBeenCalledTimes(1));
});

it('supports Escape and traps confirmation keyboard focus', async () => {
  const { actor, dialog } = await confirmDialog();
  await actor.tab({ shift: true });
  expect(within(dialog).getByRole('button', { name: 'Delete permanently' })).toHaveFocus();
  await actor.keyboard('{Escape}');
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(fetchMock).not.toHaveBeenCalled();
});


it('dismisses the dropdown with Escape or an outside click', async () => {
  const actor = userEvent.setup();
  render(<><PostActions {...props} /><button>Outside</button></>);
  const trigger = screen.getByRole('button', { name: 'Post actions' });
  await actor.click(trigger);
  await actor.keyboard('{Escape}');
  expect(trigger).toHaveAttribute('aria-expanded', 'false');
  await actor.click(trigger);
  await actor.click(screen.getByRole('button', { name: 'Outside' }));
  expect(screen.queryByRole('button', { name: 'Edit post' })).not.toBeInTheDocument();
});
