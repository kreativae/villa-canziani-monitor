export default function SettingsPage() {
  return (
    <div className="p-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>
        <p className="text-sm text-gray-500 mt-0.5">Variáveis de ambiente e integrações</p>
      </div>

      <section className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-4">
        <h2 className="text-sm font-semibold text-gray-700">Variáveis necessárias</h2>
        <div className="space-y-2 text-sm font-mono">
          {[
            ["NEXT_PUBLIC_API_URL", "URL do backend FastAPI (ex: https://api.railway.app)"],
            ["NEXT_PUBLIC_SUPABASE_URL", "URL do projeto Supabase"],
            ["NEXT_PUBLIC_SUPABASE_ANON_KEY", "Chave pública anônima do Supabase"],
          ].map(([key, desc]) => (
            <div key={key} className="flex flex-col gap-0.5">
              <code className="text-blue-700 text-xs">{key}</code>
              <span className="text-gray-500 text-xs font-sans">{desc}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 space-y-2">
        <h2 className="text-sm font-semibold text-gray-700">Deploy rápido</h2>
        <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
          <li>Crie um projeto no <strong>Supabase</strong> e rode a migration <code className="bg-gray-100 px-1 rounded">001_initial.sql</code></li>
          <li>Suba o <strong>backend</strong> no Railway ou Render (usa o <code className="bg-gray-100 px-1 rounded">Dockerfile</code>)</li>
          <li>Configure as env vars acima no painel da Vercel</li>
          <li>Deploy do <strong>frontend</strong> na Vercel apontando para o repo</li>
        </ol>
      </section>
    </div>
  );
}
