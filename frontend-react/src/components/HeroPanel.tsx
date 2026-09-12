export default function HeroPanel() {
  return <section className="relative min-h-[280px] overflow-hidden rounded-[26px] border border-white/10 bg-[linear-gradient(115deg,rgba(91,70,191,.42),rgba(14,88,117,.24)_48%,rgba(88,48,73,.3))] p-7 shadow-2xl shadow-black/20 sm:p-10">
    <div className="relative z-[1] text-[.7rem] font-bold tracking-[.14em] text-[#cad3ee]">SMART CINEMA / 2026</div>
    <h1 className="relative z-[1] mt-5 font-['Space_Grotesk'] text-[clamp(2.5rem,5vw,4.6rem)] font-bold leading-[1.03] tracking-[-.05em] text-white">Discover the next<br /><em className="not-italic text-[#c7c0ff]">movie you will love.</em></h1>
    <p className="relative z-[1] mt-4 max-w-xl text-base text-[#bdc8e3]">Personalized picks, gentle learning, and a smarter watchlist built around your taste.</p>
    <div className="absolute -right-16 -top-28 h-[390px] w-[390px] rounded-full border border-white/10 shadow-[0_0_100px_rgba(22,200,238,.12)]" /><div className="absolute right-20 -top-9 h-[230px] w-[230px] rounded-full border border-[#8066ff]/30" />
  </section>
}
