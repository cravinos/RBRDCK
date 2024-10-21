import { UserGroups } from '@/components/user-groups'

export default function GroupsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">User Groups</h1>
      <UserGroups />
    </div>
  )
}