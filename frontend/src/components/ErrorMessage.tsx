export function ErrorMessage({ error }: {
    error: string | null;
}) {
    return error ? <p className="error" role="alert">{error}</p> : null;
}
