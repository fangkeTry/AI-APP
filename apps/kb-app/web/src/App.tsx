import { useEffect, useState } from 'react'
import { ArrowLeft, BookOpen, Check, FileText, Moon, Plus, Search, Sun, X } from 'lucide-react'

type NoteSummary = { title: string; updated?: string; snippet?: string }
type Note = { title: string; content: string; content_html: string }
type Theme = 'light' | 'dark'

async function api<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options)
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || '请求失败，请稍后重试')
  return data
}

export function App() {
  const [notes, setNotes] = useState<NoteSummary[]>([])
  const [selected, setSelected] = useState<Note | null>(null)
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [original, setOriginal] = useState('')
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('kb-theme') as Theme | null
    return saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  })

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('kb-theme', theme)
  }, [theme])

  async function loadList() {
    setLoading(true)
    try { setNotes((await api<{ notes: NoteSummary[] }>('/api/list')).notes); setError('') }
    catch (cause) { setError((cause as Error).message) }
    finally { setLoading(false) }
  }

  useEffect(() => { void loadList() }, [])
  useEffect(() => {
    const timer = window.setTimeout(async () => {
      if (!query.trim()) { void loadList(); return }
      try { setNotes((await api<{ results: NoteSummary[] }>('/api/search?q=' + encodeURIComponent(query))).results); setError('') }
      catch (cause) { setError((cause as Error).message) }
    }, 240)
    return () => clearTimeout(timer)
  }, [query])

  async function openNote(noteTitle: string) {
    try {
      const note = await api<Note>('/api/note?name=' + encodeURIComponent(noteTitle + '.md'))
      setSelected(note); setTitle(note.title); setContent(note.content); setOriginal(note.content)
      setEditing(false); setError(''); setNotice('')
    } catch (cause) { setError((cause as Error).message) }
  }

  function createNote() {
    setSelected(null); setTitle(''); setContent(''); setOriginal(''); setEditing(true); setError(''); setNotice('')
  }

  async function saveNote() {
    if (!title.trim()) { setError('请输入笔记标题'); return }
    setSaving(true); setError('')
    try {
      await api('/api/save', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title: title.trim(), content, original_content: selected?.title === title.trim() ? original : undefined }) })
      await loadList(); await openNote(title.trim()); setNotice('笔记已保存')
    } catch (cause) {
      const message = (cause as Error).message
      setError(message.includes('同名笔记') ? '保存冲突：已有同名但内容不同的笔记，请更换标题后再保存。' : message)
    } finally { setSaving(false) }
  }

  const showDetailOnMobile = Boolean(selected || editing)

  return <div className="mx-auto flex min-h-screen max-w-content flex-col px-lg pb-3xl sm:px-2xl">
    <header className="flex items-center gap-md py-xl sm:py-2xl">
      <span className="flex h-3xl w-3xl items-center justify-center rounded-md bg-accent text-on-accent"><BookOpen size={18} aria-hidden /></span>
      <div className="min-w-0 flex-1"><h1 className="m-0 text-xl font-semibold leading-tight">本地知识库</h1><p className="m-0 mt-xs text-sm text-text-secondary">Markdown 笔记，只留在本机</p></div>
      <button className="icon-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')} aria-label={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}>{theme === 'dark' ? <Sun size={19}/> : <Moon size={19}/>}</button>
      <button className="btn-primary" onClick={createNote}><Plus size={18}/><span className="hidden sm:inline">新建笔记</span><span className="sm:hidden">新建</span></button>
    </header>

    {error && <div role="alert" className="mb-lg flex items-start gap-sm rounded-md bg-danger-soft px-lg py-md text-sm text-danger"><span className="flex-1">{error}</span><button className="min-h-touch min-w-touch" onClick={() => setError('')} aria-label="关闭错误"><X size={17}/></button></div>}
    {notice && <div role="status" className="mb-lg flex items-center gap-sm rounded-md bg-accent-soft px-lg py-md text-sm text-accent"><Check size={17}/>{notice}</div>}

    <main className="grid min-h-0 flex-1 gap-lg md:grid-cols-[300px_minmax(0,1fr)]">
      <aside className={`${showDetailOnMobile ? 'hidden md:flex' : 'flex'} min-h-[60vh] flex-col rounded-lg border-hairline border-border bg-surface p-md shadow-card`}>
        <label className="relative block"><Search className="pointer-events-none absolute left-lg top-1/2 -translate-y-1/2 text-text-tertiary" size={18}/><input className="field pl-[44px]" value={query} onChange={event => setQuery(event.target.value)} placeholder="搜索标题或内容…" aria-label="搜索笔记"/></label>
        <div className="flex items-center justify-between px-sm pb-sm pt-xl"><h2 className="m-0 text-sm font-semibold">{query ? '搜索结果' : '最近笔记'}</h2><span className="rounded-pill bg-accent-soft px-md py-xs text-xs text-accent">{notes.length}</span></div>
        <div className="flex flex-col gap-xs overflow-y-auto">
          {loading ? <p className="px-sm text-sm text-text-secondary">正在读取笔记…</p> : notes.length === 0 ? <div className="px-sm py-3xl text-center"><FileText className="mx-auto mb-md text-text-tertiary"/><p className="m-0 text-sm text-text-secondary">{query ? '没有找到相关笔记' : '还没有笔记，写下第一篇吧'}</p></div> : notes.map(note => <button key={note.title} className={`min-h-touch rounded-md px-md py-md text-left transition-colors duration-fast hover:bg-surface-soft ${selected?.title === note.title ? 'bg-accent-soft' : ''}`} onClick={() => void openNote(note.title)}><span className="block truncate font-medium">{note.title}</span><span className="mt-xs block line-clamp-2 text-sm leading-normal text-text-secondary">{note.snippet || (note.updated ? new Date(note.updated).toLocaleString('zh-CN') : '')}</span></button>)}
        </div>
      </aside>

      <section className={`${showDetailOnMobile ? 'flex' : 'hidden md:flex'} min-h-[60vh] min-w-0 flex-col rounded-lg border-hairline border-border bg-surface p-lg shadow-card sm:p-2xl`}>
        {(selected || editing) && <button className="mb-lg flex min-h-touch items-center gap-sm self-start text-sm text-text-secondary md:hidden" onClick={() => { setSelected(null); setEditing(false) }}><ArrowLeft size={18}/>返回笔记</button>}
        {editing ? <>
          <div className="mb-xl"><p className="m-0 text-sm text-text-secondary">{selected ? '编辑笔记' : '新建笔记'}</p><h2 className="m-0 mt-xs text-2xl font-semibold">把想法记下来</h2></div>
          <label className="mb-lg block"><span className="mb-sm block text-sm font-medium">标题</span><input className="field text-lg font-medium" value={title} onChange={event => setTitle(event.target.value)} placeholder="给笔记起个名字" autoFocus/></label>
          <label className="flex min-h-0 flex-1 flex-col"><span className="mb-sm block text-sm font-medium">正文（Markdown）</span><textarea className="field min-h-[360px] flex-1 resize-y py-lg font-mono leading-normal" value={content} onChange={event => setContent(event.target.value)} placeholder={'# 从这里开始\n\n写下你的想法…'}/></label>
          <div className="mt-xl flex flex-wrap justify-end gap-sm"><button className="btn-ghost" onClick={() => selected ? void openNote(selected.title) : setEditing(false)}>取消</button><button className="btn-primary" disabled={saving} onClick={() => void saveNote()}>{saving ? '保存中…' : '保存笔记'}</button></div>
        </> : selected ? <>
          <div className="mb-xl flex items-start gap-lg border-b-hairline border-border pb-xl"><div className="min-w-0 flex-1"><p className="m-0 text-sm text-text-secondary">笔记</p><h2 className="m-0 mt-xs break-words text-2xl font-semibold leading-tight sm:text-3xl">{selected.title}</h2></div><button className="btn-ghost shrink-0" onClick={() => setEditing(true)}>编辑</button></div>
          <article className="prose-kb" dangerouslySetInnerHTML={{ __html: selected.content_html }}/>
        </> : <div className="m-auto max-w-[420px] py-3xl text-center"><span className="mx-auto mb-xl flex h-[56px] w-[56px] items-center justify-center rounded-lg bg-accent-soft text-accent"><FileText size={25}/></span><h2 className="m-0 text-2xl font-semibold">打开一篇笔记</h2><p className="mb-xl mt-md text-text-secondary">从左侧选择已有笔记，或创建一篇新的 Markdown 笔记。</p><button className="btn-primary" onClick={createNote}><Plus size={18}/>新建笔记</button></div>}
      </section>
    </main>
  </div>
}
