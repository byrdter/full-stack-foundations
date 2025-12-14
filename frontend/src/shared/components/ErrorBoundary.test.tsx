import { render, screen } from "@testing-library/react";

import { ErrorBoundary } from "./ErrorBoundary";
import { ErrorFallback } from "./ErrorFallback";

function Boom(): never {
  throw new Error("boom");
}

describe("ErrorBoundary", () => {
  it("renders fallback UI when a child throws", () => {
    render(
      <ErrorBoundary fallback={<ErrorFallback title="Oops" message="Something went wrong" />}>
        <Boom />
      </ErrorBoundary>,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(/oops/i);
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });
});
