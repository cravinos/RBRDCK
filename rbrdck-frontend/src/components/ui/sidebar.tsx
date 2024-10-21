import Link from 'next/link'
import { Home, GitPullRequest, Folder, Users } from 'lucide-react'

export function Sidebar() {
  return (
    <div className="flex h-screen w-64 flex-col bg-gray-100 p-3">
      <div className="mb-6 flex items-center space-x-2">
        <Home className="h-6 w-6" />
        <span className="text-xl font-bold">RBRDCK</span>
      </div>
      <nav className="space-y-2">
        <Link href="/" className="flex items-center space-x-2 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-200">
          <GitPullRequest className="h-5 w-5" />
          <span>Pull Requests</span>
        </Link>
        <Link href="/projects" className="flex items-center space-x-2 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-200">
          <Folder className="h-5 w-5" />
          <span>Projects</span>
        </Link>
        <Link href="/groups" className="flex items-center space-x-2 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-200">
          <Users className="h-5 w-5" />
          <span>User Groups</span>
        </Link>
      </nav>
    </div>
  )
}