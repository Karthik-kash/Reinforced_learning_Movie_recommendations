import type { Page } from '../types'

type Props = { page: Page; title: string; query: string; onQueryChange: (value: string) => void; onSearch: () => void }

export default function PageHeading({ page, title, query, onQueryChange, onSearch }: Props) {
  return <section className="mb-5 mt-10 flex flex-col items-stretch justify-between gap-5 sm:flex-row sm:items-end"><div><div className="text-[.7rem] font-bold tracking-[.14em] text-[#cad3ee]">{page === 'Profile' ? 'PREFERENCES' : 'YOUR SPACE'}</div><h2 className="mt-1.5 font-['Space_Grotesk'] text-2xl font-semibold tracking-[-.03em] text-white sm:text-[2rem]">{title}</h2></div>{page === 'Search' && <form className="flex min-w-0 items-center gap-2 rounded-[13px] border border-white/10 bg-[#080d17]/70 p-1.5 pl-3.5 text-[#aebbd7] sm:min-w-[420px]" onSubmit={(event) => { event.preventDefault(); onSearch() }}><span>⌕</span><input autoFocus className="w-full bg-transparent text-white outline-none placeholder:text-[#7081a8]" value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search titles or genres" /><button className="rounded-[9px] bg-gradient-to-br from-[#8066ff] to-[#16c8ee] px-3.5 py-2 text-sm font-bold text-white" type="submit">Search</button></form>}</section>
}
