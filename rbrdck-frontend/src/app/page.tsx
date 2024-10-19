import { PullRequests } from '@/components/ui/pull-requests'

export default function Home() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Pull Requests</h1>
      <PullRequests />
    </div>
  )
}