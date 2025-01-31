"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import { ArrowUp, Paperclip, Calendar, Globe, Mic } from "lucide-react"

interface ChatProps {
  selectedFile: string | null
  fileContent: string
}

export function Chat({ selectedFile, fileContent }: ChatProps) {
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI tutor. I can help you understand and improve your code. Select a file to get started!",
    },
  ])
  const [input, setInput] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setMessages((prev) => [
      ...prev,
      { role: "user", content: input },
      {
        role: "assistant",
        content: `I see you're working with ${selectedFile}. Let me help you understand this code better...`,
      },
    ])
    setInput("")
  }

  const handleFileUpload = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 px-6">
        <div className="max-w-3xl mx-auto py-6 space-y-6">
          {messages.map((message, i) => (
            <div
              key={i}
              className={`rounded-lg p-4 ${
                message.role === "assistant"
                  ? "bg-zinc-800/50 text-white"
                  : "ml-auto max-w-[80%] bg-blue-600 text-white"
              }`}
            >
              {message.content}
            </div>
          ))}
        </div>
      </ScrollArea>
      <div className="border-t border-zinc-800 bg-black p-6">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={sendMessage} className="flex flex-col gap-3">
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={(e) => {
                // Handle file upload
                console.log(e.target.files)
              }}
              multiple
            />
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message CodeTutor..."
              className="min-h-[44px] flex-1 resize-none bg-zinc-800/50 border-zinc-700 text-white"
            />
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="h-9 w-9 hover:bg-zinc-800"
                  onClick={handleFileUpload}
                >
                  <Paperclip className="h-5 w-5" />
                </Button>
                <Button type="button" size="icon" variant="ghost" className="h-9 w-9 hover:bg-zinc-800">
                  <Calendar className="h-5 w-5" />
                </Button>
                <Button type="button" size="icon" variant="ghost" className="h-9 w-9 hover:bg-zinc-800">
                  <Globe className="h-5 w-5" />
                </Button>
              </div>
              <div className="flex-1" />
              <Button type="button" size="icon" variant="ghost" className="h-9 w-9 hover:bg-zinc-800">
                <Mic className="h-5 w-5" />
              </Button>
              <Button type="submit" size="icon" className="h-9 w-9 bg-white text-black hover:bg-zinc-200">
                <ArrowUp className="h-5 w-5" />
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

