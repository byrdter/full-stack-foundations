import { FormEvent, useState } from "react";

import { useEcho } from "../hooks";
import type { EchoRequest } from "../types";

export function EchoForm() {
  const [message, setMessage] = useState("");
  const mutation = useEcho();

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!message.trim()) return;

    const payload: EchoRequest = { message: message.trim() };
    mutation.mutate(payload, {
      onSuccess: () => setMessage(""),
    });
  };

  return (
    <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
      <label htmlFor="echo-message">Echo message</label>
      <input
        id="echo-message"
        name="message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type a message"
        style={{
          padding: "0.5rem",
          borderRadius: "6px",
          border: "1px solid #cbd5e1",
        }}
      />
      <button
        type="submit"
        disabled={mutation.isPending || !message.trim()}
        style={{
          padding: "0.5rem 0.75rem",
          borderRadius: "6px",
          border: "1px solid #0f172a",
          background: "#0f172a",
          color: "white",
          cursor: mutation.isPending || !message.trim() ? "not-allowed" : "pointer",
        }}
      >
        {mutation.isPending ? "Sending..." : "Send"}
      </button>

      {mutation.isSuccess ? <p aria-live="polite">Response: {mutation.data?.message}</p> : null}
      {mutation.isError ? (
        <p aria-live="polite" style={{ color: "#b91c1c" }}>
          Failed to send.
        </p>
      ) : null}
    </form>
  );
}
