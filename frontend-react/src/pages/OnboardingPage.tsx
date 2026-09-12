import { useState } from 'react'
import { movieApi } from '../lib/api'

const genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Fantasy', 'Romance', 'Thriller', 'Mystery', 'Crime']

type Props = { username: string; onComplete: () => void }

export default function OnboardingPage({ username, onComplete }: Props) {
  const [selected, setSelected] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const save = async () => {
    setSaving(true)
    try {
      await movieApi.updatePreferences(selected)
      onComplete()
    } finally {
      setSaving(false)
    }
  }

  return <main className="grid min-h-screen place-items-center bg-[#0b1020] px-5 py-10 text-[#edf2ff]"><section className="w-full max-w-[620px] rounded-[26px] border border-white/10 bg-[#121926]/90 p-7 shadow-2xl shadow-black/30 sm:p-10"><div className="mb-8 flex items-center gap-3"><span className="grid h-12 w-12 place-items-center rounded-[15px] bg-gradient-to-br from-[#8066ff] to-[#16c8ee] font-bold">MV</span><span><strong className="block font-['Space_Grotesk'] text-xl">MovieVerse</strong><small className="text-[.65rem] tracking-[.16em] text-[#aebbd7]">PERSONAL CINEMA</small></span></div><div className="text-[.7rem] font-bold tracking-[.14em] text-[#cad3ee]">FIRST, YOUR TASTE</div><h1 className="mt-2 font-['Space_Grotesk'] text-3xl font-semibold">Welcome, {username}.</h1><p className="mt-3 max-w-lg text-[#aebbd7]">Pick a few genres you enjoy. This gives your first recommendations a thoughtful starting point.</p><div className="my-8 flex flex-wrap gap-2.5">{genres.map((genre) => <button key={genre} className={`rounded-full border px-4 py-2.5 text-sm transition ${selected.includes(genre) ? 'border-[#8066ff]/60 bg-[#8066ff]/30 text-white' : 'border-white/10 bg-white/[.04] text-[#aebbd7] hover:border-[#8066ff]/40'}`} onClick={() => setSelected((current) => current.includes(genre) ? current.filter((item) => item !== genre) : [...current, genre])}>{genre}</button>)}</div><button className="rounded-xl bg-gradient-to-br from-[#8066ff] to-[#16c8ee] px-5 py-3 font-bold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60" onClick={() => void save()} disabled={saving}>{saving ? 'Setting up your recommendations...' : selected.length ? 'Continue to MovieVerse' : 'Skip for now'}<span className="ml-2">→</span></button></section></main>
}
