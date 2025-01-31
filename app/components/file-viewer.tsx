"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

interface FileViewerProps {
  filename: string
  content: string
  onContentChange: (content: string) => void
}

export function FileViewer({ filename, content, onContentChange }: FileViewerProps) {
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="flex h-1/2 flex-col border-b border-zinc-800">
      <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-2 bg-black">
        <span className="text-sm font-[system-ui]">{filename}</span>
        <Button variant="ghost" size="sm" className="h-7 px-2 text-sm" onClick={() => setIsEditing(!isEditing)}>
          {isEditing ? "Save" : "Edit"}
        </Button>
      </div>
      <ScrollArea className="flex-1 p-6">
        {isEditing ? (
          <textarea
            className="h-full w-full bg-black font-mono text-sm text-white"
            value={content}
            onChange={(e) => onContentChange(e.target.value)}
          />
        ) : (
          <pre className="font-mono text-sm">
            <code>{content}</code>
          </pre>
        )}
      </ScrollArea>
    </div>
  )
}

