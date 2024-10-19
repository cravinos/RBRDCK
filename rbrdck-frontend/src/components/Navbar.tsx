import React from 'react'
import { Button } from "./ui/Button"

export default function Navbar() {
  return (
    <nav className="bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <a href="/" className="text-xl font-bold">
            RBRDCK
          </a>
          <ul className="flex space-x-4">
            <li>
              <Button asChild className="text-primary-foreground hover:text-primary-foreground/80">
                <a href="/">Home</a>
              </Button>
            </li>
            <li>
              <Button asChild className="text-primary-foreground hover:text-primary-foreground/80">
                <a href="/projects">Projects</a>
              </Button>
            </li>
            <li>
              <Button asChild className="text-primary-foreground hover:text-primary-foreground/80">
                <a href="/pull-requests">Pull Requests</a>
              </Button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  )
}