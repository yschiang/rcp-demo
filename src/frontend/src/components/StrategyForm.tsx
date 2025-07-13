import React, { useState } from 'react'

export default function StrategyForm() {
  const [yamlText, setYamlText] = useState("")

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const text = await file.text()
      setYamlText(text)
    }
  }

  return (
    <div>
      <input type="file" accept=".yaml,.yml" onChange={handleUpload} />
      <pre style={{ backgroundColor: "#eee", padding: "1rem", marginTop: "1rem" }}>
        {yamlText}
      </pre>
    </div>
  )
}
