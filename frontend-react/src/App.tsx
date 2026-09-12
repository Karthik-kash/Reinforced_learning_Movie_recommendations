import { useEffect, useMemo, useState } from 'react'
import { apiRequest, movieApi } from './lib/api'
import type { Dashboard, Movie, Page, Profile } from './types'
import TopNav from './components/TopNav'
import HeroPanel from './components/HeroPanel'
import PageHeading from './components/PageHeading'
import { ApiAlert, EmptyState, LoadingState } from './components/FeedbackStates'
import LibraryPage from './pages/LibraryPage'
import DashboardPage from './pages/DashboardPage'
import ProfilePage from './pages/ProfilePage'
import AuthScreen from './components/AuthScreen'
import OnboardingPage from './pages/OnboardingPage'
import { authApi, type AuthResponse, type AuthUser } from './auth/authApi'

const pageTitles: Record<Page, string> = {
  Recommendations: 'Curated for your next watch',
  Search: 'Find something worth watching',
  Watchlist: 'Your saved cinema',
  History: 'Your viewing trail',
  Dashboard: 'Taste, measured',
  Profile: 'Shape your cinema profile',
}

function App() {
  const [authUser, setAuthUser] = useState<AuthUser | null>(null)
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [page, setPage] = useState<Page>('Recommendations')
  const [query, setQuery] = useState('')
  const [movies, setMovies] = useState<Movie[]>([])
  const [profile, setProfile] = useState<Profile | null>(null)
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')

  const loadPage = async (nextPage: Page, nextQuery = query) => {
    setLoading(true)
    setError('')
    try {
      if (nextPage === 'Recommendations') setMovies(await movieApi.recommendations())
      if (nextPage === 'Search' && nextQuery.trim()) setMovies((await movieApi.search(nextQuery)).items)
      if (nextPage === 'Watchlist') setMovies(await movieApi.watchlist())
      if (nextPage === 'History') setMovies(await movieApi.history())
      if (nextPage === 'Profile') setProfile(await movieApi.profile())
      if (nextPage === 'Dashboard') setDashboard(await movieApi.dashboard())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Could not connect to MovieVerse API.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!sessionStorage.getItem('movieverse_access_token')) {
      return
    }
    void authApi.me()
      .then((user) => {
        setAuthUser(user)
        return movieApi.recommendations()
      })
      .then(setMovies)
      .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : 'Could not connect to MovieVerse API.'))
      .finally(() => setLoading(false))
  }, [])

  const handleAuthenticated = (response: AuthResponse, isNewAccount: boolean) => {
    sessionStorage.setItem('movieverse_access_token', response.access_token)
    setAuthUser(response.user)
    setShowOnboarding(isNewAccount)
    setPage('Recommendations')
    if (!isNewAccount) void loadPage('Recommendations')
  }

  const logout = () => {
    sessionStorage.removeItem('movieverse_access_token')
    setAuthUser(null)
    setMovies([])
    setProfile(null)
    setDashboard(null)
  }

  const navigate = (nextPage: Page) => {
    setPage(nextPage)
    if (nextPage !== 'Search') setQuery('')
    void loadPage(nextPage)
  }

  const performAction = async (path: string, method = 'POST', body?: object) => {
    try {
      await apiRequest(path, { method, body: body ? JSON.stringify(body) : undefined })
      setToast('Your cinema profile has been updated.')
      window.setTimeout(() => setToast(''), 2400)
      void loadPage(page, query)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'That action could not be completed.')
    }
  }

  const watchlistIds = useMemo(() => new Set(profile?.watchlist ?? []), [profile])
  const hasLibraryPage = page === 'Recommendations' || page === 'Search' || page === 'Watchlist' || page === 'History'
  const searchIsEmpty = page === 'Search' && !query

  if (!authUser && !sessionStorage.getItem('movieverse_access_token')) return <AuthScreen onAuthenticated={handleAuthenticated} />
  if (showOnboarding && authUser) return <OnboardingPage username={authUser.username} onComplete={() => { setShowOnboarding(false); void loadPage('Recommendations') }} />

  return <div className="min-h-screen bg-[#0b1020] text-[#edf2ff]">
    <TopNav page={page} username={authUser?.username ?? 'Viewer'} isDemo={authUser?.is_demo ?? false} onNavigate={navigate} onLogout={logout} />
    <main className="mx-auto mb-20 mt-8 w-[calc(100%-2rem)] max-w-[1400px] sm:w-[calc(100%-3rem)]">
      <HeroPanel />
      <PageHeading page={page} title={pageTitles[page]} query={query} onQueryChange={setQuery} onSearch={() => void loadPage('Search', query)} />
      {error && <ApiAlert message={error} />}
      {toast && <div className="fixed bottom-6 right-6 z-20 rounded-[15px] border border-[#48dcb8]/30 bg-[#0f2c2b]/95 px-5 py-4 text-sm text-[#dffdf4] shadow-2xl">{toast}</div>}
      {loading && <LoadingState />}
      {!loading && searchIsEmpty && <EmptyState title="Start with a title or genre." message="Search the full movie catalog to find your next watch." />}
      {!loading && hasLibraryPage && !searchIsEmpty && <LibraryPage page={page as 'Recommendations' | 'Search' | 'Watchlist' | 'History'} movies={movies} watchlistIds={watchlistIds} onWatched={(id) => void performAction(`/interactions/${id}/watched`)} onToggleWatchlist={(id) => void performAction(`/interactions/${id}/watchlist`, watchlistIds.has(id) ? 'DELETE' : 'POST')} onRate={(id, rating) => void performAction(`/interactions/${id}/rating`, 'POST', { rating })} />}
      {!loading && page === 'Dashboard' && dashboard && <DashboardPage data={dashboard} />}
      {!loading && page === 'Profile' && profile && authUser && <ProfilePage profile={profile} user={authUser} onSaved={() => { setToast('Preferences saved. Recommendations will adapt from here.'); navigate('Recommendations') }} />}
    </main>
  </div>
}

export default App
