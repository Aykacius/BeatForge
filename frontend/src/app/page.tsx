"use client"

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-5xl font-bold gradient-primary bg-clip-text text-transparent mb-4">
          BeatForge
        </h1>
        <p className="text-xl text-slate-300 mb-8">
          Generate osu!standard beatmaps from MP3 files
        </p>
        <a
          href="/upload"
          className="button-primary inline-block"
        >
          Get Started
        </a>
      </div>
    </div>
  )
}
