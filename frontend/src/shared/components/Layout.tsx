import { Link, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div
      style={{
        fontFamily: "Inter, system-ui, Avenir, Helvetica, Arial, sans-serif",
        margin: "2rem auto",
        maxWidth: "960px",
        padding: "0 1rem",
      }}
    >
      <nav style={{ display: "flex", justifyContent: "space-between", marginBottom: "2rem" }}>
        <Link to="/" style={{ fontWeight: 600, textDecoration: "none", color: "#0f172a" }}>
          Full-Stack AI Starter
        </Link>
      </nav>
      <Outlet />
    </div>
  );
}
