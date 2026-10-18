/** Hero 區塊：Server Component（純靜態，無狀態） */
export default function Hero() {
  return (
    <section
      aria-labelledby="hero-title"
      className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 text-white"
    >
      <div className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-6 py-20 md:py-28 lg:grid-cols-2">
        <div className="text-center lg:text-left">
          <p className="mb-4 inline-block rounded-full bg-white/15 px-3 py-1 text-sm font-medium">
            全新 2.0 版上線
          </p>
          <h1
            id="hero-title"
            className="text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl lg:text-6xl"
          >
            讓團隊協作快十倍
          </h1>
          <p className="mt-6 text-lg text-white/85 sm:text-xl">
            一個平台整合任務、文件與自動化，把重複工作交給系統，專注在真正重要的事。
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start">
            <a
              href="#signup"
              className="rounded-lg bg-white px-6 py-3 text-center font-semibold text-indigo-700 shadow-lg transition duration-200 hover:-translate-y-0.5 hover:scale-105 hover:shadow-xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              免費試用
            </a>
            <a
              href="#demo"
              className="rounded-lg border-2 border-white/80 px-6 py-3 text-center font-semibold text-white transition duration-200 hover:-translate-y-0.5 hover:bg-white/10 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              查看 Demo
            </a>
          </div>
        </div>

        {/* 裝飾用產品示意圖，對螢幕閱讀器隱藏；桌面才顯示形成雙欄 */}
        <div aria-hidden="true" className="hidden lg:block">
          <div className="rounded-2xl bg-white/10 p-6 shadow-2xl ring-1 ring-white/20 backdrop-blur">
            <div className="mb-4 flex gap-2">
              <span className="h-3 w-3 rounded-full bg-red-400" />
              <span className="h-3 w-3 rounded-full bg-yellow-300" />
              <span className="h-3 w-3 rounded-full bg-green-400" />
            </div>
            <div className="space-y-3">
              <div className="h-4 w-3/4 rounded bg-white/40" />
              <div className="h-4 w-1/2 rounded bg-white/30" />
              <div className="grid grid-cols-3 gap-3 pt-4">
                <div className="h-20 rounded-lg bg-white/25" />
                <div className="h-20 rounded-lg bg-white/35" />
                <div className="h-20 rounded-lg bg-white/25" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
