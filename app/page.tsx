"use client"

import { useState, useRef } from "react"
import { FileExplorer } from "./components/file-explorer"
import { FileViewer } from "./components/file-viewer"
import { Chat } from "./components/chat"
import { Resources } from "./components/resources"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"

export default function CodeTutor() {
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>("")
  const [isCodePanelOpen, setIsCodePanelOpen] = useState(true)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (path: string, content: string) => {
    setSelectedFile(path)
    setFileContent(content)
  }

  return (
    <div className="flex h-screen bg-black text-white">
      {/* File Explorer */}
      <div
        className={`${
          isCodePanelOpen ? "w-72" : "w-0"
        } border-r border-zinc-800 transition-all duration-300 overflow-hidden`}
      >
        <div className="flex items-center justify-between p-3 border-b border-zinc-800">
          <span className="font-medium text-sm">Explorer</span>
          <Button variant="ghost" size="sm" className="h-6 w-6" onClick={() => setIsCodePanelOpen(!isCodePanelOpen)}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>
        <FileExplorer onFileSelect={handleFileSelect} />
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {!isCodePanelOpen && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute left-0 top-3 m-2 h-6 w-6"
            onClick={() => setIsCodePanelOpen(true)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        )}

        <ResizablePanelGroup direction="vertical">
          <ResizablePanel defaultSize={50}>
            {selectedFile && (
              <FileViewer filename={selectedFile} content={fileContent} onContentChange={setFileContent} />
            )}
          </ResizablePanel>
          <ResizablePanel defaultSize={50}>
            <div className="h-full border-t border-zinc-800">
              <Tabs defaultValue="chat" className="h-full">
                <div className="border-b border-zinc-800 px-4">
                  <TabsList className="bg-transparent">
                    <TabsTrigger value="chat" className="data-[state=active]:bg-zinc-800">
                      Chat
                    </TabsTrigger>
                    <TabsTrigger value="resources" className="data-[state=active]:bg-zinc-800">
                      Resources
                    </TabsTrigger>
                  </TabsList>
                </div>
                <TabsContent value="chat" className="h-[calc(100%-45px)]">
                  <Chat selectedFile={selectedFile} fileContent={fileContent} />
                </TabsContent>
                <TabsContent value="resources" className="h-[calc(100%-45px)]">
                  <Resources selectedFile={selectedFile} />
                </TabsContent>
              </Tabs>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  )
}

