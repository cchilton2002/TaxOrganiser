import React, { useRef, useState } from 'react'
import axios from 'axios';


const Upload = () => {
  const [userId, setUserId] = useState("");
  const [file, setFile] = useState([]);
  const [message, setMessage] = useState("");
  const fileInputRef = useRef(null);

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!userId || file.length===0){
      setMessage("Please enter a user_id and upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("user_id", userId);
    file.forEach((f) => {
      formData.append("files", f);
    });

    try {
      const response = await axios.post("/api/upload", formData);
      setMessage(response.data.message || "Upload successful");

    } catch (err) {
      console.error(err)
      setMessage("Error uploading file.")
    }
  }

  const handleFileDelete = () => {
    setFile([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = null;
    }
  };


  return (
    <div className="p-6 bg-white rounded-xl shadow-md max-w-xl mx-auto mt-8">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Upload Payslip</h2>

      <form onSubmit={handleUpload} className="flex flex-col gap-4">
        <input
          type="text"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />

        <div className="flex flex-row gap-2">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="bg-blue-100 text-blue-700 font-medium px-4 py-2 rounded hover:bg-blue-200 transition"
            >
              Choose File
            </button>
            {file.length > 0 ? (
              <ul className="text-sm text-gray-600 space-y-1">
                {file.map((f, idx) => (
                  <li key={idx}>• {f.name}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-600">No file selected</p>
            )}

            {file.length > 0 && (
              <button
                type="button"
                onClick={handleFileDelete}
                className="text-red-500 hover:text-red-700 text-xl font-bold focus:outline-none"
                aria-label="Remove file"
              >
                ×
              </button>
            )}
          </div>
          <input
            type="file"
            accept=".pdf"
            multiple
            ref={fileInputRef}
            onChange={(e) => {
              const selectedFiles = Array.from(e.target.files);
              setFile((prevFiles) => [...prevFiles, ...selectedFiles]);
            }}
            style={{ display: "none" }}
          />
        </div>

        <button
          type="submit"
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition"
        >
          Upload
        </button>
      </form>

      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </div>

  )
}

export default Upload
