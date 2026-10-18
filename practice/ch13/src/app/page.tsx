export default function Home() {
  return (
    <main style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>Freelancer Dashboard API</h1>
      <p>
        客戶 API：<code>/api/clients</code>（需要{" "}
        <code>Authorization: Bearer &lt;JWT&gt;</code>）
      </p>
    </main>
  );
}
